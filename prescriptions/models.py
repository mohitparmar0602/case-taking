from django.db import models
from django.conf import settings
from django.utils import timezone


class Prescription(models.Model):
    consultation = models.OneToOneField(
        'consultations.Consultation',
        on_delete=models.CASCADE,
        related_name='prescription'
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_prescriptions',
        limit_choices_to={'role': 'DOCTOR'}
    )
    prescription_date = models.DateField(default=timezone.now)
    general_advice = models.TextField(blank=True, help_text="General instructions, dietary precautions, hydration")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-prescription_date', '-created_at']

    def __str__(self):
        return f"Rx for {self.patient.get_full_name()} by {self.doctor.display_title} on {self.prescription_date}"


class PrescriptionItem(models.Model):
    class DosageForm(models.TextChoices):
        TABLET = 'TABLET', 'Tablet (Tab)'
        CAPSULE = 'CAPSULE', 'Capsule (Cap)'
        SYRUP = 'SYRUP', 'Syrup (Syp)'
        INJECTION = 'INJECTION', 'Injection (Inj)'
        OINTMENT = 'OINTMENT', 'Ointment / Gel'
        DROPS = 'DROPS', 'Drops'
        INHALER = 'INHALER', 'Inhaler'
        OTHER = 'OTHER', 'Other'

    class Timing(models.TextChoices):
        AFTER_MEALS = 'AFTER_MEALS', 'After Meals'
        BEFORE_MEALS = 'BEFORE_MEALS', 'Before Meals'
        WITH_MEALS = 'WITH_MEALS', 'With Food / Meals'
        EMPTY_STOMACH = 'EMPTY_STOMACH', 'Empty Stomach'
        BEDTIME = 'BEDTIME', 'At Bedtime'

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='items'
    )
    medicine_name = models.CharField(max_length=200, help_text="Generic / Brand name of medication")
    dosage_form = models.CharField(max_length=20, choices=DosageForm.choices, default=DosageForm.TABLET)
    strength_dosage = models.CharField(max_length=100, help_text="e.g. 500mg, 10ml, 1 puff")
    frequency = models.CharField(max_length=100, help_text="e.g. 1-0-1 (Twice daily), 1-1-1 (TID), Once daily")
    timing = models.CharField(max_length=30, choices=Timing.choices, default=Timing.AFTER_MEALS)
    duration = models.CharField(max_length=100, help_text="e.g. 5 days, 14 days, 1 month")
    instructions = models.CharField(max_length=255, blank=True, help_text="e.g. Take with warm water, avoid dairy")

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.get_dosage_form_display()} {self.medicine_name} {self.strength_dosage} ({self.frequency})"
