from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

from .models import Patient
from .forms import PatientRegistrationForm, PatientSearchForm
from accounts.permissions import registration_staff_required, patient_directory_required
from audit.services import log_audit_event
from audit.models import AuditLog


@login_required
@patient_directory_required
def patient_list_view(request):
    form = PatientSearchForm(request.GET)
    patients_qs = Patient.objects.filter(is_active=True).order_by('-created_at')

    query = request.GET.get('q', '').strip()
    gender = request.GET.get('gender', '')
    blood_group = request.GET.get('blood_group', '')

    if query:
        patients_qs = patients_qs.filter(
            Q(patient_id__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone_number__icontains=query)
        )
    if gender:
        patients_qs = patients_qs.filter(gender=gender)
    if blood_group:
        patients_qs = patients_qs.filter(blood_group=blood_group)

    paginator = Paginator(patients_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'patients/patient_list.html', {
        'page_obj': page_obj,
        'form': form,
        'total_count': patients_qs.count(),
        'query': query,
        'gender': gender,
        'blood_group': blood_group,
    })


@login_required
@registration_staff_required
def patient_create_view(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.registered_by = request.user
            patient.save()

            log_audit_event(
                request=request,
                user=request.user,
                action=AuditLog.Action.PATIENT_REGISTER,
                record_type="Patient",
                record_id=patient.patient_id,
                description=f"Registered patient {patient.get_full_name()} ({patient.patient_id})."
            )
            messages.success(request, f"Patient {patient.get_full_name()} successfully registered with ID: {patient.patient_id}")
            return redirect('patients:patient_detail', pk=patient.pk)
        else:
            messages.error(request, "Failed to register patient. Please check form inputs.")
    else:
        form = PatientRegistrationForm()

    return render(request, 'patients/patient_form.html', {
        'form': form,
        'is_edit': False,
    })


@login_required
def patient_detail_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    
    # Overview & Related data
    latest_vital = patient.vitals.first()
    latest_history = patient.medical_histories.first()
    recent_consultation = patient.consultations.first()
    upcoming_appointment = patient.appointments.filter(
        appointment_date__gte=timezone.localdate(),
        status__in=['CONFIRMED', 'PENDING']
    ).first()

    # Data for the 9 profile tabs
    medical_histories = patient.medical_histories.all().order_by('-created_at')
    vital_records = patient.vitals.all().order_by('-measurement_time')
    consultations_list = patient.consultations.select_related('doctor', 'appointment').all().order_by('-created_at')
    prescriptions_list = patient.prescriptions.prefetch_related('items').select_related('doctor').all().order_by('-prescription_date')
    appointments_list = patient.appointments.select_related('doctor').all().order_by('-appointment_date', '-appointment_time')
    documents_list = patient.documents.select_related('uploaded_by').all().order_by('-uploaded_at')

    # Activity Timeline compilation
    timeline_events = []
    timeline_events.append({
        'date': patient.created_at,
        'title': 'Patient Registered',
        'type': 'registration',
        'description': f'Registered into system by {patient.registered_by.display_title if patient.registered_by else "Staff"}.',
        'badge': 'bg-primary',
        'icon': 'bi-person-check',
    })

    for v in vital_records[:5]:
        timeline_events.append({
            'date': v.measurement_time,
            'title': f'Vitals Recorded (BP: {v.blood_pressure_display}, HR: {v.heart_rate or "N/A"} bpm)',
            'type': 'vital',
            'description': f'Recorded by {v.recorded_by.display_title if v.recorded_by else "Clinical Staff"}. BMI: {v.bmi or "N/A"}.',
            'badge': 'bg-info',
            'icon': 'bi-activity',
        })

    for c in consultations_list[:5]:
        timeline_events.append({
            'date': c.created_at,
            'title': f'Consultation: {c.consultation_id} ({c.get_status_display()})',
            'type': 'consultation',
            'description': f'Doctor: {c.doctor.display_title}. Diagnosis: {c.provisional_diagnosis or c.final_diagnosis or "Under evaluation"}.',
            'badge': 'bg-success' if c.is_finalized else 'bg-warning',
            'icon': 'bi-clipboard2-pulse',
        })

    for a in appointments_list[:5]:
        timeline_events.append({
            'date': timezone.make_aware(timezone.datetime.combine(a.appointment_date, a.appointment_time)),
            'title': f'Appointment ({a.get_status_display()})',
            'type': 'appointment',
            'description': f'With {a.doctor.display_title}. Reason: {a.reason}.',
            'badge': 'bg-secondary',
            'icon': 'bi-calendar-event',
        })

    # Sort timeline events chronologically descending
    timeline_events.sort(key=lambda x: x['date'], reverse=True)

    return render(request, 'patients/patient_detail.html', {
        'patient': patient,
        'latest_vital': latest_vital,
        'latest_history': latest_history,
        'recent_consultation': recent_consultation,
        'upcoming_appointment': upcoming_appointment,
        'medical_histories': medical_histories,
        'vital_records': vital_records,
        'consultations_list': consultations_list,
        'prescriptions_list': prescriptions_list,
        'appointments_list': appointments_list,
        'documents_list': documents_list,
        'timeline_events': timeline_events,
    })


@login_required
@registration_staff_required
def patient_update_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            log_audit_event(
                request=request,
                user=request.user,
                action=AuditLog.Action.PATIENT_UPDATE,
                record_type="Patient",
                record_id=patient.patient_id,
                description=f"Updated demographics for patient {patient.get_full_name()}."
            )
            messages.success(request, f"Patient {patient.get_full_name()} details updated successfully.")
            return redirect('patients:patient_detail', pk=patient.pk)
        else:
            messages.error(request, "Failed to update patient details. Please check the errors below.")
    else:
        form = PatientRegistrationForm(instance=patient)

    return render(request, 'patients/patient_form.html', {
        'form': form,
        'is_edit': True,
        'patient': patient,
    })


@login_required
def patient_detail_by_pid_view(request, pid):
    """Retrieve patient dossier using unique PID (slug / re_path converter)."""
    patient = get_object_or_404(Patient, patient_id=pid, is_active=True)
    return patient_detail_view(request, pk=patient.pk)


@login_required
def patients_by_blood_group_view(request, group):
    """Filter active patients by specific blood group (str converter)."""
    form = PatientSearchForm(initial={'blood_group': group})
    patients_qs = Patient.objects.filter(is_active=True, blood_group=group).order_by('-created_at')

    paginator = Paginator(patients_qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'patients/patient_list.html', {
        'page_obj': page_obj,
        'form': form,
        'total_count': patients_qs.count(),
        'blood_group': group,
    })


@login_required
def patient_search_api_view(request):
    """
    JSON API endpoint returning matching patient master records.
    INT253 Mandatory Requirement: JsonResponse deriving from real database models.
    """
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({
            'status': 'success',
            'count': 0,
            'results': [],
            'message': 'No query parameter provided.'
        })

    patients = Patient.objects.filter(is_active=True).filter(
        Q(patient_id__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(phone_number__icontains=query)
    )[:15]

    data = [
        {
            'id': p.pk,
            'patient_id': p.patient_id,
            'full_name': p.get_full_name(),
            'first_name': p.first_name,
            'last_name': p.last_name,
            'age': p.age,
            'gender': p.get_gender_display(),
            'blood_group': p.blood_group,
            'phone_number': p.phone_number,
            'city': p.city,
            'state': p.state,
        }
        for p in patients
    ]

    return JsonResponse({
        'status': 'success',
        'count': len(data),
        'results': data,
    })

