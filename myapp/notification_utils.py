from urllib.parse import urlparse

from django.urls import resolve, reverse
from django.urls.exceptions import NoReverseMatch, Resolver404


def normalized_user_role(user):
    return (getattr(user, 'role', '') or '').strip().lower()


def role_key(user_or_role):
    """Return the canonical app role used for role-specific navigation."""
    if isinstance(user_or_role, str):
        role = user_or_role.strip().lower()
        is_superuser = False
    else:
        role = normalized_user_role(user_or_role)
        is_superuser = bool(getattr(user_or_role, 'is_superuser', False))

    if is_superuser or role in {'admin', 'administrator'}:
        return 'administrator'
    if role in {'dost_staff', 'staff'}:
        return 'staff'
    if role == 'beneficiary':
        return 'beneficiary'
    if role == 'proponent':
        return 'proponent'
    return 'proponent'


ROLE_DASHBOARD_URL_NAMES = {
    'administrator': 'administrator_dashboard_url',
    'staff': 'staff_dashboard_url',
    'proponent': 'proponent_dashboard_url',
    'beneficiary': 'beneficiary_dashboard_url',
}


ROLE_SECTION_URL_NAMES = {
    'administrator': {
        'announcements': 'administrator_announcements_url',
        'audit-logs': 'administrator_audit_logs_url',
        'budgets': 'administrator_budgets_url',
        'calendar': 'administrator_calendar_url',
        'communication-hub': 'administrator_communication_hub_url',
        'extension-requests': 'administrator_extension_requests_url',
        'forecast': 'administrator_forecast_url',
        'forms': 'administrator_forms_url',
        'group-chats': 'administrator_group_chats_url',
        'messages': 'administrator_messages_url',
        'projects': 'administrator_projects_url',
        'proposals': 'administrator_proposals_url',
        'reports': 'administrator_reports_url',
        'settings': 'administrator_settings_url',
        'system-health': 'administrator_system_health_url',
        'tasks': 'administrator_task_list_url',
        'users': 'administrator_users_url',
    },
    'staff': {
        'announcements': 'staff_announcements_url',
        'audit-logs': 'staff_audit_logs_url',
        'budgets': 'staff_budgets_url',
        'forms': 'staff_forms_url',
        'group-chats': 'staff_group_chats_url',
        'messages': 'staff_messages_url',
        'personal-tasks': 'staff_personal_tasks_url',
        'projects': 'staff_projects_url',
        'proposals': 'staff_proposals_url',
        'reports': 'staff_reports_url',
        'settings': 'staff_settings_url',
        'tasks': 'staff_task_list_url',
        'users': 'staff_users_url',
    },
    'proponent': {
        'announcements': 'proponent_announcements_url',
        'audit-logs': 'proponent_audit_logs_url',
        'budgets': 'proponent_budgets_url',
        'extension-requests': 'proponent_extension_requests_url',
        'forms': 'proponent_forms_url',
        'group-chats': 'proponent_group_chats_url',
        'messages': 'proponent_messages_url',
        'projects': 'proponent_projects_url',
        'proposals': 'proponent_proposals_url',
        'reports': 'proponent_reports_url',
        'settings': 'proponent_settings_url',
        'tasks': 'proponent_task_list_url',
    },
    'beneficiary': {
        'announcements': 'beneficiary_announcements_url',
        'audit-logs': 'beneficiary_audit_logs_url',
        'forms': 'beneficiary_forms_url',
        'group-chats': 'beneficiary_group_chats_url',
        'messages': 'beneficiary_messages_url',
        'projects': 'beneficiary_projects_url',
        'proposals': 'beneficiary_proposals_url',
        'reports': 'beneficiary_reports_url',
        'settings': 'beneficiary_settings_url',
        'tasks': 'beneficiary_task_list_url',
    },
}


ROLE_CONVERSATION_URL_NAMES = {
    'administrator': 'administrator_conversation_url',
    'staff': 'staff_conversation_url',
    'proponent': 'proponent_conversation_url',
    'beneficiary': 'beneficiary_conversation_url',
}


ROLE_PATH_SEGMENTS = set(ROLE_DASHBOARD_URL_NAMES)


def dashboard_url_for_user(user_or_role):
    role = role_key(user_or_role)
    return reverse(ROLE_DASHBOARD_URL_NAMES.get(role, 'proponent_dashboard_url'))


def notification_url_for_user(user_or_role, section, **kwargs):
    """Build a notification URL that belongs to the receiver's role."""
    role = role_key(user_or_role)
    normalized_section = (section or '').strip('/').replace('_', '-')

    if normalized_section == 'dashboard':
        return dashboard_url_for_user(role)

    if normalized_section == 'conversation':
        url_name = ROLE_CONVERSATION_URL_NAMES.get(role)
        partner_id = kwargs.get('partner_id')
        if url_name and partner_id:
            return reverse(url_name, kwargs={'partner_id': partner_id})

    url_name = ROLE_SECTION_URL_NAMES.get(role, {}).get(normalized_section)
    if url_name:
        return reverse(url_name)

    return dashboard_url_for_user(role)


def _extract_notification_section(path_segments):
    if not path_segments:
        return 'dashboard'

    first = path_segments[0]
    if first in ROLE_PATH_SEGMENTS:
        return path_segments[1] if len(path_segments) > 1 else 'dashboard'

    if first == 'projects':
        return 'projects'

    return first


def normalized_notification_link_for_user(user, link):
    """Prevent stale or cross-role notification links from leaving the user's area."""
    if not link:
        return dashboard_url_for_user(user)

    parsed = urlparse(str(link))
    if parsed.netloc or (parsed.scheme and parsed.scheme not in {'http', 'https'}):
        return dashboard_url_for_user(user)

    path = parsed.path or '/'
    if not path.startswith('/'):
        return dashboard_url_for_user(user)

    segments = [segment for segment in path.strip('/').split('/') if segment]
    user_role = role_key(user)
    link_role = segments[0] if segments and segments[0] in ROLE_PATH_SEGMENTS else None
    section = _extract_notification_section(segments)

    if section == 'messages' and len(segments) >= 3 and segments[-2] == 'conversation':
        try:
            return notification_url_for_user(user, 'conversation', partner_id=int(segments[-1]))
        except (TypeError, ValueError, NoReverseMatch):
            return notification_url_for_user(user, 'messages')

    if link_role and link_role != user_role:
        return notification_url_for_user(user, section)

    if not link_role and user_role != 'administrator' and section in ROLE_SECTION_URL_NAMES['administrator']:
        return notification_url_for_user(user, section)

    try:
        resolve(path)
        return link
    except Resolver404:
        return notification_url_for_user(user, section)
