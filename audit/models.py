from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    class Action(models.TextChoices):
        LOGIN = 'LOGIN', 'User Login'
        LOGOUT = 'LOGOUT', 'User Logout'
        PATIENT_REGISTER = 'PATIENT_REGISTER', 'Patient Registered'
        PATIENT_UPDATE = 'PATIENT_UPDATE', 'Patient Demographic Updated'
        VITAL_RECORD = 'VITAL_RECORD', 'Vital Signs Intake Recorded'
        HISTORY_RECORD = 'HISTORY_RECORD', 'Medical History Recorded'
        CONSULTATION_START = 'CONSULTATION_START', 'Consultation Started'
        CONSULTATION_UPDATE = 'CONSULTATION_UPDATE', 'Consultation Draft Updated'
        CONSULTATION_FINALIZE = 'CONSULTATION_FINALIZE', 'Consultation Finalized & Locked'
        CONSULTATION_AMEND = 'CONSULTATION_AMEND', 'Consultation Addendum Added'
        PRESCRIPTION_SAVE = 'PRESCRIPTION_SAVE', 'Prescription Authored'
        APPOINTMENT_BOOK = 'APPOINTMENT_BOOK', 'Appointment Booked'
        APPOINTMENT_UPDATE = 'APPOINTMENT_UPDATE', 'Appointment Status Changed'
        DOCUMENT_UPLOAD = 'DOCUMENT_UPLOAD', 'Medical Document Uploaded'
        DOCUMENT_DOWNLOAD = 'DOCUMENT_DOWNLOAD', 'Medical Document Downloaded'
        STAFF_UPDATE = 'STAFF_UPDATE', 'Staff Profile / Account Modified'
        SECURITY_ALERT = 'SECURITY_ALERT', 'Unauthorized Access Attempt'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_entries'
    )
    action = models.CharField(max_length=40, choices=Action.choices, db_index=True)
    record_type = models.CharField(max_length=50, blank=True, help_text="e.g. Patient, Consultation, Appointment")
    record_id = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous/System"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.get_action_display()} by {user_str}"
