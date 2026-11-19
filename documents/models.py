import os
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_file_size(value):
    max_size_mb = 10
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"File size exceeds maximum allowed limit of {max_size_mb} MB.")


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    allowed = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.txt']
    if ext not in allowed:
        raise ValidationError(f"Unsupported file format '{ext}'. Allowed: {', '.join(allowed)}")


class PatientDocument(models.Model):
    class DocType(models.TextChoices):
        LAB_REPORT = 'LAB_REPORT', 'Laboratory Test Report'
        RADIOLOGY = 'RADIOLOGY', 'Radiology / X-Ray / CT / MRI'
        PREV_PRESCRIPTION = 'PREV_PRESCRIPTION', 'Previous External Prescription'
        DISCHARGE_SUMMARY = 'DISCHARGE_SUMMARY', 'Hospital Discharge Summary'
        SCANNED_RECORD = 'SCANNED_RECORD', 'Scanned Clinical Record'
        OTHER = 'OTHER', 'Other Medical Document'

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='documents'
    )
    consultation = models.ForeignKey(
        'consultations.Consultation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents'
    )
    document_type = models.CharField(
        max_length=30,
        choices=DocType.choices,
        default=DocType.LAB_REPORT
    )
    title = models.CharField(max_length=200, help_text="Document title / descriptive label")
    file = models.FileField(
        upload_to='patient_documents/%Y/%m/',
        validators=[validate_file_size, validate_file_extension]
    )
    file_size_bytes = models.PositiveIntegerField(default=0)
    file_extension = models.CharField(max_length=10, blank=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size_bytes = self.file.size
            self.file_extension = os.path.splitext(self.file.name)[1].lower().replace('.', '')
        super().save(*args, **kwargs)

    @property
    def file_size_display(self):
        size = self.file_size_bytes
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{round(size / 1024, 1)} KB"
        else:
            return f"{round(size / (1024 * 1024), 2)} MB"

    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()}) for {self.patient.get_full_name()}"
