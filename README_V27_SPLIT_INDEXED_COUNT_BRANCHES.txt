V27 - SPLIT INDEXED POSTGRESQL COUNT BRANCHES

The V26 query still timed out because PostgreSQL chose one slow plan for the
combined county OR polling-station condition.

V27 performs the county count as two independent indexed branches:

1. active voters whose LOWER(county) matches the selected county; and
2. active voters whose LOWER(polling_station) is in that county's station list.

The branches are combined with UNION on national_id so the same voter is
counted once. This allows PostgreSQL to use the existing partial geography and
polling-station indexes separately and avoids the slow OR plan.

The same branch strategy applies to constituency and ward filters. Candidate
results and stream statistics remain visible if the register count fails.
