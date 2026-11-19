from django.contrib import admin
from .models import Consultation, ConsultationAmendment


class ConsultationAmendmentInline(admin.TabularInline):
    model = ConsultationAmendment
    extra = 0
    readonly_fields = ('author', 'created_at')


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = (
        'consultation_id',
        'patient',
        'doctor',
        'is_finalized',
        'finalized_at',
        'created_at',
    )
    list_filter = ('is_finalized', 'created_at', 'doctor')
    search_fields = (
        'consultation_id',
        'patient__patient_id',
        'patient__first_name',
        'patient__last_name',
        'doctor__username',
        'provisional_diagnosis',
        'final_diagnosis',
    )
    readonly_fields = ('consultation_id', 'finalized_at', 'finalized_by', 'created_at', 'updated_at')
    inlines = [ConsultationAmendmentInline]
    ordering = ('-created_at',)


@admin.register(ConsultationAmendment)
class ConsultationAmendmentAdmin(admin.ModelAdmin):
    list_display = ('consultation', 'author', 'created_at')
    search_fields = ('consultation__consultation_id', 'author__username', 'amendment_note')
    readonly_fields = ('created_at',)
