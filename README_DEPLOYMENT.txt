V22.62: Prevent empty report generation/deposit for closed streams with zero simulated voters.
2027 TRAINING E-BALLOT PROTOTYPE V1

NON-BINDING TRAINING / SIMULATION ONLY.

Flow:
Demo verification -> President -> Governor -> Senator -> Woman Rep -> MNA -> MCA
-> Review -> Save simulated ballot -> Simulated tally dashboard.

Candidate cards currently use Candidate 1..N placeholders and numbered photo boxes.
The six simulated selections are stored only in a local demo SQLite database.

This package is deliberately not connected to the production voter-verification
system and must not be used to record or tally official votes.

Render:
Build: pip install -r requirements.txt
Start: gunicorn app:app
Set FLASK_SECRET_KEY to a random secret.


V2 CASCADING ELECTORAL UNITS
- Bundles county_main.csv.
- Replaces manual County, Constituency, Ward, Polling Station and Stream typing
  with cascading dropdowns.
- Hierarchy:
  County -> Constituency -> Ward -> Polling Station -> Stream.
- Uses list_name and parent keys from county_main.csv.
- Includes all 47 counties and the polling-station-stream rows in that file.
- No new Render environment variable is required.


V3 SELECTION FEEDBACK
- Selected candidate card changes to a light highlighted background.
- Selected card rises/pops out slightly.
- Stronger shadow and border make the choice obvious.
- A visible "✓ SELECTED" badge appears on the chosen candidate.
- Text confirmation announces the selected candidate.
- Only one candidate can remain selected because the ballot uses radio buttons.


V4 REVIEW VOTER ID
- The review screen now prominently displays the demo voter's ID number.
- The voter is asked to confirm the ID before saving the simulated ballot set.
- The ID is read from the current session and is not manually re-entered on review.


V5 TERMINAL / STREAM LOCK
- The electoral hierarchy is selected only once per computer/browser.
- The chosen County, Constituency, Ward, Polling Station and Stream are stored
  locally in that browser as the terminal assignment.
- Subsequent voters only enter their voter ID.
- Clicking "Next voter on this computer" returns to the ID entry screen while
  retaining the same voting stream.
- A "Change voting stream" control is available if the computer is moved to
  another room/stream.
- The assignment survives ordinary page refreshes and browser restarts because
  it is kept in browser local storage.
- Clearing browser/site data will clear the terminal assignment.
- No new Render environment variables are required.


V6 SUBSEQUENT VOTER SUBMISSION FIX
- Fixes the issue where the second/subsequent voter could enter an ID but the
  Start button appeared not to respond.
- Cause: hidden terminal setup dropdowns still had HTML 'required' validation.
  On later voters those dropdowns were empty on page load, so the browser
  silently blocked form submission even though the saved stream was valid.
- Terminal setup completeness is now validated only when the stream is first
  locked.
- Once a terminal is locked, its setup dropdowns are disabled and the stored
  electoral-unit values are submitted through hidden fields.
- Subsequent voters can now enter only their voter ID and continue directly to
  the six training ballots.


V7 NO DOUBLE VOTING — TRAINING SIMULATION
- A voter ID that already has a saved simulated ballot set is blocked from
  starting another six-ballot session.
- The check happens when the voter ID is entered and is repeated again before
  the simulated selections are written.
- A clear red warning is shown for duplicate voter IDs.
- The same ID remains blocked across different terminals as long as those
  terminals use the same persistent demo database.
- Resetting all simulated votes from the tally dashboard clears this training
  restriction because the demo vote records are deleted.


V8 SHOW ZERO-VOTE CANDIDATES
- The simulated tally dashboard now lists every configured candidate in every
  election category, even when that candidate has received 0 votes.
- President shows Candidate 1 through Candidate 10.
- Governor, Senator, Woman Rep, MNA and MCA show all candidates configured in
  the prototype.
- Vote counts update automatically as simulated ballots are saved.


V9 RANKED TALLIES
- Candidates in every election section are sorted from highest votes to lowest.
- A Rank column is shown.
- Candidates with equal vote totals share the same rank.
- Candidate slot number is used only to keep tied candidates in a stable order.
- Zero-vote candidates remain visible and are ranked after candidates with votes.


V10 DUPLICATE-VOTER POLLING-STATION MESSAGE
- When a previously used voter ID is entered, the warning now identifies the
  polling station recorded with that simulated ballot.
- Example:
  "Voter ID 10703460 has already voted at RATTA PRIMARY SCHOOL polling station
  and cannot vote again."


V11 — REGISTERED VOTER SUMMARIES
Uses bundled agents_login.csv. total_registered_voters is read by poll_station_name (stream).
At the end of EACH elective-position tally: Total Votes Cast, Registered Voters per stream,
Registered Voters per polling station, and Votes Not Cast. Detailed stream and station tables
are also shown. Polling-station registered totals include all streams belonging to the station.
TRAINING / SIMULATION ONLY.


V12 — A4 PRINT BUTTONS
- Every elective-position tally has its own Print button.
- Clicking it opens the browser/operating-system print dialog for the connected/default printer.
- Only that elective-position section is included in the print job.
- Print CSS requests A4 portrait paper and removes dashboard navigation/buttons from the printed page.
- The browser controls the actual printer selection; a normal web application cannot silently force a specific connected printer without browser/OS or kiosk-print configuration.
TRAINING / SIMULATION ONLY.


V13 — CANDIDATE AGENT SIGNATURE LINES
- At the end of every elective-position printout, a Candidate Agents' Certification section is added.
- One signature row is created for every candidate listed in that tally.
- Columns: Candidate, Agent Name, Signature, Date / Time.
- Includes blank Polling Station and Stream confirmation lines.
- Certification text states that signatories confirm the printout is a true copy of the simulated results for that polling station stream.
- Designed to print as part of the same A4 tally printout.
TRAINING / SIMULATION ONLY.


V14 — PRESIDING / RETURNING OFFICER SIGNATURES
- Adds an Election Officials' Certification area to every elective-position printout.
- Presiding Officer: Name, Signature, Date/Time.
- Returning Officer: Name, Signature, Date/Time.
- Appears after the candidate-agent certification section.
TRAINING / SIMULATION ONLY.


V15 — POLLING STATION STREAM COUNT
- The "Registered Voters / Votes Cast Per Polling Station" table now includes
  "No. of Streams".
- This count shows how many polling station streams contribute to the
  Registered Voters total for that polling station.
- The count is derived from county_main.csv using the same station-to-stream
  relationship used to calculate registered voters.
TRAINING / SIMULATION ONLY.


V16 — PRE-OPENING ZERO-VOTE + OPEN/CLOSE REPORT
- Each stream must pass a 0 pre-cast simulated-votes check before simulated voting can start.
- The actual opening and closing timestamps are recorded on the same-day stream session.
- A printable A4 report shows the clean-system check, date, scheduled hours, actual timestamps,
  schedule comparison, candidate-agent signature lines, Presiding Officer and Returning Officer.
- Set the required hours in Render Environment:
  VOTING_OPEN_TIME=HH:MM
  VOTING_CLOSE_TIME=HH:MM
  No legal/official hours are assumed by the prototype; enter the hours required for your training exercise.
TRAINING / SIMULATION ONLY.


V17 — CASCADING STREAM CONTROL FROM county_main.csv
The Pre-Opening / Closing Control page no longer requires manual typing of electoral units.
It uses the existing /api/hierarchy endpoint backed by county_main.csv:
County -> Constituency -> Ward -> Polling Station -> Stream.
Each selection filters the next dropdown and the selected values are submitted to the
existing zero-precast-vote/open-stream procedure.
TRAINING / SIMULATION ONLY.


V18 — SIX ELECTIVE-POSITION AGENT SIGNATURES
The printable stream opening/closing report now provides candidate-agent signature rows
for all six elective positions because the same candidate may have a different agent
at each polling-station stream.

Opening certification sections:
- President: Candidate 1–10
- Governor: Candidate 1–6
- Senator: Candidate 1–6
- Woman Representative: Candidate 1–6
- MNA: Candidate 1–6
- MCA: Candidate 1–6

Closing certification repeats the same six elective-position agent signature sections.
Each row has Candidate, Agent Name, Signature, and Date/Time.
Presiding Officer and Returning Officer signature lines are included separately for
both opening and closing.

The report may span multiple A4 pages so that each agent has adequate signing space.
TRAINING / SIMULATION ONLY.


V19 — DYNAMIC PRINTED REPORT HEADER
A dynamic header/logo image can now be displayed on all printed reports using a Render
environment variable.

Add this environment variable in Render:
REPORT_HEADER_IMAGE_URL=https://your-public-image-url.example/header.png

The image is NOT hard-coded into the application. The application reads the URL at runtime.
Changing REPORT_HEADER_IMAGE_URL changes the printed report header without editing the code.

The dynamic header appears on:
- Voting Stream Opening / Closing Report
- President tally printout
- Governor tally printout
- Senator tally printout
- Woman Representative tally printout
- MNA tally printout
- MCA tally printout

Important:
- The value must be a direct, publicly accessible image URL (PNG/JPG/WebP).
- Do not use a Google Drive page/share URL unless it resolves directly to the image.
- If REPORT_HEADER_IMAGE_URL is empty, no header image is printed.
TRAINING / SIMULATION ONLY.


V20 — BUNDLED REPORT HEADER IMAGE
The supplied ODM Vote Count and Transmission header image is now included inside:
static/odm_report_header.png

Recommended Render environment variable:
REPORT_HEADER_IMAGE_URL=/static/odm_report_header.png

The application also defaults automatically to that local path if the variable is omitted.

Advantages:
- No dependency on GitHub raw URLs.
- Works even when the GitHub repository is private.
- Header is served directly by the Render web application.
- Changing the environment variable later can still point to a different public image if desired.

The header appears on all printed reports supported by V19:
- Voting Stream Opening / Closing Report
- President tally
- Governor tally
- Senator tally
- Woman Representative tally
- MNA tally
- MCA tally

TRAINING / SIMULATION ONLY.


V21 — OPEN/CLOSE REPORT IN NEW TAB
The "View / Print Opening & Closing Report" link now opens the report in a separate
browser tab using target="_blank" and rel="noopener".
The Voting Stream Control page remains open in the original tab, so after printing or
reviewing the report the operator can simply close the report tab instead of using Back.
TRAINING / SIMULATION ONLY.


V22 — HARD LOCK VOTING TERMINAL TO PRE-OPENED STREAM
After the pre-voting zero-vote verification opens a polling-station stream, that browser/device
is locked to the selected County, Constituency, Ward, Polling Station and Stream for that day.

Security/flow changes:
- The lock is stored in a signed, HttpOnly browser cookie.
- Ballot start ignores any manually posted geography and uses only the signed terminal lock.
- Ballot casting re-checks that the session geography still matches the signed terminal lock.
- The stream-control page no longer offers a second manual stream-opening form after locking.
- The voter screen displays the locked Polling Station and Stream.
- The previous "Change voting stream" workflow is no longer available during ballot casting.
- Closing the stream does not permit further voters in that stream.

This is a per-browser/device training-terminal lock. Clearing browser cookies or using another
browser/device creates a different terminal context; for a stronger multi-device simulation,
terminal identity and locks should be stored centrally in a persistent simulation database.
TRAINING / SIMULATION ONLY.


V22.1 — CONTROLLED TERMINAL RESET
Built directly from stable V22.

Adds "Reset Terminal for New Stream" on the Stream Control page.

Reset is allowed only when:
1. No simulated ballot has yet been cast in the currently locked polling-station stream; OR
2. The currently locked stream has been formally closed.

Reset is blocked if the stream is still open and any simulated votes already exist.

When reset succeeds:
- signed terminal-lock cookie is removed
- current Flask voting session is cleared
- operator returns to station/stream selection
- a different County / Constituency / Ward / Polling Station / Stream can be chosen

The working V22 ballot and stream-lock flow is otherwise unchanged.
TRAINING / SIMULATION ONLY.


V22.2 — ODM MEMBERSHIP PHOTO VERIFICATION GATE
Built from stable V22.1 training simulation.

Before the simulated ballot begins:
- Officer enters National ID.
- App queries the ODM Membership Registration Database.
- The matching member's ID Photo and Passport Photo are displayed side by side.
- Member name, membership number and membership polling station are also displayed when available.
- Officer must click "Identity Confirmed — Continue to Simulation Ballot".
- A member not found in the ODM Membership Registration Database cannot proceed.
- Existing duplicate-voter and locked-stream checks remain in place.

Membership form fields used:
basics/national_id_no
basics/id_photo
basics/passport_photo
members_particulars/odm_membership_no
members_particulars/first_name
members_particulars/other_names
members_particulars/surname
electorals_units/poll_station_label or selected_poll_station1

Required Render environment variables:
KOBO_BASE_URL=https://kf.kobotoolbox.org
MEMBERSHIP_ASSET_UID=<UID OF MEMBERSHIP RECRUITMENT PORTAL>
KOBO_API_TOKEN=<YOUR EXISTING KOBO TOKEN>

Photos are proxied server-side so the membership database API token is not exposed to the browser.

IMPORTANT: This package connects membership verification only to the NON-BINDING TRAINING /
SIMULATION ballot. It is not designed or provided for recording binding political votes.


V22.3 — ODM POLLING-STATION MATCH GATE
Built from V22.2.

The voter can proceed to the training/simulation ballot only when the polling station stored
in the ODM Membership Registration Database matches the polling station locked on the voting terminal.

Membership fields used for station matching, in priority order:
- electorals_units/selected_poll_station1
- particulars_confirmation/selected_poll_station1_confirmation
- stored_particulars_confirmed/selected_poll_station1_calculation
- stored_particulars_confirmed/selected_poll_station1_confirmed

Display label:
- electorals_units/poll_station_label

The comparison normalizes capitalization, spaces, punctuation, and underscores so values such as:
MWENA PRIMARY SCHOOL
and
mwena_primary_school
are treated as the same station.

If the stations match:
- ID Photo and Passport Photo are shown
- green POLLING STATION MATCH CONFIRMED message appears
- officer can confirm identity and continue to the simulation ballot

If they do not match, or no membership polling station is available:
- red POLLING STATION MISMATCH message appears
- both station values are displayed
- Continue button is disabled
- voter cannot enter the simulation ballot

The server re-checks the station-match flag at /membership/confirm so this is not only a browser/UI restriction.

TRAINING / SIMULATION ONLY.


V22.4 — TALLY PRINT DATE/TIME/GPS
Built from V22.3.

Each printed simulated tally report now records:
- Report date
- Report time (Africa/Nairobi / Kenya time)
- GPS latitude
- GPS longitude
- Browser-reported GPS accuracy
- GPS capture status

The timestamp and GPS are captured when the operator clicks the individual Print button
for President, Governor, Senator, Woman Rep, MNA or MCA.

GPS uses the browser Geolocation API and therefore requires the user/device to allow Location
permission for the Render site. If permission is denied or the device/browser cannot obtain
a position, the report clearly prints that GPS was not captured rather than inventing a location.

TRAINING / SIMULATION ONLY.


V22.5 — OPENING REPORT ONLY
The stream report has been simplified to contain only morning opening details.

Included:
- Polling Station
- Stream
- Date
- 0 pre-cast votes verification
- Scheduled opening time
- Actual opening timestamp
- Opening time check
- Candidate-agent opening verification/signatures
- Election-official opening signatures
- Dynamic report header

Removed from this report:
- Scheduled closing
- Actual closing timestamp
- Closing check
- Distinct simulated voters recorded

Closing information remains in the final vote-count/tally reports.
TRAINING / SIMULATION ONLY.


V22.6 — AUTOMATIC DATE/TIME/GPS CAPTURE FIX
Built from V22.5.

Changes:
- Date and Kenya time are populated automatically when the tally dashboard loads.
- GPS is requested automatically when the tally dashboard loads.
- GPS is requested again immediately before each individual tally is printed.
- A short render delay is used before opening print preview so the freshly captured values
  are visible on the printed report.
- All tally sections receive the same captured page-load GPS value.
- If browser Location permission is denied, the report now states:
  "Location permission denied — allow Location for this site".
- If GPS cannot be obtained, the report gives the specific browser status instead of remaining
  indefinitely at "Waiting for print".

On Render/HTTPS, browser geolocation should work when Location permission is granted.
TRAINING / SIMULATION ONLY.


V22.7 — MORNING OPENING CERTIFICATION ONLY
- Removed Closing Certification — Candidate Agents from the morning Opening Report only.
- Removed Closing — Election Officials from the morning Opening Report.
- Opening Certification — Candidate Agents remains.
- Opening — Election Officials remains.
- Closing candidate-agent certification remains in the final tally reports.
- V22.6 date/time/GPS tally-report changes are retained.
TRAINING / SIMULATION ONLY.

V22.8 — OPENING STATION GPS
Morning Opening Report now captures current device GPS: latitude, longitude, accuracy and status.
Location permission must be allowed. TRAINING / SIMULATION ONLY.


V22.9 — PERSISTED OPENING GPS FIX
The previous opening-report GPS script was not guaranteed to execute because the report template
did not contain a closing </body> tag. V22.9 changes the workflow so GPS is captured BEFORE the
stream is opened and stored with the stream-opening record.

New opening workflow:
1. Select County / Constituency / Ward / Polling Station / Stream.
2. Click "Capture GPS, Verify 0 Pre-Cast Votes & Open Stream".
3. Browser asks for Location permission.
4. Stream opens only after a current GPS fix is obtained.
5. Latitude, longitude and browser-reported accuracy are stored in stream_sessions.
6. The morning opening report reads the stored opening GPS from the database, so opening a new
   report tab does not need to obtain GPS again.

Existing stream records opened before V22.9 will not contain stored opening GPS. For those records,
the report attempts a browser GPS fallback and labels it clearly as a current-device fallback.

TRAINING / SIMULATION ONLY.


V22.10 — CANDIDATE REGISTRATION PORTAL INTEGRATION
==================================================
TRAINING / SIMULATION ONLY — NOT FOR OFFICIAL OR BINDING ELECTION USE.

Add this Render environment variable to the TRAINING BALLOT web service:
CANDIDATE_PORTAL_BASE_URL=https://your-candidate-registration-service.onrender.com

Do not add a trailing slash.

Candidate scope:
President = National
Governor = County
Senator = County
Woman Representative = County
MNA = Constituency
MCA = Ward

The training ballot sends its locked County, Constituency and Ward to the Candidate
Registration Portal API and receives only active candidates applicable to that location.

The ballot displays candidate photo, full name, Candidate ID, membership number and bio.
Simulated vote records now store stable Candidate ID and Candidate Name snapshots so
later candidate reordering does not change the identity of previously cast simulation votes.

If candidate data is unavailable, the ballot blocks the affected simulated position instead
of falling back to placeholder candidates.


V22.11 — SELECTED CANDIDATE PHOTOS ON REVIEW SCREEN
===================================================
TRAINING / SIMULATION ONLY.

The final review screen now re-loads each selected candidate profile from the
Candidate Registration Portal and displays a large candidate photograph for:
President, Governor, Senator, Woman Representative, MNA and MCA.

The photograph is displayed together with the election position, candidate name
and Candidate ID. Each selection has a clearly labelled Change button.

This visual review is intended to make confirmation easier for users who may have
difficulty reading candidate names. Candidate photos supplement the names and do
not replace the existing selection confirmation controls.


V22.13 — DELIBERATE CATEGORY SKIP + SKIP STATISTICS
===================================================
TRAINING / SIMULATION ONLY.

Each ballot category now includes a very prominent red SKIP button.

The voter is explicitly told that:
- SKIP means no candidate receives their selection in that category;
- the voter is intentionally leaving that category without a candidate choice;
- after confirmation, the system moves to the next category.

The browser displays a confirmation dialog before recording a skip.

Candidate choices are visually simplified to:
- candidate photograph
- candidate name

Candidate ID, membership number and biography are no longer displayed in the choice cards.

REVIEW SCREEN
A skipped category appears as a prominent red SKIPPED card.
A selected candidate appears with photograph and name.

TALLY / PARTICIPATION STATISTICS
For each elective category, reports now show:
- votes cast for candidates;
- voters who skipped the category;
- registered voters;
- skipped / registered-voters count and percentage;
- total category participation;
- registered voters who gave no response in that category.

Per-stream and per-polling-station tables also show category skips separately.

Skip records are stored with the internal candidate_id sentinel "__SKIP__".
They are excluded from candidate ranking and candidate vote totals.


V22.14 — SOFTER SKIP SECTION + POINTER CURSORS
=============================================
TRAINING / SIMULATION ONLY.

The SKIP section has been visually reduced so it remains clear without dominating
the candidate-selection screen.

Changes:
- thinner border
- lighter background
- smaller warning heading and explanation
- smaller, narrower SKIP button
- SKIP remains clearly distinct from selecting a candidate
- mouse cursor changes to a pointing hand over SKIP and Save/Continue buttons
- pointer cursor also applies to other button-style controls


V22.15 — READ-ONLY PRESIDENTIAL DASHBOARD API
=============================================
TRAINING / SIMULATION ONLY.

Adds:
GET /api/dashboard/president

The endpoint returns aggregated presidential simulation totals by polling-station stream.
It does NOT return voter National IDs.

Required Render environment variable:
DASHBOARD_API_KEY=<long shared secret>

The separate Presidential Simulation Results Dashboard sends this value in the
X-Dashboard-Key request header.

The feed includes:
- active presidential candidate names and IDs;
- candidate vote totals;
- category skips;
- participant totals;
- stream County / Constituency / Ward / Polling Station / Stream;
- stream opening/closing status and timestamps.

This endpoint is read-only and exists only to support the non-binding training/simulation dashboard.


V22.16 — GLOBAL DEVICE-OWNERSHIP LOCK
=====================================
TRAINING / SIMULATION ONLY.

PURPOSE
Once a polling-station stream is opened and locked to one browser/device, another
device anywhere cannot:
- unlock it;
- reset it;
- close it;
- take it over;
- open the same station/stream as its own terminal.

HOW IT WORKS
The old signed browser cookie is no longer trusted by itself.

V22.16 adds a central PostgreSQL table:
simulation_terminal_locks

When a device opens a stream:
1. the browser receives a random owner token;
2. only a SHA-256 hash of that owner token is stored centrally;
3. the polling station + stream + date is reserved atomically in PostgreSQL;
4. another device trying the same polling-station stream is blocked;
5. Reset and Close validate both the local device token and the central PostgreSQL ownership record.

A copied or manually constructed station/stream URL does not grant ownership.

OWNER DEVICE RESET
The existing controlled Reset Terminal function remains available only on the original
owning device and only under the existing reset rules:
- no simulated votes exist in the open stream, OR
- the stream has formally been closed.

When the legitimate owner resets, the central lock is marked released and may then be
claimed by another device.

IMPORTANT
If the owner browser loses its cookies, that device also loses its ownership credential.
For security, another device is NOT allowed to recover or release the lock automatically.

RENDER REQUIREMENT
Set DATABASE_URL on the voting simulation web service to a Render PostgreSQL
Internal Database URL.

The PostgreSQL database is required for cross-device / cross-instance locking.
If DATABASE_URL or PostgreSQL is unavailable, lock-sensitive opening actions fail closed
instead of falling back to insecure browser-only locking.

This database is separate from the existing SQLite simulated vote store in V22.16;
it is used specifically as the authoritative global terminal-lock registry.


V22.17 — OPENING REPORT USES REGISTERED CANDIDATE NAMES
=======================================================
TRAINING / SIMULATION ONLY.

The Voting Stream Opening Report no longer prints hard-coded rows such as:
Candidate 1, Candidate 2, Candidate 3, etc.

When the report is opened, the simulation uses the stream's stored:
- County
- Constituency
- Ward

to query the connected Candidate Registration & Profile Portal.

The Opening Certification — Candidate Agents section now lists the actual active
registered candidate names applicable to that stream:
- President: national candidates
- Governor: candidates for the stream's county
- Senator: candidates for the stream's county
- Woman Representative: candidates for the stream's county
- MNA: candidates for the stream's constituency
- MCA: candidates for the stream's ward

If a position has no active registered candidate, the report states that no active
registered candidate was found instead of displaying placeholder Candidate numbers.

The Candidate Registration Portal connection continues to use:
CANDIDATE_PORTAL_BASE_URL


V22.25 — OPEN STREAM BUTTON MOVED UNDER VERIFICATION RIBBON
===========================================================
TRAINING / SIMULATION ONLY.

On the voter verification screen:
- the old bottom text link "Open / Close Voting Stream & Print Opening Report" has been removed;
- the wording is now "Open Voting Stream & Print Opening Report";
- it is displayed as a pronounced clickable button directly below the orange
  "ODM Voter ID & Photo Verification" ribbon;
- the button has a black background, orange border, hover/press feedback and pointer cursor;
- the rest of the verification screen is unchanged.


V22.26 — PRE-OPENING CONTROL ORANGE RIBBON
==========================================
TRAINING / SIMULATION ONLY.

On the Voting Stream Control screen:
- "Pre-Opening / Closing Control" has been changed to "Pre-Opening Control";
- the heading is centered;
- it appears inside an orange ribbon directly below the ODM project header;
- the rest of the stream-control functionality remains unchanged.


V22.28 — RESET BUTTON ALIGNMENT FIX
===================================
The previous V22.27 CSS targeted the wrong form class.

The actual template uses:
terminal-reset-form
reset-terminal-btn

V22.28 targets those exact classes, centers the Reset Terminal for New Stream
button, and changes the button to orange immediately when clicked.


V22.31 — CORRECT POST-RESET NEW-STREAM WORKFLOW
===============================================
TRAINING / SIMULATION ONLY.

This fixes the V22.30 behavior that removed the Reset Terminal control too early.

NORMAL LOCKED STREAM
- The screen remains "Pre-Opening Control".
- "Reset Terminal for New Stream" remains available under the existing safe-reset rules.
- The user can therefore actually reset the current terminal.

AFTER A SUCCESSFUL RESET
1. The terminal returns to the stream-selection screen.
2. The user selects and opens/locks a NEW polling-station stream.
3. Only after that new stream has successfully been locked:
   - the orange ribbon changes to "Voting Control";
   - the center button changes to "Training Ballot".
4. Clicking Training Ballot opens the voter verification/training ballot screen.

The temporary post-reset display state is consumed when the Training Ballot is opened.
If the user later returns to Voting Stream Control, the normal controlled-reset button
is available again under the existing reset rules.


V22.32 — STREAM ASSIGNMENT REQUIRED BEFORE VOTER ENTRY
======================================================
TRAINING / SIMULATION ONLY.

INITIAL VERIFICATION SCREEN
The initial screen now displays:
"This computer is not yet assigned to any polling station."

Before pre-opening:
- voter ID input is disabled;
- Verify voter photos is disabled;
- the screen does not use browser localStorage to pretend a stream is assigned;
- the authoritative central terminal lock is used instead.

A voter ID becomes available only when:
1. this device owns a valid central polling-station/stream lock;
2. the stream has a successful opening record for today;
3. the stream has not been closed.

SERVER-SIDE ENFORCEMENT
The /start voter-verification endpoint independently checks the same conditions.
A manually crafted POST request therefore cannot bypass the disabled screen.

The user must use "Open Voting Stream & Print Opening Report" to complete the
pre-opening process before voter verification can begin.


V22.35 — RESET BEFORE ACTIVE TERMINAL LOCK
==========================================
TRAINING / SIMULATION ONLY.

A previous central terminal assignment is no longer treated as an active voting lock.

Correct workflow:
1. If the device still has a previous assignment, Voting Stream Control shows
   "PREVIOUS TERMINAL ASSIGNMENT DETECTED — RESET REQUIRED".
2. Voter ID entry stays disabled.
3. The operator presses Reset Terminal for New Stream.
4. The previous central lock is released.
5. The operator selects a new County / Constituency / Ward / Polling Station / Stream.
6. GPS is captured, zero pre-cast votes are verified, and the new stream is opened.
7. Only then is the terminal treated as locked for voting and voter verification is enabled.

The central PostgreSQL ownership protection is retained so another device cannot take over
an active stream.


V22.37 — STREAM LOCK PERSISTS BETWEEN VOTERS
============================================
TRAINING / SIMULATION ONLY.

Fixes the issue where selecting/finishing one voter caused the next voter screen
to act as though the terminal needed to be reset again.

The terminal activation state is now stored in a signed device cookie tied to:
- session date;
- polling station;
- stream.

This state survives Flask session.clear(), which is used to clear one voter's
temporary verification/ballot data.

Correct behavior:
1. Reset terminal when changing to a new polling-station stream.
2. Select/open the new stream.
3. The stream becomes active and remains locked to that device.
4. Voter 1 is verified and completes the simulation.
5. Voter 2, Voter 3, etc. can be entered without resetting or reopening the stream.
6. The lock remains active until the voting stream is formally closed or the
   authorized owner device performs a controlled reset.

The central PostgreSQL device-ownership lock remains authoritative.


V22.38 — STRICT 6:00 PM CLOSING + NO REOPEN
===========================================
TRAINING / SIMULATION ONLY.

Official closing is fixed at 18:00 (6:00 PM) Africa/Nairobi.

BEFORE 18:00
- Close Voting Stream is not available.
- The control screen states that voting cannot be closed before 18:00.
- A direct/manually crafted POST to /stream/close is also rejected server-side.
- The stream remains locked and active for subsequent voters.

AT/AFTER 18:00
- The owning device may formally close the stream.
- The close action marks the central PostgreSQL lock with closed_at.
- The local stream session is also marked closed.
- The active voting cookie is removed.

AFTER FORMAL CLOSING
- The stream cannot be reopened.
- Resetting/releasing the device does not make that same closed stream reusable.
- /stream/open checks both local stream_sessions and the central PostgreSQL lock.
- The central claim function refuses to reclaim a row with closed_at set.

This prevents reopening on another device or Render instance as long as DATABASE_URL
points to the shared PostgreSQL database.


V22.40 — TALLY DASHBOARD ONLY AFTER FORMAL CLOSING
==================================================
TRAINING / SIMULATION ONLY.

The tally dashboard is now unavailable while the voting stream is open.

BEFORE FORMAL CLOSING
- "Open tally dashboard" is disabled on the completion screen.
- Header links to Simulated Tallies display as locked text.
- Direct access to /tallies returns a locked screen with HTTP 403.
- Known tally-print routes are protected with the same server-side check.
- The locked screen explains that tallies cannot be opened, viewed or printed
  before voting is formally closed.

AFTER FORMAL CLOSING
- Tally dashboard links become available.
- The owning/closed stream can open, view and print the tally reports.

This is enforced from the stream's closed_at record, not only from button visibility.


V22.41 — CLOSING BUTTON ALWAYS VISIBLE
======================================
TRAINING / SIMULATION ONLY.

The Voting Control screen now always shows the closing button while a stream is open.

Before 18:00 (6:00 PM) Africa/Nairobi:
- Close Voting Stream Permanently is visible but disabled.
- The screen explains that it will activate at the official closing time.

At/after 18:00:
- The same button becomes active only on the device that owns the central stream lock.
- Closing remains permanent and the stream cannot be reopened.

The stream-control route now also derives Polling Station and Stream from the
authoritative terminal lock when the screen is opened without query parameters.
This prevents the UI from incorrectly saying the browser does not own the stream
simply because the URL omitted the polling-station/stream values.


V22.43 — TALLIES AVAILABLE AFTER FORMAL CLOSING
===============================================
TRAINING / SIMULATION ONLY.

This fixes the case where the tally dashboard remained unavailable after the
voting stream had already been formally closed.

On successful closing:
- active voting access is removed;
- a signed read-only closed-stream reference is stored on the same device;
- the closed stream remains permanently non-reopenable;
- /tallies becomes available for that closed stream;
- the Voting Control screen displays:
  "Open / View / Print Tally Dashboard";
- the completion screen also enables the tally dashboard only when closed.

Before formal closing, /tallies still returns the locked screen and cannot be viewed
or printed.


V22.44 — REMOVE RESET BUTTON FROM TALLY VIEW
============================================
TRAINING / SIMULATION ONLY.

Removed the visible "Reset all simulated votes" control from the bottom of
the tally dashboard. The tally dashboard remains a post-closing results,
viewing and printing screen.


V22.45 — CANDIDATE IMAGES ON FINAL TALLY REPORT
===============================================
TRAINING / SIMULATION ONLY.

The post-closing final tally report now displays each registered candidate's
Candidate Portal photograph beside the candidate name and vote count.

Candidate photographs are also displayed in the candidate-agent certification
table at a smaller print-friendly size.

The photographs use the existing photo_url supplied by the connected Candidate
Registration & Profile Portal. Candidates without an available photo display a
"No photo" placeholder.

V22.46 — EMAIL INDIVIDUAL CLOSED TALLY REPORTS
===============================================
TRAINING / SIMULATION ONLY.

Each election tally now has an Email button beside its Print button. The officer
enters the destination email address and only that election's report is emailed.
The same post-closing access gate is enforced server-side, so reports cannot be
emailed before the voting stream has been officially closed.

Add these Render environment variables:
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-sending-email@example.com
SMTP_PASSWORD=your-provider-app-password
SMTP_FROM_EMAIL=your-sending-email@example.com
SMTP_FROM_NAME=ODM Training Tally Reports
SMTP_USE_TLS=true

For Gmail, SMTP_PASSWORD should be a Google App Password, not the normal account
password. Other SMTP providers can be used by changing the host, port and login.


V22.48 — CURRENT LABELS + PHOTO ZOOM
====================================
TRAINING / SIMULATION ONLY.

On ODM Membership Photo Verification:
- Locked Voting Station -> Current Voting Station
- Locked Stream -> Current Stream
- Other visible locked-station wording on this screen is changed to Current.
- ID Photo and Passport Photo can be clicked/tapped to enlarge in a full-screen lightbox.
- Press Escape, click outside the image, or click X to close the enlarged photo.


V22.49 — SMTP EMAIL DIAGNOSTICS / GMAIL SUPPORT
================================================
TRAINING / SIMULATION ONLY.

The application reads these exact Render environment variables:
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
SMTP_FROM_EMAIL
SMTP_FROM_NAME
SMTP_USE_TLS
SMTP_USE_SSL

GMAIL (recommended port 587):
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=youraccount@gmail.com
SMTP_PASSWORD=<16-character Google App Password>
SMTP_FROM_EMAIL=youraccount@gmail.com
SMTP_FROM_NAME=ODM Training Tally Reports
SMTP_USE_TLS=true
SMTP_USE_SSL=false

Alternative Gmail SSL configuration (port 465):
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=youraccount@gmail.com
SMTP_PASSWORD=<16-character Google App Password>
SMTP_FROM_EMAIL=youraccount@gmail.com
SMTP_FROM_NAME=ODM Training Tally Reports
SMTP_USE_TLS=false
SMTP_USE_SSL=true

Do not use SMTP_FROM; this application expects SMTP_FROM_EMAIL.
The recipient can still be any valid email address.

The email API now returns specific safe messages for authentication, connection, timeout, and SMTP errors. Passwords are never returned to the browser.


V22.50 PDF EMAIL ATTACHMENTS
- Each election tally Email button now converts that specific closed-stream tally report to an A4 PDF.
- The PDF is attached to the email for easy download and printing.
- Existing SMTP environment variables are unchanged.
- Tally access remains blocked until the stream is officially closed.


V22.52 — CENTRAL PDF REPORT REPOSITORY
======================================
TRAINING / SIMULATION ONLY.

After a polling-station stream is formally closed, the application redirects to the final tally dashboard. The six rendered tally sections are automatically converted to PDFs and deposited in the shared PostgreSQL repository under these groups:
- Presidential Reports
- Gubernatorial Reports
- Senatorial Reports
- Women Rep Reports
- MNA Reports
- MCA Reports

Repository URL: /report-repository
Each record stores election category, county, constituency, ward, polling station, stream, formal closing timestamp, deposit timestamp, filename and the PDF bytes. Each report has View and Download controls.

DATABASE: Uses the existing DATABASE_URL / Render PostgreSQL. No new environment variable is required. The simulation_pdf_reports table is created automatically.

IMPORTANT: PostgreSQL is used rather than the Render service filesystem so the central PDFs survive web-service restarts/redeploys and are shared across devices connected to the same database.


V22.53 — TEMPORARY 8:00 AM TEST CLOSING
For TRAINING / SIMULATION testing only, the official close gate is temporarily set to 08:00 (8:00 AM) Africa/Nairobi.
Restore the intended closing time after testing.

V22.56 FAST REPOSITORY ENGINE
- Reuses PostgreSQL connections through psycopg_pool instead of opening a new TLS DB connection for every repository query.
- Database/table/index initialization runs once per web worker, not on every repository request.
- Repository landing counts are cached briefly (default 20 seconds) and invalidated immediately when a new PDF is deposited.
- Cascading filter dropdowns are fetched through one pooled connection.
- PDF byte data remains lazy-loaded only on View/Download.
- Added composite metadata indexes for category/date and geographic filtering.
Optional tuning: PG_POOL_MAX_SIZE=8 and REPO_COUNTS_TTL_SECONDS=20 (defaults already applied; no Render variables required).


V22.59 — PDF LOCATION IDENTIFICATION, HIGH-SPEED REPOSITORY PRESERVED
County, Constituency, Ward and Polling Station Stream are displayed immediately below the ODM PDF logo header. Repository pooling, caching, indexes and lazy PDF retrieval remain unchanged from V22.58.


V22.61 PERFORMANCE NOTE
- Existing repository PDFs are detected before PDF rendering, so revisiting a closed tally does not regenerate six PDFs.
- New PDFs are deposited one category at a time to avoid saturating the web service.
- Render runs Gunicorn with 2 workers x 2 threads so repository browsing can remain responsive during PDF generation.
- V22.60 visible County / Constituency / Ward / Polling Station Stream PDF header is preserved.


V22.68 REPOSITORY DELETE ADMIN PROTECTION
Set these Render environment variables before using Delete:
ADMIN_USERNAME=<your administrator username>
ADMIN_PASSWORD=<a strong administrator password>
Only an authenticated repository administrator sees the Delete buttons. The server also rejects direct delete requests from non-admin sessions.

V22.74 LIVE PRESIDENTIAL DASHBOARD FEED
----------------------------------------
The training simulation now mirrors completed ballot-category selections into PostgreSQL as anonymous simulation dashboard events. The mirror contains no National ID, phone number or membership number. This lets the separate Presidential Simulation Results Dashboard show current simulated presidential selections and retain those aggregate events across Render deploys/restarts.

The existing DATABASE_URL is used; no additional database service is required. Keep DASHBOARD_API_KEY configured on this service and set the same value as SIMULATION_DASHBOARD_API_KEY on the separate dashboard service.

V22.75 UPDATE
- Admin-only reopening of a formally closed TRAINING/SIMULATION stream.
- Existing simulated votes are preserved.
- The admin device becomes the active stream owner after reopening.
- Stale repository PDFs for that stream are removed so fresh PDFs can be generated after the stream is closed again.
- Existing voter-session duplicate protections remain in force.
