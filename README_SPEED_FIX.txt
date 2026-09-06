GUBERNATORIAL LIVE DATA SPEED FIX

- Dashboard HTML opens immediately.
- Dashboard upstream timeout defaults to 30 seconds to allow a sleeping Render voting service to wake.
- Automatic refreshes do not overlap.
- Voting simulation governor feed no longer performs vote-mirroring work during a dashboard read.
- Governor feed uses a short 3-second server-side cache to reduce duplicate PostgreSQL aggregation.
- Completed simulation votes are still mirrored at final /cast.
