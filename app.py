import os, csv, re, time, threading
from functools import wraps
from collections import defaultdict

import requests
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'CHANGE-ME')

SIMULATION_BASE_URL = os.getenv('SIMULATION_BASE_URL', '').rstrip('/')
SIMULATION_DASHBOARD_API_KEY = os.getenv('SIMULATION_DASHBOARD_API_KEY', '').strip()
COUNTY_MAIN_FILENAME = os.getenv('COUNTY_MAIN_FILENAME', 'county_main.csv').strip()
AGENTS_LOGIN_FILENAME = os.getenv('AGENTS_LOGIN_FILENAME', 'agents_login.csv').strip()
CACHE_SECONDS = max(3, int(os.getenv('CACHE_SECONDS', '10')))
UPSTREAM_TIMEOUT_SECONDS = max(5.0, float(os.getenv('UPSTREAM_TIMEOUT_SECONDS', '30')))
AUTH_USERNAME = os.getenv('AUTH_USERNAME', '').strip()
AUTH_PASSWORD_HASH = os.getenv('AUTH_PASSWORD_HASH', '').strip()

_http = requests.Session()
_fetch_lock = threading.Lock()
_cache = {'snapshot': None, 'snapshot_at': 0.0, 'last_error': ''}
_geo = None
_registered = None


def norm(v):
    return re.sub(r'[-_\s]+', ' ', str(v or '').strip().lower()).strip()


def friendly(v):
    text = str(v or '').strip()
    return re.sub(r'\s+', ' ', re.sub(r'[_-]+', ' ', text)).title() if text else ''


def to_int(v):
    try:
        return int(float(str(v or '0').replace(',', '').strip()))
    except Exception:
        return 0


def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if AUTH_USERNAME and AUTH_PASSWORD_HASH and not session.get('dashboard_user'):
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required.'}), 401
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapped


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not AUTH_USERNAME or not AUTH_PASSWORD_HASH:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if username == AUTH_USERNAME and check_password_hash(AUTH_PASSWORD_HASH, password):
            session['dashboard_user'] = username
            return redirect(url_for('index'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html')


@app.get('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


def load_geo():
    global _geo
    if _geo is not None:
        return _geo

    path = os.path.join(BASE_DIR, COUNTY_MAIN_FILENAME)
    with open(path, encoding='utf-8-sig', errors='replace', newline='') as f:
        rows = list(csv.DictReader(f))

    counties, constituencies, wards, stations, streams = {}, {}, {}, {}, {}
    for r in rows:
        kind, name = r.get('list_name', ''), r.get('name', '')
        if not name:
            continue
        item = {k: (v or '') for k, v in r.items()}
        if kind == 'county': counties[norm(name)] = item
        elif kind == 'constituency': constituencies[norm(name)] = item
        elif kind == 'ward': wards[norm(name)] = item
        elif kind == 'poll_station': stations[norm(name)] = item
        elif kind == 'poll_station_stream': streams[norm(name)] = item

    by_stream = {}
    counties_ui = {}
    constituencies_ui = defaultdict(dict)
    wards_ui = defaultdict(dict)
    expected_by_filter = defaultdict(list)

    for _, srow in streams.items():
        station = stations.get(norm(srow.get('poll_station_key')), {})
        ward = wards.get(norm(station.get('ward_key')), {})
        constituency = constituencies.get(norm(ward.get('constituency_key')), {})
        county = counties.get(norm(constituency.get('county_key')), {})
        geo = {
            'county': county.get('name', ''),
            'county_label': county.get('label') or friendly(county.get('name', '')),
            'constituency': constituency.get('name', ''),
            'constituency_label': constituency.get('label') or friendly(constituency.get('name', '')),
            'ward': ward.get('name', ''),
            'ward_label': ward.get('label') or friendly(ward.get('name', '')),
            'poll_station': station.get('name', ''),
            'stream': srow.get('name', ''),
        }
        skey = norm(geo['stream'])
        by_stream[skey] = geo

        ck, cok, wk = norm(geo['county']), norm(geo['constituency']), norm(geo['ward'])
        if ck:
            counties_ui[ck] = {'value': geo['county'], 'label': geo['county_label']}
        if ck and cok:
            constituencies_ui[ck][cok] = {'value': geo['constituency'], 'label': geo['constituency_label']}
        if ck and cok and wk:
            wards_ui[(ck, cok)][wk] = {'value': geo['ward'], 'label': geo['ward_label']}

        expected_by_filter[('', '', '')].append(skey)
        expected_by_filter[(ck, '', '')].append(skey)
        expected_by_filter[(ck, cok, '')].append(skey)
        expected_by_filter[(ck, cok, wk)].append(skey)

    _geo = {
        'by_stream': by_stream,
        'counties_ui': counties_ui,
        'constituencies_ui': constituencies_ui,
        'wards_ui': wards_ui,
        'expected_by_filter': expected_by_filter,
    }
    return _geo


def load_registered():
    global _registered
    if _registered is not None:
        return _registered
    idx = {}
    path = os.path.join(BASE_DIR, AGENTS_LOGIN_FILENAME)
    try:
        with open(path, encoding='utf-8-sig', errors='replace', newline='') as f:
            for r in csv.DictReader(f):
                stream = str(r.get('poll_station_name', '') or '').strip()
                if stream:
                    idx[norm(stream)] = to_int(r.get('total_registered_voters'))
    except Exception:
        pass
    _registered = idx
    return idx


def fetch_snapshot(force=False):
    now = time.time()
    if not force and _cache['snapshot'] is not None and now - _cache['snapshot_at'] < CACHE_SECONDS:
        return _cache['snapshot']

    with _fetch_lock:
        now = time.time()
        if not force and _cache['snapshot'] is not None and now - _cache['snapshot_at'] < CACHE_SECONDS:
            return _cache['snapshot']
        if not SIMULATION_BASE_URL or not SIMULATION_DASHBOARD_API_KEY:
            raise RuntimeError('Simulation dashboard connection is not configured.')
        try:
            r = _http.get(
                f'{SIMULATION_BASE_URL}/api/dashboard/governor',
                headers={'X-Dashboard-Key': SIMULATION_DASHBOARD_API_KEY},
                timeout=(3.0, UPSTREAM_TIMEOUT_SECONDS),
            )
            if not r.ok:
                raise RuntimeError(f'Simulation API HTTP {r.status_code}')
            data = r.json()
            _cache['snapshot'] = data
            _cache['snapshot_at'] = time.time()
            _cache['last_error'] = ''
            return data
        except Exception as exc:
            _cache['last_error'] = str(exc)
            if _cache['snapshot'] is not None:
                return _cache['snapshot']
            raise RuntimeError(f'Voting simulation is temporarily unavailable: {exc}')


def build_summary(county='', constituency='', ward=''):
    snap = fetch_snapshot()
    geo = load_geo()
    reg = load_registered()

    key = (norm(county), norm(constituency), norm(ward))
    expected = geo['expected_by_filter'].get(key, [])
    allowed = set(expected)
    stream_rows = snap.get('streams') or []

    candidate_names = {}
    candidate_votes = defaultdict(int)
    candidate_selections = skipped = participants = 0
    opened = closed = 0
    last_updated = ''

    for c in snap.get('candidates') or []:
        cid = str(c.get('candidate_id', '') or '')
        if cid:
            candidate_names[cid] = c.get('name') or cid

    for row in stream_rows:
        skey = norm(row.get('stream'))
        if skey not in allowed:
            continue
        status = str(row.get('status') or '').upper()
        if status in {'OPEN', 'CLOSED'}: opened += 1
        if status == 'CLOSED': closed += 1
        candidate_selections += to_int(row.get('candidate_selections'))
        skipped += to_int(row.get('skipped'))
        participants += to_int(row.get('participants'))
        names = row.get('candidate_names') or {}
        for cid, n in (row.get('candidate_votes') or {}).items():
            candidate_names[cid] = names.get(cid) or candidate_names.get(cid) or cid
            candidate_votes[cid] += to_int(n)
        t = row.get('closed_at') or row.get('opened_at') or ''
        if t > last_updated: last_updated = t

    registered = sum(reg.get(skey, 0) for skey in expected)
    expected_count = len(expected)
    not_started = max(0, expected_count - opened)
    total_votes_not_cast = max(0, registered - participants)

    # For the national/all-counties view, the upstream aggregate is authoritative.
    # This also prevents a harmless stream-key formatting difference from hiding live votes.
    if not county and not constituency and not ward:
        upstream_total = to_int((snap.get('totals') or {}).get('candidate_selections'))
        upstream_skipped = to_int((snap.get('totals') or {}).get('skipped'))
        upstream_participants = to_int((snap.get('totals') or {}).get('participants'))
        if upstream_total or upstream_skipped or upstream_participants:
            candidate_selections = upstream_total
            skipped = upstream_skipped
            participants = upstream_participants
            candidate_votes = defaultdict(int)
            for c in snap.get('candidates') or []:
                cid = str(c.get('candidate_id', '') or '')
                if cid:
                    candidate_names[cid] = c.get('name') or cid
                    candidate_votes[cid] = to_int(c.get('votes'))

    candidates = []
    for cid in set(candidate_names) | set(candidate_votes):
        votes = candidate_votes.get(cid, 0)
        candidates.append({
            'candidate_id': cid,
            'candidate': candidate_names.get(cid, cid),
            'votes': votes,
            'share': round((votes / candidate_selections * 100), 2) if candidate_selections else 0,
        })
    candidates.sort(key=lambda x: (-x['votes'], x['candidate'].lower()))

    return {
        'filters': {'county': county, 'constituency': constituency, 'ward': ward},
        'totals': {
            'registered_voters': registered,
            'candidate_selections': candidate_selections,
            'skipped': skipped,
            'participants': participants,
            'turnout_percent': round(participants / registered * 100, 2) if registered else 0,
            'skip_percent_registered': round(skipped / registered * 100, 2) if registered else 0,
            'total_votes_not_cast': total_votes_not_cast,
        },
        'reporting': {
            'expected_streams': expected_count,
            'opened_streams': opened,
            'closed_streams': closed,
            'not_started_streams': not_started,
        },
        'candidates': candidates,
        'last_updated': last_updated,
        'data_age_seconds': max(0, int(time.time() - _cache['snapshot_at'])) if _cache['snapshot_at'] else None,
        'using_cached_snapshot': bool(_cache['last_error']),
        'warning': _cache['last_error'] if _cache['last_error'] else '',
    }

def build_stream_status(county='', constituency='', ward='', submission_status='all', page=1, page_size=100):
    """Fast paginated stream submission view built from local hierarchy + cached live snapshot."""
    geo = load_geo()
    key = (norm(county), norm(constituency), norm(ward))
    expected = geo['expected_by_filter'].get(key, [])

    # Reuse the snapshot already loaded by the dashboard whenever possible so this
    # list does not create a second upstream request during normal page loading.
    snap = _cache.get('snapshot')
    if snap is None:
        snap = fetch_snapshot()

    live_by_stream = {}
    for row in (snap.get('streams') or []):
        skey = norm(row.get('stream'))
        if skey:
            live_by_stream[skey] = row

    wanted = str(submission_status or 'all').strip().lower()
    rows = []
    submitted_count = 0
    not_submitted_count = 0

    for skey in expected:
        g = geo['by_stream'].get(skey, {})
        live = live_by_stream.get(skey, {})
        live_status = str(live.get('status') or '').strip().upper()
        submitted = live_status == 'CLOSED'
        if submitted:
            submitted_count += 1
        else:
            not_submitted_count += 1

        if wanted == 'submitted' and not submitted:
            continue
        if wanted == 'not_submitted' and submitted:
            continue

        rows.append({
            'county': g.get('county_label') or friendly(g.get('county')),
            'constituency': g.get('constituency_label') or friendly(g.get('constituency')),
            'ward': g.get('ward_label') or friendly(g.get('ward')),
            'poll_station': friendly(g.get('poll_station')),
            'stream': g.get('stream') or live.get('stream') or '',
            'submission_status': 'CLOSED & SUBMITTED' if submitted else 'NOT YET SUBMITTED',
            'operational_status': live_status if live_status in {'OPEN', 'CLOSED'} else 'NOT STARTED',
            'opened_at': live.get('opened_at') or '',
            'closed_at': live.get('closed_at') or '',
        })

    rows.sort(key=lambda r: (
        norm(r['county']), norm(r['constituency']), norm(r['ward']),
        norm(r['poll_station']), norm(r['stream'])
    ))

    try:
        page = max(1, int(page))
    except Exception:
        page = 1
    try:
        page_size = min(200, max(25, int(page_size)))
    except Exception:
        page_size = 100

    total_filtered = len(rows)
    total_pages = max(1, (total_filtered + page_size - 1) // page_size)
    if page > total_pages:
        page = total_pages
    start = (page - 1) * page_size
    page_rows = rows[start:start + page_size]

    return {
        'filters': {
            'county': county,
            'constituency': constituency,
            'ward': ward,
            'submission_status': wanted,
        },
        'counts': {
            'expected_streams': len(expected),
            'submitted': submitted_count,
            'not_submitted': not_submitted_count,
            'filtered': total_filtered,
        },
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'rows': page_rows,
        'snapshot_age_seconds': max(0, int(time.time() - _cache['snapshot_at'])) if _cache['snapshot_at'] else None,
    }


@app.get('/')
@login_required
def index():
    return render_template('index.html', auth_enabled=bool(AUTH_USERNAME and AUTH_PASSWORD_HASH))


@app.get('/api/summary')
@login_required
def api_summary():
    try:
        return jsonify(build_summary(request.args.get('county', ''), request.args.get('constituency', ''), request.args.get('ward', '')))
    except Exception as exc:
        return jsonify({'error': str(exc)}), 503

@app.get('/api/stream-status')
@login_required
def api_stream_status():
    try:
        return jsonify(build_stream_status(
            request.args.get('county', ''),
            request.args.get('constituency', ''),
            request.args.get('ward', ''),
            request.args.get('submission_status', 'all'),
            request.args.get('page', 1),
            request.args.get('page_size', 100),
        ))
    except Exception as exc:
        return jsonify({'error': str(exc)}), 503


@app.get('/api/counties')
@login_required
def api_counties():
    rows = list(load_geo()['counties_ui'].values())
    return jsonify(sorted(rows, key=lambda x: x['label']))


@app.get('/api/constituencies')
@login_required
def api_constituencies():
    ck = norm(request.args.get('county', ''))
    rows = list(load_geo()['constituencies_ui'].get(ck, {}).values())
    return jsonify(sorted(rows, key=lambda x: x['label']))


@app.get('/api/wards')
@login_required
def api_wards():
    ck = norm(request.args.get('county', ''))
    cok = norm(request.args.get('constituency', ''))
    rows = list(load_geo()['wards_ui'].get((ck, cok), {}).values())
    return jsonify(sorted(rows, key=lambda x: x['label']))


@app.post('/api/refresh')
@login_required
def api_refresh():
    try:
        fetch_snapshot(force=True)
        return jsonify({'success': True})
    except Exception as exc:
        return jsonify({'success': False, 'error': str(exc)}), 503


@app.get('/health')
def health():
    # Never call the upstream simulation from health checks.
    return jsonify({'ok': True, 'service': 'gubernatorial-simulation-dashboard-fresh'})


# Load local CSV indexes once at worker startup. This is local-only and avoids
# expensive parsing during the first browser request.
try:
    load_geo()
    load_registered()
except Exception:
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5000')))
