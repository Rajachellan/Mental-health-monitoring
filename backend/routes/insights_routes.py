from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from backend.services.insights_service import (
    assessment_detail_for_user,
    build_employee_dashboard,
    build_org_dashboard,
)
from backend.services.super_insights_service import build_super_dashboard

insights_routes = Blueprint('insights', __name__, url_prefix='/api/insights')


@insights_routes.route('/super/dashboard', methods=['GET'])
@login_required
def super_dashboard():
    if getattr(current_user, 'role', None) != 'super':
        return jsonify({'error': 'Forbidden'}), 403
    return jsonify({'data': build_super_dashboard()}), 200


@insights_routes.route('/org/dashboard', methods=['GET'])
@login_required
def org_dashboard():
    if getattr(current_user, 'role', None) != 'org':
        return jsonify({'error': 'Forbidden'}), 403
    try:
        data = build_org_dashboard(current_user.record.id)
        return jsonify({'data': data}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@insights_routes.route('/employee/dashboard', methods=['GET'])
@login_required
def employee_dashboard():
    if getattr(current_user, 'role', None) != 'employee':
        return jsonify({'error': 'Forbidden'}), 403
    try:
        data = build_employee_dashboard(current_user.record.id)
        return jsonify({'data': data}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@insights_routes.route('/employee/assessment/<int:assessment_id>', methods=['GET'])
@login_required
def employee_assessment_detail(assessment_id):
    if getattr(current_user, 'role', None) != 'employee':
        return jsonify({'error': 'Forbidden'}), 403
    try:
        detail = assessment_detail_for_user(assessment_id, current_user.record.id)
        return jsonify({'data': detail}), 200
    except ValueError:
        return jsonify({'error': 'Not found'}), 404
