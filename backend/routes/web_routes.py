from flask import Blueprint, Response, redirect, request, url_for
from flask_login import current_user

from backend.models.organization import Organization

web_routes = Blueprint('web', __name__)


def _require_org_or_super_admin_ui():
    """
    Organization management UI (orgs, employees, initiate calls, system health).
    Allowed: org admin or super admin. Bootstrap: zero orgs -> open access.
    Employees are redirected to the employee login/portal.
    """
    if Organization.query.count() == 0:
        return None
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login_org', next=request.url))
    role = getattr(current_user, 'role', None)
    if role in ('org', 'super'):
        return None
    if role == 'employee':
        return redirect(url_for('auth.login_employee', next=request.url))
    return redirect(url_for('auth.login_org', next=request.url))


def _sidebar_nav_html(active_path, role, bootstrap):
    """Left nav for admin shell: routes and insight portals based on role."""

    def item(href, icon, label):
        is_home = href == '/' and active_path == '/'
        active = (
            ' class="active"'
            if (active_path == href or is_home)
            else ''
        )
        return (
            f'<li><a href="{href}"{active}><span>{icon}</span> {label}</a></li>'
        )

    lines = [
        item('/', '🏢', 'Organizations'),
        item('/employees', '👥', 'Add Employee'),
        item('/view-employees', '📞', 'Initiate calls'),
        item('/dashboard', '⚕️', 'System Health'),
    ]
    if bootstrap:
        lines.append(item('/auth/login/org', '🔐', 'Org insights login'))
        lines.append(item('/auth/login/employee', '👤', 'Employee insights login'))
        lines.append(item('/auth/login/super', '🛡️', 'Super admin login'))
    else:
        lines.append(item('/portal/org', '📊', 'Organization insights'))
        if role == 'super':
            lines.append(item('/portal/super', '🛡️', 'Super admin insights'))
        lines.append('<li><a href="/auth/logout"><span>🚪</span> Log out</a></li>')
    return '<ul class="sidebar-nav">\n' + '\n'.join(lines) + '\n</ul>'


def _top_bar_html(role, bootstrap):
    """Fixed top strip: sign-in CTAs when bootstrapping; role + logout when admin."""
    base = (
        '<header role="banner" style="position:fixed;top:0;left:0;right:0;z-index:10003;'
        'height:48px;background:#0f172a;display:flex;align-items:center;padding:0 16px;gap:12px;'
        'font-family:system-ui,sans-serif;box-shadow:0 2px 8px rgba(0,0,0,.2);">'
    )
    if bootstrap:
        return (
            base
            + '<span style="color:#f8fafc;font-weight:700;margin-right:auto;font-size:14px;">MHM · Sign in</span>'
            + '<a href="/auth/login/org" style="background:#2563eb;color:#fff;text-decoration:none;padding:9px 14px;border-radius:8px;font-weight:600;font-size:13px;">Organization login</a>'
            + '<a href="/auth/login/employee" style="background:#fff;color:#1e40af;text-decoration:none;padding:9px 14px;border-radius:8px;font-weight:600;font-size:13px;">Employee login</a>'
            + '<a href="/auth/login/super" style="background:#334155;color:#f8fafc;text-decoration:none;padding:9px 14px;border-radius:8px;font-weight:600;font-size:13px;">Super admin</a>'
            + '</header>'
        )
    who = 'Organization admin' if role == 'org' else 'Super admin'
    return (
        base
        + f'<span style="color:#f8fafc;font-weight:700;margin-right:auto;font-size:14px;">MHM · {who}</span>'
        + '<a href="/auth/logout" style="background:#fff;color:#1e40af;text-decoration:none;padding:9px 14px;border-radius:8px;font-weight:600;font-size:13px;">Log out</a>'
        + '</header>'
    )


def _inject_admin_shell(page_html, active_path):
    """Inject dynamic top bar + sidebar; hide promo banner when signed-in admin."""
    role = getattr(current_user, 'role', None) if current_user.is_authenticated else None
    bootstrap = Organization.query.count() == 0
    html = page_html.replace('<!--MHM_ADMIN_TOP_BAR-->', _top_bar_html(role, bootstrap))
    html = html.replace('<!--MHM_ADMIN_SIDE_NAV-->', _sidebar_nav_html(active_path, role, bootstrap))
    if role in ('org', 'super') and not bootstrap:
        html = html.replace('</head>', '<style>.login-banner{display:none!important}</style></head>', 1)
    return html

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mental Health Monitoring System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        :root {
            --primary: #2563eb;
            --primary-light: #3b82f6;
            --dark: #1e293b;
            --gray: #64748b;
            --gray-light: #f1f5f9;
            --gray-lighter: #f8fafc;
            --border: #e2e8f0;
            --success: #10b981;
            --warning: #f59e0b;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--gray-lighter);
            color: var(--dark);
            display: flex;
            min-height: 100vh;
            line-height: 1.6;
        }
        /* Sidebar Navigation */
        .sidebar {
            width: 280px;
            background: white;
            border-right: 1px solid var(--border);
            padding: 0;
            position: fixed;
            left: 0;
            top: 0;
            bottom: 0;
            overflow-y: auto;
            z-index: 1000;
        }
        .sidebar-brand {
            padding: 24px 20px;
            border-bottom: 1px solid var(--border);
        }
        .sidebar-brand h2 {
            font-size: 1.5em;
            color: var(--primary);
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        .sidebar-brand p {
            font-size: 0.75em;
            color: var(--gray);
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 500;
        }
        .sidebar-nav {
            list-style: none;
            padding: 12px 0;
        }
        .sidebar-nav li {
            margin: 0;
        }
        .sidebar-nav a {
            display: flex;
            align-items: center;
            padding: 12px 20px;
            color: var(--gray);
            text-decoration: none;
            font-size: 0.95em;
            font-weight: 500;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
            gap: 10px;
        }
        .sidebar-nav a:hover {
            background: var(--gray-light);
            color: var(--primary);
            border-left-color: var(--primary);
        }
        .sidebar-nav a.active {
            background: var(--primary-light);
            background: rgba(37, 99, 235, 0.08);
            color: var(--primary);
            border-left-color: var(--primary);
            font-weight: 600;
        }
        .sidebar-nav a span {
            font-size: 1.1em;
        }
        /* Main Content */
        .main-content {
            margin-left: 280px;
            flex: 1;
            padding: 32px;
            background: var(--gray-lighter);
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            margin-bottom: 32px;
        }
        .header h1 {
            font-size: 2.2em;
            font-weight: 700;
            color: var(--dark);
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }
        .header p {
            color: var(--gray);
            font-size: 1em;
        }
        .status-box {
            background: white;
            border: 1px solid var(--border);
            border-left: 4px solid var(--success);
            padding: 16px 20px;
            border-radius: 8px;
            margin-bottom: 24px;
            font-weight: 500;
            color: var(--success);
            font-size: 0.95em;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }
        .stat-card {
            background: white;
            padding: 24px;
            border-radius: 8px;
            border: 1px solid var(--border);
            text-align: center;
            transition: all 0.2s ease;
        }
        .stat-card:hover {
            border-color: var(--primary);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08);
        }
        .stat-card h3 {
            font-size: 0.9em;
            color: var(--gray);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }
        .stat-card .number {
            font-size: 2.2em;
            font-weight: 700;
            color: var(--primary);
            margin: 8px 0;
        }
        .stat-card .label {
            color: var(--gray);
            font-size: 0.85em;
            font-weight: 500;
        }
        .form-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 32px;
        }
        .form-card {
            background: white;
            padding: 28px;
            border-radius: 8px;
            border: 1px solid var(--border);
        }
        .form-card h2 {
            color: var(--dark);
            margin-bottom: 20px;
            font-size: 1.4em;
            font-weight: 600;
        }
        .form-group {
            margin-bottom: 16px;
        }
        .form-group label {
            display: block;
            margin-bottom: 6px;
            color: var(--dark);
            font-weight: 500;
            font-size: 0.95em;
        }
        .form-group input,
        .form-group select {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 0.95em;
            font-family: inherit;
            transition: all 0.2s;
            background: white;
            color: var(--dark);
        }
        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.08);
        }
        button {
            background: var(--primary);
            color: white;
            padding: 11px 24px;
            border: none;
            border-radius: 6px;
            font-size: 0.95em;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.2s;
        }
        button:hover {
            background: var(--primary-light);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        }
        button:active {
            transform: translateY(0);
        }
        .message {
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 16px;
            display: none;
            font-size: 0.95em;
            border: 1px solid;
        }
        .message.success {
            background: rgba(16, 185, 129, 0.08);
            color: #047857;
            border-color: rgba(16, 185, 129, 0.3);
            display: block;
        }
        .message.error {
            background: rgba(239, 68, 68, 0.08);
            color: #991b1b;
            border-color: rgba(239, 68, 68, 0.3);
            display: block;
        }
        .orgs-list, .emps-list {
            background: white;
            padding: 24px;
            border-radius: 8px;
            border: 1px solid var(--border);
            margin-bottom: 32px;
        }
        .orgs-list h3, .emps-list h3 {
            color: var(--dark);
            margin-bottom: 16px;
            font-size: 1.3em;
            font-weight: 600;
        }
        .list-item {
            padding: 16px;
            margin: 12px 0;
            background: var(--gray-light);
            border-left: 3px solid var(--primary);
            border-radius: 6px;
            transition: all 0.2s;
        }
        .list-item:hover {
            background: rgba(37, 99, 235, 0.04);
        }
        .list-item strong {
            color: var(--dark);
            font-weight: 600;
        }
        .list-item .email {
            font-size: 0.9em;
            color: var(--gray);
            margin-top: 6px;
        }
        .login-banner {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 12px;
            padding: 14px 18px;
            margin-bottom: 24px;
            background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%);
            border: 1px solid var(--border);
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(15,23,42,.06);
        }
        .login-banner-lead {
            font-weight: 600;
            color: var(--dark);
            flex-basis: 100%;
            font-size: 0.95rem;
            margin-bottom: 4px;
        }
        .login-banner-btn {
            display: inline-block;
            padding: 10px 18px;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            text-decoration: none;
            transition: 0.15s;
            border: 2px solid transparent;
        }
        .login-banner-btn-primary {
            background: var(--primary);
            color: white !important;
        }
        .login-banner-btn-outline {
            background: white;
            color: var(--primary) !important;
            border-color: var(--primary);
        }
        .login-banner-note {
            flex-basis: 100%;
            font-size: 0.82rem;
            color: var(--gray);
            margin: 6px 0 0 0;
            line-height: 1.45;
        }
        @media (max-width: 768px) {
            .form-section {
                grid-template-columns: 1fr;
            }
            .sidebar {
                width: 250px;
            }
            .main-content {
                margin-left: 250px;
                padding: 20px;
            }
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>

    <script>
        function setActiveNav(path) {
            const links = document.querySelectorAll('.sidebar-nav a');
            links.forEach(link => {
                if (link.getAttribute('href') === path) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        }
        window.addEventListener('load', () => {
            setActiveNav(window.location.pathname);
        });
    </script>
</head>
<body class="has-top-strip">
<style>
body.has-top-strip .sidebar { top: 48px !important; height: calc(100vh - 48px) !important; }
body.has-top-strip .main-content { padding-top: 48px !important; }
</style>
    <!--MHM_ADMIN_TOP_BAR-->
    <!-- Sidebar Navigation -->
    <aside class="sidebar">
        <div class="sidebar-brand">
            <h2>🏥 MHM</h2>
            <p>Mental Health</p>
        </div>
        <!--MHM_ADMIN_SIDE_NAV-->
    </aside>

    <!-- Main Content -->
    <div class="main-content">
        <div class="login-banner" role="navigation" aria-label="Sign in">
            <span class="login-banner-lead">Already registered? Sign in to wellbeing insights</span>
            <a href="/auth/login/org" class="login-banner-btn login-banner-btn-primary">Organization login</a>
            <a href="/auth/login/employee" class="login-banner-btn login-banner-btn-outline">Employee login</a>
            <p class="login-banner-note">Insights dashboards: /portal/org and /portal/employee · Admin tools below require org login when organizations exist.</p>
        </div>
        <div class="container">
        <div class="header">
            <h1>System Health</h1>
            <p>Mental Health Monitoring System - Assessment & Tracking</p>
        </div>

        <div class="status-box">
            <h3>✅ System Status: ONLINE</h3>
            <p>API ready · Configure SECRET_KEY and WEBHOOK_SECRET for production</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>📊 API Status</h3>
                <div class="number">✓</div>
                <div class="label">REST API Operational</div>
            </div>
            <div class="stat-card">
                <h3>🏢 Organizations</h3>
                <div class="number" id="org-count">0</div>
                <div class="label">Total registered</div>
            </div>
            <div class="stat-card">
                <h3>👥 Employees</h3>
                <div class="number" id="emp-count">0</div>
                <div class="label">Total registered</div>
            </div>
            <div class="stat-card">
                <h3>📈 Assessment Progress</h3>
                <div class="number" id="assess-percent">0%</div>
                <div class="label">Completed</div>
            </div>
        </div>

        <div class="orgs-list">
            <h3>📋 Organizations List</h3>
            <div id="orgsList"></div>
        </div>

        <div class="emps-list">
            <h3>📋 Employees List</h3>
            <div id="empsList"></div>
        </div>
    </div>

    <script>
        // Load data on page load
        window.addEventListener('load', () => {
            loadOrganizations();
            loadEmployees();
            loadStats();
            // Refresh every 5 seconds
            setInterval(() => {
                loadStats();
                loadOrganizations();
                loadEmployees();
            }, 5000);
        });

        function loadStats() {
            fetch('/api/organizations')
                .then(r => r.json())
                .then(data => {
                    if (data.data && Array.isArray(data.data)) {
                        document.getElementById('org-count').textContent = data.data.length;
                        
                        let totalEmps = 0;
                        for (const org of data.data) {
                            totalEmps += org.total_employees || 0;
                        }
                        document.getElementById('emp-count').textContent = totalEmps;
                    }
                })
                .catch(e => console.error('Error loading stats:', e));
        }

        function loadOrganizations() {
            fetch('/api/organizations')
                .then(r => r.json())
                .then(data => {
                    const select = document.getElementById('orgSelect');
                    select.innerHTML = '<option value="">-- Select Organization --</option>';
                    
                    const list = document.getElementById('orgsList');
                    if (data.data && data.data.length > 0) {
                        list.innerHTML = data.data.map(org => `
                            <div class="list-item">
                                <strong>${org.name}</strong>
                                <div class="email">${org.email} | ${org.phone}</div>
                                <div class="email" style="margin-top: 8px;">
                                    Industry: <strong>${org.industry || 'N/A'}</strong> | 
                                    Employees: <strong>${org.total_employees || 0}</strong>
                                </div>
                            </div>
                        `).join('');
                        
                        data.data.forEach(org => {
                            const option = document.createElement('option');
                            option.value = org.id;
                            option.textContent = org.name;
                            select.appendChild(option);
                        });
                    } else {
                        list.innerHTML = '<p style="color: #999; text-align: center;">No organizations yet. <a href="/" style="color: #667eea;">Create one now</a>!</p>';
                    }
                })
                .catch(e => console.error('Error loading organizations:', e));
        }

        function loadEmployees() {
            fetch('/api/employees')
                .then(r => {
                    if (!r.ok) return Promise.resolve({data: []});
                    return r.json();
                })
                .then(data => {
                    const list = document.getElementById('empsList');
                    if (data.data && data.data.length > 0) {
                        list.innerHTML = data.data.map(emp => `
                            <div class="list-item">
                                <strong>${emp.full_name}</strong>
                                <div class="email">${emp.email} | ${emp.phone}</div>
                                <div class="email" style="margin-top: 8px;">
                                    ID: <strong>${emp.employee_id}</strong> | 
                                    Status: <strong>${emp.status}</strong> | 
                                    Score: <strong>${emp.assessment_score !== null ? emp.assessment_score : 'N/A'}</strong>
                                </div>
                            </div>
                        `).join('');
                    } else {
                        list.innerHTML = '<p style="color: #999; text-align: center;">No employees yet. Add employees from the form above.</p>';
                    }
                })
                .catch(e => console.error('Error loading employees:', e));
        }
    </script>
        </div>
    </div>
</body>
</html>
"""

ORG_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Organization - Mental Health Monitoring</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        :root {
            --primary: #2563eb;
            --primary-light: #3b82f6;
            --dark: #1e293b;
            --gray: #64748b;
            --gray-light: #f1f5f9;
            --gray-lighter: #f8fafc;
            --border: #e2e8f0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--gray-lighter);
            color: var(--dark);
            display: flex;
            min-height: 100vh;
        }
        /* Sidebar */
        .sidebar {
            width: 280px;
            background: white;
            border-right: 1px solid var(--border);
            padding: 0;
            position: fixed;
            left: 0;
            top: 0;
            bottom: 0;
            overflow-y: auto;
            z-index: 1000;
        }
        .sidebar-brand {
            padding: 24px 20px;
            border-bottom: 1px solid var(--border);
        }
        .sidebar-brand h2 {
            font-size: 1.5em;
            color: var(--primary);
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        .sidebar-brand p {
            font-size: 0.75em;
            color: var(--gray);
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 500;
        }
        .sidebar-nav {
            list-style: none;
            padding: 12px 0;
        }
        .sidebar-nav li {
            margin: 0;
        }
        .sidebar-nav a {
            display: flex;
            align-items: center;
            padding: 12px 20px;
            color: var(--gray);
            text-decoration: none;
            font-size: 0.95em;
            font-weight: 500;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
            gap: 10px;
        }
        .sidebar-nav a:hover {
            background: var(--gray-light);
            color: var(--primary);
            border-left-color: var(--primary);
        }
        .sidebar-nav a.active {
            background: rgba(37, 99, 235, 0.08);
            color: var(--primary);
            border-left-color: var(--primary);
            font-weight: 600;
        }
        .sidebar-nav a span {
            font-size: 1.1em;
        }
        /* Main Content */
        .main-content {
            margin-left: 280px;
            flex: 1;
            padding: 32px;
            background: var(--gray-lighter);
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        .card {
            background: white;
            border-radius: 8px;
            border: 1px solid var(--border);
            padding: 32px;
        }
        .header {
            margin-bottom: 28px;
        }
        .header h1 {
            color: var(--dark);
            font-size: 2em;
            margin-bottom: 8px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        .header p {
            color: var(--gray);
            font-size: 1em;
        }
        .form-group {
            margin-bottom: 18px;
        }
        .form-group label {
            display: block;
            margin-bottom: 6px;
            color: var(--dark);
            font-weight: 500;
            font-size: 0.95em;
        }
        .form-group input {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 0.95em;
            transition: all 0.2s;
            font-family: inherit;
            background: white;
            color: var(--dark);
        }
        .form-group input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.08);
        }
        button {
            background: var(--primary);
            color: white;
            padding: 11px 24px;
            border: none;
            border-radius: 6px;
            font-size: 0.95em;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.2s;
        }
        button:hover {
            background: var(--primary-light);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        }
        button:active {
            transform: translateY(0);
        }
        .message {
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 16px;
            display: none;
            font-size: 0.95em;
            border: 1px solid;
        }
        .message.success {
            background: rgba(16, 185, 129, 0.08);
            color: #047857;
            border-color: rgba(16, 185, 129, 0.3);
            display: block;
        }
        .message.error {
            background: rgba(239, 68, 68, 0.08);
            color: #991b1b;
            border-color: rgba(239, 68, 68, 0.3);
            display: block;
        }
        .login-banner {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 12px;
            padding: 14px 18px;
            margin-bottom: 24px;
            background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%);
            border: 1px solid var(--border);
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(15,23,42,.06);
        }
        .login-banner-lead {
            font-weight: 600;
            color: var(--dark);
            flex-basis: 100%;
            font-size: 0.95rem;
            margin-bottom: 4px;
        }
        .login-banner-btn {
            display: inline-block;
            padding: 10px 18px;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            text-decoration: none;
            transition: 0.15s;
            border: 2px solid transparent;
        }
        .login-banner-btn-primary {
            background: var(--primary);
            color: white !important;
        }
        .login-banner-btn-outline {
            background: white;
            color: var(--primary) !important;
            border-color: var(--primary);
        }
        .login-banner-note {
            flex-basis: 100%;
            font-size: 0.82rem;
            color: var(--gray);
            margin: 6px 0 0 0;
            line-height: 1.45;
        }
        @media (max-width: 768px) {
            .sidebar {
                width: 250px;
            }
            .main-content {
                margin-left: 250px;
                padding: 20px;
            }
            .card {
                padding: 20px;
            }
            .header h1 {
                font-size: 1.5em;
            }
        }
    </style>
</head>
<body class="has-top-strip">
<style>
body.has-top-strip .sidebar { top: 48px !important; height: calc(100vh - 48px) !important; }
body.has-top-strip .main-content { padding-top: 48px !important; }
</style>
    <!--MHM_ADMIN_TOP_BAR-->
    <aside class="sidebar">
        <div class="sidebar-brand">
            <h2>MHM</h2>
            <p>Health Monitor</p>
        </div>
        <!--MHM_ADMIN_SIDE_NAV-->
    </aside>
    <div class="main-content">
        <div class="login-banner" role="navigation" aria-label="Sign in">
            <span class="login-banner-lead">Already registered? Sign in to wellbeing insights</span>
            <a href="/auth/login/org" class="login-banner-btn login-banner-btn-primary">Organization login</a>
            <a href="/auth/login/employee" class="login-banner-btn login-banner-btn-outline">Employee login</a>
            <p class="login-banner-note">Charts and trends: sign in above. First-time setup? Create your organization below (only when no org exists yet).</p>
        </div>
        <div class="container">
            <div class="card">
                <div class="header">
                    <h1>Create Organization</h1>
                    <p>Add a new organization to the system</p>
                </div>

                <div id="orgMessage" class="message"></div>
                
                <form id="orgForm" onsubmit="createOrganization(event)">
                    <div class="form-group">
                        <label for="orgName">Organization Name *</label>
                        <input type="text" id="orgName" required placeholder="e.g., Tech Corp India">
                    </div>
                    <div class="form-group">
                        <label for="orgEmail">Email Address *</label>
                        <input type="email" id="orgEmail" required placeholder="e.g., contact@techcorp.com">
                    </div>
                    <div class="form-group">
                        <label for="orgPhone">Phone Number *</label>
                        <input type="tel" id="orgPhone" required placeholder="e.g., +91-9876543210">
                    </div>
                    <div class="form-group">
                        <label for="orgAddress">Address</label>
                        <input type="text" id="orgAddress" placeholder="e.g., 123 Tech Park, Bangalore">
                    </div>
                    <div class="form-group">
                        <label for="orgIndustry">Industry *</label>
                        <input type="text" id="orgIndustry" required placeholder="e.g., Technology">
                    </div>
                    <div class="form-group">
                        <label for="orgAdminPw">Admin password (for organization insights login)</label>
                        <input type="password" id="orgAdminPw" autocomplete="new-password" placeholder="Choose a secure password">
                    </div>
                    <button type="submit">Create Organization</button>
                </form>
            </div>
        </div>
    </div>

    <script>
        function setActiveNav(path) {
            document.querySelectorAll('.sidebar-nav a').forEach(link => {
                if (link.getAttribute('href') === path) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        }

        window.addEventListener('load', () => {
            setActiveNav('/');
        });

        function createOrganization(event) {
            event.preventDefault();
            
            const name = document.getElementById('orgName').value;
            const email = document.getElementById('orgEmail').value;
            const phone = document.getElementById('orgPhone').value;
            const address = document.getElementById('orgAddress').value;
            const industry = document.getElementById('orgIndustry').value;
            const admin_password = document.getElementById('orgAdminPw').value;

            const msgEl = document.getElementById('orgMessage');
            msgEl.textContent = 'Creating...';
            msgEl.className = 'message';

            const body = {name, email, phone, address, industry};
            if (admin_password) body.admin_password = admin_password;

            fetch('/api/organizations', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body)
            })
            .then(r => r.json())
            .then(data => {
                if (data.data) {
                    msgEl.textContent = '✓ Organization created successfully!';
                    msgEl.className = 'message success';
                    document.getElementById('orgForm').reset();
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1500);
                } else {
                    msgEl.textContent = '✗ Error: ' + (data.error || 'Failed to create');
                    msgEl.className = 'message error';
                }
            })
            .catch(e => {
                msgEl.textContent = '✗ Error: ' + e.message;
                msgEl.className = 'message error';
            });
        }
    </script>
</body>
</html>
"""

VIEW_EMPLOYEES_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Initiate calls — Mental Health Monitoring</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        :root {
            --primary: #2563eb;
            --primary-light: #3b82f6;
            --dark: #1e293b;
            --gray: #64748b;
            --gray-light: #f1f5f9;
            --gray-lighter: #f8fafc;
            --border: #e2e8f0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--gray-lighter);
            color: var(--dark);
            display: flex;
            min-height: 100vh;
        }
        .sidebar {
            width: 280px;
            position: fixed;
            left: 0;
            top: 0;
            height: 100vh;
            background: white;
            border-right: 1px solid var(--border);
            overflow-y: auto;
            padding-top: 0;
            z-index: 1000;
        }
        .sidebar-brand {
            padding: 24px 20px;
            border-bottom: 1px solid var(--border);
        }
        .sidebar-brand h2 {
            color: var(--primary);
            font-size: 1.5em;
            margin-bottom: 4px;
            font-weight: 600;
        }
        .sidebar-brand p {
            color: var(--gray);
            font-size: 0.75em;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 500;
        }
        .sidebar-nav {
            list-style: none;
            padding: 12px 0;
        }
        .sidebar-nav li {
            margin: 0;
        }
        .sidebar-nav a {
            display: flex;
            align-items: center;
            padding: 12px 20px;
            color: var(--gray);
            text-decoration: none;
            transition: all 0.2s;
            border-left: 3px solid transparent;
            gap: 10px;
            font-weight: 500;
        }
        .sidebar-nav a:hover {
            background: var(--gray-light);
            color: var(--primary);
            border-left-color: var(--primary);
        }
        .sidebar-nav a.active {
            background: rgba(37, 99, 235, 0.08);
            color: var(--primary);
            border-left-color: var(--primary);
            font-weight: 600;
        }
        .sidebar-nav span {
            font-size: 1.1em;
        }
        .main-content {
            margin-left: 280px;
            flex: 1;
            padding: 32px;
        }
        .page-header {
            margin-bottom: 28px;
        }
        .page-header h1 {
            color: var(--dark);
            font-size: 2em;
            margin-bottom: 8px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        .page-header p {
            color: var(--gray);
            font-size: 1em;
        }
        .selector-card {
            background: white;
            border-radius: 8px;
            border: 1px solid var(--border);
            padding: 24px;
            margin-bottom: 28px;
        }
        .selector-card h2 {
            color: var(--dark);
            margin-bottom: 16px;
            font-size: 1.2em;
            font-weight: 600;
        }
        .form-group {
            margin-bottom: 0;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: var(--dark);
            font-weight: 500;
            font-size: 0.95em;
        }
        .form-group select {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 0.95em;
            font-family: inherit;
            transition: all 0.2s;
            background: white;
            color: var(--dark);
        }
        .form-group select:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.08);
        }
        .employees-list {
            background: white;
            border-radius: 8px;
            border: 1px solid var(--border);
            padding: 24px;
        }
        .employees-list h2 {
            color: var(--dark);
            margin-bottom: 16px;
            font-size: 1.2em;
            font-weight: 600;
        }
        .employee-card {
            padding: 18px;
            margin: 12px 0;
            background: var(--gray-light);
            border-left: 3px solid var(--primary);
            border-radius: 6px;
            transition: all 0.2s;
        }
        .employee-card:hover {
            background: rgba(37, 99, 235, 0.04);
            transform: translateX(4px);
        }
        .employee-name {
            font-size: 1.1em;
            font-weight: 600;
            color: var(--dark);
            margin-bottom: 12px;
        }
        .employee-detail {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 12px;
            font-size: 0.9em;
        }
        .detail-item {
            color: var(--gray);
        }
        .detail-label {
            font-weight: 600;
            color: var(--dark);
        }
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.85em;
        }
        .status-pending {
            background: rgba(245, 158, 11, 0.1);
            color: #92400e;
        }
        .status-completed {
            background: rgba(16, 185, 129, 0.1);
            color: #065f46;
        }
        .status-in_progress {
            background: rgba(59, 130, 246, 0.1);
            color: #1e40af;
        }
        .empty-message {
            text-align: center;
            color: var(--gray);
            padding: 40px;
            font-size: 1em;
        }
        .action-buttons {
            display: flex;
            gap: 10px;
            margin-top: 12px;
            flex-wrap: wrap;
        }
        .call-button {
            flex: 1;
            min-width: 120px;
            padding: 8px 14px;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.9em;
        }
        .call-button:hover {
            background: var(--primary-light);
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
        }
        .call-button:active {
            transform: translateY(0);
        }
        .call-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .login-banner {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 12px;
            padding: 14px 18px;
            margin-bottom: 24px;
            background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%);
            border: 1px solid var(--border);
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(15,23,42,.06);
        }
        .login-banner-lead {
            font-weight: 600;
            color: var(--dark);
            flex-basis: 100%;
            font-size: 0.95rem;
            margin-bottom: 4px;
        }
        .login-banner-btn {
            display: inline-block;
            padding: 10px 18px;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            text-decoration: none;
            transition: 0.15s;
            border: 2px solid transparent;
        }
        .login-banner-btn-primary {
            background: var(--primary);
            color: white !important;
        }
        .login-banner-btn-outline {
            background: white;
            color: var(--primary) !important;
            border-color: var(--primary);
        }
        .login-banner-note {
            flex-basis: 100%;
            font-size: 0.82rem;
            color: var(--gray);
            margin: 6px 0 0 0;
            line-height: 1.45;
        }
        @media (max-width: 768px) {
            .sidebar {
                width: 250px;
            }
            .main-content {
                margin-left: 250px;
                padding: 20px;
            }
            .employee-detail {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body class="has-top-strip">
<style>
body.has-top-strip .sidebar { top: 48px !important; height: calc(100vh - 48px) !important; }
body.has-top-strip .main-content { padding-top: 48px !important; }
</style>
    <!--MHM_ADMIN_TOP_BAR-->
    <aside class="sidebar">
        <div class="sidebar-brand">
            <h2>MHM</h2>
            <p>Health Monitor</p>
        </div>
        <!--MHM_ADMIN_SIDE_NAV-->
    </aside>
    <div class="main-content">
        <div class="login-banner" role="navigation" aria-label="Sign in">
            <span class="login-banner-lead">Already registered? Sign in to wellbeing insights</span>
            <a href="/auth/login/org" class="login-banner-btn login-banner-btn-primary">Organization login</a>
            <a href="/auth/login/employee" class="login-banner-btn login-banner-btn-outline">Employee login</a>
            <p class="login-banner-note">Insights dashboards open after login at /portal/org or /portal/employee.</p>
        </div>
        <div class="page-header">
            <h1>Initiate calls</h1>
            <p>Select an organization, then start outbound wellbeing calls for employees</p>
        </div>

        <div class="selector-card">
            <h2>Select Organization</h2>
            <div class="form-group">
                <label for="orgSelect">Choose an organization *</label>
                <select id="orgSelect" onchange="loadEmployeesForOrg()">
                    <option value="">-- Select Organization --</option>
                </select>
            </div>
        </div>

        <div class="employees-list" id="employeesContainer">
            <h2>Employees</h2>
            <div class="empty-message">Select an organization to view employees</div>
        </div>
    </div>

    <script>
        function setActiveNav(path) {
            document.querySelectorAll('.sidebar-nav a').forEach(link => {
                if (link.getAttribute('href') === path) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        }

        function escapeAttr(value) {
            return String(value ?? '')
                .replace(/&/g, '&amp;')
                .replace(/"/g, '&quot;')
                .replace(/</g, '&lt;')
                .replace(/'/g, '&#39;');
        }

        // Load organizations on page load
        window.addEventListener('load', () => {
            setActiveNav('/view-employees');
            loadOrganizations();
            document.getElementById('employeesContainer').addEventListener('click', function (e) {
                const btn = e.target.closest('.call-button');
                if (!btn || !this.contains(btn)) return;
                const phone = btn.getAttribute('data-phone');
                const employeeId = parseInt(btn.getAttribute('data-employee-id'), 10);
                initiateCall(e, phone, employeeId);
            });
        });

        function loadOrganizations() {
            fetch('/api/organizations')
                .then(r => r.json())
                .then(data => {
                    const select = document.getElementById('orgSelect');
                    
                    if (data.data && data.data.length > 0) {
                        data.data.forEach(org => {
                            const option = document.createElement('option');
                            option.value = org.id;
                            option.textContent = org.name + ' (' + (org.total_employees || 0) + ' employees)';
                            select.appendChild(option);
                        });
                    }
                })
                .catch(e => console.error('Error loading organizations:', e));
        }

        function initiateCall(ev, phoneNumber, employeeId) {
            const button = ev.target.closest('.call-button');
            if (!button) return;

            if (!phoneNumber) {
                alert('Phone number not available for this employee');
                return;
            }

            // Show loading state
            const originalText = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '⏳ Initiating...';

            // Make API call to webhook
            const webhookUrl = 'https://sanjaysiva1997.app.n8n.cloud/webhook/14fea4b0-c69b-4e2a-aa29-3dcb4f2fd6af';
            const payload = {
                'Phone Number': phoneNumber,
                employee_id: employeeId
            };

            fetch(webhookUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            })
            .then(response => {
                if (response.ok) {
                    button.innerHTML = '✓ Call Initiated';
                    setTimeout(() => {
                        button.disabled = false;
                        button.innerHTML = originalText;
                    }, 2000);
                } else {
                    throw new Error('Call initiation failed with status ' + response.status);
                }
            })
            .catch(error => {
                console.error('Error initiating call:', error);
                alert('Failed to initiate call: ' + error.message);
                button.disabled = false;
                button.innerHTML = originalText;
            });
        }

        function loadEmployeesForOrg() {
            const orgId = document.getElementById('orgSelect').value;
            const container = document.getElementById('employeesContainer');

            if (!orgId) {
                container.innerHTML = '<h2>Employees</h2><div class="empty-message">Select an organization to view employees</div>';
                return;
            }

            // Get organization details
            fetch(`/api/organizations`)
                .then(r => r.json())
                .then(data => {
                    const org = data.data.find(o => o.id == orgId);
                    const orgName = org ? org.name : 'Organization';

                    // Get employees for this organization
                    fetch(`/api/employees/organization/${orgId}`)
                        .then(r => r.json())
                        .then(empData => {
                            if (empData.data && empData.data.length > 0) {
                                const employeesHTML = empData.data.map(emp => `
                                    <div class="employee-card">
                                        <div class="employee-name">${emp.full_name}</div>
                                        <div class="detail-item" style="margin-bottom: 8px;">
                                            <span class="detail-label">Email:</span> ${emp.email}
                                        </div>
                                        <div class="detail-item">
                                            <span class="detail-label">Phone:</span> ${emp.phone}
                                        </div>
                                        <div class="employee-detail">
                                            <div>
                                                <span class="detail-label">Employee ID:</span> ${emp.employee_id}
                                            </div>
                                            <div>
                                                <span class="detail-label">Department:</span> ${emp.department || 'N/A'}
                                            </div>
                                            <div>
                                                <span class="detail-label">Status:</span> 
                                                <span class="status-badge status-${emp.status}">${emp.status}</span>
                                            </div>
                                            <div>
                                                <span class="detail-label">Score:</span> ${emp.assessment_score !== null ? emp.assessment_score : 'N/A'}
                                            </div>
                                        </div>
                                        <div class="action-buttons">
                                            <button type="button" class="call-button" data-phone="${escapeAttr(emp.phone)}" data-employee-id="${escapeAttr(emp.id)}">☎️ Initiate Call</button>
                                        </div>
                                    </div>
                                `).join('');

                                container.innerHTML = `<h2>Employees (${empData.data.length})</h2>${employeesHTML}`;
                            } else {
                                container.innerHTML = `<h2>Employees</h2><div class="empty-message">No employees found in this organization</div>`;
                            }
                        })
                        .catch(e => {
                            console.error('Error loading employees:', e);
                            container.innerHTML = '<h2>Employees</h2><div class="empty-message">Error loading employees</div>';
                        });
                })
                .catch(e => console.error('Error loading organizations:', e));
        }
    </script>
</body>
</html>
"""

EMP_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add Employee - Mental Health Monitoring</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        :root {
            --primary: #2563eb;
            --primary-light: #3b82f6;
            --dark: #1e293b;
            --gray: #64748b;
            --gray-light: #f1f5f9;
            --gray-lighter: #f8fafc;
            --border: #e2e8f0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--gray-lighter);
            color: var(--dark);
            display: flex;
            min-height: 100vh;
        }
        .sidebar {
            width: 280px;
            position: fixed;
            left: 0;
            top: 0;
            height: 100vh;
            background: white;
            border-right: 1px solid var(--border);
            overflow-y: auto;
            padding-top: 0;
            z-index: 1000;
        }
        .sidebar-brand {
            padding: 24px 20px;
            border-bottom: 1px solid var(--border);
        }
        .sidebar-brand h2 {
            color: var(--primary);
            font-size: 1.5em;
            margin-bottom: 4px;
            font-weight: 600;
        }
        .sidebar-brand p {
            color: var(--gray);
            font-size: 0.75em;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 500;
        }
        .sidebar-nav {
            list-style: none;
            padding: 12px 0;
        }
        .sidebar-nav li {
            margin: 0;
        }
        .sidebar-nav a {
            display: flex;
            align-items: center;
            padding: 12px 20px;
            color: var(--gray);
            text-decoration: none;
            transition: all 0.2s;
            border-left: 3px solid transparent;
            gap: 10px;
            font-weight: 500;
        }
        .sidebar-nav a:hover {
            background: var(--gray-light);
            color: var(--primary);
            border-left-color: var(--primary);
        }
        .sidebar-nav a.active {
            background: rgba(37, 99, 235, 0.08);
            color: var(--primary);
            border-left-color: var(--primary);
            font-weight: 600;
        }
        .sidebar-nav span {
            font-size: 1.1em;
        }
        .main-content {
            margin-left: 280px;
            flex: 1;
            padding: 32px;
        }
        .page-container {
            max-width: 700px;
            margin: 0 auto;
        }
        .page-header {
            margin-bottom: 28px;
        }
        .page-header h1 {
            color: var(--dark);
            font-size: 2em;
            margin-bottom: 8px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        .page-header p {
            color: var(--gray);
            font-size: 1em;
        }
        .card {
            background: white;
            border-radius: 8px;
            border: 1px solid var(--border);
            padding: 32px;
        }
        .form-group {
            margin-bottom: 18px;
        }
        .form-group label {
            display: block;
            margin-bottom: 6px;
            color: var(--dark);
            font-weight: 500;
            font-size: 0.95em;
        }
        .form-group input,
        .form-group select {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 0.95em;
            font-family: inherit;
            transition: all 0.2s;
            background: white;
            color: var(--dark);
        }
        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.08);
        }
        button {
            background: var(--primary);
            color: white;
            padding: 11px 24px;
            border: none;
            border-radius: 6px;
            font-size: 0.95em;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: all 0.2s;
        }
        button:hover {
            background: var(--primary-light);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        }
        button:active {
            transform: translateY(0);
        }
        .message {
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 16px;
            display: none;
            font-size: 0.95em;
            border: 1px solid;
        }
        .message.success {
            background: rgba(16, 185, 129, 0.08);
            color: #047857;
            border-color: rgba(16, 185, 129, 0.3);
            display: block;
        }
        .message.error {
            background: rgba(239, 68, 68, 0.08);
            color: #991b1b;
            border-color: rgba(239, 68, 68, 0.3);
            display: block;
        }
        .login-banner {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 12px;
            padding: 14px 18px;
            margin-bottom: 24px;
            background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%);
            border: 1px solid var(--border);
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(15,23,42,.06);
        }
        .login-banner-lead {
            font-weight: 600;
            color: var(--dark);
            flex-basis: 100%;
            font-size: 0.95rem;
            margin-bottom: 4px;
        }
        .login-banner-btn {
            display: inline-block;
            padding: 10px 18px;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            text-decoration: none;
            transition: 0.15s;
            border: 2px solid transparent;
        }
        .login-banner-btn-primary {
            background: var(--primary);
            color: white !important;
        }
        .login-banner-btn-outline {
            background: white;
            color: var(--primary) !important;
            border-color: var(--primary);
        }
        .login-banner-note {
            flex-basis: 100%;
            font-size: 0.82rem;
            color: var(--gray);
            margin: 6px 0 0 0;
            line-height: 1.45;
        }
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }
        .form-grid > .form-group {
            margin-bottom: 0;
        }
        @media (max-width: 768px) {
            .sidebar {
                width: 250px;
            }
            .main-content {
                margin-left: 250px;
                padding: 20px;
            }
            .card {
                padding: 20px;
            }
            .page-header h1 {
                font-size: 1.5em;
            }
            .form-grid {
                grid-template-columns: 1fr;
                gap: 0;
            }
            .form-grid > .form-group {
                margin-bottom: 18px;
            }
        }
    </style>
</head>
<body class="has-top-strip">
<style>
body.has-top-strip .sidebar { top: 48px !important; height: calc(100vh - 48px) !important; }
body.has-top-strip .main-content { padding-top: 48px !important; }
</style>
    <!--MHM_ADMIN_TOP_BAR-->
    <aside class="sidebar">
        <div class="sidebar-brand">
            <h2>MHM</h2>
            <p>Health Monitor</p>
        </div>
        <!--MHM_ADMIN_SIDE_NAV-->
    </aside>
    <div class="main-content">
        <div class="login-banner" role="navigation" aria-label="Sign in">
            <span class="login-banner-lead">Already registered? Sign in to wellbeing insights</span>
            <a href="/auth/login/org" class="login-banner-btn login-banner-btn-primary">Organization login</a>
            <a href="/auth/login/employee" class="login-banner-btn login-banner-btn-outline">Employee login</a>
            <p class="login-banner-note">Insights dashboards open after login at /portal/org or /portal/employee.</p>
        </div>
        <div class="page-container">
            <div class="page-header">
                <h1>Add Employee</h1>
                <p>Register a new employee in the system</p>
            </div>

            <div class="card">
                <div id="empMessage" class="message"></div>
                
                <form id="empForm" onsubmit="addEmployee(event)">
                    <div class="form-group">
                        <label for="orgSelect">Select Organization *</label>
                        <select id="orgSelect" required></select>
                    </div>
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="empFirstName">First Name *</label>
                            <input type="text" id="empFirstName" required placeholder="e.g., Rajesh">
                        </div>
                        <div class="form-group">
                            <label for="empLastName">Last Name *</label>
                            <input type="text" id="empLastName" required placeholder="e.g., Kumar">
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="empEmail">Email Address *</label>
                        <input type="email" id="empEmail" required placeholder="e.g., rajesh@company.com">
                    </div>
                    <div class="form-group">
                        <label for="empPhone">Phone Number *</label>
                        <input type="tel" id="empPhone" required placeholder="e.g., +91-9876543211">
                    </div>
                    <div class="form-group">
                        <label for="empId">Employee ID *</label>
                        <input type="text" id="empId" required placeholder="e.g., EMP001">
                    </div>
                    <div class="form-grid" style="margin-bottom: 18px;">
                        <div class="form-group">
                            <label for="empDept">Department *</label>
                            <input type="text" id="empDept" required placeholder="e.g., Engineering">
                        </div>
                        <div class="form-group">
                            <label for="empDesg">Designation</label>
                            <input type="text" id="empDesg" placeholder="e.g., Senior Developer">
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="empPortalPw">Portal password (for employee insights login)</label>
                        <input type="password" id="empPortalPw" autocomplete="new-password" placeholder="Employee login password">
                    </div>
                    <button type="submit">Add Employee</button>
                </form>
            </div>
        </div>
    </div>

    <script>
        function setActiveNav(path) {
            document.querySelectorAll('.sidebar-nav a').forEach(link => {
                if (link.getAttribute('href') === path) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        }

        // Load organizations on page load
        window.addEventListener('load', () => {
            setActiveNav('/employees');
            loadOrganizations();
        });

        function loadOrganizations() {
            fetch('/api/organizations')
                .then(r => r.json())
                .then(data => {
                    const select = document.getElementById('orgSelect');
                    select.innerHTML = '<option value="">-- Select Organization --</option>';
                    
                    if (data.data && data.data.length > 0) {
                        data.data.forEach(org => {
                            const option = document.createElement('option');
                            option.value = org.id;
                            option.textContent = org.name;
                            select.appendChild(option);
                        });
                    }
                })
                .catch(e => console.error('Error loading organizations:', e));
        }

        function addEmployee(event) {
            event.preventDefault();
            
            const orgId = document.getElementById('orgSelect').value;
            const firstName = document.getElementById('empFirstName').value;
            const lastName = document.getElementById('empLastName').value;
            const email = document.getElementById('empEmail').value;
            const phone = document.getElementById('empPhone').value;
            const empId = document.getElementById('empId').value;
            const dept = document.getElementById('empDept').value;
            const desg = document.getElementById('empDesg').value;
            const portal_password = document.getElementById('empPortalPw').value;

            const msgEl = document.getElementById('empMessage');
            msgEl.textContent = 'Adding...';
            msgEl.className = 'message';

            const empPayload = {
                    organization_id: parseInt(orgId),
                    first_name: firstName,
                    last_name: lastName,
                    email,
                    phone,
                    employee_id: empId,
                    department: dept,
                    designation: desg
            };
            if (portal_password) empPayload.portal_password = portal_password;

            fetch('/api/employees', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(empPayload)
            })
            .then(r => r.json())
            .then(data => {
                if (data.data) {
                    msgEl.textContent = '✓ Employee added successfully!';
                    msgEl.className = 'message success';
                    document.getElementById('empForm').reset();
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1500);
                } else {
                    msgEl.textContent = '✗ Error: ' + (data.error || 'Failed to add');
                    msgEl.className = 'message error';
                }
            })
            .catch(e => {
                msgEl.textContent = '✗ Error: ' + e.message;
                msgEl.className = 'message error';
            });
        }
    </script>
</body>
</html>
"""

@web_routes.route('/', methods=['GET'])
def create_org():
    """Render organization creation page"""
    denied = _require_org_or_super_admin_ui()
    if denied:
        return denied
    return Response(_inject_admin_shell(ORG_PAGE, '/'), mimetype='text/html')

@web_routes.route('/employees', methods=['GET'])
def add_emp():
    """Render employee addition page"""
    denied = _require_org_or_super_admin_ui()
    if denied:
        return denied
    return Response(_inject_admin_shell(EMP_PAGE, '/employees'), mimetype='text/html')

@web_routes.route('/view-employees', methods=['GET'])
def view_emps():
    """Render view employees by organization page"""
    denied = _require_org_or_super_admin_ui()
    if denied:
        return denied
    return Response(_inject_admin_shell(VIEW_EMPLOYEES_PAGE, '/view-employees'), mimetype='text/html')

@web_routes.route('/dashboard', methods=['GET'])
def dashboard():
    """Render dashboard overview page"""
    denied = _require_org_or_super_admin_ui()
    if denied:
        return denied
    return Response(_inject_admin_shell(HTML_TEMPLATE, '/dashboard'), mimetype='text/html')

