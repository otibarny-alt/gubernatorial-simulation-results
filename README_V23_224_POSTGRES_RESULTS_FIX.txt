POSTGRESQL RESULTS SOURCE FIX

Deploy the V23.224 voting-system package first, then deploy each matching
dashboard package.

On every dashboard Render service, set MASTER_REGISTER_DATABASE_URL to the
same PostgreSQL Internal Database URL used by the voting system. Redeploy after
saving the variable.

The dashboards now count active voters directly from master_voters with the
selected county, constituency, ward and polling-station filters.

The voting API now requests candidates using the electoral area found in the
durable vote records. Unfiltered candidate requests previously returned only
national candidates, which caused Governor, Senator, Woman Representative, MNA
and MCA dashboards to show no candidate rows.

Only formally CLOSED streams contribute votes and participation totals.
