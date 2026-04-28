from flask import Blueprint, current_app, jsonify, request

from backend.services.assessment_service import AssessmentService

webhook_routes = Blueprint('webhooks', __name__, url_prefix='/api/webhooks')


def _normalize_phone(phone):
    if phone is None:
        return None
    return ''.join(c for c in str(phone) if c.isdigit() or c == '+')


@webhook_routes.route('/call-complete', methods=['POST'])
def call_complete():
    expected = current_app.config.get('WEBHOOK_SECRET')
    secret = request.headers.get('X-Webhook-Secret')
    if not expected or secret != expected:
        return jsonify({'error': 'Unauthorized'}), 401

    payload = request.get_json(silent=True) or {}
    transcript = payload.get('transcript') or payload.get('text') or ''
    employee_id = payload.get('employee_id')
    phone = payload.get('phone') or payload.get('Phone Number')
    duration = payload.get('call_duration_seconds')
    if duration is None:
        duration = payload.get('duration')
    notes = payload.get('notes')

    try:
        duration = int(duration) if duration is not None else None
    except (TypeError, ValueError):
        duration = None

    from backend.models.employee import Employee

    emp = None
    if employee_id is not None:
        try:
            emp = Employee.query.get(int(employee_id))
        except (TypeError, ValueError):
            emp = None
    if emp is None and phone:
        normalized = _normalize_phone(phone)
        candidates = Employee.query.all()
        for e in candidates:
            if _normalize_phone(e.phone) == normalized:
                emp = e
                break

    if emp is None:
        return jsonify({'error': 'employee_id or matching phone required'}), 400
    if not str(transcript).strip():
        return jsonify({'error': 'transcript required'}), 400

    assessment = AssessmentService.create_assessment_from_transcript(
        employee_id=emp.id,
        transcript=str(transcript),
        call_duration_seconds=duration,
        call_notes=str(notes) if notes else None,
    )
    return jsonify({'message': 'Assessment recorded', 'data': assessment.to_dict()}), 201
