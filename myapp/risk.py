from datetime import timedelta

from django.db.models import Avg, Count, Q
from django.urls import reverse
from django.utils import timezone

from .models import Notification, Project, ProjectMilestone, ProjectRiskAssessment, Task, User


DELAY_KEYWORDS = (
    'delay', 'delayed', 'pending', 'lacking', 'unliquidated', 'time frame lapsed',
    'verification', 'reconciliation', 'request for extension', 'extension',
    'awaiting', 'not yet', 'for signature', 'retrieval', 'returned'
)

FLAGGED_RISK_LEVELS = {'at_risk', 'likely_delayed', 'already_delayed'}


def _status_text(value):
    return (value or '').strip().lower()


def _project_is_finished(project):
    status = _status_text(project.status)
    return status in {'completed', 'complete', 'terminated', 'cancelled', 'canceled'}


def _actual_progress(project):
    task_qs = Task.objects.filter(project=project)
    aggregate = task_qs.aggregate(avg=Avg('progress_percentage'), total=Count('id'))
    milestone_aggregate = ProjectMilestone.objects.filter(project=project).aggregate(
        avg=Avg('progress_percentage'),
        total=Count('id'),
    )
    progress_values = []
    if aggregate['total']:
        progress_values.append(float(aggregate['avg'] or 0))
    if milestone_aggregate['total']:
        progress_values.append(float(milestone_aggregate['avg'] or 0))
    if progress_values:
        return int(round(sum(progress_values) / len(progress_values)))
    status = _status_text(project.status)
    if status in {'completed', 'complete'}:
        return 100
    if status in {'ongoing', 'on-going', 'in progress', 'in_progress'}:
        return 40
    return 0


def _expected_progress(project, today):
    if not project.project_start or not project.project_end:
        return 0
    total_days = max((project.project_end - project.project_start).days, 1)
    elapsed_days = max((today - project.project_start).days, 0)
    return int(min(100, round((elapsed_days / total_days) * 100)))


def prediction_evidence(project):
    today = timezone.localdate()
    expected = _expected_progress(project, today)
    actual = _actual_progress(project)
    task_stats = Task.objects.filter(project=project).aggregate(
        total=Count('id'),
        average=Avg('progress_percentage'),
    )
    milestone_stats = ProjectMilestone.objects.filter(project=project).aggregate(
        total=Count('id'),
        average=Avg('progress_percentage'),
    )
    overdue_tasks = Task.objects.filter(project=project, due_date__lt=today).exclude(status='completed').count()
    missing_requirements = _missing_requirements_count(project)
    days_remaining = (project.project_end - today).days if project.project_end else None
    progress_gap = max(expected - actual, 0)
    projected_completion_days = None
    projected_completion_date = None

    if project.project_start and actual > 0:
        elapsed_days = max((today - project.project_start).days, 1)
        projected_completion_days = int(round(elapsed_days / (actual / 100)))
        projected_completion_date = project.project_start + timedelta(days=projected_completion_days)

    return {
        'actual_progress': actual,
        'expected_progress': expected,
        'progress_gap': progress_gap,
        'task_count': task_stats['total'] or 0,
        'task_average': int(round(task_stats['average'] or 0)),
        'milestone_count': milestone_stats['total'] or 0,
        'milestone_average': int(round(milestone_stats['average'] or 0)),
        'overdue_tasks': overdue_tasks,
        'missing_requirements': missing_requirements,
        'days_remaining': days_remaining,
        'projected_completion_days': projected_completion_days,
        'projected_completion_date': projected_completion_date,
    }


def _missing_requirements_count(project):
    return project.requirements.filter(status='missing').count() if hasattr(project, 'requirements') else 0


def assess_project_delay_risk(project, save=True):
    today = timezone.localdate()
    score = 0
    reasons = []
    suggested_extension_days = 0
    days_remaining = None

    if not project.project_end:
        score += 10
        reasons.append('No project end date is encoded, so deadline monitoring is incomplete.')
    else:
        days_remaining = (project.project_end - today).days
        if days_remaining < 0 and not _project_is_finished(project):
            overdue_days = abs(days_remaining)
            score += 30
            reasons.append(f'Project deadline passed {overdue_days} day(s) ago and the project is not completed.')
            suggested_extension_days = max(suggested_extension_days, min(180, overdue_days + 30))
        elif days_remaining <= 30 and not _project_is_finished(project):
            score += 20
            reasons.append(f'Only {days_remaining} day(s) remain before the target end date.')

    expected = _expected_progress(project, today)
    actual = _actual_progress(project)
    if expected and actual + 15 < expected and not _project_is_finished(project):
        gap = expected - actual
        score += 20
        reasons.append(f'Progress appears behind schedule by about {gap}% based on dates and task progress.')
        suggested_extension_days = max(suggested_extension_days, 30)

    overdue_tasks = Task.objects.filter(project=project, due_date__lt=today).exclude(status='completed').count()
    if overdue_tasks:
        score += min(25, overdue_tasks * 8)
        reasons.append(f'{overdue_tasks} task(s) are overdue.')
        suggested_extension_days = max(suggested_extension_days, 30)

    missing_requirements = _missing_requirements_count(project)
    if missing_requirements:
        score += min(15, missing_requirements * 3)
        reasons.append(f'{missing_requirements} project requirement(s) are still marked missing.')

    liquidation = _status_text(project.status_of_liquidation)
    if 'time frame lapsed' in liquidation or ('unliquidated' in liquidation and project.project_end and project.project_end < today):
        score += 15
        reasons.append('Liquidation status indicates unliquidated records beyond the allowed timeframe.')
    elif 'unliquidated' in liquidation:
        score += 10
        reasons.append('Liquidation is still unliquidated and may affect project closure.')

    latest_event = project.chronology.order_by('-event_date', '-date_created').first() if hasattr(project, 'chronology') else None
    if latest_event and latest_event.event_date and (today - latest_event.event_date).days > 45 and not _project_is_finished(project):
        score += 10
        reasons.append('No recent chronology update has been recorded in the last 45 days.')

    searchable_text = ' '.join([
        project.remarks or '',
        project.status or '',
        project.status_of_liquidation or '',
        project.donation_status or '',
    ]).lower()
    if any(keyword in searchable_text for keyword in DELAY_KEYWORDS):
        score += 10
        reasons.append('Remarks/status contain delay-related terms from the office tracking file.')

    score = min(score, 100)
    if score >= 85:
        level = 'already_delayed'
    elif score >= 65:
        level = 'likely_delayed'
    elif score >= 40:
        level = 'at_risk'
    else:
        level = 'on_track'

    if not reasons:
        reasons.append('No major delay indicators found from current dates, tasks, requirements, and remarks.')

    if save:
        defaults = {
            'score': score,
            'level': level,
            'reasons': reasons,
            'suggested_extension_days': suggested_extension_days or 30,
            'days_remaining': days_remaining,
            'expected_progress': expected,
            'actual_progress': actual,
        }
        try:
            assessment = ProjectRiskAssessment.objects.get(project=project)
            changed_fields = []
            for field, value in defaults.items():
                if getattr(assessment, field) != value:
                    setattr(assessment, field, value)
                    changed_fields.append(field)
            if changed_fields:
                assessment.save(update_fields=[*changed_fields, 'last_checked'])
        except ProjectRiskAssessment.DoesNotExist:
            assessment = ProjectRiskAssessment.objects.create(project=project, **defaults)

        project_updates = []
        if project.delay_risk_status != level:
            project.delay_risk_status = level
            project_updates.append('delay_risk_status')
        if project.delay_risk_score != score:
            project.delay_risk_score = score
            project_updates.append('delay_risk_score')
        if project.delay_risk_reasons != reasons:
            project.delay_risk_reasons = reasons
            project_updates.append('delay_risk_reasons')
        if project_updates:
            project.delay_risk_last_checked = timezone.now()
            project_updates.extend(['delay_risk_last_checked', 'date_updated'])
            project.save(update_fields=project_updates)
        return assessment

    return {
        'score': score,
        'level': level,
        'reasons': reasons,
        'suggested_extension_days': suggested_extension_days or 30,
        'days_remaining': days_remaining,
        'expected_progress': expected,
        'actual_progress': actual,
    }


def refresh_delay_risks(notify=True, limit=None):
    projects = Project.objects.all().order_by('project_end', 'id')
    if limit:
        projects = projects[:limit]

    assessments = []
    for project in projects:
        assessment = assess_project_delay_risk(project, save=True)
        assessments.append(assessment)
        if notify and assessment.level in FLAGGED_RISK_LEVELS and not _project_is_finished(project):
            notify_admins_for_delay_risk(assessment)
    return assessments


def notify_admins_for_delay_risk(assessment):
    now = timezone.now()
    if assessment.last_admin_notified_at and now - assessment.last_admin_notified_at < timedelta(hours=24):
        return

    admins = User.objects.filter(Q(role='admin') | Q(role='administrator') | Q(is_superuser=True), status='active').distinct()
    if not admins.exists():
        admins = User.objects.filter(Q(role='admin') | Q(role='administrator') | Q(is_superuser=True)).distinct()

    project = assessment.project
    link = f"{reverse('administrator_forecast_url')}?level=all&notify=0&project={project.pk}#forecast-project-{project.pk}"
    legacy_link = reverse('administrator_projects_detail_url', args=[project.pk])
    level_label = assessment.get_level_display()
    for admin in admins:
        has_open_alert = Notification.objects.filter(
            receiver=admin,
            category='delay_risk',
            link__in=[link, legacy_link],
            status='unread',
        ).exists()
        if has_open_alert:
            continue

        Notification.objects.create(
            sender=None,
            receiver=admin,
            message=f'Delay risk: {project.project_code or project.project_title} is {level_label} ({assessment.score}%).',
            category='delay_risk',
            link=link,
        )
    assessment.last_admin_notified_at = now
    assessment.save(update_fields=['last_admin_notified_at'])
