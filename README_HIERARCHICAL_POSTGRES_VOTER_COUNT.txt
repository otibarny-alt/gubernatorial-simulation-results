HIERARCHICAL POSTGRESQL VOTER COUNT FIX

The registered-voter denominator now follows the official county_main.csv
polling-station hierarchy. A ward count includes every active PostgreSQL voter
whose ward is labelled correctly OR whose polling station belongs to that ward.

This fixes under-counts caused by blank, abbreviated or historically different
ward text in master_voters. National IDs remain de-duplicated with
COUNT(DISTINCT national_id).
