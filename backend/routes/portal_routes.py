from flask import Blueprint, Response, redirect, url_for
from flask_login import current_user, login_required

portal_routes = Blueprint('portal', __name__)


ORG_PORTAL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Organization insights</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root { --p:#2563eb; --bg:#f8fafc; --card:#fff; --b:#e2e8f0; --t:#1e293b; --g:#64748b; }
    body { margin:0; font-family:system-ui,sans-serif; background:var(--bg); color:var(--t); }
    header h1 { font-size:1.12rem; margin:0; flex:1; min-width:180px; }
    .portal-head { background:var(--card); border-bottom:1px solid var(--b); padding:14px 24px 18px; }
    .portal-head-row { display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px; margin-bottom:10px; }
    .portal-bar { display:flex; flex-wrap:wrap; gap:6px 10px; align-items:center; }
    .portal-bar a { color:var(--p); text-decoration:none; font-weight:600; font-size:.86rem; padding:7px 12px; border-radius:8px; }
    .portal-bar a:hover { background:rgba(37,99,235,.08); }
    .portal-bar a.active { background:rgba(37,99,235,.14); color:#1e40af; }
    main { padding:24px; max-width:1280px; margin:0 auto; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:20px; margin-bottom:24px; }
    .panel { background:var(--card); border:1px solid var(--b); border-radius:12px; padding:20px; }
    .panel h2 { margin:0 0 12px; font-size:.95rem; color:var(--g); text-transform:uppercase; letter-spacing:.04em; }
    .kpi { font-size:2rem; font-weight:700; color:var(--p); }
    canvas { max-height:320px; }
    .pill { display:inline-block; padding:4px 10px; border-radius:999px; background:rgba(37,99,235,.1); color:var(--p); font-size:.8rem; font-weight:600; }
    .detail { margin-top:20px; }
    table { width:100%; border-collapse:collapse; font-size:.88rem; }
    th,td { text-align:left; padding:8px 10px; border-bottom:1px solid var(--b); }
  </style>
</head>
<body>
<header class="portal-head">
  <div class="portal-head-row">
    <h1><span class="pill">Organization</span> Insights overview</h1>
  </div>
  <nav class="portal-bar" aria-label="Primary">
    <a href="/">Admin home</a>
    <a href="/view-employees">Initiate calls</a>
    <a href="/portal/org" class="active">Organization insights</a>
    <a href="/auth/logout">Log out</a>
  </nav>
</header>
<main id="root">
  <p>Loading dashboards…</p>
</main>
<script>
(async function () {
  const r = await fetch('/api/insights/org/dashboard', { credentials: 'same-origin' });
  if (r.status === 401) { window.location = '/auth/login/org'; return; }
  const json = await r.json();
  if (!json.data) { document.getElementById('root').innerHTML = '<p>Unable to load data.</p>'; return; }
  const d = json.data;
  const ov = d.overview || {};
  document.getElementById('root').innerHTML = `
    <div class="grid">
      <div class="panel"><h2>Employees</h2><div class="kpi">${ov.total_employees ?? '—'}</div></div>
      <div class="panel"><h2>Avg wellbeing score</h2><div class="kpi">${ov.avg_score != null ? ov.avg_score.toFixed(1) : '—'}</div></div>
      <div class="panel"><h2>Avg sentiment (compound)</h2><div class="kpi">${ov.avg_sentiment_compound != null ? ov.avg_sentiment_compound : '—'}</div></div>
    </div>
    <div class="grid">
      <div class="panel"><h2>Latest sentiment distribution</h2><canvas id="chSent"></canvas></div>
      <div class="panel"><h2>Avg score by department</h2><canvas id="chDept"></canvas></div>
    </div>
    <div class="panel detail"><h2>Assessment trend (90 days)</h2><canvas id="chLine"></canvas></div>
    <div class="panel detail"><h2>Recent assessments</h2><div id="tbl"></div></div>
  `;

  const sd = d.sentiment_distribution || {};
  new Chart(document.getElementById('chSent'), {
    type: 'doughnut',
    data: {
      labels: ['Positive','Neutral','Negative'],
      datasets: [{ data: [sd.positive||0, sd.neutral||0, sd.negative||0],
        backgroundColor: ['#10b981','#94a3b8','#f43f5e'] }]
    },
    options: { plugins: { legend: { position: 'bottom' } } }
  });

  const dept = d.department_avg_scores || [];
  new Chart(document.getElementById('chDept'), {
    type: 'bar',
    data: {
      labels: dept.map(x => x.department),
      datasets: [{ label: 'Avg score', data: dept.map(x => x.avg_score), backgroundColor: '#3b82f6' }]
    },
    options: { scales: { y: { beginAtZero: true, max: 100 } }, plugins: { legend: { display: false } } }
  });

  const tl = d.timeline || [];
  new Chart(document.getElementById('chLine'), {
    type: 'line',
    data: {
      labels: tl.map(x => x.date.slice(0, 10)),
      datasets: [{
        label: 'Score',
        data: tl.map(x => x.score),
        borderColor: '#2563eb',
        tension: 0.2,
        fill: false
      }]
    },
    options: { scales: { x: { ticks: { maxTicksLimit: 10 } } } }
  });

  const rows = (tl.slice(-15)).reverse().map(x =>
    `<tr><td>${x.date}</td><td>${x.score}</td><td>${x.sentiment_label||'—'}</td><td>${x.employee_id}</td></tr>`).join('');
  document.getElementById('tbl').innerHTML = '<table><thead><tr><th>Date</th><th>Score</th><th>Sentiment</th><th>Emp ID</th></tr></thead><tbody>' + rows + '</tbody></table>';
})();
</script>
</body>
</html>
"""


EMP_PORTAL_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Your insights</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root { --p:#2563eb; --bg:#f8fafc; --card:#fff; --b:#e2e8f0; --t:#1e293b; --g:#64748b; }
    body { margin:0; font-family:system-ui,sans-serif; background:var(--bg); color:var(--t); }
    header h1 { font-size:1.12rem; margin:0; flex:1; min-width:180px; }
    .portal-head { background:var(--card); border-bottom:1px solid var(--b); padding:14px 24px 18px; }
    .portal-head-row { display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px; margin-bottom:10px; }
    .portal-bar { display:flex; flex-wrap:wrap; gap:6px 10px; align-items:center; }
    .portal-bar a { color:var(--p); text-decoration:none; font-weight:600; font-size:.86rem; padding:7px 12px; border-radius:8px; }
    .portal-bar a:hover { background:rgba(37,99,235,.08); }
    .portal-bar a.active { background:rgba(37,99,235,.14); color:#1e40af; }
    main { padding:24px; max-width:960px; margin:0 auto; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:16px; margin-bottom:20px; }
    .panel { background:var(--card); border:1px solid var(--b); border-radius:12px; padding:18px; }
    .panel h2 { margin:0 0 10px; font-size:.85rem; color:var(--g); text-transform:uppercase; letter-spacing:.04em; }
    .kpi { font-size:1.75rem; font-weight:700; color:var(--p); }
    canvas { max-height:280px; }
    .list { font-size:.9rem; line-height:1.5; }
    .list article { border-bottom:1px solid var(--b); padding:12px 0; }
    button.link { background:none;border:none;color:var(--p);cursor:pointer;font-weight:600;text-decoration:underline;padding:0;font:inherit;}
    #detailBox { white-space:pre-wrap; font-size:.88rem; background:#f1f5f9; padding:12px; border-radius:8px; margin-top:12px; display:none; }
  </style>
</head>
<body>
<header class="portal-head">
  <div class="portal-head-row">
    <h1>Personal wellbeing insights</h1>
  </div>
  <nav class="portal-bar" aria-label="Primary">
    <a href="/portal/employee" class="active">My wellbeing</a>
    <a href="/auth/logout">Log out</a>
  </nav>
</header>
<main id="root"><p>Loading…</p></main>
<div id="detailBox"></div>
<script>
(async function () {
  const r = await fetch('/api/insights/employee/dashboard', { credentials: 'same-origin' });
  if (r.status === 401) { window.location = '/auth/login/employee'; return; }
  const json = await r.json();
  if (!json.data) { document.getElementById('root').innerHTML = '<p>Unable to load.</p>'; return; }
  const d = json.data;
  const emp = d.employee || {};
  const ov = d.overview || {};
  document.getElementById('root').innerHTML = `
    <p style="margin-bottom:16px;"><strong>${emp.full_name||''}</strong> · ${emp.email||''}</p>
    <div class="grid">
      <div class="panel"><h2>Latest score</h2><div class="kpi">${ov.latest_score != null ? ov.latest_score : '—'}</div></div>
      <div class="panel"><h2>Assessments</h2><div class="kpi">${ov.assessment_count ?? 0}</div></div>
    </div>
    <div class="grid">
      <div class="panel"><h2>Score over time</h2><canvas id="chLine"></canvas></div>
      <div class="panel"><h2>Latest sentiment mix</h2><canvas id="chRadar"></canvas></div>
    </div>
    <div class="panel list"><h2>History</h2><div id="hist"></div></div>
  `;

  const tl = d.timeline || [];
  new Chart(document.getElementById('chLine'), {
    type: 'line',
    data: {
      labels: tl.map(x => x.date.slice(0, 10)),
      datasets: [{ label: 'Score', data: tl.map(x => x.score), borderColor: '#2563eb', tension: 0.2, fill: true, backgroundColor: 'rgba(37,99,235,.08)' }]
    },
    options: { scales: { y: { beginAtZero: true, max: 100 } } }
  });

  const br = d.latest_sentiment_breakdown;
  if (br) {
    new Chart(document.getElementById('chRadar'), {
      type: 'bar',
      data: {
        labels: ['Positive', 'Neutral', 'Negative'],
        datasets: [{ data: [br.pos, br.neu, br.neg], backgroundColor: ['#10b981','#94a3b8','#f43f5e'] }]
      },
      options: { scales: { y: { beginAtZero: true, max: 1 } }, plugins: { legend: { display: false } } }
    });
  } else {
    document.getElementById('chRadar').replaceWith(Object.assign(document.createElement('p'), { textContent: 'Complete a voice assessment to see sentiment mix.' }));
  }

  const hist = document.getElementById('hist');
  (d.assessments||[]).forEach(function (a) {
    const art = document.createElement('article');
    art.innerHTML = '<strong>' + a.assessment_date.slice(0,10) + '</strong> · Score ' + a.score + ' · ' + (a.sentiment_label||'') +
      (a.has_transcript ? ' · <button type="button" class="link" data-aid="'+a.id+'">View details</button>' : '');
    hist.appendChild(art);
  });

  hist.addEventListener('click', async function (ev) {
    const btn = ev.target.closest('button[data-aid]');
    if (!btn) return;
    const box = document.getElementById('detailBox');
    box.style.display = 'block';
    box.textContent = 'Loading…';
    const rr = await fetch('/api/insights/employee/assessment/' + btn.dataset.aid, { credentials: 'same-origin' });
    const jj = await rr.json();
    if (jj.data) {
      box.textContent = 'Summary\n' + (jj.data.summary||'') + '\n\nRecommendations\n' + (jj.data.recommendations||'') +
        '\n\nTranscript\n' + (jj.data.transcript||'(none)');
    } else box.textContent = 'Could not load.';
  });
})();
</script>
</body>
</html>
"""


SUPER_PORTAL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Super admin — platform insights</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root { --p:#1d4ed8; --bg:#f8fafc; --card:#fff; --b:#e2e8f0; --t:#1e293b; --g:#64748b; }
    body { margin:0; font-family:system-ui,sans-serif; background:var(--bg); color:var(--t); }
    header h1 { font-size:1.12rem; margin:0; flex:1; min-width:180px; }
    .portal-head { background:var(--card); border-bottom:1px solid var(--b); padding:14px 24px 18px; }
    .portal-head-row { display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px; margin-bottom:10px; }
    .portal-bar { display:flex; flex-wrap:wrap; gap:6px 10px; align-items:center; }
    .portal-bar a { color:var(--p); text-decoration:none; font-weight:600; font-size:.86rem; padding:7px 12px; border-radius:8px; }
    .portal-bar a:hover { background:rgba(37,99,235,.08); }
    .portal-bar a.active { background:rgba(37,99,235,.14); color:#1e40af; }
    main { padding:24px; max-width:1400px; margin:0 auto; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:16px; margin-bottom:24px; }
    .panel { background:var(--card); border:1px solid var(--b); border-radius:12px; padding:18px; }
    .panel h2 { margin:0 0 10px; font-size:.82rem; color:var(--g); text-transform:uppercase; letter-spacing:.04em; }
    .kpi { font-size:1.85rem; font-weight:700; color:var(--p); }
    canvas { max-height:300px; }
    .pill { display:inline-block; padding:4px 10px; border-radius:999px; background:rgba(29,78,216,.12); color:var(--p); font-size:.8rem; font-weight:600; }
    table { width:100%; border-collapse:collapse; font-size:.85rem; }
    th,td { text-align:left; padding:8px 10px; border-bottom:1px solid var(--b); }
    .scroll { overflow:auto; max-height:360px; }
    .detail { margin-top:20px; }
  </style>
</head>
<body>
<header class="portal-head">
  <div class="portal-head-row">
    <h1><span class="pill">Super admin</span> All organizations & analytics</h1>
  </div>
  <nav class="portal-bar" aria-label="Primary">
    <a href="/">Admin home</a>
    <a href="/view-employees">Initiate calls</a>
    <a href="/portal/super" class="active">Super admin insights</a>
    <a href="/auth/logout">Log out</a>
  </nav>
</header>
<main id="root"><p>Loading platform insights…</p></main>
<script>
(function () {
  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
  }
  (async function () {
    const r = await fetch('/api/insights/super/dashboard', { credentials: 'same-origin' });
    if (r.status === 401) { window.location = '/auth/login/super'; return; }
    if (r.status === 403) { document.getElementById('root').innerHTML = '<p>Access denied.</p>'; return; }
    const json = await r.json();
    if (!json.data) { document.getElementById('root').innerHTML = '<p>Unable to load data.</p>'; return; }
    const d = json.data;
    const ov = d.overview || {};
    document.getElementById('root').innerHTML = `
      <div class="grid">
        <div class="panel"><h2>Organizations</h2><div class="kpi">${ov.organization_count ?? '—'}</div></div>
        <div class="panel"><h2>Employees (all)</h2><div class="kpi">${ov.total_employees ?? '—'}</div></div>
        <div class="panel"><h2>Assessments (all)</h2><div class="kpi">${ov.total_assessments ?? '—'}</div></div>
        <div class="panel"><h2>Global avg wellbeing score</h2><div class="kpi">${ov.global_avg_score != null ? ov.global_avg_score : '—'}</div></div>
        <div class="panel"><h2>Avg sentiment (compound)</h2><div class="kpi">${ov.avg_sentiment_compound != null ? ov.avg_sentiment_compound : '—'}</div></div>
      </div>
      <div class="grid">
        <div class="panel"><h2>Sentiment distribution (latest per employee)</h2><canvas id="chSent"></canvas></div>
        <div class="panel"><h2>Avg score by organization</h2><canvas id="chOrg"></canvas></div>
      </div>
      <div class="panel detail"><h2>Assessment trend (90 days, daily average)</h2><canvas id="chLine"></canvas></div>
      <div class="panel detail"><h2>Organizations</h2><div class="scroll" id="tblOrgs"></div></div>
      <div class="panel detail"><h2>Employees (preview)</h2><div class="scroll" id="tblEmp"></div></div>
    `;

    const sd = d.sentiment_distribution || {};
    new Chart(document.getElementById('chSent'), {
      type: 'doughnut',
      data: {
        labels: ['Positive','Neutral','Negative'],
        datasets: [{ data: [sd.positive||0, sd.neutral||0, sd.negative||0],
          backgroundColor: ['#10b981','#94a3b8','#f43f5e'] }]
      },
      options: { plugins: { legend: { position: 'bottom' } } }
    });

    const orgRows = d.organizations || [];
    const orgLabels = orgRows.map(function (o) {
      var on = o.organization && o.organization.name;
      return on || ('Org #' + (o.organization && o.organization.id));
    });
    const orgScores = orgRows.map(function (o) {
      return o.average_score != null ? Number(o.average_score) : 0;
    });
    new Chart(document.getElementById('chOrg'), {
      type: 'bar',
      data: {
        labels: orgLabels,
        datasets: [{ label: 'Avg score', data: orgScores, backgroundColor: '#2563eb' }]
      },
      options: { scales: { y: { beginAtZero: true, max: 100 } }, plugins: { legend: { display: false } } }
    });

    const tl = d.timeline || [];
    var byDay = {};
    tl.forEach(function (x) {
      var day = x.date.slice(0, 10);
      if (!byDay[day]) byDay[day] = { sum: 0, n: 0 };
      byDay[day].sum += x.score;
      byDay[day].n += 1;
    });
    var dayKeys = Object.keys(byDay).sort();
    var dailyAvg = dayKeys.map(function (k) { return byDay[k].sum / byDay[k].n; });

    new Chart(document.getElementById('chLine'), {
      type: 'line',
      data: {
        labels: dayKeys,
        datasets: [{
          label: 'Daily avg score',
          data: dailyAvg,
          borderColor: '#1d4ed8',
          tension: 0.2,
          fill: false
        }]
      },
      options: { scales: { x: { ticks: { maxTicksLimit: 14 } } } }
    });

    var orgHtml = '<table><thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Employees</th><th>Avg score</th></tr></thead><tbody>';
    orgRows.forEach(function (o) {
      var org = o.organization || {};
      orgHtml += '<tr><td>' + esc(org.id) + '</td><td>' + esc(org.name) + '</td><td>' + esc(org.email) +
        '</td><td>' + esc(o.total_employees) + '</td><td>' + esc(o.average_score != null ? o.average_score.toFixed(1) : '—') + '</td></tr>';
    });
    orgHtml += '</tbody></table>';
    document.getElementById('tblOrgs').innerHTML = orgHtml || '<p>No organizations.</p>';

    var prev = d.employees_preview || [];
    var empHtml = '<table><thead><tr><th>ID</th><th>Org</th><th>Name</th><th>Email</th><th>Dept</th><th>Score</th></tr></thead><tbody>';
    prev.forEach(function (e) {
      empHtml += '<tr><td>' + esc(e.id) + '</td><td>' + esc(e.organization_name) + '</td><td>' + esc(e.full_name) +
        '</td><td>' + esc(e.email) + '</td><td>' + esc(e.department) + '</td><td>' + esc(e.assessment_score) + '</td></tr>';
    });
    empHtml += '</tbody></table>';
    document.getElementById('tblEmp').innerHTML = empHtml || '<p>No employees.</p>';
  })();
})();
</script>
</body>
</html>
"""


@portal_routes.route('/portal/super')
@login_required
def super_portal():
    if getattr(current_user, 'role', None) != 'super':
        return redirect(url_for('auth.login_super'))
    return Response(SUPER_PORTAL_HTML, mimetype='text/html')


@portal_routes.route('/portal/org')
@login_required
def org_portal():
    if getattr(current_user, 'role', None) != 'org':
        return redirect(url_for('auth.login_org'))
    return Response(ORG_PORTAL_HTML, mimetype='text/html')


@portal_routes.route('/portal/employee')
@login_required
def employee_portal():
    if getattr(current_user, 'role', None) != 'employee':
        return redirect(url_for('auth.login_employee'))
    return Response(EMP_PORTAL_HTML, mimetype='text/html')
