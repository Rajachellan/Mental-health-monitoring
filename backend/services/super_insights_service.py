"""Aggregate metrics across all organizations for super-admin dashboards."""

from collections import defaultdict
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

    # --- Extended analytics (charts / comparisons) ---
    all_assessments = Assessment.query.all()
    pending_calls = sum(
        1
        for a in all_assessments
        if (a.call_status or '') in ('pending', 'in_progress')
    )
    completed_calls = sum(
        1 for a in all_assessments if (a.call_status or '') == 'completed'
    )

    risk_status_counts = defaultdict(int)
    for a in all_assessments:
        key = (a.status or 'unknown').lower()
        risk_status_counts[key] += 1

    # Last ~8 months: assessments recorded vs calls marked completed (by assessment month)
    month_bucket = defaultdict(lambda: {'recorded': 0, 'calls_completed': 0})
    cutoff_m = datetime.utcnow() - timedelta(days=240)
    for a in Assessment.query.filter(Assessment.assessment_date >= cutoff_m).all():
        mk = a.assessment_date.strftime('%Y-%m')
        month_bucket[mk]['recorded'] += 1
        if (a.call_status or '').lower() == 'completed':
            month_bucket[mk]['calls_completed'] += 1
    month_keys = sorted(month_bucket.keys())[-8:]
    monthly_comparison = [
        {
            'month': k,
            'label': k[5:] if len(k) > 5 else k,
            'recorded': month_bucket[k]['recorded'],
            'calls_completed': month_bucket[k]['calls_completed'],
        }
        for k in month_keys
    ]

    # Last 12 weeks (Mon start): volume vs completed
    since_w = datetime.utcnow() - timedelta(weeks=13)
    week_bucket = defaultdict(lambda: {'recorded': 0, 'calls_completed': 0})
    for a in Assessment.query.filter(Assessment.assessment_date >= since_w).all():
        d = a.assessment_date
        if getattr(d, 'tzinfo', None) is not None:
            d = d.replace(tzinfo=None)
        monday = d - timedelta(days=d.weekday())
        wk = monday.date().isoformat()
        week_bucket[wk]['recorded'] += 1
        if (a.call_status or '').lower() == 'completed':
            week_bucket[wk]['calls_completed'] += 1
    week_keys = sorted(week_bucket.keys())[-12:]
    weekly_comparison = [
        {
            'week_start': k,
            'label': k[5:] if len(k) > 7 else k,
            'recorded': week_bucket[k]['recorded'],
            'calls_completed': week_bucket[k]['calls_completed'],
        }
        for k in week_keys
    ]

    # Assessments per weekday (last 90 days)
    since_d = datetime.utcnow() - timedelta(days=90)
    weekday_counts = [0] * 7
    for a in Assessment.query.filter(Assessment.assessment_date >= since_d).all():
        weekday_counts[a.assessment_date.weekday()] += 1
    weekday_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    # Daily series for area chart: avg score + volume (90d)
    daily_map = defaultdict(lambda: {'scores': [], 'n': 0})
    for a in Assessment.query.filter(Assessment.assessment_date >= since).all():
        day = a.assessment_date.strftime('%Y-%m-%d')
        daily_map[day]['scores'].append(a.score)
        daily_map[day]['n'] += 1
    day_keys_sorted = sorted(daily_map.keys())
    daily_area = [
        {
            'date': d,
            'avg_score': round(
                sum(daily_map[d]['scores']) / len(daily_map[d]['scores']), 2
            )
            if daily_map[d]['scores']
            else None,
            'volume': daily_map[d]['n'],
        }
        for d in day_keys_sorted
    ]

    # Radial-style split: supportive vs attention (positive vs rest) on latest-per-employee sentiment
    pos_n = sentiment_buckets.get('positive', 0)
    rest_n = sentiment_buckets.get('neutral', 0) + sentiment_buckets.get('negative', 0)
    sentiment_arc = {'positive': pos_n, 'other': rest_n, 'total_latest': pos_n + rest_n}

    return {
        'overview': {
            'organization_count': len(orgs),
            'total_employees': total_employees,
            'total_assessments': total_assessments,
            'global_avg_score': global_avg_score,
            'avg_sentiment_compound': avg_compound,
            'pending_calls': pending_calls,
            'completed_calls': completed_calls,
            'completion_rate_pct': round(100.0 * completed_calls / total_assessments, 1)
            if total_assessments
            else None,
        },
        'organizations': org_summaries,
        'sentiment_distribution': sentiment_buckets,
        'timeline': timeline,
        'employees_preview': employees_preview,
        'risk_status_distribution': dict(risk_status_counts),
        'monthly_comparison': monthly_comparison,
        'weekly_comparison': weekly_comparison,
        'weekday_volume': {'labels': weekday_labels, 'counts': weekday_counts},
        'daily_area': daily_area,
        'sentiment_arc': sentiment_arc,
    }
