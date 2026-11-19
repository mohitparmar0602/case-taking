from django import forms
from .models import InstitutionSettings


class InstitutionSettingsForm(forms.ModelForm):
    class Meta:
        model = InstitutionSettings
        fields = [
            'name', 'tagline', 'code', 'patient_id_prefix',
            'email', 'phone', 'emergency_helpline',
            'address', 'city', 'state', 'postal_code', 'website',
            'default_follow_up_days', 'enable_audit_trail', 'logo'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'tagline': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'patient_id_prefix': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_helpline': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'default_follow_up_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'enable_audit_trail': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }
