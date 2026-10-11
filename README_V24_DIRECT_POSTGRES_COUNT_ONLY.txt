V24 - DIRECT POSTGRESQL REGISTER COUNT ONLY

The Registered Voters card no longer falls back to the voting API's partial
county count. It always executes the filtered count directly against the
PostgreSQL master_voters table.

County filtering counts active voters where either:
- the normalized county field matches the selected county; or
- the voter's polling station belongs to the selected county in county_main.csv.

This prevents a county total from being smaller than a ward total because of
blank, inconsistent or legacy geography text.

REQUIRED RENDER VARIABLE

MASTER_REGISTER_DATABASE_URL must be set on the Gubernatorial Results Dashboard
service to the voting system PostgreSQL Internal Database URL. After saving the
variable, perform a new deployment. If PostgreSQL cannot be reached, the page
returns a clear error instead of displaying a false fallback number.
