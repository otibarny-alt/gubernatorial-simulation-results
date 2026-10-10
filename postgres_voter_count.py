import os
import re

import psycopg


def _norm(value):
    return re.sub(r"[-_\s]+", " ", str(value or "").strip().lower()).strip()


def count_registered_voters(county="", constituency="", ward="", poll_station=""):
    """Count the authoritative active PostgreSQL master register directly."""
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

    clauses = ["COALESCE(active, TRUE) IS TRUE"]
    params = []
    for column, value in (
        ("county", county),
        ("constituency", constituency),
        ("ward", ward),
        ("polling_station", poll_station),
    ):
        if value:
            clauses.append(
                "LOWER(REGEXP_REPLACE(TRIM(COALESCE(" + column + ", '')), "
                "'[[:space:]_-]+', ' ', 'g')) = %s"
            )
            params.append(_norm(value))

    sql = (
        "SELECT COUNT(DISTINCT national_id) FROM master_voters WHERE "
        + " AND ".join(clauses)
    )
    with psycopg.connect(database_url, connect_timeout=8, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SET statement_timeout TO '20s'")
            cursor.execute("SET default_transaction_read_only TO on")
            cursor.execute(sql, params)
            row = cursor.fetchone()
    return int((row or [0])[0] or 0)

