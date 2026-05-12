from django import template

register = template.Library()


@register.filter
def user_initials(user_obj):
    if not user_obj:
        return "?"

    first_name = getattr(user_obj, "first_name", None) or ""
    last_name = getattr(user_obj, "last_name", None) or ""

    first_initial = first_name[:1].upper() if first_name else ""
    last_initial = last_name[:1].upper() if last_name else ""

    initials = f"{first_initial}{last_initial}".strip()
    if initials:
        return initials

    username = getattr(user_obj, "username", None) or ""
    if username:
        return username[:1].upper()

    full_name = ""
    if hasattr(user_obj, "get_full_name"):
        try:
            full_name = (user_obj.get_full_name() or "").strip()
        except Exception:
            full_name = ""

    if full_name:
        parts = [part for part in full_name.split() if part]
        if len(parts) >= 2:
            return f"{parts[0][0].upper()}{parts[-1][0].upper()}"
        if len(parts) == 1:
            return parts[0][0].upper()

    return "?"
