NON-BLOCKING RESULTS AND REGISTER COUNT FIX

Deploy every package to its matching results-dashboard service.

Each dashboard still reads the authoritative active voter total directly from
PostgreSQL. Successful counts are cached for two minutes. A slow or unavailable
database count can no longer prevent closed-stream votes, candidates and stream
statistics from rendering; the dashboard falls back to the voting API's last
PostgreSQL-backed register breakdown for that request.

Set MASTER_REGISTER_DATABASE_URL on every dashboard service to the same Render
PostgreSQL Internal Database URL used by the voting system.
