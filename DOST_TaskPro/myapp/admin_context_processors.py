from .models import Notification


def notifications_context(request):
    if request.user.is_authenticated:
        # Get all notifications for the user (for the global notification bell)
        # Show recent notifications in the dropdown, but count all unread
        unread_count = Notification.objects.filter(
            receiver=request.user,
            status='unread'
        ).count()

        # Show recent 10 notifications in the dropdown regardless of category
        notifications = Notification.objects.filter(
            receiver=request.user
        ).order_by('-timestamp')[:10]
    else:
        unread_count = 0
        notifications = []

    return {
        'unread_notifications_count': unread_count,
        'notifications_list': notifications
    }


def simple_mode(request):
    """Expose a `simple_mode` boolean to templates.

    Priority: per-user attribute (if present) > cookie value. The project
    currently doesn't have a `simple_mode` field on the custom User model,
    so the cookie fallback is used. When you add a DB-backed flag, the
    per-user value will be honored.
    """
    mode = False
    # Prefer a user-level attribute if available
    if getattr(request, 'user', None) and request.user.is_authenticated:
        mode = bool(getattr(request.user, 'simple_mode', False))

    # Fallback to cookie if not set on user
    if not mode:
        cookie_val = request.COOKIES.get('simple_mode')
        if cookie_val and str(cookie_val).lower() in ('1', 'true', 'yes'):
            mode = True

    return {'simple_mode': mode}
