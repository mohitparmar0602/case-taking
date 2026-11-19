from django import forms
from .models import Consultation, ConsultationAmendment


class ConsultationForm(forms.ModelForm):
    follow_up_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = Consultation
        fields = [
            'patient', 'appointment', 'status',
            'chief_complaints', 'history_of_present_illness', 'past_history_summary',
            'general_examination', 'systemic_examination', 'local_examination', 'clinical_observations',
            'provisional_diagnosis', 'final_diagnosis', 'treatment_plan',
            'recommended_investigations', 'dietary_lifestyle_advice', 'follow_up_date',
            'doctor_private_notes'
        ]
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'appointment': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'chief_complaints': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Primary presenting clinical complaints, duration, and triggering events...'
            }),
            'history_of_present_illness': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Chronological narrative of onset, symptom progression, severity...'
            }),
            'past_history_summary': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Pertinent past medical, surgical, allergy or medication history noted for this visit...'
            }),
            'general_examination': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Pallor, Icterus, Cyanosis, Clubbing, Lymphadenopathy, Edema (P/I/C/C/L/E)...'
            }),
            'systemic_examination': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'CVS (S1/S2 heard), RS (bilateral clear/wheeze), CNS, Abdomen (soft, non-tender)...'
            }),
            'local_examination': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Specific anatomical site evaluation...'
            }),
            'clinical_observations': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Physician notes on case severity, risk stratification...'
            }),
            'provisional_diagnosis': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Acute Bronchitis / Suspected Type 2 Diabetes'
            }),
            'final_diagnosis': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'e.g. Acute Viral Bronchitis (J20.9), Essential Hypertension (I10)'
            }),
            'treatment_plan': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Clinical management approach, procedures performed, immediate therapeutic actions...'
            }),
            'recommended_investigations': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'e.g. Complete Blood Count (CBC), Chest X-Ray PA view, Fasting Blood Sugar (FBS)...'
            }),
            'dietary_lifestyle_advice': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'e.g. Low sodium diet, brisk walking 30 mins/day, adequate hydration...'
            }),
            'doctor_private_notes': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2,
                'placeholder': 'Confidential clinical notes (internal reference only)...'
            }),
        }


class ConsultationAmendmentForm(forms.ModelForm):
    class Meta:
        model = ConsultationAmendment
        fields = ['amendment_note']
        widgets = {
            'amendment_note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Document post-finalization corrections, laboratory report follow-ups, or clinical observations...'
            }),
        }
