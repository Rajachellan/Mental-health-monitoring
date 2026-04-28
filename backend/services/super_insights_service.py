"""Aggregate metrics across all organizations for super-admin dashboards."""

from datetime import datetime, timedelta

from backend.models.assessment import Assessment
from backend.models.employee import Employee
from backend.models.organization import Organization
from backend.services.organization_service import OrganizationService


def build_super_dashboard():
    """Global KPIs, per-org summaries, sentiment mix, timeline, and employee preview."""
    orgs = Organization.query.order_by(Organization.name).all()

    total_employees = Employee.query.count()
    total_assessments = Assessment.query.count()

    org_summaries = []
    for org in orgs:
        stats = OrganizationService.get_organization_stats(org.id)
        org_summaries.append(
            {
                'organization': org.to_dict(),
                'total_employees': stats['total_employees'],
                'average_score': stats['average_score'],
                'assessment_status': stats['assessment_status'],
            }
        )

    sentiment_buckets = {'positive': 0, 'neutral': 0, 'negative': 0}
    employees = Employee.query.all()
    for emp in employees:
        latest = (
            Assessment.query.filter_by(employee_id=emp.id)
            .order_by(Assessment.assessment_date.desc())
            .first()
        )
        if latest:
            label = latest.sentiment_label or 'neutral'
            if label in sentiment_buckets:
                sentiment_buckets[label] += 1

    since = datetime.utcnow() - timedelta(days=90)
    timeline_q = (
        Assessment.query.filter(Assessment.assessment_date >= since)
        .order_by(Assessment.assessment_date.asc())
    )
    timeline = []
    for a in timeline_q.all():
        emp = Employee.query.get(a.employee_id)
        timeline.append(
            {
                'date': a.assessment_date.isoformat(),
                'score': a.score,
                'sentiment_label': a.sentiment_label,
                'employee_id': a.employee_id,
                'organization_id': emp.organization_id if emp else None,
                'organization_name': (
                    emp.organization.name if emp and emp.organization else None
                ),
            }
        )

    compounds = [
        x.sentiment_compound
        for x in Assessment.query.all()
        if x.sentiment_compound is not None
    ]
    avg_compound = round(sum(compounds) / len(compounds), 4) if compounds else None

    scores = [e.assessment_score for e in employees if e.assessment_score is not None]
    global_avg_score = round(sum(scores) / len(scores), 2) if scores else None

    employees_preview = []
    for emp in Employee.query.order_by(Employee.id).limit(150).all():
        row = emp.to_dict()
        row['organization_name'] = (
            emp.organization.name if emp.organization else None
        )
        employees_preview.append(row)

    return {
        'overview': {
            'organization_count': len(orgs),
            'total_employees': total_employees,
            'total_assessments': total_assessments,
            'global_avg_score': global_avg_score,
            'avg_sentiment_compound': avg_compound,
        },
        'organizations': org_summaries,
        'sentiment_distribution': sentiment_buckets,
        'timeline': timeline,
        'employees_preview': employees_preview,
    }
