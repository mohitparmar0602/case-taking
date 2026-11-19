from django import forms
from django.utils import timezone
from .models import Appointment
from accounts.models import User
from patients.models import Patient


class AppointmentBookingForm(forms.ModelForm):
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.filter(is_active=True).order_by('first_name', 'last_name'),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'select_patient'})
    )
    doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Role.DOCTOR, is_active=True).order_by('first_name'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'min': str(timezone.localdate())})
    )
    appointment_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )

    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'appointment_date', 'appointment_time', 'reason', 'status']
        widgets = {
            'reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Routine consultation, Follow-up, Fever & cough'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class AppointmentStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'cancellation_reason']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'cancellation_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for cancellation or rescheduling...'}),
        }
