from flask import Blueprint, Response, redirect, request, url_for
from flask_login import login_user, logout_user
from html import escape
from werkzeug.security import check_password_hash

from backend.auth.principal import Principal
from backend.models.employee import Employee
from backend.models.organization import Organization
from backend.models.super_admin import SuperAdmin

auth_routes = Blueprint('auth', __name__, url_prefix='/auth')


def _safe_redirect_target(raw, default):
    """Avoid open redirects: only same-site relative paths."""
    if not raw or not isinstance(raw, str):
        return default
    raw = raw.strip()
    if not raw.startswith('/') or raw.startswith('//'):
        return default
    return raw


_LOGIN_STYLES = """
    :root { --primary: #2563eb; --dark: #1e293b; --gray: #64748b; --border: #e2e8f0; --bg: #f8fafc; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: var(--bg); color: var(--dark); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 24px; }
    .card { background: white; border: 1px solid var(--border); border-radius: 12px; padding: 32px; max-width: 420px; width: 100%; box-shadow: 0 4px 24px rgba(15,23,42,.06); }
    h1 { font-size: 1.35rem; margin-bottom: 6px; }
    p.sub { color: var(--gray); font-size: .9rem; margin-bottom: 20px; }
    label { display: block; font-size: .88rem; font-weight: 500; margin-bottom: 6px; }
    input, select { width: 100%; padding: 10px 12px; border: 1px solid var(--border); border-radius: 8px; margin-bottom: 14px; font-size: .95rem; }
    button { width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
    button:hover { filter: brightness(1.05); }
    .err { background: #fef2f2; color: #991b1b; padding: 10px 12px; border-radius: 8px; margin-bottom: 14px; font-size: .9rem; border: 1px solid #fecaca; }
    .links { margin-top: 16px; font-size: .88rem; color: var(--gray); text-align: center; }
    .links a { color: var(--primary); }
"""


@auth_routes.route('/login/org', methods=['GET', 'POST'])
def login_org():
    error = None
    next_after = request.args.get('next') or ''
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip()
        password = request.form.get('password') or ''
        next_after = request.form.get('next') or ''
        org = Organization.query.filter_by(email=email).first()
        if not org or not org.password_hash or not check_password_hash(
            org.password_hash, password
        ):
            error = 'Invalid credentials, or portal not set. Use admin_password when creating the organization.'
        else:
            login_user(Principal.from_org(org), remember=True)
            safe_next = _safe_redirect_target(next_after, '/portal/org')
            return redirect(safe_next)
    html = f"""
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Organization login</title><style>{_LOGIN_STYLES}</style></head>
<body><div class="card">
<h1>Organization insights</h1>
<p class="sub">Sign in with your organization email and admin password.</p>
{"<div class='err'>" + error + "</div>" if error else ""}
<form method="post" action="">
  <input type="hidden" name="next" value="{escape(next_after)}">
  <label>Email</label>
  <input type="email" name="email" required autocomplete="username">
  <label>Password</label>
  <input type="password" name="password" required autocomplete="current-password">
  <button type="submit">Sign in</button>
</form>
<div class="links"><a href="/auth/login/employee">Employee login</a> · <a href="/auth/login/super">Super admin</a> · <a href="/">Home</a></div>
</div></body></html>
"""
    return Response(html, mimetype='text/html')


@auth_routes.route('/login/employee', methods=['GET', 'POST'])
def login_employee():
    error = None
    next_after = request.args.get('next') or ''
    if request.method == 'POST':
        org_id = request.form.get('organization_id')
        email = (request.form.get('email') or '').strip()
        password = request.form.get('password') or ''
        next_after = request.form.get('next') or ''
        try:
            oid = int(org_id)
        except (TypeError, ValueError):
            oid = None
        emp = (
            Employee.query.filter_by(organization_id=oid, email=email).first()
            if oid is not None
            else None
        )
        if (
            not emp
            or not emp.password_hash
            or not check_password_hash(emp.password_hash, password)
        ):
            error = 'Invalid credentials, or portal password not set for this employee.'
        else:
            login_user(Principal.from_employee(emp), remember=True)
            safe_next = _safe_redirect_target(next_after, '/portal/employee')
            return redirect(safe_next)
    html = f"""
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Employee login</title><style>{_LOGIN_STYLES}</style></head>
<body><div class="card">
<h1>Employee insights</h1>
<p class="sub">Use your organization ID, work email, and portal password.</p>
{"<div class='err'>" + error + "</div>" if error else ""}
<form method="post" action="">
  <input type="hidden" name="next" value="{escape(next_after)}">
  <label>Organization ID</label>
  <input type="number" name="organization_id" required min="1" placeholder="e.g. 1">
  <label>Email</label>
  <input type="email" name="email" required autocomplete="username">
  <label>Password</label>
  <input type="password" name="password" required autocomplete="current-password">
  <button type="submit">Sign in</button>
</form>
<div class="links"><a href="/auth/login/org">Organization login</a> · <a href="/auth/login/super">Super admin</a> · <a href="/">Home</a></div>
</div></body></html>
"""
    return Response(html, mimetype='text/html')


@auth_routes.route('/login/super', methods=['GET', 'POST'])
def login_super():
    error = None
    next_after = request.args.get('next') or ''
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip()
        password = request.form.get('password') or ''
        next_after = request.form.get('next') or ''
        user = SuperAdmin.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            error = 'Invalid super admin credentials.'
        else:
            login_user(Principal.from_super(user), remember=True)
            safe_next = _safe_redirect_target(next_after, '/portal/super')
            return redirect(safe_next)
    html = f"""
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Super admin login</title><style>{_LOGIN_STYLES}</style></head>
<body><div class="card">
<h1>Super admin</h1>
<p class="sub">Platform-wide access to all organizations, employees & aggregate analytics.</p>
{"<div class='err'>" + error + "</div>" if error else ""}
<form method="post" action="">
  <input type="hidden" name="next" value="{escape(next_after)}">
  <label>Email</label>
  <input type="email" name="email" required autocomplete="username">
  <label>Password</label>
  <input type="password" name="password" required autocomplete="current-password">
  <button type="submit">Sign in</button>
</form>
<div class="links"><a href="/auth/login/org">Organization login</a> · <a href="/auth/login/employee">Employee login</a> · <a href="/">Home</a></div>
</div></body></html>
"""
    return Response(html, mimetype='text/html')


@auth_routes.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.login_org'))
