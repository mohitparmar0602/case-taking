from django.contrib import admin
from .models import InstitutionSettings


@admin.register(InstitutionSettings)
class InstitutionSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'email', 'phone', 'city', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # Singleton pattern: Only 1 settings record allowed
        return not InstitutionSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
