from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'action', 'user', 'record_type', 'record_id', 'ip_address')
    list_filter = ('action', 'record_type', 'timestamp')
    search_fields = ('user__username', 'record_id', 'description', 'ip_address')
    readonly_fields = ('user', 'action', 'record_type', 'record_id', 'description', 'ip_address', 'user_agent', 'timestamp')
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        return False  # Audit logs cannot be manually forged

    def has_change_permission(self, request, obj=None):
        return False  # Audit logs are immutable

    def has_delete_permission(self, request, obj=None):
        return False  # Audit logs cannot be deleted
