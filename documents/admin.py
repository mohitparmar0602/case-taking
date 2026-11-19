from django.contrib import admin
from .models import PatientDocument


@admin.register(PatientDocument)
class PatientDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'patient',
        'document_type',
        'file_size_display',
        'uploaded_by',
        'uploaded_at',
    )
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('title', 'patient__patient_id', 'patient__first_name', 'patient__last_name', 'description')
    readonly_fields = ('file_size_bytes', 'file_extension', 'uploaded_at')
    ordering = ('-uploaded_at',)
