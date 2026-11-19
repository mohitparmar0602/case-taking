from django import forms
from django.forms import inlineformset_factory
from .models import Prescription, PrescriptionItem


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['general_advice']
        widgets = {
            'general_advice': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g. Drink plenty of warm water. Avoid oily/spicy foods. Rest for 3 days.'
            }),
        }


class PrescriptionItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionItem
        fields = ['medicine_name', 'dosage_form', 'strength_dosage', 'frequency', 'timing', 'duration', 'instructions']
        widgets = {
            'medicine_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Paracetamol / Amoxicillin'}),
            'dosage_form': forms.Select(attrs={'class': 'form-select'}),
            'strength_dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 500 mg'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1-0-1 (Twice daily)'}),
            'timing': forms.Select(attrs={'class': 'form-select'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 5 days'}),
            'instructions': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. After food'}),
        }


PrescriptionItemFormSet = inlineformset_factory(
    Prescription,
    PrescriptionItem,
    form=PrescriptionItemForm,
    extra=1,
    can_delete=True
)
