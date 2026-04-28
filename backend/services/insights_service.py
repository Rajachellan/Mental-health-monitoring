"""Aggregated metrics for organization and employee insight dashboards."""

from collections import defaultdict
from datetime import datetime, timedelta

from backend.models.assessment import Assessment
from backend.models.employee import Employee
from backend.models.organization import Organization
from backend.services.organization_service import OrganizationService


def build_org_dashboard(org_id):
    org = Organization.query.get(org_id)
    if not org:
        raise ValueError(f'Organization with ID {org_id} not found')

    stats = OrganizationService.get_organization_stats(org_id)
    employees = Employee.query.filter_by(organization_id=org_id).all()

    dept_scores = defaultdict(list)
    sentiment_buckets = {'positive': 0, 'neutral': 0, 'negative': 0}

    for emp in employees:
        assessments = (
            Assessment.query.filter_by(employee_id=emp.id)
            .order_by(Assessment.assessment_date.desc())
            .all()
        )
        if assessments:
            latest = assessments[0]
            dept = emp.department or 'Unassigned'
            dept_scores[dept].append(latest.score)
            label = latest.sentiment_label or 'neutral'
            if label in sentiment_buckets:
                sentiment_buckets[label] += 1

    dept_avg = []
    for dept, scores in sorted(dept_scores.items()):
        dept_avg.append(
            {'department': dept, 'avg_score': round(sum(scores) / len(scores), 2), 'count': len(scores)}
        )

    since = datetime.utcnow() - timedelta(days=90)
    recent_q = (
        Assessment.query.join(Employee)
        .filter(
            Employee.organization_id == org_id,
            Assessment.assessment_date >= since,
        )
        .order_by(Assessment.assessment_date.asc())
    )
    timeline = []
    for a in recent_q.all():
        timeline.append(
            {
                'date': a.assessment_date.isoformat(),
                'score': a.score,
                'sentiment_compound': a.sentiment_compound,
                'employee_id': a.employee_id,
                'sentiment_label': a.sentiment_label,
            }
        )

    assessments_with_sentiment = (
        Assessment.query.join(Employee)
        .filter(
            Employee.organization_id == org_id,
            Assessment.sentiment_compound.isnot(None),
        )
        .all()
    )
    compounds = [x.sentiment_compound for x in assessments_with_sentiment if x.sentiment_compound is not None]
    avg_compound = round(sum(compounds) / len(compounds), 4) if compounds else None

    return {
        'organization': org.to_dict(),
        'overview': {
            'total_employees': stats['total_employees'],
            'avg_score': stats['average_score'],
            'avg_sentiment_compound': avg_compound,
            'assessment_status': stats['assessment_status'],
        },
        'department_avg_scores': dept_avg,
        'sentiment_distribution': sentiment_buckets,
        'timeline': timeline,
    }


def build_employee_dashboard(employee_id):
    emp = Employee.query.get(employee_id)
    if not emp:
        raise ValueError(f'Employee with ID {employee_id} not found')

    assessments = (
        Assessment.query.filter_by(employee_id=employee_id)
        .order_by(Assessment.assessment_date.asc())
        .all()
    )

    timeline = []
    for a in assessments:
        timeline.append(
            {
                'date': a.assessment_date.isoformat(),
                'score': a.score,
                'status': a.status,
                'sentiment_compound': a.sentiment_compound,
                'sentiment_label': a.sentiment_label,
                'sentiment_pos': a.sentiment_pos,
                'sentiment_neg': a.sentiment_neg,
                'sentiment_neu': a.sentiment_neu,
                'call_duration': a.call_duration,
            }
        )

    latest = assessments[-1] if assessments else None
    latest_breakdown = None
    if latest and latest.sentiment_pos is not None:
        latest_breakdown = {
            'pos': latest.sentiment_pos,
            'neg': latest.sentiment_neg,
            'neu': latest.sentiment_neu,
            'label': latest.sentiment_label,
        }

    assessment_records = []
    for a in reversed(assessments):
        assessment_records.append(
            {
                'id': a.id,
                'assessment_date': a.assessment_date.isoformat(),
                'score': a.score,
                'status': a.status,
                'summary': a.summary,
                'recommendations': a.recommendations,
                'sentiment_label': a.sentiment_label,
                'sentiment_compound': a.sentiment_compound,
                'call_duration': a.call_duration,
                'has_transcript': bool(a.transcript),
            }
        )

    return {
        'employee': emp.to_dict(),
        'overview': {
            'latest_score': emp.assessment_score,
            'last_assessment_date': emp.last_assessment_date.isoformat()
            if emp.last_assessment_date
            else None,
            'assessment_count': len(assessments),
        },
        'timeline': timeline,
        'latest_sentiment_breakdown': latest_breakdown,
        'assessments': assessment_records,
    }


def assessment_detail_for_user(assessment_id, employee_id):
    """Fetch one assessment including transcript for the owning employee."""
    a = Assessment.query.get(assessment_id)
    if not a or a.employee_id != employee_id:
        raise ValueError('Assessment not found')
    return {
        'id': a.id,
        'assessment_date': a.assessment_date.isoformat(),
        'score': a.score,
        'status': a.status,
        'summary': a.summary,
        'recommendations': a.recommendations,
        'transcript': a.transcript,
        'sentiment_compound': a.sentiment_compound,
        'sentiment_label': a.sentiment_label,
        'sentiment_pos': a.sentiment_pos,
        'sentiment_neg': a.sentiment_neg,
        'sentiment_neu': a.sentiment_neu,
        'call_duration': a.call_duration,
        'call_notes': a.call_notes,
    }
