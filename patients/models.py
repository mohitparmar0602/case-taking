from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import date


class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        OTHER = 'OTHER', 'Other'

    class BloodGroup(models.TextChoices):
        A_POS = 'A+', 'A+'
        A_NEG = 'A-', 'A-'
        B_POS = 'B+', 'B+'
        B_NEG = 'B-', 'B-'
        AB_POS = 'AB+', 'AB+'
        AB_NEG = 'AB-', 'AB-'
        O_POS = 'O+', 'O+'
        O_NEG = 'O-', 'O-'
        UNKNOWN = 'UNKNOWN', 'Unknown'

    class MaritalStatus(models.TextChoices):
        SINGLE = 'SINGLE', 'Single'
        MARRIED = 'MARRIED', 'Married'
        DIVORCED = 'DIVORCED', 'Divorced'
        WIDOWED = 'WIDOWED', 'Widowed'
        OTHER = 'OTHER', 'Other'

    class RegistrationSource(models.TextChoices):
        WALK_IN = 'WALK_IN', 'Walk-in / OPD'
        EMERGENCY = 'EMERGENCY', 'Emergency'
        REFERRAL = 'REFERRAL', 'Referral'
        ONLINE = 'ONLINE', 'Online Portal'

    patient_id = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        help_text="Unique Patient Registration Identifier"
    )
    first_name = models.CharField(max_length=100, db_index=True)
    last_name = models.CharField(max_length=100, db_index=True)
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(help_text="Current calculated or reported age")
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.MALE)
    blood_group = models.CharField(max_length=10, choices=BloodGroup.choices, default=BloodGroup.UNKNOWN)
    
    phone_number = models.CharField(max_length=20, db_index=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100, default="New Delhi")
    state = models.CharField(max_length=100, default="Delhi")
    pin_code = models.CharField(max_length=15, default="110001")

    # Emergency Details
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_number = models.CharField(max_length=20, blank=True)
    emergency_relationship = models.CharField(max_length=50, blank=True, help_text="e.g. Spouse, Parent, Sibling")

    # Additional Details
    marital_status = models.CharField(max_length=20, choices=MaritalStatus.choices, default=MaritalStatus.SINGLE)
    occupation = models.CharField(max_length=100, blank=True)
    registration_source = models.CharField(
        max_length=20,
        choices=RegistrationSource.choices,
        default=RegistrationSource.WALK_IN
    )
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_patients'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient_id']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.patient_id} - {self.get_full_name()} ({self.age}y/{self.get_gender_display()})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def calculate_age_from_dob(self):
        if self.date_of_birth:
            today = date.today()
            born = self.date_of_birth
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return self.age

    def save(self, *args, **kwargs):
        if self.date_of_birth:
            self.age = self.calculate_age_from_dob()
        if not self.patient_id:
            # Generate Unique Patient ID: PAT-YYYY-000001
            year = timezone.now().strftime('%Y')
            prefix = f"PAT-{year}-"
            last_patient = Patient.objects.filter(patient_id__startswith=prefix).order_by('-id').first()
            if last_patient:
                try:
                    last_num = int(last_patient.patient_id.split('-')[-1])
                    new_num = last_num + 1
                except ValueError:
                    new_num = Patient.objects.count() + 1
            else:
                new_num = 1
            self.patient_id = f"{prefix}{new_num:04d}"
        super().save(*args, **kwargs)
