import os
import re
import threading
import time

import psycopg

from dashboard_geo_index import build_geo_index

_CACHE = {}
_CACHE_LOCK = threading.Lock()
CACHE_SECONDS = max(30, int(os.getenv("REGISTER_COUNT_CACHE_SECONDS", "120")))
_GEO_INDEX = None


def _norm(value):
    return re.sub(r"[-_\s]+", " ", str(value or "").strip().lower()).strip()


def _scope_polling_stations(county="", constituency="", ward=""):
    global _GEO_INDEX
    if _GEO_INDEX is None:
        filename = os.getenv("COUNTY_MAIN_FILENAME", "county_main.csv").strip()
        _GEO_INDEX = build_geo_index(os.path.join(os.path.dirname(__file__), filename))
    wanted = (_norm(county), _norm(constituency), _norm(ward))
    return sorted({
        _norm(geo.get("poll_station"))
        for geo in _GEO_INDEX.get("by_stream", {}).values()
        if (not wanted[0] or _norm(geo.get("county")) == wanted[0])
        and (not wanted[1] or _norm(geo.get("constituency")) == wanted[1])
        and (not wanted[2] or _norm(geo.get("ward")) == wanted[2])
        and _norm(geo.get("poll_station"))
    })


def count_registered_voters(county="", constituency="", ward="", poll_station=""):
    """Count the authoritative active PostgreSQL master register directly."""
    cache_key = tuple(_norm(v) for v in (county, constituency, ward, poll_station))
    with _CACHE_LOCK:
        cached = _CACHE.get(cache_key)
    if cached and time.monotonic() - cached[0] < CACHE_SECONDS:
        return cached[1]

    database_url = (
        os.getenv("MASTER_REGISTER_DATABASE_URL", "").strip()
        or os.getenv("DATABASE_URL", "").strip()
    )
    if not database_url:
        raise RuntimeError(
            "MASTER_REGISTER_DATABASE_URL is not configured on this results dashboard."
        )
    if database_url.startswith("postgres://"):
        database_url = "postgresql://" + database_url[len("postgres://"):]

    # master_voters already has partial indexes on LOWER(county),
    # LOWER(constituency), LOWER(ward) and LOWER(polling_station) WHERE active.
    # Do not wrap those columns in REGEXP_REPLACE/TRIM here: doing so forces a
    # full-table scan and caused county requests to exceed the old 5s timeout.
    def indexed(column):
        return "LOWER(" + column + ")"

    branches = []
    params = []

    def add_direct(fields):
        predicates = ["active"]
        for column, value in fields:
            if value:
                predicates.append(indexed(column) + " = %s")
                params.append(_norm(value))
        branches.append(
            "SELECT national_id FROM master_voters WHERE " +
            " AND ".join(predicates)
        )

    def add_stations(stations):
        if stations:
            branches.append(
                "SELECT national_id FROM master_voters WHERE active AND " +
                indexed("polling_station") + " = ANY(%s)"
            )
            params.append(stations)

    if poll_station:
        add_direct((("polling_station", poll_station),))
    elif ward:
        stations = _scope_polling_stations(county, constituency, ward)
        add_direct((("county", county), ("constituency", constituency),
                    ("ward", ward)))
        add_stations(stations)
    elif constituency:
        stations = _scope_polling_stations(county, constituency)
        add_direct((("county", county), ("constituency", constituency)))
        add_stations(stations)
    elif county:
        stations = _scope_polling_stations(county)
        add_direct((("county", county),))
        add_stations(stations)
    else:
        add_direct(())

    # Keep indexed branches separate. PostgreSQL was choosing a sequential
    # scan for `county = value OR polling_station = ANY(...)`, even though each
    # side has a suitable partial index. UNION lets each branch use its own
    # index and removes duplicate voter IDs before the final count.
    sql = "SELECT COUNT(*) FROM (" + " UNION ".join(branches) + ") AS scoped_voters"
    with psycopg.connect(database_url, connect_timeout=3, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SET statement_timeout TO '30s'")
            cursor.execute("SET default_transaction_read_only TO on")
            cursor.execute("SET enable_seqscan TO off")
            cursor.execute(sql, params)
            row = cursor.fetchone()
    result = int((row or [0])[0] or 0)
    with _CACHE_LOCK:
        _CACHE[cache_key] = (time.monotonic(), result)
    return result

