"""Dark-themed Super Admin analytics dashboard (Chart.js). Loaded by portal_routes."""

SUPER_PORTAL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Super admin — platform analytics</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root {
      --bg:#12121b; --card:#1c1c26; --border:#2d2d3a;
      --cyan:#00f2ff; --magenta:#ff00e5; --purple:#7000ff; --blue:#3b82f6;
      --text:#e2e8f0; --muted:#64748b; --grid:#2d2d3a;
    }
    body.super-dash { margin:0; font-family:system-ui,-apple-system,sans-serif; background:var(--bg); color:var(--text); min-height:100vh; }
    .super-dash header.portal-head { background:#16161f; border-bottom:1px solid var(--border); }
    .super-dash .portal-head-row h1 { color:var(--text); }
    .super-dash .pill { background:linear-gradient(135deg,rgba(112,0,255,.35),rgba(0,242,255,.2)); border:1px solid rgba(0,242,255,.25); color:var(--cyan); }
    .super-dash .portal-bar a { color:#94a3b8; }
    .super-dash .portal-bar a:hover { color:var(--cyan); background:rgba(0,242,255,.08); }
    .super-dash .portal-bar a.active { color:var(--cyan); background:rgba(0,242,255,.12); }
    .dash-wrap { padding:20px 24px 48px; max-width:1480px; margin:0 auto; }
    .dash-hero { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; margin-bottom:16px; }
    .hero-card {
      border-radius:16px; padding:22px 24px; min-height:120px;
      background:linear-gradient(135deg,rgba(112,0,255,.45) 0%,rgba(255,0,229,.18) 100%);
      border:1px solid rgba(255,0,229,.25);
      box-shadow:0 8px 32px rgba(0,0,0,.35);
    }
    .hero-card.alt {
      background:linear-gradient(135deg,rgba(0,242,255,.25) 0%,rgba(59,130,246,.35) 100%);
      border-color:rgba(0,242,255,.3);
    }
    .hero-card h3 { margin:0 0 8px; font-size:.75rem; font-weight:600; text-transform:uppercase; letter-spacing:.08em; color:rgba(255,255,255,.75); }
    .hero-card .big { font-size:2.1rem; font-weight:800; letter-spacing:-.03em; color:#fff; }
    .hero-card .sub { margin-top:8px; font-size:.82rem; color:rgba(255,255,255,.65); }
    .dash-pills { display:flex; flex-wrap:wrap; gap:10px; margin-bottom:20px; }
    .pill-stat {
      background:var(--card); border:1px solid var(--border); border-radius:12px; padding:10px 16px; font-size:.85rem;
      display:flex; align-items:center; gap:10px; color:var(--text);
    }
    .pill-stat em { font-style:normal; color:var(--cyan); font-weight:700; }
    .dash-grid {
      display:grid; grid-template-columns:repeat(12,1fr); gap:16px; margin-bottom:16px;
    }
    .dash-panel {
      background:var(--card); border:1px solid var(--border); border-radius:14px; padding:16px 18px;
      box-shadow:0 4px 24px rgba(0,0,0,.25);
    }
    .dash-panel h2 {
      margin:0 0 14px; font-size:.72rem; font-weight:600; text-transform:uppercase; letter-spacing:.09em; color:var(--muted);
    }
    .dash-panel.w6 { grid-column:span 6; }
    .dash-panel.w4 { grid-column:span 4; }
    .dash-panel.w8 { grid-column:span 8; }
    .dash-panel.w12 { grid-column:span 12; }
    @media (max-width:1024px) {
      .dash-panel.w6,.dash-panel.w4,.dash-panel.w8 { grid-column:span 12; }
    }
    .dash-panel canvas { max-height:320px !important; }
    .dash-tables { display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:16px; margin-top:8px; }
    .dash-tables .scroll { overflow:auto; max-height:320px; }
    .dash-tables table { width:100%; border-collapse:collapse; font-size:.82rem; }
    .dash-tables th,.dash-tables td { padding:8px 10px; border-bottom:1px solid var(--border); text-align:left; color:#cbd5e1; }
    .dash-tables th { color:var(--muted); font-weight:600; font-size:.72rem; text-transform:uppercase; letter-spacing:.04em; }
  </style>
</head>
<body class="super-dash">
<header class="portal-head">
  <div class="portal-head-row">
    <h1><span class="pill">Super admin</span> Platform analytics</h1>
  </div>
  <nav class="portal-bar" aria-label="Primary">
    <a href="/">Admin home</a>
    <a href="/view-employees">Initiate calls</a>
    <a href="/portal/super" class="active">Super admin insights</a>
    <a href="/auth/logout">Log out</a>
  </nav>
</header>
<main id="root" class="dash-wrap"><p style="color:var(--muted);">Loading platform insights…</p></main>
<script>
(function () {
  function esc(s) {
    return String(s == null ? '' : s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
  }

  function chartTextColor() { return '#94a3b8'; }
  function chartGridColor() { return '#2d2d3a'; }

  function baseChartOpts() {
    return {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { labels: { color: chartTextColor(), font: { size: 11 } } },
        tooltip: {
          backgroundColor: 'rgba(22,22,31,.95)',
          titleColor: '#e2e8f0',
          bodyColor: '#cbd5e1',
          borderColor: '#3b82f6',
          borderWidth: 1
        }
      },
      scales: {
        x: {
          grid: { color: chartGridColor() },
          ticks: { color: '#64748b', maxRotation: 45, minRotation: 0 }
        },
        y: {
          grid: { color: chartGridColor() },
          ticks: { color: '#64748b' }
        }
      }
    };
  }

  function gradientBar(ctx, area, c1, c2) {
    if (!area) return c1;
    const g = ctx.createLinearGradient(0, area.bottom, 0, area.top);
    g.addColorStop(0, c2);
    g.addColorStop(1, c1);
    return g;
  }

  (async function () {
    const r = await fetch('/api/insights/super/dashboard', { credentials: 'same-origin' });
    if (r.status === 401) { window.location = '/auth/login/super'; return; }
    if (r.status === 403) { document.getElementById('root').innerHTML = '<p>Access denied.</p>'; return; }
    const json = await r.json();
    if (!json.data) { document.getElementById('root').innerHTML = '<p>Unable to load data.</p>'; return; }
    const d = json.data;
    const ov = d.overview || {};

    document.getElementById('root').innerHTML =
      '<div class="dash-hero">' +
        '<div class="hero-card">' +
          '<h3>Global avg wellbeing score</h3>' +
          '<div class="big" id="heroScore">—</div>' +
          '<div class="sub">Across all organizations (employee latest scores)</div>' +
        '</div>' +
        '<div class="hero-card alt">' +
          '<h3>Call completion rate</h3>' +
          '<div class="big" id="heroComplete">—</div>' +
          '<div class="sub">Completed call assessments ÷ total assessments</div>' +
        '</div>' +
      '</div>' +
      '<div class="dash-pills" id="dashPills"></div>' +
      '<div class="dash-grid">' +
        '<div class="dash-panel w8">' +
          '<h2>Recorded vs completed calls (by month)</h2>' +
          '<canvas id="chMonthly"></canvas>' +
        '</div>' +
        '<div class="dash-panel w4">' +
          '<h2>Volume &amp; score (90 days)</h2>' +
          '<canvas id="chArea"></canvas>' +
        '</div>' +
        '<div class="dash-panel w6">' +
          '<h2>Weekly volume — recorded vs completed</h2>' +
          '<canvas id="chWeekly"></canvas>' +
        '</div>' +
        '<div class="dash-panel w6">' +
          '<h2>Assessments by weekday (90d)</h2>' +
          '<canvas id="chWeekday"></canvas>' +
        '</div>' +
        '<div class="dash-panel w4">' +
          '<h2>Latest sentiment (per employee)</h2>' +
          '<canvas id="chSent"></canvas>' +
        '</div>' +
        '<div class="dash-panel w4">' +
          '<h2>Supportive vs needs attention</h2>' +
          '<canvas id="chArc"></canvas>' +
          '<p id="arcNote" style="margin:10px 0 0;font-size:.78rem;color:var(--muted);text-align:center;line-height:1.4;"></p>' +
        '</div>' +
        '<div class="dash-panel w4">' +
          '<h2>Risk band (all assessments)</h2>' +
          '<canvas id="chRisk"></canvas>' +
        '</div>' +
        '<div class="dash-panel w6">' +
          '<h2>Avg score by organization</h2>' +
          '<canvas id="chOrg"></canvas>' +
        '</div>' +
        '<div class="dash-panel w6">' +
          '<h2>Daily avg score (90 days)</h2>' +
          '<canvas id="chDaily"></canvas>' +
        '</div>' +
      '</div>' +
      '<div class="dash-tables">' +
        '<div class="dash-panel"><h2>Organizations</h2><div class="scroll" id="tblOrgs"></div></div>' +
        '<div class="dash-panel"><h2>Employees (preview)</h2><div class="scroll" id="tblEmp"></div></div>' +
      '</div>';

    document.getElementById('heroScore').textContent =
      ov.global_avg_score != null ? Number(ov.global_avg_score).toFixed(1) : '—';
    document.getElementById('heroComplete').textContent =
      ov.completion_rate_pct != null ? String(ov.completion_rate_pct) + '%' : '—';

    var pills = document.getElementById('dashPills');
    pills.innerHTML =
      '<span class="pill-stat">Orgs <em>' + (ov.organization_count ?? '—') + '</em></span>' +
      '<span class="pill-stat">Employees <em>' + (ov.total_employees ?? '—') + '</em></span>' +
      '<span class="pill-stat">Assessments <em>' + (ov.total_assessments ?? '—') + '</em></span>' +
      '<span class="pill-stat">Pending calls <em>' + (ov.pending_calls ?? 0) + '</em></span>' +
      '<span class="pill-stat">Completed calls <em>' + (ov.completed_calls ?? 0) + '</em></span>' +
      '<span class="pill-stat">Avg sentiment <em>' + (ov.avg_sentiment_compound != null ? ov.avg_sentiment_compound : '—') + '</em></span>';

    Chart.defaults.color = chartTextColor();
    Chart.defaults.borderColor = chartGridColor();

    var mc = d.monthly_comparison || [];
    new Chart(document.getElementById('chMonthly'), {
      type: 'line',
      data: {
        labels: mc.map(function (x) { return x.label || x.month; }),
        datasets: [
          {
            label: 'Recorded assessments',
            data: mc.map(function (x) { return x.recorded; }),
            borderColor: '#00f2ff',
            backgroundColor: 'rgba(0,242,255,.08)',
            tension: 0.35,
            fill: false,
            borderWidth: 2,
            pointRadius: 3
          },
          {
            label: 'Calls completed',
            data: mc.map(function (x) { return x.calls_completed; }),
            borderColor: '#ff00e5',
            borderDash: [6, 4],
            tension: 0.35,
            fill: false,
            borderWidth: 2,
            pointRadius: 3
          }
        ]
      },
      options: Object.assign({}, baseChartOpts(), {
        scales: {
          x: Object.assign({}, baseChartOpts().scales.x, { ticks: Object.assign({}, baseChartOpts().scales.x.ticks, { maxTicksLimit: 10 }) }),
          y: Object.assign({}, baseChartOpts().scales.y, { beginAtZero: true, ticks: Object.assign({}, baseChartOpts().scales.y.ticks, { stepSize: 1 }) })
        },
        plugins: Object.assign({}, baseChartOpts().plugins, { legend: { position: 'bottom' } })
      })
    });

    var da = d.daily_area || [];
    new Chart(document.getElementById('chArea'), {
      type: 'line',
      data: {
        labels: da.map(function (x) { return x.date.slice(5); }),
        datasets: [
          {
            label: 'Avg score',
            data: da.map(function (x) { return x.avg_score; }),
            yAxisID: 'y',
            borderColor: '#7000ff',
            backgroundColor: 'rgba(112,0,255,.25)',
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            pointRadius: 0
          },
          {
            label: 'Daily volume',
            data: da.map(function (x) { return x.volume; }),
            yAxisID: 'y1',
            borderColor: '#00f2ff',
            backgroundColor: 'rgba(0,242,255,.12)',
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            pointRadius: 0
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        interaction: { mode: 'index', intersect: false },
        plugins: baseChartOpts().plugins,
        scales: {
          x: Object.assign({}, baseChartOpts().scales.x, { ticks: Object.assign({}, baseChartOpts().scales.x.ticks, { maxTicksLimit: 12 }) }),
          y: {
            type: 'linear',
            position: 'left',
            min: 0,
            max: 100,
            grid: { color: chartGridColor() },
            ticks: { color: '#64748b' },
            title: { display: true, text: 'Score', color: '#64748b', font: { size: 11 } }
          },
          y1: {
            type: 'linear',
            position: 'right',
            min: 0,
            grid: { drawOnChartArea: false },
            ticks: { color: '#64748b' },
            title: { display: true, text: 'Count', color: '#64748b', font: { size: 11 } }
          }
        }
      }
    });

    var wc = d.weekly_comparison || [];
    new Chart(document.getElementById('chWeekly'), {
      type: 'line',
      data: {
        labels: wc.map(function (x) { return x.label || x.week_start; }),
        datasets: [
          {
            label: 'Recorded',
            data: wc.map(function (x) { return x.recorded; }),
            borderColor: '#00f2ff',
            tension: 0.3,
            fill: true,
            backgroundColor: 'rgba(0,242,255,.15)',
            borderWidth: 2
          },
          {
            label: 'Completed',
            data: wc.map(function (x) { return x.calls_completed; }),
            borderColor: '#ff00e5',
            tension: 0.3,
            fill: true,
            backgroundColor: 'rgba(255,0,229,.12)',
            borderWidth: 2
          }
        ]
      },
      options: Object.assign({}, baseChartOpts(), {
        scales: {
          x: Object.assign({}, baseChartOpts().scales.x, { ticks: Object.assign({}, baseChartOpts().scales.x.ticks, { maxTicksLimit: 12 }) }),
          y: Object.assign({}, baseChartOpts().scales.y, { beginAtZero: true })
        },
        plugins: Object.assign({}, baseChartOpts().plugins, { legend: { position: 'bottom' } })
      })
    });

    var wv = d.weekday_volume || { labels: [], counts: [] };
    var wCtx = document.getElementById('chWeekday').getContext('2d');
    new Chart(wCtx, {
      type: 'bar',
      data: {
        labels: wv.labels || [],
        datasets: [{
          label: 'Assessments',
          data: (wv.counts || []).map(function (n) { return n; }),
          borderRadius: 8,
          borderSkipped: false,
          backgroundColor: function (ctx) {
            var ch = ctx.chart;
            var ca = ch.chartArea;
            return gradientBar(ch.ctx, ca, '#00f2ff', '#3b82f6');
          }
        }]
      },
      options: Object.assign({}, baseChartOpts(), {
        plugins: Object.assign({}, baseChartOpts().plugins, { legend: { display: false } }),
        scales: Object.assign({}, baseChartOpts().scales, {
          y: Object.assign({}, baseChartOpts().scales.y, { beginAtZero: true })
        })
      })
    });

    var sd = d.sentiment_distribution || {};
    new Chart(document.getElementById('chSent'), {
      type: 'doughnut',
      data: {
        labels: ['Positive', 'Neutral', 'Negative'],
        datasets: [{
          data: [sd.positive || 0, sd.neutral || 0, sd.negative || 0],
          backgroundColor: ['#10b981', '#64748b', '#f43f5e'],
          borderWidth: 0,
          hoverOffset: 8
        }]
      },
      options: {
        cutout: '62%',
        plugins: Object.assign({}, baseChartOpts().plugins, {
          legend: { position: 'right', labels: { boxWidth: 12, padding: 14 } }
        })
      }
    });

    var arc = d.sentiment_arc || { positive: 0, other: 0 };
    var arcTotal = arc.total_latest || ((arc.positive || 0) + (arc.other || 0));
    var pctPos = arcTotal ? Math.round(100 * (arc.positive || 0) / arcTotal) : 0;
    new Chart(document.getElementById('chArc'), {
      type: 'doughnut',
      data: {
        labels: ['Positive trend', 'Neutral / negative'],
        datasets: [{
          data: [arc.positive || 0, arc.other || 0],
          backgroundColor: ['#ff00e5', '#334155'],
          borderWidth: 0
        }]
      },
      options: {
        cutout: '72%',
        plugins: Object.assign({}, baseChartOpts().plugins, {
          legend: { position: 'bottom', labels: { color: chartTextColor(), padding: 12 } }
        })
      }
    });
    var arcNoteEl = document.getElementById('arcNote');
    if (arcNoteEl) {
      arcNoteEl.textContent = arcTotal
        ? pctPos + '% positive share (latest sentiment per employee)'
        : 'No sentiment breakdown yet.';
    }

    var risk = d.risk_status_distribution || {};
    var riskLabels = Object.keys(risk);
    var riskVals = riskLabels.map(function (k) { return risk[k]; });
    var riskColors = ['#22c55e', '#eab308', '#f97316', '#ef4444', '#64748b'];
    if (!riskLabels.length) {
      document.getElementById('chRisk').style.display = 'none';
      var rp = document.getElementById('chRisk').closest('.dash-panel');
      if (rp) {
        var empty = document.createElement('p');
        empty.style.cssText = 'color:var(--muted);font-size:.85rem;margin:12px 0 0;';
        empty.textContent = 'No risk band data.';
        rp.appendChild(empty);
      }
    } else {
    new Chart(document.getElementById('chRisk'), {
      type: 'bar',
      data: {
        labels: riskLabels.map(function (s) { return s.charAt(0).toUpperCase() + s.slice(1); }),
        datasets: [{
          label: 'Count',
          data: riskVals,
          borderRadius: 6,
          backgroundColor: riskLabels.map(function (_, i) { return riskColors[i % riskColors.length]; })
        }]
      },
      options: Object.assign({}, baseChartOpts(), {
        indexAxis: 'y',
        plugins: Object.assign({}, baseChartOpts().plugins, { legend: { display: false } }),
        scales: Object.assign({}, baseChartOpts().scales, {
          x: Object.assign({}, baseChartOpts().scales.x, { beginAtZero: true })
        })
      })
    });
    }

    var orgRows = d.organizations || [];
    var orgLabels = orgRows.map(function (o) {
      var on = o.organization && o.organization.name;
      return on || ('Org #' + (o.organization && o.organization.id));
    });
    var orgScores = orgRows.map(function (o) {
      return o.average_score != null ? Number(o.average_score) : 0;
    });
    var oCtx = document.getElementById('chOrg').getContext('2d');
    new Chart(oCtx, {
      type: 'bar',
      data: {
        labels: orgLabels,
        datasets: [{
          label: 'Avg score',
          data: orgScores,
          borderRadius: 8,
          backgroundColor: function (ctx) {
            var ch = ctx.chart;
            var ca = ch.chartArea;
            return gradientBar(ch.ctx, ca, '#7000ff', '#3b82f6');
          }
        }]
      },
      options: Object.assign({}, baseChartOpts(), {
        plugins: Object.assign({}, baseChartOpts().plugins, { legend: { display: false } }),
        scales: Object.assign({}, baseChartOpts().scales, {
          y: Object.assign({}, baseChartOpts().scales.y, { beginAtZero: true, max: 100 })
        })
      })
    });

    var tl = d.timeline || [];
    var byDay = {};
    tl.forEach(function (x) {
      var day = x.date.slice(0, 10);
      if (!byDay[day]) byDay[day] = { sum: 0, n: 0 };
      byDay[day].sum += x.score;
      byDay[day].n += 1;
    });
    var dayKeys = Object.keys(byDay).sort();
    var dailyAvg = dayKeys.map(function (k) { return byDay[k].sum / byDay[k].n; });

    new Chart(document.getElementById('chDaily'), {
      type: 'line',
      data: {
        labels: dayKeys.map(function (k) { return k.slice(5); }),
        datasets: [{
          label: 'Daily avg score',
          data: dailyAvg,
          borderColor: '#00f2ff',
          backgroundColor: 'rgba(0,242,255,.12)',
          tension: 0.35,
          fill: true,
          borderWidth: 2,
          pointRadius: 0
        }]
      },
      options: Object.assign({}, baseChartOpts(), {
        scales: Object.assign({}, baseChartOpts().scales, {
          x: Object.assign({}, baseChartOpts().scales.x, { ticks: Object.assign({}, baseChartOpts().scales.x.ticks, { maxTicksLimit: 14 }) }),
          y: Object.assign({}, baseChartOpts().scales.y, { min: 0, max: 100 })
        }),
        plugins: Object.assign({}, baseChartOpts().plugins, { legend: { display: false } })
      })
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
