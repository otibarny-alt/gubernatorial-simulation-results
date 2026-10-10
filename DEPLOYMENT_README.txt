VALID CLOSED-STREAM RESULTS DASHBOARDS

Deploy each ZIP to its matching Render dashboard service. Do not deploy these
packages to the voting-system service.

Included fixes:
- Matches stream activity using county, constituency and ward instead of a
  non-unique stream label.
- Preserves polling stations and streams that share names in other locations.
- Publishes votes, participation and skipped ballots only after a stream is
  formally CLOSED.
- Shows OPEN streams as operational activity without adding their provisional
  votes to the valid result.

After deploying, wait for Render to finish, open the dashboard, select WEST
POKOT, and use Refresh Live Data. The closed stream should appear under streams
closed and its candidate totals should be included.
