import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory

import psycopg2
import psycopg2.extras

app = Flask(__name__)

# ── Database connection ─────────────────────────────────────────
# On Render, DATABASE_URL is set automatically when you attach a PostgreSQL DB.
# Locally, you can set it in a .env file or just use SQLite fallback.
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id              SERIAL PRIMARY KEY,
            submitted_at    TEXT NOT NULL,
            consent         TEXT,
            startup_name    TEXT,
            role            TEXT,
            stage           TEXT,
            team_size       TEXT,
            time_to_market  TEXT,
            biz_changes     TEXT,
            uncertainty     TEXT,
            domain          TEXT,
            product_desc    TEXT,
            tech_stack      TEXT,
            deployment      TEXT,
            devops          TEXT,
            extra_fields    TEXT
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

init_db()

# ── Routes ──────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('.', 'startup_survey_web.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json or {}
    now = datetime.utcnow().isoformat()

    core = {
        'submitted_at':   now,
        'consent':        data.get('consent'),
        'startup_name':   data.get('startup_name'),
        'role':           data.get('role'),
        'stage':          data.get('stage'),
        'team_size':      data.get('team_size'),
        'time_to_market': data.get('time_to_market'),
        'biz_changes':    data.get('biz_changes'),
        'uncertainty':    data.get('uncertainty'),
        'domain':         data.get('domain'),
        'product_desc':   data.get('product_desc'),
        'tech_stack':     ','.join(data.get('tech_stack', [])) if isinstance(data.get('tech_stack'), list) else data.get('tech_stack', ''),
        'deployment':     data.get('deployment'),
        'devops':         data.get('devops'),
    }

    known_keys = set(core.keys())
    extra = {k: v for k, v in data.items() if k not in known_keys}

    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO responses
            (submitted_at, consent, startup_name, role, stage, team_size,
             time_to_market, biz_changes, uncertainty, domain, product_desc,
             tech_stack, deployment, devops, extra_fields)
        VALUES
            (%(submitted_at)s, %(consent)s, %(startup_name)s, %(role)s, %(stage)s,
             %(team_size)s, %(time_to_market)s, %(biz_changes)s, %(uncertainty)s,
             %(domain)s, %(product_desc)s, %(tech_stack)s, %(deployment)s,
             %(devops)s, %(extra_fields)s)
    ''', {**core, 'extra_fields': json.dumps(extra)})
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'ok', 'message': 'Response saved!'})

@app.route('/dashboard')
def dashboard():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM responses ORDER BY submitted_at DESC')
    rows = cur.fetchall()
    cur.close()
    conn.close()

    total = len(rows)
    roles, stages, domains = {}, {}, {}
    for r in rows:
        roles[r['role']]   = roles.get(r['role'], 0) + 1
        stages[r['stage']] = stages.get(r['stage'], 0) + 1
        domains[r['domain']] = domains.get(r['domain'], 0) + 1

    def bars(data):
        mx = max(data.values()) if data else 1
        return ''.join([
            f'<div class="bar-row">'
            f'<div class="bar-label">{k or "N/A"}</div>'
            f'<div class="bar" style="width:{max(4,int(v/mx*220))}px"></div>'
            f'<div class="bar-val">{v}</div></div>'
            for k, v in sorted(data.items(), key=lambda x: -x[1])
        ])

    rows_html = ''.join([
        f"<tr><td>{r['id']}</td>"
        f"<td>{str(r['submitted_at'])[:16].replace('T',' ')}</td>"
        f"<td>{r['startup_name'] or '<em style=color:#bbb>Anonymous</em>'}</td>"
        f"<td><span class='badge'>{r['role'] or '—'}</span></td>"
        f"<td>{r['stage'] or '—'}</td>"
        f"<td>{r['domain'] or '—'}</td>"
        f"<td>{r['team_size'] or '—'}</td></tr>"
        for r in rows
    ]) or "<tr><td colspan='7' style='text-align:center;color:#aaa;padding:30px'>No responses yet. Share the survey!</td></tr>"

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Survey Dashboard</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;color:#333;padding:30px}}
  h1{{color:#667eea;margin-bottom:5px}} .subtitle{{color:#888;margin-bottom:30px}}
  .stats{{display:flex;gap:20px;flex-wrap:wrap;margin-bottom:30px}}
  .card{{background:white;border-radius:12px;padding:20px 28px;box-shadow:0 2px 12px rgba(0,0,0,.08);min-width:180px}}
  .card h3{{font-size:13px;color:#888;text-transform:uppercase;letter-spacing:1px}}
  .card p{{font-size:36px;font-weight:700;color:#667eea;margin-top:8px}}
  .breakdown{{background:white;border-radius:12px;padding:20px;box-shadow:0 2px 12px rgba(0,0,0,.08);margin-bottom:30px}}
  .breakdown h2{{font-size:16px;color:#555;margin-bottom:15px}}
  .bar-row{{display:flex;align-items:center;gap:12px;margin-bottom:8px}}
  .bar-label{{width:140px;font-size:13px;text-align:right;color:#666}}
  .bar{{background:linear-gradient(90deg,#667eea,#764ba2);border-radius:4px;height:20px;min-width:4px}}
  .bar-val{{font-size:12px;color:#888}}
  table{{width:100%;border-collapse:collapse;background:white;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.08)}}
  th{{background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:12px 16px;text-align:left;font-size:13px}}
  td{{padding:11px 16px;font-size:13px;border-bottom:1px solid #f0f0f0}}
  tr:last-child td{{border-bottom:none}} tr:hover td{{background:#fafbff}}
  a{{color:#667eea;text-decoration:none}}
  .badge{{display:inline-block;padding:2px 10px;border-radius:20px;background:#ede9fe;color:#6d28d9;font-size:11px;font-weight:600}}
</style></head><body>
<h1>📊 Survey Dashboard</h1>
<p class="subtitle">Software Development Practices — Startup Survey</p>
<div class="stats"><div class="card"><h3>Total Responses</h3><p>{total}</p></div></div>
<div class="breakdown"><h2>By Role</h2>{bars(roles)}</div>
<div class="breakdown"><h2>By Stage</h2>{bars(stages)}</div>
<div class="breakdown"><h2>By Domain</h2>{bars(domains)}</div>
<table><thead><tr><th>#</th><th>Submitted</th><th>Startup</th><th>Role</th><th>Stage</th><th>Domain</th><th>Team</th></tr></thead>
<tbody>{rows_html}</tbody></table>
<p style="margin-top:20px;color:#aaa;font-size:12px">
  <a href="/">← Back to Survey</a> &nbsp;|&nbsp; <a href="/export">⬇ Export JSON</a>
</p></body></html>"""

@app.route('/export')
def export():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM responses ORDER BY submitted_at DESC')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    result = []
    for r in rows:
        rec = dict(r)
        if rec.get('extra_fields'):
            rec.update(json.loads(rec['extra_fields']))
            del rec['extra_fields']
        if rec.get('tech_stack'):
            rec['tech_stack'] = rec['tech_stack'].split(',')
        result.append(rec)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
