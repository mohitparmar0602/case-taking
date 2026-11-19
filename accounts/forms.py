from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import User, StaffProfile


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your username',
            'autocomplete': 'username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg border-end-0',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        })
    )


class StaffCreationForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'staff@hospital.org'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Set Temporary Password'}),
        min_length=6
    )

    # Profile fields
    employee_id = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. DOC-101, REC-201'})
    )
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cardiology, OPD, Reception'})
    )
    specialization = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. General Medicine, Pediatrics'})
    )
    qualification = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MBBS, MD, B.Sc Nursing'})
    )
    license_number = forms.CharField(
        max_length=60,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MCI-2024-9876'})
    )
    consultation_fee = forms.DecimalField(
        required=False,
        initial=500.00,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '500.00'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unique username'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_employee_id(self):
        emp_id = self.cleaned_data['employee_id'].strip().upper()
        if StaffProfile.objects.filter(employee_id=emp_id).exists():
            raise forms.ValidationError(f"Employee ID '{emp_id}' is already registered to another staff member.")
        return emp_id

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            StaffProfile.objects.create(
                user=user,
                employee_id=self.cleaned_data['employee_id'].strip().upper(),
                department=self.cleaned_data.get('department', ''),
                specialization=self.cleaned_data.get('specialization', ''),
                qualification=self.cleaned_data.get('qualification', ''),
                license_number=self.cleaned_data.get('license_number', ''),
                consultation_fee=self.cleaned_data.get('consultation_fee') or 500.00
            )
        return user


class StaffUpdateForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(choices=User.Role.choices, widget=forms.Select(attrs={'class': 'form-select'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    # Staff Profile fields
    department = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    specialization = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    qualification = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    license_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    consultation_fee = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = StaffProfile
        fields = ['department', 'specialization', 'qualification', 'license_number', 'consultation_fee', 'biography']
        widgets = {
            'biography': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
