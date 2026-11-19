from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class MedicalHistory(models.Model):
    class Severity(models.TextChoices):
        MILD = 'MILD', 'Mild'
        MODERATE = 'MODERATE', 'Moderate'
        SEVERE = 'SEVERE', 'Severe'

    class SmokingStatus(models.TextChoices):
        NEVER = 'NEVER', 'Non-smoker'
        FORMER = 'FORMER', 'Former smoker'
        OCCASIONAL = 'OCCASIONAL', 'Occasional smoker'
        REGULAR = 'REGULAR', 'Regular smoker'

    class AlcoholStatus(models.TextChoices):
        NONE = 'NONE', 'Non-drinker'
        OCCASIONAL = 'OCCASIONAL', 'Occasional drinker'
        MODERATE = 'MODERATE', 'Moderate drinker'
        HEAVY = 'HEAVY', 'Heavy drinker'

    class DietType(models.TextChoices):
        VEGETARIAN = 'VEGETARIAN', 'Vegetarian'
        NON_VEGETARIAN = 'NON_VEGETARIAN', 'Non-Vegetarian'
        VEGAN = 'VEGAN', 'Vegan'
        EGGETARIAN = 'EGGETARIAN', 'Eggetarian'

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='medical_histories'
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_medical_histories'
    )

    # Section A: Chief Complaints
    chief_complaint = models.TextField(help_text="Primary presenting complaint")
    duration = models.CharField(max_length=100, help_text="e.g. 3 days, 2 weeks")
    onset = models.CharField(max_length=100, blank=True, help_text="e.g. Sudden, Gradual, Post-injury")
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MODERATE)
    frequency = models.CharField(max_length=100, blank=True, help_text="e.g. Intermittent, Continuous, Episodic")
    associated_symptoms = models.TextField(blank=True, help_text="e.g. Nausea, headache, dizziness")

    # Section B: History of Present Illness (HPI)
    hpi_description = models.TextField(help_text="Detailed chronological description of the illness")
    progression = models.CharField(max_length=100, blank=True, help_text="e.g. Worsening, Improving, Fluctuating")
    aggravating_factors = models.TextField(blank=True, help_text="Factors that make symptoms worse")
    relieving_factors = models.TextField(blank=True, help_text="Factors that improve symptoms")
    related_observations = models.TextField(blank=True)

    # Section C: Past Medical History
    previous_illnesses = models.TextField(blank=True, help_text="e.g. Jaundice, Tuberculosis, Malaria")
    chronic_conditions = models.TextField(blank=True, help_text="e.g. Hypertension, Type 2 Diabetes, Asthma")
    previous_hospitalizations = models.TextField(blank=True, help_text="Past hospital stays and reasons")
    existing_health_conditions = models.TextField(blank=True)

    # Section D: Past Surgical History
    past_surgeries = models.TextField(blank=True, help_text="Surgical procedures, approx dates, and hospital")

    # Section E: Family History
    family_medical_history = models.TextField(
        blank=True,
        help_text="e.g. Diabetes (Father), Hypertension (Mother), Heart Disease"
    )

    # Section F: Personal & Social History
    smoking_history = models.CharField(max_length=20, choices=SmokingStatus.choices, default=SmokingStatus.NEVER)
    alcohol_history = models.CharField(max_length=20, choices=AlcoholStatus.choices, default=AlcoholStatus.NONE)
    dietary_habits = models.CharField(max_length=30, choices=DietType.choices, default=DietType.VEGETARIAN)
    sleep_patterns = models.CharField(max_length=100, blank=True, help_text="e.g. 7-8 hrs undisturbed, Insomnia")
    physical_activity = models.CharField(max_length=100, blank=True, help_text="e.g. Sedentary, Moderate exercise")

    # Section G: Allergy History
    known_allergies = models.TextField(
        blank=True,
        help_text="e.g. Penicillin, Sulfa drugs, Peanuts, Dust mites"
    )
    allergy_type = models.CharField(max_length=100, blank=True, help_text="e.g. Drug, Food, Environmental")
    allergy_reaction = models.CharField(max_length=200, blank=True, help_text="e.g. Rash, Anaphylaxis, Swelling")
    allergy_severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MILD)
    is_allergy_unknown = models.BooleanField(default=False, help_text="Check if patient reports no known allergies (NKA)")

    # Section H: Medication History
    current_medications = models.TextField(
        blank=True,
        help_text="Name, dosage, frequency of current routine medicines"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Medical histories"

    def __str__(self):
        return f"History for {self.patient.patient_id} ({self.created_at.strftime('%d-%b-%Y')})"


class VitalRecord(models.Model):
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='vitals'
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_vitals'
    )
    measurement_time = models.DateTimeField(default=timezone.now)

    # Vitals
    temperature_f = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Body Temperature in Fahrenheit (°F), e.g. 98.6"
    )
    systolic_bp = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Systolic Blood Pressure (mmHg), e.g. 120"
    )
    diastolic_bp = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Diastolic Blood Pressure (mmHg), e.g. 80"
    )
    heart_rate = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Heart Rate / Pulse (beats per minute), e.g. 72"
    )
    respiratory_rate = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Respiratory Rate (breaths per minute), e.g. 16"
    )
    oxygen_saturation = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="SpO2 percentage (%), e.g. 98.0"
    )
    height_cm = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Height in centimeters (cm), e.g. 172.5"
    )
    weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in kilograms (kg), e.g. 68.5"
    )
    bmi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Body Mass Index auto-calculated: Weight(kg)/(Height(m))^2"
    )
    pain_score = models.PositiveSmallIntegerField(
        default=0,
        help_text="Pain Scale rating from 0 (No pain) to 10 (Worst possible pain)"
    )
    observations = models.TextField(
        blank=True,
        help_text="Nurse/Doctor preliminary clinical intake observations"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-measurement_time']

    def calculate_bmi(self):
        if self.height_cm and self.weight_kg and self.height_cm > 0:
            height_m = Decimal(self.height_cm) / Decimal(100)
            bmi_val = Decimal(self.weight_kg) / (height_m * height_m)
            return round(bmi_val, 2)
        return None

    def save(self, *args, **kwargs):
        calculated = self.calculate_bmi()
        if calculated is not None:
            self.bmi = calculated
        super().save(*args, **kwargs)

    @property
    def blood_pressure_display(self):
        if self.systolic_bp and self.diastolic_bp:
            return f"{self.systolic_bp}/{self.diastolic_bp} mmHg"
        return "Not recorded"

    @property
    def bmi_category(self):
        if not self.bmi:
            return "N/A"
        if self.bmi < Decimal('18.5'):
            return "Underweight"
        elif self.bmi < Decimal('25.0'):
            return "Normal"
        elif self.bmi < Decimal('30.0'):
            return "Overweight"
        else:
            return "Obese"

    def __str__(self):
        return f"Vitals for {self.patient.patient_id} at {self.measurement_time.strftime('%d-%b-%Y %H:%M')}"
