from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


class Consultation(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed / Finalized'
        CANCELLED = 'CANCELLED', 'Cancelled'

    consultation_id = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        help_text="Unique Consultation Reference Code"
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='consultations'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_consultations',
        limit_choices_to={'role': 'DOCTOR'}
    )
    appointment = models.OneToOneField(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultation'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS
    )

    # Clinical Case-Taking Documentation
    chief_complaints = models.TextField(help_text="Patient's primary presenting complaints and onset")
    history_of_present_illness = models.TextField(blank=True, help_text="Detailed chronological illness narrative")
    past_history_summary = models.TextField(blank=True, help_text="Relevant past medical, surgical or chronic history")
    
    # Examination Findings
    general_examination = models.TextField(
        blank=True,
        help_text="General appearance, pallor, icterus, cyanosis, clubbing, lymphadenopathy, edema"
    )
    systemic_examination = models.TextField(
        blank=True,
        help_text="CVS (Heart sounds), RS (Chest sounds), CNS, Abdomen (tenderness/organomegaly)"
    )
    local_examination = models.TextField(blank=True, help_text="Specific anatomical inspection/palpation")
    clinical_observations = models.TextField(blank=True, help_text="Doctor's diagnostic thought process and notes")

    # Diagnosis & Care Plan
    provisional_diagnosis = models.CharField(max_length=255, blank=True, help_text="Initial working clinical diagnosis")
    final_diagnosis = models.TextField(blank=True, help_text="Confirmed final diagnosis & clinical coding")
    treatment_plan = models.TextField(blank=True, help_text="Comprehensive management and therapeutic strategy")
    recommended_investigations = models.TextField(
        blank=True,
        help_text="Laboratory tests, radiology, imaging or pathology workup"
    )
    dietary_lifestyle_advice = models.TextField(blank=True, help_text="Dietary precautions, exercise, lifestyle modifications")
    follow_up_date = models.DateField(null=True, blank=True, help_text="Next suggested clinic visit")
    doctor_private_notes = models.TextField(blank=True, help_text="Confidential administrative or physician notes")

    # Finalization & Integrity Lock
    is_finalized = models.BooleanField(
        default=False,
        help_text="Once finalized, records cannot be overwritten. Only auditable amendments are allowed."
    )
    finalized_at = models.DateTimeField(null=True, blank=True)
    finalized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='finalized_consultations'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['consultation_id']),
            models.Index(fields=['doctor', 'status']),
            models.Index(fields=['patient', 'created_at']),
        ]

    def save(self, *args, **kwargs):
        allow_finalized_edit = kwargs.pop('allow_finalized_edit', False)

        if not self.consultation_id:
            year = timezone.now().strftime('%Y')
            prefix = f"CON-{year}-"
            last_con = Consultation.objects.filter(consultation_id__startswith=prefix).order_by('-id').first()
            if last_con:
                try:
                    num = int(last_con.consultation_id.split('-')[-1]) + 1
                except ValueError:
                    num = Consultation.objects.count() + 1
            else:
                num = 1
            self.consultation_id = f"{prefix}{num:04d}"

        # Prevent unauthorized modification if already finalized
        if self.pk:
            orig = Consultation.objects.get(pk=self.pk)
            if orig.is_finalized and not allow_finalized_edit:
                # If finalizing in this save:
                if not (not orig.is_finalized and self.is_finalized):
                    raise ValidationError("Finalized consultations cannot be silently modified. Use formal clinical amendments.")

        super().save(*args, **kwargs)

    def finalize(self, user):
        """Finalize consultation and lock for modifications."""
        self.is_finalized = True
        self.finalized_at = timezone.now()
        self.finalized_by = user
        self.status = self.Status.COMPLETED
        if self.appointment:
            self.appointment.status = self.appointment.Status.COMPLETED
            self.appointment.save()
        self.save(allow_finalized_edit=True)

    def __str__(self):
        return f"{self.consultation_id} - {self.patient.get_full_name()} with {self.doctor.display_title} ({self.get_status_display()})"


class ConsultationAmendment(models.Model):
    """
    Legally compliant medical amendment log.
    If corrections or follow-up notes are required after consultation finalization,
    they are logged here without tampering with the original record.
    """
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='amendments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='consultation_amendments'
    )
    amendment_note = models.TextField(help_text="Detailed note or addendum to the finalized case record")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Addendum to {self.consultation.consultation_id} by {self.author.display_title} on {self.created_at.strftime('%d-%b-%Y')}"
