import csv
import re
from collections import defaultdict


def _norm(value):
    return re.sub(r"[-_\s]+", " ", str(value or "").strip().lower()).strip()


def _friendly(value):
    text = str(value or "").strip()
    return re.sub(r"\s+", " ", re.sub(r"[_-]+", " ", text)).title() if text else ""


def build_geo_index(path):
    """Build a duplicate-safe county_main hierarchy and stream count index."""
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as handle:
        rows = list(csv.DictReader(handle))

    counties = {_norm(r.get("name")): r for r in rows if r.get("list_name") == "county"}
    constituencies = [r for r in rows if r.get("list_name") == "constituency"]
    constituency_by_name = {_norm(r.get("name")): r for r in constituencies}
    constituency_by_number = {f"{i:03d}": r for i, r in enumerate(constituencies, 1)}
    wards_by_name = defaultdict(list)
    for row in rows:
        if row.get("list_name") == "ward":
            wards_by_name[_norm(row.get("name"))].append(row)

    stations_by_name = defaultdict(list)
    for row in rows:
        if row.get("list_name") != "poll_station":
            continue
        code = str(row.get("poll_station_code") or "").strip()
        try:
            padded = str(round(float(code))).zfill(12)
        except Exception:
            padded = ""
        coded_constituency = constituency_by_number.get(padded[2:5]) if len(padded) >= 5 else None
        ward_options = wards_by_name.get(_norm(row.get("ward_key")), [])
        ward = next((w for w in ward_options
                     if coded_constituency and _norm(w.get("constituency_key")) == _norm(coded_constituency.get("name"))), None)
        ward = ward or (ward_options[0] if ward_options else None)
        constituency = constituency_by_name.get(_norm((ward or {}).get("constituency_key"))) or coded_constituency
        county = counties.get(_norm((constituency or {}).get("county_key")))
        station = dict(row)
        station.update(_county=county or {}, _constituency=constituency or {}, _ward=ward or {})
        stations_by_name[_norm(row.get("name"))].append(station)

    stream_groups = []
    for row in (r for r in rows if r.get("list_name") == "poll_station_stream"):
        key = _norm(row.get("poll_station_key"))
        if not stream_groups or stream_groups[-1][0] != key:
            stream_groups.append((key, []))
        stream_groups[-1][1].append(row)

    occurrences = defaultdict(int)
    geographies = []
    for key, stream_rows in stream_groups:
        candidates = stations_by_name.get(key, [])
        occurrence = occurrences[key]
        occurrences[key] += 1
        station = candidates[min(occurrence, len(candidates) - 1)] if candidates else {}
        county = station.get("_county", {})
        constituency = station.get("_constituency", {})
        ward = station.get("_ward", {})
        for stream in stream_rows:
            geographies.append({
                "county": county.get("name", ""),
                "county_label": county.get("label") or _friendly(county.get("name")),
                "constituency": constituency.get("name", ""),
                "constituency_label": constituency.get("label") or _friendly(constituency.get("name")),
                "ward": ward.get("name", ""),
                "ward_label": ward.get("label") or _friendly(ward.get("name")),
                "poll_station": station.get("name", ""),
                "stream": stream.get("name", ""),
            })

    counties_ui = {}
    constituencies_ui = defaultdict(dict)
    wards_ui = defaultdict(dict)
    expected_by_filter = defaultdict(list)
    by_stream = {}
    for index, geo in enumerate(geographies):
        ck, cok, wk = _norm(geo["county"]), _norm(geo["constituency"]), _norm(geo["ward"])
        stream_identity = "|".join((_norm(geo["poll_station"]), _norm(geo["stream"]), str(index)))
        by_stream[stream_identity] = geo
        if ck:
            counties_ui[ck] = {"value": geo["county"], "label": geo["county_label"]}
        if ck and cok:
            constituencies_ui[ck][cok] = {"value": geo["constituency"], "label": geo["constituency_label"]}
        if ck and cok and wk:
            wards_ui[(ck, cok)][wk] = {"value": geo["ward"], "label": geo["ward_label"]}
        for filter_key in set((("", "", ""), (ck, "", ""), (ck, cok, ""), (ck, cok, wk))):
            expected_by_filter[filter_key].append(stream_identity)
    return {"by_stream": by_stream, "counties_ui": counties_ui,
            "constituencies_ui": constituencies_ui, "wards_ui": wards_ui,
            "expected_by_filter": expected_by_filter}
