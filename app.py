import os
from flask import Flask
from backend.database.db import init_db
from backend.routes.organization_routes import org_routes
from backend.routes.employee_routes import emp_routes
from backend.routes.web_routes import web_routes

def create_app(database_url='sqlite:///mental_health.db'):
    """Create and configure Flask application"""
    
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(web_routes)
    app.register_blueprint(org_routes)
    app.register_blueprint(emp_routes)
    
    # Base route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=8080)