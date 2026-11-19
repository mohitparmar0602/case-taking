from .models import AuditLog


def get_client_ip(request):
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_audit_event(request=None, user=None, action=None, record_type="", record_id="", description=""):
    """
    Centralized logging helper to reliably register auditable security and clinical actions.
    """
    try:
        actor = user
        if not actor and request and hasattr(request, 'user') and request.user.is_authenticated:
            actor = request.user

        ip = get_client_ip(request) if request else None
        agent = request.META.get('HTTP_USER_AGENT', '')[:250] if request else ''

        AuditLog.objects.create(
            user=actor,
            action=action,
            record_type=record_type,
            record_id=str(record_id) if record_id else "",
            description=description,
            ip_address=ip,
            user_agent=agent
        )
    except Exception as e:
        # Prevent audit logging failures from crashing transactions, but write warning
        import logging
        logging.getLogger(__name__).error(f"Audit log write failed: {e}")
