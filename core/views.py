from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages

from accounts.models import User
from accounts.permissions import admin_required, doctor_required, receptionist_required, nurse_required
from patients.models import Patient
from consultations.models import Consultation
from appointments.models import Appointment
from medical_records.models import VitalRecord
from audit.models import AuditLog
from audit.services import log_audit_event
from .models import InstitutionSettings
from .forms import InstitutionSettingsForm


def home_view(request):
    """
    Public marketing landing page (Carevia Healthcare Platform) for SIH 2026.
    Redirects authenticated staff directly to their appropriate dashboard.
    """
    if request.user.is_authenticated:
        return dashboard_router(request)

    doctors = User.objects.filter(role=User.Role.DOCTOR, is_active=True).select_related('profile')
    institution = InstitutionSettings.get_settings()

    if request.method == 'POST' and 'public_booking_submit' in request.POST:
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        doctor_id = request.POST.get('doctor_id')
        preferred_date_str = request.POST.get('preferred_date')
        reason = request.POST.get('reason', 'General Consultation').strip()

        if first_name and last_name and phone and doctor_id and preferred_date_str:
            try:
                doctor = User.objects.get(pk=doctor_id, role=User.Role.DOCTOR)
                # Find or register patient
                patient = Patient.objects.filter(phone=phone).first()
                if not patient:
                    patient = Patient.objects.create(
                        first_name=first_name,
                        last_name=last_name,
                        phone=phone,
                        gender=Patient.Gender.OTHER,
                        address="Online Web Booking"
                    )

                # Find an available slot for this doctor on preferred_date
                candidate_slots = ['09:30', '10:30', '11:30', '14:30', '15:30', '16:30', '17:30']
                booked_time = None
                for slot in candidate_slots:
                    if not Appointment.objects.filter(
                        doctor=doctor,
                        appointment_date=preferred_date_str,
                        appointment_time=slot
                    ).exclude(status=Appointment.Status.CANCELLED).exists():
                        booked_time = slot
                        break

                if not booked_time:
                    booked_time = '18:00'

                apt = Appointment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    appointment_date=preferred_date_str,
                    appointment_time=booked_time,
                    reason=reason or "General Consultation Intake",
                    status=Appointment.Status.PENDING
                )
                messages.success(
                    request,
                    f"Thank you, {first_name}! Your appointment request ({apt.appointment_id}) with {doctor.display_title} on {preferred_date_str} at {booked_time} has been registered in the system. Our desk will confirm shortly."
                )
                return redirect('core:home')
            except Exception as e:
                messages.error(request, f"Unable to process booking request: {e}")
        else:
            messages.error(request, "Please fill in all required fields to submit an appointment request.")

    return render(request, 'core/home.html', {
        'doctors': doctors,
        'institution': institution,
    })


def clinical_care_view(request):
    """Public Clinical Care modules and architecture page."""
    return render(request, 'core/clinical_care.html')


def how_it_works_view(request):
    """Public How It Works - The Four Pillars of Modern Case-Taking workflow page."""
    return render(request, 'core/how_it_works.html')


@login_required
def dashboard_router(request):
    """Direct logged-in user to their specialized role dashboard."""
    user = request.user
    if user.is_admin_user:
        return redirect('core:admin_dashboard')
    elif user.role == User.Role.DOCTOR:
        return redirect('core:doctor_dashboard')
    elif user.role == User.Role.RECEPTIONIST:
        return redirect('core:receptionist_dashboard')
    elif user.role == User.Role.NURSE:
        return redirect('core:nurse_dashboard')
    return redirect('core:admin_dashboard')


@login_required
@admin_required
def admin_dashboard(request):
    today = timezone.localdate()
    seven_days_ago = today - timedelta(days=6)

    # Key Statistics (Real database aggregations)
    total_patients = Patient.objects.filter(is_active=True).count()
    new_patients_today = Patient.objects.filter(created_at__date=today).count()
    total_consultations = Consultation.objects.count()
    consultations_today = Consultation.objects.filter(created_at__date=today).count()
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=today,
        status__in=[Appointment.Status.CONFIRMED, Appointment.Status.PENDING]
    ).count()
    pending_appointments = Appointment.objects.filter(status=Appointment.Status.PENDING).count()
    completed_appointments = Appointment.objects.filter(status=Appointment.Status.COMPLETED).count()

    total_doctors = User.objects.filter(role=User.Role.DOCTOR, is_active=True).count()
    total_nurses = User.objects.filter(role=User.Role.NURSE, is_active=True).count()
    total_receptionists = User.objects.filter(role=User.Role.RECEPTIONIST, is_active=True).count()
    total_staff = User.objects.filter(is_active=True).count()

    # 7-Day Chart Data for Registrations and Consultations
    labels = []
    reg_counts = []
    con_counts = []

    for i in range(7):
        day = seven_days_ago + timedelta(days=i)
        day_str = day.strftime('%d %b')
        labels.append(day_str)
        reg_counts.append(Patient.objects.filter(created_at__date=day).count())
        con_counts.append(Consultation.objects.filter(created_at__date=day).count())

    # Recent Records
    recent_patients = Patient.objects.filter(is_active=True).order_by('-created_at')[:6]
    recent_consultations = Consultation.objects.select_related('patient', 'doctor').order_by('-created_at')[:6]
    today_appointments = Appointment.objects.select_related('patient', 'doctor').filter(
        appointment_date=today
    ).order_by('appointment_time')[:6]
    recent_audit_logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:8]

    return render(request, 'core/admin_dashboard.html', {
        'total_patients': total_patients,
        'new_patients_today': new_patients_today,
        'total_consultations': total_consultations,
        'consultations_today': consultations_today,
        'upcoming_appointments': upcoming_appointments,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
        'total_doctors': total_doctors,
        'total_nurses': total_nurses,
        'total_receptionists': total_receptionists,
        'total_staff': total_staff,
        'chart_labels': labels,
        'reg_counts': reg_counts,
        'con_counts': con_counts,
        'recent_patients': recent_patients,
        'recent_consultations': recent_consultations,
        'today_appointments': today_appointments,
        'recent_audit_logs': recent_audit_logs,
    })


@login_required
@doctor_required
def doctor_dashboard(request):
    today = timezone.localdate()
    doctor = request.user

    my_appointments_today = Appointment.objects.select_related('patient').filter(
        doctor=doctor,
        appointment_date=today
    ).order_by('appointment_time')

    my_consultations_today = Consultation.objects.filter(
        doctor=doctor,
        created_at__date=today
    ).count()

    my_pending_drafts = Consultation.objects.filter(
        doctor=doctor,
        is_finalized=False
    ).select_related('patient').order_by('-updated_at')

    recent_completed = Consultation.objects.filter(
        doctor=doctor,
        is_finalized=True
    ).select_related('patient').order_by('-finalized_at')[:6]

    total_my_consultations = Consultation.objects.filter(doctor=doctor).count()
    upcoming_apt_count = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__gte=today,
        status=Appointment.Status.CONFIRMED
    ).count()

    return render(request, 'core/doctor_dashboard.html', {
        'my_appointments_today': my_appointments_today,
        'my_consultations_today': my_consultations_today,
        'my_pending_drafts': my_pending_drafts,
        'recent_completed': recent_completed,
        'total_my_consultations': total_my_consultations,
        'upcoming_apt_count': upcoming_apt_count,
    })


@login_required
@receptionist_required
def receptionist_dashboard(request):
    today = timezone.localdate()

    today_registrations = Patient.objects.filter(created_at__date=today).order_by('-created_at')
    today_appointments = Appointment.objects.select_related('patient', 'doctor').filter(
        appointment_date=today
    ).order_by('appointment_time')

    pending_checkins = today_appointments.filter(status=Appointment.Status.CONFIRMED)
    total_registered_today = today_registrations.count()
    total_appointments_today = today_appointments.count()

    doctors = User.objects.filter(role=User.Role.DOCTOR, is_active=True).select_related('profile')

    return render(request, 'core/receptionist_dashboard.html', {
        'today_registrations': today_registrations[:8],
        'today_appointments': today_appointments,
        'pending_checkins': pending_checkins,
        'total_registered_today': total_registered_today,
        'total_appointments_today': total_appointments_today,
        'doctors': doctors,
    })


@login_required
@nurse_required
def nurse_dashboard(request):
    today = timezone.localdate()

    # Patients registered today or with appointments today
    appointments_today = Appointment.objects.select_related('patient', 'doctor').filter(
        appointment_date=today
    ).order_by('appointment_time')

    # Recent vitals entered by this nurse or recorded today
    recent_vitals = VitalRecord.objects.select_related('patient', 'recorded_by').filter(
        created_at__date=today
    ).order_by('-measurement_time')[:10]

    vitals_count_today = VitalRecord.objects.filter(created_at__date=today).count()
    active_queue_count = appointments_today.filter(status=Appointment.Status.CONFIRMED).count()

    return render(request, 'core/nurse_dashboard.html', {
        'appointments_today': appointments_today,
        'recent_vitals': recent_vitals,
        'vitals_count_today': vitals_count_today,
        'active_queue_count': active_queue_count,
    })


@login_required
@admin_required
def institution_settings_view(request):
    settings_obj = InstitutionSettings.get_settings()
    if request.method == 'POST':
        form = InstitutionSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            log_audit_event(
                request=request,
                user=request.user,
                action=AuditLog.Action.STAFF_UPDATE,
                record_type="InstitutionSettings",
                record_id="1",
                description="Administrator updated institution profile and global settings."
            )
            messages.success(request, "Institution settings updated successfully.")
            return redirect('core:settings')
    else:
        form = InstitutionSettingsForm(instance=settings_obj)

    return render(request, 'core/settings.html', {'form': form, 'settings_obj': settings_obj})


def unauthorized_view(request):
    return render(request, 'core/unauthorized.html', status=403)


def custom_404_view(request, exception=None):
    """Custom 404 Not Found error handler (INT253 Mandatory Requirement)."""
    return render(request, '404.html', status=404)


def custom_500_view(request):
    """Custom 500 Internal Server Error handler (INT253 Mandatory Requirement)."""
    return render(request, '500.html', status=500)

