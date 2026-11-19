from django.contrib import admin
from .models import VitalRecord, MedicalHistory


@admin.register(VitalRecord)
class VitalRecordAdmin(admin.ModelAdmin):
    list_display = (
        'patient',
        'systolic_bp',
        'diastolic_bp',
        'heart_rate',
        'oxygen_saturation',
        'temperature_f',
        'bmi',
        'recorded_by',
        'measurement_time',
    )
    list_filter = ('measurement_time', 'recorded_by')
    search_fields = ('patient__patient_id', 'patient__first_name', 'patient__last_name', 'recorded_by__username')
    readonly_fields = ('measurement_time', 'bmi')
    ordering = ('-measurement_time',)


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'patient',
        'chief_complaint',
        'duration',
        'severity',
        'smoking_history',
        'alcohol_history',
        'dietary_habits',
        'recorded_by',
        'created_at',
    )
    list_filter = ('severity', 'smoking_history', 'alcohol_history', 'dietary_habits', 'created_at')
    search_fields = ('patient__patient_id', 'patient__first_name', 'patient__last_name', 'chief_complaint', 'known_allergies')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
