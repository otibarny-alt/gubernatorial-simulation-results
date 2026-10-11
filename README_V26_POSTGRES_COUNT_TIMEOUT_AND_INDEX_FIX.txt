V26 - POSTGRESQL REGISTER COUNT TIMEOUT AND INDEX FIX

The Render log identified the exact failure:

    psycopg.errors.QueryCanceled: canceling statement due to statement timeout

The county count previously applied REGEXP_REPLACE and TRIM to every geography
column. PostgreSQL therefore could not use the existing master_voters indexes
and the query exceeded the dashboard's five-second statement timeout.

V26 changes the count to:

- use the indexed LOWER(county), LOWER(constituency), LOWER(ward) and
  LOWER(polling_station) expressions;
- use the partial indexes restricted to active voter rows;
- use COUNT(*) because national_id is already unique in master_voters; and
- allow up to 30 seconds as a safety ceiling.

Candidate results, votes, participation and streams remain independent from
the registered-voter count as introduced in V25.
