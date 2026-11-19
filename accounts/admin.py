from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StaffProfile


class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False
    verbose_name_plural = 'Staff Profile'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (StaffProfileInline,)
    list_display = ('username', 'first_name', 'last_name', 'role', 'email', 'phone', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Healthcare Role & Contact', {
            'fields': ('role', 'phone'),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Healthcare Role & Contact', {
            'fields': ('role', 'phone'),
        }),
    )


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'department', 'specialization', 'qualification', 'is_active_staff')
    search_fields = ('employee_id', 'user__username', 'user__first_name', 'user__last_name', 'department')
    list_filter = ('department', 'is_active_staff')
