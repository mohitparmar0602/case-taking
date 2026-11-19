from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json

from patients.models import Patient
from .forms import MedicalHistoryForm, VitalRecordForm
from accounts.permissions import clinical_staff_required
from audit.services import log_audit_event
from audit.models import AuditLog


@login_required
@clinical_staff_required
def record_vitals_view(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)

    if request.method == 'POST':
        form = VitalRecordForm(request.POST)
        if form.is_valid():
            vital = form.save(commit=False)
            vital.patient = patient
            vital.recorded_by = request.user
            vital.save()

            log_audit_event(
                request=request,
                user=request.user,
                action=AuditLog.Action.VITAL_RECORD,
                record_type="VitalRecord",
                record_id=str(vital.id),
                description=f"Recorded vital signs for {patient.patient_id} (BP: {vital.blood_pressure_display}, HR: {vital.heart_rate or 'N/A'}, BMI: {vital.bmi or 'N/A'})."
            )
            messages.success(request, f"Vital signs recorded successfully for {patient.get_full_name()}!")
            return redirect('patients:patient_detail', pk=patient.pk)
        else:
            messages.error(request, "Please correct errors in the vital signs form.")
    else:
        form = VitalRecordForm()

    return render(request, 'medical_records/record_vitals.html', {
        'patient': patient,
        'form': form,
        'recent_vitals': patient.vitals.all().order_by('-measurement_time')[:5],
    })


@login_required
@clinical_staff_required
def record_medical_history_view(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)

    if request.method == 'POST':
        form = MedicalHistoryForm(request.POST)
        if form.is_valid():
            history = form.save(commit=False)
            history.patient = patient
            history.recorded_by = request.user
            history.save()

            log_audit_event(
                request=request,
                user=request.user,
                action=AuditLog.Action.HISTORY_RECORD,
                record_type="MedicalHistory",
                record_id=str(history.id),
                description=f"Recorded comprehensive medical history for {patient.patient_id} by {request.user.display_title}."
            )
            messages.success(request, f"Medical history saved for {patient.get_full_name()}!")
            return redirect('patients:patient_detail', pk=patient.pk)
        else:
            messages.error(request, "Please check the history form fields.")
    else:
        # Prepopulate with the latest history if exists to speed up clinician workflow
        latest = patient.medical_histories.first()
        if latest:
            initial = {
                'chronic_conditions': latest.chronic_conditions,
                'previous_illnesses': latest.previous_illnesses,
                'past_surgeries': latest.past_surgeries,
                'family_medical_history': latest.family_medical_history,
                'smoking_history': latest.smoking_history,
                'alcohol_history': latest.alcohol_history,
                'dietary_habits': latest.dietary_habits,
                'known_allergies': latest.known_allergies,
                'allergy_type': latest.allergy_type,
                'allergy_reaction': latest.allergy_reaction,
                'allergy_severity': latest.allergy_severity,
                'is_allergy_unknown': latest.is_allergy_unknown,
                'current_medications': latest.current_medications,
            }
            form = MedicalHistoryForm(initial=initial)
        else:
            form = MedicalHistoryForm()

    return render(request, 'medical_records/record_history.html', {
        'patient': patient,
        'form': form,
    })


@login_required
def vitals_trends_view(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    vitals_qs = patient.vitals.all().order_by('measurement_time')

    dates = []
    systolic_list = []
    diastolic_list = []
    hr_list = []
    spo2_list = []

    for v in vitals_qs:
        dates.append(v.measurement_time.strftime('%d-%b %H:%M'))
        systolic_list.append(v.systolic_bp)
        diastolic_list.append(v.diastolic_bp)
        hr_list.append(v.heart_rate)
        spo2_list.append(float(v.oxygen_saturation) if v.oxygen_saturation else None)

    return render(request, 'medical_records/vitals_trends.html', {
        'patient': patient,
        'vitals_qs': vitals_qs.order_by('-measurement_time'),
        'chart_dates': json.dumps(dates),
        'chart_systolic': json.dumps(systolic_list),
        'chart_diastolic': json.dumps(diastolic_list),
        'chart_hr': json.dumps(hr_list),
        'chart_spo2': json.dumps(spo2_list),
    })


@login_required
def vitals_json_api_view(request, patient_id):
    """
    JSON API returning time-series vital telemetry for real-time charting.
    INT253 Mandatory Requirement: Database-derived JsonResponse.
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    vitals_qs = patient.vitals.all().order_by('measurement_time')
    data = [
        {
            'id': v.id,
            'timestamp': v.measurement_time.strftime('%Y-%m-%d %H:%M'),
            'systolic': v.systolic_bp,
            'diastolic': v.diastolic_bp,
            'pulse': v.heart_rate,
            'spo2': float(v.oxygen_saturation) if v.oxygen_saturation else None,
            'temp': float(v.temperature_f) if v.temperature_f else None,
            'bmi': float(v.bmi) if v.bmi else None,
            'bp_display': v.blood_pressure_display,
            'bmi_category': v.bmi_category,
        }
        for v in vitals_qs
    ]
    return JsonResponse({
        'status': 'success',
        'patient_id': patient.patient_id,
        'patient_name': patient.get_full_name(),
        'count': len(data),
        'vitals': data,
    })

