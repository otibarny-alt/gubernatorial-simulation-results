2027 GUBERNATORIAL SIMULATION RESULTS DASHBOARD — FRESH V1
==========================================================

Purpose
-------
A clean, lightweight TRAINING / SIMULATION dashboard. It does not record votes and is not an official election result system.

Architecture
------------
- Browser page renders immediately.
- One live data request: /api/summary
- Dashboard server calls only the Voting Simulation governor feed: /api/dashboard/governor
- No direct PostgreSQL connection.
- No county-winner calculations.
- No stream-detail/recent-activity calls during page load.
- Local county/constituency/ward and registered-voter CSVs are indexed once at startup.
- Upstream snapshot is cached and shared among dashboard requests.

Render build command
--------------------
pip install -r requirements.txt

Render start command
--------------------
gunicorn app:app --workers 2 --threads 2 --timeout 60

Required environment variables
------------------------------
FLASK_SECRET_KEY=<long random secret>
SIMULATION_BASE_URL=https://YOUR-VOTING-SIMULATION.onrender.com
SIMULATION_DASHBOARD_API_KEY=<same value as DASHBOARD_API_KEY on Voting Simulation>
AUTH_USERNAME=admin
AUTH_PASSWORD_HASH=<Werkzeug-compatible password hash>

Recommended performance variables
---------------------------------
CACHE_SECONDS=10
UPSTREAM_TIMEOUT_SECONDS=30

Do NOT add DATABASE_URL or PG_POOL variables to this dashboard.

Expected deployment files
-------------------------
app.py
requirements.txt
render.yaml
.env.example
county_main.csv
agents_login.csv
templates/index.html
templates/login.html

After deploy
------------
1. Open /health first. It should respond immediately and does NOT call the Voting Simulation.
2. Open the dashboard and sign in.
3. The HTML page should load immediately. Live totals can take longer only if the upstream Voting Simulation itself is waking from sleep.
4. Once the upstream responds, the dashboard refreshes every 15 seconds.
