from django.contrib import admin
from .models import Prescription, PrescriptionItem


class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'patient',
        'doctor',
        'consultation',
        'prescription_date',
        'is_active',
        'created_at',
    )
    list_filter = ('is_active', 'prescription_date', 'doctor')
    search_fields = ('patient__patient_id', 'patient__first_name', 'patient__last_name', 'doctor__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PrescriptionItemInline]
    ordering = ('-prescription_date', '-created_at')


@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ('prescription', 'medicine_name', 'dosage_form', 'strength_dosage', 'frequency', 'duration', 'timing')
    search_fields = ('medicine_name', 'prescription__patient__first_name', 'prescription__patient__last_name')
    list_filter = ('dosage_form', 'timing')
