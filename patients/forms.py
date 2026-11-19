from django import forms
from .models import Patient


class PatientRegistrationForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_date_of_birth'})
    )

    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'age', 'gender', 'blood_group',
            'phone_number', 'email', 'address', 'city', 'state', 'pin_code',
            'emergency_contact_name', 'emergency_contact_number', 'emergency_relationship',
            'marital_status', 'occupation', 'registration_source'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Rahul'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Sharma'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age in years', 'min': '0', 'max': '130', 'id': 'id_age'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'patient@example.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'House / Street address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'pin_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PIN Code'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name of relative/guardian'}),
            'emergency_contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency phone number'}),
            'emergency_relationship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Father, Spouse'}),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Engineer, Teacher, Retired'}),
            'registration_source': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        first = cleaned_data.get('first_name', '').strip()
        last = cleaned_data.get('last_name', '').strip()
        phone = cleaned_data.get('phone_number', '').strip()

        # Check for potential accidental duplicate if creating new record
        if not self.instance.pk and first and last and phone:
            existing = Patient.objects.filter(
                first_name__iexact=first,
                last_name__iexact=last,
                phone_number=phone
            )
            if existing.exists():
                existing_p = existing.first()
                raise forms.ValidationError(
                    f"Warning: A patient record with identical name ({first} {last}) and phone number ({phone}) already exists (Patient ID: {existing_p.patient_id})."
                )
        return cleaned_data


class PatientSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by Patient ID, Name, or Phone Number...'
        })
    )
    gender = forms.ChoiceField(
        choices=[('', 'All Genders')] + Patient.Gender.choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    blood_group = forms.ChoiceField(
        choices=[('', 'All Blood Groups')] + Patient.BloodGroup.choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
