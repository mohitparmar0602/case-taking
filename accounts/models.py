from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Super Admin'
        DOCTOR = 'DOCTOR', 'Doctor'
        RECEPTIONIST = 'RECEPTIONIST', 'Receptionist'
        NURSE = 'NURSE', 'Nurse'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.DOCTOR,
        help_text="Designated role for Role-Based Access Control (RBAC)."
    )
    phone = models.CharField(max_length=20, blank=True, help_text="Direct contact phone number")

    class Meta:
        ordering = ['first_name', 'last_name', 'username']

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_doctor_user(self):
        return self.role == self.Role.DOCTOR

    @property
    def is_receptionist_user(self):
        return self.role == self.Role.RECEPTIONIST

    @property
    def is_nurse_user(self):
        return self.role == self.Role.NURSE

    @property
    def is_clinical_staff(self):
        return self.role in [self.Role.DOCTOR, self.Role.NURSE] or self.is_superuser

    @property
    def full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.username

    @property
    def display_title(self):
        if self.role == self.Role.DOCTOR:
            return f"Dr. {self.full_name}"
        return self.full_name

    def get_dashboard_url(self):
        if self.is_admin_user:
            return 'core:admin_dashboard'
        elif self.role == self.Role.DOCTOR:
            return 'core:doctor_dashboard'
        elif self.role == self.Role.RECEPTIONIST:
            return 'core:receptionist_dashboard'
        elif self.role == self.Role.NURSE:
            return 'core:nurse_dashboard'
        return 'core:dashboard'

    def __str__(self):
        return f"{self.display_title} ({self.get_role_display()})"


class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    employee_id = models.CharField(max_length=30, unique=True, help_text="Institutional Employee/Staff ID")
    specialization = models.CharField(max_length=100, blank=True, help_text="e.g. General Medicine, Pediatrics, Cardiology")
    department = models.CharField(max_length=100, blank=True, default="General OPD")
    qualification = models.CharField(max_length=100, blank=True, help_text="e.g. MBBS, MD, B.Sc. Nursing")
    license_number = models.CharField(max_length=60, blank=True, help_text="Medical registration/licensing council ID")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    biography = models.TextField(blank=True)
    is_active_staff = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__first_name', 'employee_id']

    def __str__(self):
        return f"{self.user.display_title} - {self.employee_id} ({self.department})"
