V25 - RESULTS REMAIN VISIBLE WHEN REGISTER COUNT IS UNAVAILABLE

- Candidate votes, skipped votes, participants and stream statistics now load
  independently from the PostgreSQL registered-voter count.
- A missing or unreachable MASTER_REGISTER_DATABASE_URL no longer causes the
  complete dashboard response to fail and reset every result to zero.
- Affected register-dependent cards display "Unavailable" until PostgreSQL is
  configured, instead of showing a false zero or partial fallback total.
- The direct PostgreSQL county-count correction from V24 remains in place.

Set MASTER_REGISTER_DATABASE_URL on the Gubernatorial Results Dashboard to the
voting system PostgreSQL Internal Database URL to restore the registered-voter,
turnout, votes-not-cast and skipped/registered cards.
