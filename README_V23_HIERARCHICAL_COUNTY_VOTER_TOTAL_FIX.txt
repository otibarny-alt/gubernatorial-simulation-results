V23 - HIERARCHICAL COUNTY REGISTER TOTAL FIX

The Registered Voters card now counts a selected county from the authoritative
PostgreSQL master_voters register using both:

1. the normalized county field; and
2. every polling station mapped to that county in county_main.csv.

Constituency and ward totals use the same parent-aware station mapping. This
prevents a county total from being smaller than one of its constituencies or
wards when legacy voter rows have blank, inconsistent or differently formatted
geography fields but a valid polling station.

RENDER CONFIGURATION

Set MASTER_REGISTER_DATABASE_URL on this Gubernatorial Results Dashboard to the
same Render PostgreSQL Internal Database URL used by the voting system, then
redeploy this package.
