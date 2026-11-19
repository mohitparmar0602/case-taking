from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponse
from django.db.models import Q

from .models import Consultation
from .forms import ConsultationForm, ConsultationAmendmentForm
from .pdf_generator import generate_consultation_pdf
from patients.models import Patient
from appointments.models import Appointment
from prescriptions.models import Prescription
from prescriptions.forms import PrescriptionForm, PrescriptionItemFormSet
from accounts.models import User
from accounts.permissions import doctor_required
from audit.services import log_audit_event
from audit.models import AuditLog


@login_required
def consultation_list_view(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    doctor_filter = request.GET.get('doctor', '')
    date_filter = request.GET.get('date', '')

    cons_qs = Consultation.objects.select_related('patient', 'doctor', 'appointment').all().order_by('-created_at')

    # If logged-in user is Doctor, show option to filter to own consultations or default
    if request.user.role == User.Role.DOCTOR and not request.GET.get('all_doctors'):
        # Keep all accessible, but highlight doctor's own or filter if requested
        pass

    if query:
        cons_qs = cons_qs.filter(
            Q(consultation_id__icontains=query) |
            Q(patient__first_name__icontains=query) |
            Q(patient__last_name__icontains=query) |
            Q(patient__patient_id__icontains=query) |
            Q(provisional_diagnosis__icontains=query) |
            Q(final_diagnosis__icontains=query)
        )
    if status_filter:
        cons_qs = cons_qs.filter(status=status_filter)
    if doctor_filter:
        cons_qs = cons_qs.filter(doctor_id=doctor_filter)
    if date_filter:
        cons_qs = cons_qs.filter(created_at__date=date_filter)

    paginator = Paginator(cons_qs, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    doctors = User.objects.filter(role=User.Role.DOCTOR, is_active=True)

    return render(request, 'consultations/consultation_list.html', {
        'page_obj': page_obj,
        'doctors': doctors,
        'statuses': Consultation.Status.choices,
        'selected_status': status_filter,
        'selected_doctor': doctor_filter,
        'selected_date': date_filter,
        'query': query,
    })


@login_required
@doctor_required
def consultation_create_view(request):
    patient_id = request.GET.get('patient_id')
    appointment_id = request.GET.get('appointment_id')

    patient = None
    appointment = None

    if patient_id:
        patient = get_object_or_404(Patient, pk=patient_id)
    if appointment_id:
        appointment = get_object_or_404(Appointment, pk=appointment_id)
        if not patient:
            patient = appointment.patient

    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        rx_form = PrescriptionForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                consultation = form.save(commit=False)
                # Assign logged-in doctor
                if request.user.role == User.Role.DOCTOR:
                    consultation.doctor = request.user
                elif not consultation.doctor_id:
                    consultation.doctor = request.user

                # Set started timestamp
                consultation.started_at = timezone.now()
                consultation.save()

                # If appointment linked, update its status
                if consultation.appointment:
                    consultation.appointment.status = Appointment.Status.IN_PROGRESS
                    consultation.appointment.save()

                # Check if Prescription was submitted
                if rx_form.is_valid() and (rx_form.cleaned_data.get('general_advice') or request.POST.get('items-0-medicine_name')):
                    rx = rx_form.save(commit=False)
                    rx.consultation = consultation
                    rx.patient = consultation.patient
                    rx.doctor = consultation.doctor
                    rx.save()
                    rx_itemset = PrescriptionItemFormSet(request.POST, instance=rx)
                    if rx_itemset.is_valid():
                        rx_itemset.save()

                # Check if Finalize button was clicked
                if 'finalize_now' in request.POST:
                    consultation.finalize(request.user)
                    action_type = AuditLog.Action.CONSULTATION_FINALIZE
                    action_desc = f"Finalized and locked consultation {consultation.consultation_id}."
                else:
                    action_type = AuditLog.Action.CONSULTATION_START
                    action_desc = f"Created draft consultation {consultation.consultation_id}."

                log_audit_event(
                    request=request,
                    user=request.user,
                    action=action_type,
                    record_type="Consultation",
                    record_id=consultation.consultation_id,
                    description=action_desc
                )

                messages.success(request, f"Consultation {consultation.consultation_id} recorded successfully!")
                return redirect('consultations:consultation_detail', pk=consultation.pk)
        else:
            messages.error(request, "Failed to save consultation. Please correct errors in the tabs.")
    else:
        initial = {}
        if patient:
            initial['patient'] = patient
            # Preload medical history summary into past_history_summary
            latest_hist = patient.medical_histories.first()
            if latest_hist:
                summary_parts = []
                if latest_hist.chronic_conditions:
                    summary_parts.append(f"Chronic: {latest_hist.chronic_conditions}")
                if latest_hist.known_allergies:
                    summary_parts.append(f"Allergies: {latest_hist.known_allergies}")
                if latest_hist.current_medications:
                    summary_parts.append(f"Meds: {latest_hist.current_medications}")
                initial['past_history_summary'] = " | ".join(summary_parts)

        if appointment:
            initial['appointment'] = appointment
            initial['chief_complaints'] = appointment.reason

        form = ConsultationForm(initial=initial)
        rx_form = PrescriptionForm()

    # Get patient's existing vital records & medical history for sidebar reference during consultation
    patient_vitals = patient.vitals.all()[:3] if patient else []
    patient_histories = patient.medical_histories.all()[:2] if patient else []
    patient_prev_consultations = patient.consultations.all()[:3] if patient else []

    # Prepare Prescription Item Formset
    rx_itemset = PrescriptionItemFormSet()

    return render(request, 'consultations/consultation_form.html', {
        'form': form,
        'rx_form': rx_form,
        'rx_itemset': rx_itemset,
        'patient': patient,
        'appointment': appointment,
        'patient_vitals': patient_vitals,
        'patient_histories': patient_histories,
        'patient_prev_consultations': patient_prev_consultations,
        'is_edit': False,
    })


@login_required
def consultation_detail_view(request, pk):
    consultation = get_object_or_404(
        Consultation.objects.select_related('patient', 'doctor', 'appointment', 'finalized_by'),
        pk=pk
    )
    prescription = getattr(consultation, 'prescription', None)
    prescription_items = prescription.items.all() if prescription else []
    amendments = consultation.amendments.select_related('author').all()
    amendment_form = ConsultationAmendmentForm()

    # Vitals recorded for this patient around or before consultation
    latest_vital = consultation.patient.vitals.first()

    return render(request, 'consultations/consultation_detail.html', {
        'consultation': consultation,
        'prescription': prescription,
        'prescription_items': prescription_items,
        'amendments': amendments,
        'amendment_form': amendment_form,
        'latest_vital': latest_vital,
    })


@login_required
@doctor_required
def consultation_edit_view(request, pk):
    consultation = get_object_or_404(Consultation, pk=pk)

    if consultation.is_finalized:
        messages.error(request, "This consultation has been finalized and locked. You can only record auditable amendments.")
        return redirect('consultations:consultation_detail', pk=consultation.pk)

    prescription, _ = Prescription.objects.get_or_create(
        consultation=consultation,
        defaults={'patient': consultation.patient, 'doctor': consultation.doctor}
    )

    if request.method == 'POST':
        form = ConsultationForm(request.POST, instance=consultation)
        rx_form = PrescriptionForm(request.POST, instance=prescription)
        rx_itemset = PrescriptionItemFormSet(request.POST, instance=prescription)

        if form.is_valid() and rx_form.is_valid() and rx_itemset.is_valid():
            with transaction.atomic():
                con = form.save()
                rx_form.save()
                rx_itemset.save()

                if 'finalize_now' in request.POST:
                    con.finalize(request.user)
                    log_audit_event(
                        request=request,
                        user=request.user,
                        action=AuditLog.Action.CONSULTATION_FINALIZE,
                        record_type="Consultation",
                        record_id=con.consultation_id,
                        description=f"Consultation {con.consultation_id} finalized and locked."
                    )
                    messages.success(request, f"Consultation {con.consultation_id} successfully finalized!")
                else:
                    log_audit_event(
                        request=request,
                        user=request.user,
                        action=AuditLog.Action.CONSULTATION_UPDATE,
                        record_type="Consultation",
                        record_id=con.consultation_id,
                        description=f"Consultation draft {con.consultation_id} updated."
                    )
                    messages.success(request, f"Consultation {con.consultation_id} draft saved.")

            return redirect('consultations:consultation_detail', pk=con.pk)
        else:
            messages.error(request, "Please check for errors in the consultation form.")
    else:
        form = ConsultationForm(instance=consultation)
        rx_form = PrescriptionForm(instance=prescription)
        rx_itemset = PrescriptionItemFormSet(instance=prescription)

    patient = consultation.patient
    patient_vitals = patient.vitals.all()[:3]
    patient_histories = patient.medical_histories.all()[:2]
    patient_prev_consultations = patient.consultations.exclude(pk=consultation.pk)[:3]

    return render(request, 'consultations/consultation_form.html', {
        'form': form,
        'rx_form': rx_form,
        'rx_itemset': rx_itemset,
        'patient': patient,
        'consultation': consultation,
        'patient_vitals': patient_vitals,
        'patient_histories': patient_histories,
        'patient_prev_consultations': patient_prev_consultations,
        'is_edit': True,
    })


@login_required
@doctor_required
def consultation_finalize_view(request, pk):
    consultation = get_object_or_404(Consultation, pk=pk)
    if consultation.is_finalized:
        messages.info(request, "This consultation is already finalized.")
        return redirect('consultations:consultation_detail', pk=consultation.pk)

    consultation.finalize(request.user)
    log_audit_event(
        request=request,
        user=request.user,
        action=AuditLog.Action.CONSULTATION_FINALIZE,
        record_type="Consultation",
        record_id=consultation.consultation_id,
        description=f"Physician {request.user.display_title} finalized consultation {consultation.consultation_id}."
    )
    messages.success(request, f"Consultation {consultation.consultation_id} has been officially finalized and signed.")
    return redirect('consultations:consultation_detail', pk=consultation.pk)


@login_required
@doctor_required
def consultation_amend_view(request, pk):
    consultation = get_object_or_404(Consultation, pk=pk)

    if request.method == 'POST':
        form = ConsultationAmendmentForm(request.POST)
        if form.is_valid():
            amendment = form.save(commit=False)
            amendment.consultation = consultation
            amendment.author = request.user
            amendment.save()

            log_audit_event(
                request=request,
                user=request.user,
                action=AuditLog.Action.CONSULTATION_AMEND,
                record_type="ConsultationAmendment",
                record_id=str(amendment.id),
                description=f"Added addendum to finalized consultation {consultation.consultation_id}."
            )
            messages.success(request, "Amendment addendum successfully recorded.")
        else:
            messages.error(request, "Failed to record amendment. Note text is required.")

    return redirect('consultations:consultation_detail', pk=consultation.pk)


@login_required
def consultation_pdf_view(request, pk):
    consultation = get_object_or_404(Consultation, pk=pk)
    pdf_buffer = generate_consultation_pdf(consultation)

    log_audit_event(
        request=request,
        user=request.user,
        action=AuditLog.Action.DOCUMENT_DOWNLOAD,
        record_type="ConsultationReportPDF",
        record_id=consultation.consultation_id,
        description=f"Downloaded consultation PDF summary for {consultation.consultation_id}."
    )

    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    filename = f"Consultation_{consultation.consultation_id}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


@login_required
def consultation_print_view(request, pk):
    consultation = get_object_or_404(Consultation, pk=pk)
    prescription = getattr(consultation, 'prescription', None)
    latest_vital = consultation.patient.vitals.first()
    return render(request, 'consultations/consultation_print.html', {
        'consultation': consultation,
        'prescription': prescription,
        'latest_vital': latest_vital,
    })


@login_required
def consultation_detail_by_code_view(request, code):
    """Retrieve consultation using unique code (re_path regex router)."""
    consultation = get_object_or_404(Consultation, consultation_id=code)
    return consultation_detail_view(request, pk=consultation.pk)

