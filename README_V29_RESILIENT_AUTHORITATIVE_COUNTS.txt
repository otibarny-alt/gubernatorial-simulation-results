V29 - RESILIENT AUTHORITATIVE VOTER COUNTS

The results dashboard still uses the Voting System Voters Register count API
as its sole source of registered-voter totals.

Changes:
- Converts URL keys such as west_pokot and pokot_south to the register's human
  geography values (West Pokot and Pokot South) before requesting a count.
- Retries temporary HTTP 502/503/504 responses up to three times.
- Caches successful counts for ten minutes.
- If Render briefly returns an upstream error, retains the last successful
  count instead of replacing it with "Unavailable".

Expected West Pokot constituency counts supplied by the register comparison:
Kapenguria 24,867; Kacheliba 21,231; Pokot South 20,308; Sigor 14,656.
