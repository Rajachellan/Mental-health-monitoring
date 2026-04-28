import os

from flask import Flask, redirect, request, url_for
from flask_login import LoginManager

from backend.auth.principal import Principal
from backend.database.db import init_db
from backend.models.employee import Employee
from backend.models.organization import Organization
from backend.models.super_admin import SuperAdmin
from backend.routes.auth_routes import auth_routes
from backend.routes.employee_routes import emp_routes
from backend.routes.insights_routes import insights_routes
from backend.routes.organization_routes import org_routes
from backend.routes.portal_routes import portal_routes
from backend.routes.web_routes import web_routes
from backend.routes.webhook_routes import webhook_routes


def create_app(database_url='sqlite:///mental_health.db'):
    """Create and configure Flask application"""

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-change-me-unset')
    app.config['WEBHOOK_SECRET'] = os.environ.get('WEBHOOK_SECRET', 'dev-webhook-secret-change-me')

    init_db(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login_org'

    @login_manager.user_loader
    def load_user(user_id):
        if not user_id or ':' not in str(user_id):
            return None
        role, sep, pk = str(user_id).partition(':')
        if not sep:
            return None
        try:
            pk = int(pk)
        except ValueError:
            return None
        if role == 'org':
            org = Organization.query.get(pk)
            return Principal.from_org(org)
        if role == 'employee':
            emp = Employee.query.get(pk)
            return Principal.from_employee(emp)
        if role == 'super':
            sa = SuperAdmin.query.get(pk)
            return Principal.from_super(sa)
        return None

    @login_manager.unauthorized_handler
    def unauthorized():
        path = request.path or ''
        if path.startswith('/api/insights/super') or path.startswith('/portal/super'):
            return redirect(url_for('auth.login_super', next=request.url))
        if path.startswith('/api/insights/employee') or path.startswith('/portal/employee'):
            return redirect(url_for('auth.login_employee', next=request.url))
        if path.startswith('/api/insights') or path.startswith('/portal'):
            return redirect(url_for('auth.login_org', next=request.url))
        return redirect(url_for('auth.login_org', next=request.url))

    app.register_blueprint(web_routes)
    app.register_blueprint(org_routes)
    app.register_blueprint(emp_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(insights_routes)
    app.register_blueprint(webhook_routes)
    app.register_blueprint(portal_routes)

    @app.after_request
    def _no_cache_html(response):
        ct = response.headers.get('Content-Type') or ''
        if 'text/html' in ct:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
        return response

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy'}, 200

    @app.route('/api/meta', methods=['GET'])
    def api_meta():
        """Diagnostic: confirms this process loaded auth routes and which files are on disk."""
        import backend.routes.auth_routes as ar

        rules = sorted(str(r.rule) for r in app.url_map.iter_rules())
        return {
            'cwd': os.getcwd(),
            'auth_routes_file': getattr(ar, '__file__', None),
            'has_auth_org_login': '/auth/login/org' in rules,
            'route_count': len(rules),
            'sample_routes': [x for x in rules if x.startswith('/auth')][:10],
        }, 200

    return app


# Single shared instance so `flask run`, `gunicorn app:app`, and imports all see auth routes.
app = create_app()


if __name__ == '__main__':
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '5000'))
    ok = any(str(r.rule) == '/auth/login/org' for r in app.url_map.iter_rules())
    print('[startup] cwd:', os.getcwd())
    print('[startup] /auth/login/org registered:', ok)
    if not ok:
        print('[startup] ERROR: auth routes missing — wrong app.py or partial load. Check cwd and restart.')
    print('[startup] Try: http://127.0.0.1:{}/api/meta'.format(port))
    app.run(debug=False, host=host, port=port)
