from django import forms
from .models import MedicalHistory, VitalRecord


class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = MedicalHistory
        fields = [
            # Chief complaints
            'chief_complaint', 'duration', 'onset', 'severity', 'frequency', 'associated_symptoms',
            # HPI
            'hpi_description', 'progression', 'aggravating_factors', 'relieving_factors', 'related_observations',
            # Past medical & surgical
            'previous_illnesses', 'chronic_conditions', 'previous_hospitalizations', 'existing_health_conditions',
            'past_surgeries',
            # Family & Personal
            'family_medical_history', 'smoking_history', 'alcohol_history', 'dietary_habits',
            'sleep_patterns', 'physical_activity',
            # Allergies & Medications
            'known_allergies', 'allergy_type', 'allergy_reaction', 'allergy_severity', 'is_allergy_unknown',
            'current_medications',
        ]
        widgets = {
            'chief_complaint': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. High fever with chills and persistent dry cough'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 4 days'}),
            'onset': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Sudden onset following travel'}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Continuous, peaks in evening'}),
            'associated_symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. Headache, myalgia, loss of appetite'}),
            
            'hpi_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detailed narrative of current condition, evolution over days...'}),
            'progression': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Progressively worsening over 48 hours'}),
            'aggravating_factors': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cold fluids, exertion'}),
            'relieving_factors': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Rest, paracetamol'}),
            'related_observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),

            'previous_illnesses': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. Dengue (2021), Jaundice (childhood)'}),
            'chronic_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. Type-2 Diabetes Mellitus (8 yrs), Essential HTN (5 yrs)'}),
            'previous_hospitalizations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Past hospital admissions, dates and outcomes'}),
            'existing_health_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'past_surgeries': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. Appendectomy (2018 at Apollo Hospital), Hernia repair'}),

            'family_medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. Father: Diabetic & CAD; Mother: Hypertension'}),
            'smoking_history': forms.Select(attrs={'class': 'form-select'}),
            'alcohol_history': forms.Select(attrs={'class': 'form-select'}),
            'dietary_habits': forms.Select(attrs={'class': 'form-select'}),
            'sleep_patterns': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 6-7 hours, disturbed due to cough'}),
            'physical_activity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Sedentary / 30 min morning walk'}),

            'known_allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. Penicillin, Sulfa, NSAIDs, Shellfish'}),
            'allergy_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Drug allergy'}),
            'allergy_reaction': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Urticaria, Bronchospasm'}),
            'allergy_severity': forms.Select(attrs={'class': 'form-select'}),
            'is_allergy_unknown': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            'current_medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. Metformin 500mg BD, Telmisartan 40mg OD'}),
        }


class VitalRecordForm(forms.ModelForm):
    class Meta:
        model = VitalRecord
        fields = [
            'temperature_f', 'systolic_bp', 'diastolic_bp',
            'heart_rate', 'respiratory_rate', 'oxygen_saturation',
            'height_cm', 'weight_kg', 'pain_score', 'observations'
        ]
        widgets = {
            'temperature_f': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '98.6', 'step': '0.1', 'min': '90.0', 'max': '110.0'}),
            'systolic_bp': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '120', 'min': '50', 'max': '300'}),
            'diastolic_bp': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '80', 'min': '30', 'max': '200'}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '72', 'min': '30', 'max': '250'}),
            'respiratory_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '16', 'min': '6', 'max': '60'}),
            'oxygen_saturation': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '98.0', 'step': '0.1', 'min': '50', 'max': '100'}),
            'height_cm': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_height_cm', 'placeholder': '170.0', 'step': '0.5', 'min': '30', 'max': '250'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_weight_kg', 'placeholder': '65.0', 'step': '0.1', 'min': '1', 'max': '300'}),
            'pain_score': forms.NumberInput(attrs={'class': 'form-range', 'id': 'id_pain_score', 'type': 'range', 'min': '0', 'max': '10', 'value': '0'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Intake nurse observations, conscious state, patient distress level...'}),
        }
