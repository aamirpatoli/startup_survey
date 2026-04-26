import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory

import psycopg2
import psycopg2.extras

app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL')

FIELD_LABELS = {
    'consent': 'Consent',
    'startup_name': 'Startup Name',
    'role': 'Role',
    'stage': 'Startup Stage',
    'team_size': 'Team Size',
    'time_to_market': 'Time to Market',
    'biz_changes': 'Business Model Changes',
    'uncertainty': 'Uncertainty in Requirements (1-10)',
    'domain': 'Domain',
    'product_desc': 'Product Description',
    'tech_stack': 'Technology Stack',
    'deployment': 'Deployment Environment',
    'devops': 'Use of DevOps / CI-CD',
    'methodology': 'Development Methodology',
    'agile_method': 'Agile Method',
    'sprint_length': 'Sprint Length',
    'team_structure': 'Team Structure',
    'collab_tools': 'Collaboration Tools',
    'version_control': 'Version Control',
    'code_review': 'Code Review Practice',
    'testing': 'Testing Approach',
    'documentation': 'Documentation Level',
    'tech_debt': 'Technical Debt Awareness',
    'scalability': 'Scalability Concern',
    'security': 'Security Priority',
    'regulatory': 'Regulatory Environment',
    'feedback_importance': 'Customer Feedback Importance',
    'competition': 'Market Competitiveness',
    'deadlines': 'Project Deadlines',
    'revenue_pressure': 'Revenue Pressure',
    'funding_influence': 'Investor / Incubator Influence',
    'business_risks': 'Biggest Business Risks',
    'incubator_support': 'Incubation Center Support',
    'incubator_promotes': 'Incubator Promotes Methodologies',
    'peer_agile': 'Other Startups Follow Agile',
    'ai_support': 'Support for AI-based Methodologies (1-10)',
    'incubator_influence': 'Incubator Influence on Success',
    'challenges': 'Main Challenges',
    'satisfaction': 'Satisfaction with Current Process (1-10)',
    'process_change': 'Process Changed in Last 12 Months',
    'change_reason': 'Reason for Change',
    'lessons': 'Lessons Learned',
    'mentorship_needs': 'Mentorship Needs',
    'goals': 'Top Goals',
    'ai_guidance': 'Open to AI-based Guidance',
    'pilot_participation': 'Willing to Participate in Pilot',
    'success_factors': 'What Makes a Process Successful',
    'process_issues': 'Process-related Issues',
    'ai_features': 'AI Features Needed',
    'ai_vision': 'AI Vision for Startup',
    'maturity': 'Overall Process Maturity (1-10)',
    'suggestions': 'Final Suggestions',
    'redesign': 'What Would You Do Differently',
}

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       background: #f0f2f5; color: #333; padding: 30px; }
h1 { color: #667eea; margin-bottom: 5px; }
.subtitle { color: #888; margin-bottom: 30px; }
.stats { display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 30px; }
.card { background: white; border-radius: 12px; padding: 20px 28px;
        box-shadow: 0 2px 12px rgba(0,0,0,.08); min-width: 180px; }
.card h3 { font-size: 13px; color: #888; text-transform: uppercase; letter-spacing: 1px; }
.card p { font-size: 36px; font-weight: 700; color: #667eea; margin-top: 8px; }
.breakdown { background: white; border-radius: 12px; padding: 20px;
             box-shadow: 0 2px 12px rgba(0,0,0,.08); margin-bottom: 20px; }
.breakdown h2 { font-size: 16px; color: #555; margin-bottom: 15px; }
.charts { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px; margin-bottom: 30px; }
.bar-row { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.bar-label { width: 160px; font-size: 13px; text-align: right; color: #666; }
.bar { background: linear-gradient(90deg,#667eea,#764ba2); border-radius: 4px;
       height: 20px; min-width: 4px; }
.bar-val { font-size: 12px; color: #888; }
.table-wrap { overflow-x: auto; border-radius: 12px;
              box-shadow: 0 2px 12px rgba(0,0,0,.08); margin-bottom: 20px; }
table { width: 100%; border-collapse: collapse; background: white; min-width: 900px; }
th { background: linear-gradient(135deg,#667eea,#764ba2); color: white;
     padding: 12px 14px; text-align: left; font-size: 12px; white-space: nowrap; }
td { padding: 10px 14px; font-size: 12px; border-bottom: 1px solid #f0f0f0; white-space: nowrap;
     max-width: 180px; overflow: hidden; text-overflow: ellipsis; }
tr:last-child td { border-bottom: none; }
tr.clickable:hover td { background: #f0f0ff; cursor: pointer; }
a { color: #667eea; text-decoration: none; }
a:hover { text-decoration: underline; }
.badge { display: inline-block; padding: 2px 10px; border-radius: 20px;
         background: #ede9fe; color: #6d28d9; font-size: 11px; font-weight: 600; }
.btn { display: inline-block; padding: 8px 18px; border-radius: 8px;
       background: linear-gradient(135deg,#667eea,#764ba2); color: white;
       font-size: 13px; font-weight: 600; text-decoration: none; }
.btn:hover { opacity: .9; text-decoration: none; }
.footer { margin-top: 20px; color: #aaa; font-size: 12px; display: flex; gap: 16px; align-items: center; }

/* Detail page */
.detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px,1fr));
               gap: 16px; margin-top: 24px; }
.detail-card { background: white; border-radius: 12px; padding: 20px;
               box-shadow: 0 2px 12px rgba(0,0,0,.08); }
.detail-card h3 { font-size: 13px; color: #667eea; font-weight: 700;
                  text-transform: uppercase; letter-spacing: .5px; margin-bottom: 14px;
                  padding-bottom: 8px; border-bottom: 2px solid #ede9fe; }
.field-row { display: flex; flex-direction: column; margin-bottom: 12px; }
.field-label { font-size: 11px; color: #999; text-transform: uppercase;
               letter-spacing: .5px; margin-bottom: 3px; }
.field-value { font-size: 14px; color: #333; font-weight: 500; }
.field-value.long { font-size: 13px; font-weight: 400; color: #555;
                    background: #f8f8ff; padding: 8px 10px; border-radius: 6px; }
.nav { display: flex; gap: 12px; align-items: center; margin-bottom: 24px; flex-wrap: wrap; }
"""

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

def flatten_response(r):
    rec = dict(r)
    extra = {}
    if rec.get('extra_fields'):
        try:
            extra = json.loads(rec['extra_fields'])
        except:
            pass
        del rec['extra_fields']
    rec.update(extra)
    if rec.get('tech_stack') and isinstance(rec['tech_stack'], str):
        rec['tech_stack'] = rec['tech_stack'].replace(',', ', ')
    return rec

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
    # flatten list values
    for k, v in extra.items():
        if isinstance(v, list):
            extra[k] = ', '.join(v)
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
    roles, stages, domains, teams, deployments = {}, {}, {}, {}, {}
    for r in rows:
        for d, key in [(roles,'role'),(stages,'stage'),(domains,'domain'),(teams,'team_size'),(deployments,'deployment')]:
            v = r[key] or 'N/A'
            d[v] = d.get(v, 0) + 1

    def bars(data):
        mx = max(data.values()) if data else 1
        return ''.join([
            f'<div class="bar-row"><div class="bar-label">{k}</div>'
            f'<div class="bar" style="width:{max(4,int(v/mx*200))}px"></div>'
            f'<div class="bar-val">{v}</div></div>'
            for k, v in sorted(data.items(), key=lambda x: -x[1])
        ])

    # Table with more columns
    rows_html = ''.join([
        f'<tr class="clickable" onclick="location.href=\'/response/{r["id"]}\'">'
        f'<td>{r["id"]}</td>'
        f'<td>{str(r["submitted_at"])[:16].replace("T"," ")}</td>'
        f'<td>{r["startup_name"] or "<em style=color:#bbb>Anon</em>"}</td>'
        f'<td><span class="badge">{r["role"] or "—"}</span></td>'
        f'<td>{r["stage"] or "—"}</td>'
        f'<td>{r["domain"] or "—"}</td>'
        f'<td>{r["team_size"] or "—"}</td>'
        f'<td>{r["deployment"] or "—"}</td>'
        f'<td>{r["time_to_market"] or "—"}</td>'
        f'<td><a href="/response/{r["id"]}">View all →</a></td>'
        f'</tr>'
        for r in rows
    ]) or "<tr><td colspan='10' style='text-align:center;color:#aaa;padding:30px'>No responses yet!</td></tr>"

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Survey Dashboard</title>
<style>{CSS}</style></head><body>
<h1>📊 Survey Dashboard</h1>
<p class="subtitle">Software Development Practices — Startup Survey</p>
<div class="stats">
  <div class="card"><h3>Total Responses</h3><p>{total}</p></div>
</div>
<div class="charts">
  <div class="breakdown"><h2>By Role</h2>{bars(roles)}</div>
  <div class="breakdown"><h2>By Stage</h2>{bars(stages)}</div>
  <div class="breakdown"><h2>By Domain</h2>{bars(domains)}</div>
  <div class="breakdown"><h2>By Team Size</h2>{bars(teams)}</div>
  <div class="breakdown"><h2>By Deployment</h2>{bars(deployments)}</div>
</div>
<div class="table-wrap">
<table>
  <thead><tr>
    <th>#</th><th>Submitted</th><th>Startup</th><th>Role</th>
    <th>Stage</th><th>Domain</th><th>Team</th><th>Deployment</th>
    <th>Time to Market</th><th>Details</th>
  </tr></thead>
  <tbody>{rows_html}</tbody>
</table>
</div>
<div class="footer">
  <a href="/" class="btn">← Back to Survey</a>
  <a href="/export">⬇ Export JSON</a>
</div>
</body></html>"""

@app.route('/response/<int:rid>')
def response_detail(rid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM responses WHERE id = %s', (rid,))
    row = cur.fetchone()
    # get prev/next
    cur.execute('SELECT id FROM responses ORDER BY id')
    all_ids = [r['id'] for r in cur.fetchall()]
    cur.close()
    conn.close()

    if not row:
        return '<h2>Response not found</h2>', 404

    rec = flatten_response(row)
    idx = all_ids.index(rid)
    prev_id = all_ids[idx - 1] if idx > 0 else None
    next_id = all_ids[idx + 1] if idx < len(all_ids) - 1 else None

    # Group fields into sections
    sections = {
        '🏢 Basic Info': ['startup_name','role','stage','team_size','domain','product_desc'],
        '⚙️ Development': ['tech_stack','deployment','devops','methodology','agile_method',
                           'sprint_length','team_structure','collab_tools','version_control',
                           'code_review','testing','documentation','tech_debt'],
        '📈 Business Context': ['time_to_market','biz_changes','uncertainty','scalability',
                                'security','regulatory','feedback_importance','competition',
                                'deadlines','revenue_pressure','funding_influence','business_risks'],
        '🏫 Incubator': ['incubator_support','incubator_promotes','peer_agile',
                         'ai_support','incubator_influence'],
        '🎯 Goals & Future': ['challenges','satisfaction','process_change','change_reason',
                              'lessons','mentorship_needs','goals','ai_guidance',
                              'pilot_participation','success_factors','process_issues',
                              'ai_features','ai_vision','maturity','suggestions','redesign'],
    }

    def field_html(key):
        val = rec.get(key)
        if not val:
            return ''
        label = FIELD_LABELS.get(key, key.replace('_', ' ').title())
        long_val = len(str(val)) > 60
        val_class = 'field-value long' if long_val else 'field-value'
        return f'<div class="field-row"><div class="field-label">{label}</div><div class="{val_class}">{val}</div></div>'

    sections_html = ''
    for sec_title, keys in sections.items():
        fields = ''.join([field_html(k) for k in keys if rec.get(k)])
        if fields:
            sections_html += f'<div class="detail-card"><h3>{sec_title}</h3>{fields}</div>'

    nav_html = ''
    if prev_id:
        nav_html += f'<a href="/response/{prev_id}" class="btn">← Prev</a>'
    if next_id:
        nav_html += f'<a href="/response/{next_id}" class="btn">Next →</a>'

    name = rec.get('startup_name') or f'Response #{rid}'
    submitted = str(rec.get('submitted_at',''))[:16].replace('T',' ')

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>{name} — Response Detail</title>
<style>{CSS}</style></head><body>
<div class="nav">
  <a href="/dashboard">← Dashboard</a>
  <span style="color:#bbb">|</span>
  <span style="color:#888;font-size:13px">Response #{rid} · Submitted {submitted}</span>
  <span style="flex:1"></span>
  {nav_html}
</div>
<h1>📋 {name}</h1>
<p class="subtitle">{rec.get('role','') or ''} {'· ' + rec.get('domain','') if rec.get('domain') else ''}</p>
<div class="detail-grid">{sections_html}</div>
<div class="footer">
  <a href="/dashboard">← Back to Dashboard</a>
  <a href="/export">⬇ Export All JSON</a>
</div>
</body></html>"""

@app.route('/export')
def export():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM responses ORDER BY submitted_at DESC')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([flatten_response(r) for r in rows])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
