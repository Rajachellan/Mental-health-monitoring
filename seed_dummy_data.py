"""
Populate the SQLite DB with demo organizations, employees, and call assessments.

Run from project root:
  python seed_dummy_data.py

Safe to run twice: skips creation if demo org email already exists (still prints credentials).
"""

from datetime import datetime, timedelta
from pathlib import Path

from werkzeug.security import generate_password_hash

from app import create_app
from backend.database.db import db
from backend.models.assessment import Assessment
from backend.models.employee import Employee
from backend.models.organization import Organization
from backend.models.super_admin import SuperAdmin
from backend.services.assessment_service import AssessmentService
from backend.services.employee_service import EmployeeService
from backend.services.organization_service import OrganizationService

DEMO_ORG_EMAIL = 'demo-org@mental-health.demo'
DEMO_ORG_PASSWORD = 'OrgDemo123!'
DEMO_EMP_PASSWORD = 'EmpDemo123!'
DEMO_SUPER_EMAIL = 'superadmin@mental-health.demo'
DEMO_SUPER_PASSWORD = 'SuperAdminDemo123!'


def ensure_super_admin():
    """Create demo super admin if missing (idempotent)."""
    existing = SuperAdmin.query.filter_by(email=DEMO_SUPER_EMAIL).first()
    if existing:
        return existing
    sa = SuperAdmin(
        email=DEMO_SUPER_EMAIL,
        password_hash=generate_password_hash(DEMO_SUPER_PASSWORD),
    )
    db.session.add(sa)
    db.session.commit()
    return sa


CREDENTIALS_TEXT = """\
================================================================================
DUMMY LOGIN CREDENTIALS (demo data)
================================================================================

SUPER ADMIN (platform-wide: /auth/login/super -> /portal/super)
  Email:    {super_email}
  Password: {super_password}

ORGANIZATION ADMIN (insights dashboard: /auth/login/org -> /portal/org)
  Email:    {org_email}
  Password: {org_password}

EMPLOYEE PORTAL (/auth/login/employee -> /portal/employee)
  Use Organization ID shown below with email + password.

{employee_blocks}

Webhook test (same machine, default secret):
  curl -X POST http://127.0.0.1:5000/api/webhooks/call-complete ^
    -H "Content-Type: application/json" ^
    -H "X-Webhook-Secret: dev-webhook-secret-change-me" ^
    -d "{{\\"employee_id\\": <id>, \\"transcript\\": \\"I feel okay today.\\"}}"

================================================================================
"""


def _sync_employee_from_latest(employee_id):
    emp = Employee.query.get(employee_id)
    latest = (
        Assessment.query.filter_by(employee_id=employee_id)
        .order_by(Assessment.assessment_date.desc())
        .first()
    )
    if latest and emp:
        emp.last_assessment_date = latest.assessment_date
        emp.assessment_score = latest.score
        emp.status = 'completed'
        db.session.commit()


def _backdate_assessment(assessment_id, days_ago):
    a = Assessment.query.get(assessment_id)
    if not a:
        return
    dt = datetime.utcnow() - timedelta(days=days_ago)
    a.assessment_date = dt
    a.created_at = dt
    db.session.commit()


def seed():
    application = create_app()
    with application.app_context():
        ensure_super_admin()
        existing = Organization.query.filter_by(email=DEMO_ORG_EMAIL).first()
        if existing:
            org = existing
            employees = Employee.query.filter_by(organization_id=org.id).all()
            lines = []
            for e in employees:
                lines.append(
                    f"  Org ID {org.id} | {e.email} | Password: {DEMO_EMP_PASSWORD}\n"
                    f"           ({e.get_full_name()}, {e.department or 'N/A'})"
                )
            emp_block = '\n\n'.join(lines) if lines else '  (no demo employees found)'
            text = CREDENTIALS_TEXT.format(
                super_email=DEMO_SUPER_EMAIL,
                super_password=DEMO_SUPER_PASSWORD,
                org_email=DEMO_ORG_EMAIL,
                org_password=DEMO_ORG_PASSWORD,
                employee_blocks=emp_block,
            )
            print(text)
            _write_credentials_file(text)
            print('Demo data already present; credentials printed above.')
            return

        org = OrganizationService.create_organization(
            name='Demo Wellness Corp',
            email=DEMO_ORG_EMAIL,
            phone='+91-9876500000',
            address='Demo Tech Park, Bengaluru',
            industry='Technology',
            admin_password=DEMO_ORG_PASSWORD,
        )

        staff = [
            {
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'email': 'priya.sharma@demo.local',
                'phone': '+91-9876510001',
                'employee_id': 'EMP-DEMO-001',
                'department': 'Engineering',
                'designation': 'Lead Developer',
            },
            {
                'first_name': 'Rahul',
                'last_name': 'Verma',
                'email': 'rahul.verma@demo.local',
                'phone': '+91-9876510002',
                'employee_id': 'EMP-DEMO-002',
                'department': 'Human Resources',
                'designation': 'HR Partner',
            },
            {
                'first_name': 'Sneha',
                'last_name': 'Iyer',
                'email': 'sneha.iyer@demo.local',
                'phone': '+91-9876510003',
                'employee_id': 'EMP-DEMO-003',
                'department': 'Sales',
                'designation': 'Account Executive',
            },
        ]

        created_emps = []
        for row in staff:
            emp = EmployeeService.add_employee(
                organization_id=org.id,
                portal_password=DEMO_EMP_PASSWORD,
                **row,
            )
            created_emps.append(emp)

        transcripts_sets = [
            (
                (
                    'I have been feeling exhausted and overwhelmed with deadlines.',
                    'Things are stressful but my manager checked in which helped.',
                    'Workload is still heavy but I am sleeping better and using the EAP.',
                ),
                (88, 42, 9),
            ),
            (
                (
                    'Honestly everything feels pointless lately. I dread Mondays.',
                    'A bit better this week after talking to someone.',
                    'Grateful for the team support; mood is more stable.',
                ),
                (76, 38, 6),
            ),
            (
                (
                    'Quota pressure is intense and I feel anxious before calls.',
                    'Had a rough month but celebrating one win with the team.',
                    'Feeling optimistic about next quarter after training.',
                ),
                (62, 21, 4),
            ),
        ]

        for emp, (lines, days_list) in zip(created_emps, transcripts_sets):
            for transcript, days_ago in zip(lines, days_list):
                a = AssessmentService.create_assessment_from_transcript(
                    employee_id=emp.id,
                    transcript=transcript,
                    call_duration_seconds=180,
                    call_notes='Demo seeded call',
                )
                _backdate_assessment(a.id, days_ago)
            _sync_employee_from_latest(emp.id)

        lines = []
        for e in created_emps:
            lines.append(
                f"  Org ID {org.id} | {e.email} | Password: {DEMO_EMP_PASSWORD}\n"
                f"           ({e.get_full_name()}, {e.department})"
            )
        emp_block = '\n\n'.join(lines)

        text = CREDENTIALS_TEXT.format(
            super_email=DEMO_SUPER_EMAIL,
            super_password=DEMO_SUPER_PASSWORD,
            org_email=DEMO_ORG_EMAIL,
            org_password=DEMO_ORG_PASSWORD,
            employee_blocks=emp_block,
        )
        print(text)
        _write_credentials_file(text)
        print('Demo data seeded successfully.')


def _write_credentials_file(content):
    path = Path(__file__).resolve().parent / 'DUMMY_CREDENTIALS.txt'
    try:
        path.write_text(content.strip() + '\n', encoding='utf-8')
    except OSError:
        pass


if __name__ == '__main__':
    seed()
