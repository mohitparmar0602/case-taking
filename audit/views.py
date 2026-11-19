from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from .models import AuditLog
from accounts.models import User
from accounts.permissions import admin_required


@login_required
@admin_required
def audit_log_list_view(request):
    query = request.GET.get('q', '').strip()
    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('user', '')
    date_filter = request.GET.get('date', '')

    logs_qs = AuditLog.objects.select_related('user').all().order_by('-timestamp')

    if query:
        logs_qs = logs_qs.filter(
            Q(description__icontains=query) |
            Q(record_id__icontains=query) |
            Q(record_type__icontains=query) |
            Q(ip_address__icontains=query)
        )
    if action_filter:
        logs_qs = logs_qs.filter(action=action_filter)
    if user_filter:
        logs_qs = logs_qs.filter(user_id=user_filter)
    if date_filter:
        logs_qs = logs_qs.filter(timestamp__date=date_filter)

    paginator = Paginator(logs_qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    users = User.objects.all().order_by('username')

    return render(request, 'audit/audit_list.html', {
        'page_obj': page_obj,
        'users': users,
        'actions': AuditLog.Action.choices,
        'selected_action': action_filter,
        'selected_user': user_filter,
        'selected_date': date_filter,
        'query': query,
    })
