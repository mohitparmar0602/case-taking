from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'patient_id',
        'first_name',
        'last_name',
        'gender',
        'age',
        'blood_group',
        'phone_number',
        'city',
        'is_active',
        'created_at',
    )
    list_filter = ('gender', 'blood_group', 'is_active', 'registration_source', 'created_at')
    search_fields = ('patient_id', 'first_name', 'last_name', 'phone_number', 'email', 'city')
    readonly_fields = ('patient_id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    fieldsets = (
        ('Identifiers & Status', {
            'fields': ('patient_id', 'is_active', 'registration_source', 'registered_by'),
        }),
        ('Demographics', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'age', 'gender', 'blood_group', 'marital_status'),
        }),
        ('Contact & Address', {
            'fields': ('phone_number', 'email', 'address', 'city', 'state', 'pin_code'),
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_number', 'emergency_relationship'),
        }),
        ('Insurance & System Timestamps', {
            'fields': ('insurance_provider', 'insurance_policy_number', 'created_at', 'updated_at'),
        }),
    )
