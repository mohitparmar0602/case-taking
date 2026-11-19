from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        NO_SHOW = 'NO_SHOW', 'No-show'

    appointment_id = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        help_text="Unique Appointment Reference Code"
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'role': 'DOCTOR'}
    )
    appointment_date = models.DateField(db_index=True)
    appointment_time = models.TimeField()
    reason = models.CharField(max_length=255, help_text="Reason / symptoms prompting appointment")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED
    )
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booked_appointments'
    )
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        indexes = [
            models.Index(fields=['appointment_date', 'status']),
            models.Index(fields=['doctor', 'appointment_date']),
        ]

    def clean(self):
        super().clean()
        # Prevent doctor double booking at same date & time (excluding cancelled or self)
        if self.doctor_id and self.appointment_date and self.appointment_time:
            conflicts = Appointment.objects.filter(
                doctor=self.doctor,
                appointment_date=self.appointment_date,
                appointment_time=self.appointment_time
            ).exclude(status=self.Status.CANCELLED)
            if self.pk:
                conflicts = conflicts.exclude(pk=self.pk)
            if conflicts.exists():
                raise ValidationError({
                    'appointment_time': f"Doctor {self.doctor.display_title} already has an active appointment scheduled at {self.appointment_time.strftime('%H:%M')} on {self.appointment_date}."
                })

    def save(self, *args, **kwargs):
        if not self.appointment_id:
            year = timezone.now().strftime('%Y')
            prefix = f"APT-{year}-"
            last_apt = Appointment.objects.filter(appointment_id__startswith=prefix).order_by('-id').first()
            if last_apt:
                try:
                    num = int(last_apt.appointment_id.split('-')[-1]) + 1
                except ValueError:
                    num = Appointment.objects.count() + 1
            else:
                num = 1
            self.appointment_id = f"{prefix}{num:04d}"
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.appointment_id} - {self.patient.get_full_name()} with {self.doctor.display_title} on {self.appointment_date}"
