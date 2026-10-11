V28 - EXACT VOTERS REGISTER TOTALS

WHY V27 WAS HIGHER THAN THE REGISTER

V27 combined direct PostgreSQL geography with polling-station names. Polling
station names are not globally unique, so same-named stations outside the
selected constituency could be included. V27 also did not include the legacy
Kobo members that the protected Voters Register adds after National-ID
deduplication.

V28 removes that duplicate dashboard calculation. Registered-voter totals now
come from /api/voters-register/count on the Voting Simulation System: the same
authoritative count path used by the protected Voters Register.

- Constituency and ward filters request their exact register totals.
- County totals are the sum of all authoritative constituency totals in the
  selected county.
- PostgreSQL master records and legacy Kobo members use the register's existing
  National-ID deduplication rules.
- Polling-station names are no longer used for cross-area voter inclusion.

Expected West Pokot values from the supplied comparison:

Kapenguria 24,867; Kacheliba 21,231; Pokot South 20,308; Sigor 14,656;
county total 81,062.
