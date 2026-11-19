from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

from .models import Appointment
from .forms import AppointmentBookingForm, AppointmentStatusUpdateForm
from patients.models import Patient
from accounts.models import User
from accounts.permissions import receptionist_required
from audit.services import log_audit_event
from audit.models import AuditLog


@login_required
def appointment_list_view(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    doctor_filter = request.GET.get('doctor', '')
    date_filter = request.GET.get('date', '')

    apts_qs = Appointment.objects.select_related('patient', 'doctor').all().order_by('appointment_date', 'appointment_time')

    if query:
        apts_qs = apts_qs.filter(
            Q(appointment_id__icontains=query) |
            Q(patient__first_name__icontains=query) |
            Q(patient__last_name__icontains=query) |
            Q(patient__patient_id__icontains=query)
        )
    if status_filter:
        apts_qs = apts_qs.filter(status=status_filter)
    if doctor_filter:
        apts_qs = apts_qs.filter(doctor_id=doctor_filter)
    if date_filter:
        apts_qs = apts_qs.filter(appointment_date=date_filter)

    paginator = Paginator(apts_qs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    doctors = User.objects.filter(role=User.Role.DOCTOR, is_active=True)

    return render(request, 'appointments/appointment_list.html', {
        'page_obj': page_obj,
        'doctors': doctors,
        'statuses': Appointment.Status.choices,
        'selected_status': status_filter,
        'selected_doctor': doctor_filter,
        'selected_date': date_filter,
        'query': query,
    })


@login_required
def appointment_by_status_view(request, status):
    """Filter appointments by status using str path converter."""
    status_upper = status.upper()
    apts_qs = Appointment.objects.filter(status=status_upper).select_related('patient', 'doctor').order_by('-appointment_date', '-appointment_time')
    paginator = Paginator(apts_qs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    doctors = User.objects.filter(role=User.Role.DOCTOR, is_active=True)

    return render(request, 'appointments/appointment_list.html', {
        'page_obj': page_obj,
        'doctors': doctors,
        'statuses': Appointment.Status.choices,
        'selected_status': status_upper,
        'selected_doctor': '',
        'selected_date': '',
        'query': '',
    })



@login_required
@receptionist_required
def appointment_book_view(request):
    initial = {}
    patient_id = request.GET.get('patient_id')
    if patient_id:
        initial['patient'] = get_object_or_404(Patient, pk=patient_id)

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            try:
                appointment = form.save(commit=False)
                appointment.booked_by = request.user
                appointment.save()

                log_audit_event(
                    request=request,
                    user=request.user,
                    action=AuditLog.Action.APPOINTMENT_BOOK,
                    record_type="Appointment",
                    record_id=appointment.appointment_id,
                    description=f"Booked appointment {appointment.appointment_id} for {appointment.patient.get_full_name()} with {appointment.doctor.display_title} on {appointment.appointment_date} at {appointment.appointment_time}."
                )
                messages.success(request, f"Appointment {appointment.appointment_id} booked successfully!")
                return redirect('appointments:appointment_list')
            except Exception as e:
                messages.error(request, f"Could not book appointment: {e}")
        else:
            messages.error(request, "Failed to book appointment. Please resolve the errors.")
    else:
        form = AppointmentBookingForm(initial=initial)

    return render(request, 'appointments/appointment_form.html', {
        'form': form,
        'is_edit': False,
    })


@login_required
@receptionist_required
def appointment_edit_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST, instance=appointment)
        if form.is_valid():
            try:
                form.save()
                log_audit_event(
                    request=request,
                    user=request.user,
                    action=AuditLog.Action.APPOINTMENT_UPDATE,
                    record_type="Appointment",
                    record_id=appointment.appointment_id,
                    description=f"Updated appointment details for {appointment.appointment_id}."
                )
                messages.success(request, f"Appointment {appointment.appointment_id} updated successfully.")
                return redirect('appointments:appointment_list')
            except Exception as e:
                messages.error(request, f"Update error: {e}")
    else:
        form = AppointmentBookingForm(instance=appointment)

    return render(request, 'appointments/appointment_form.html', {
        'form': form,
        'is_edit': True,
        'appointment': appointment,
    })


@login_required
def appointment_cancel_view(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == 'POST':
        form = AppointmentStatusUpdateForm(request.POST, instance=appointment)
        if form.is_valid():
            apt = form.save(commit=False)
            apt.status = Appointment.Status.CANCELLED
            apt.save()

            log_audit_event(
                request=request,
                user=request.user,
                action=AuditLog.Action.APPOINTMENT_UPDATE,
                record_type="Appointment",
                record_id=appointment.appointment_id,
                description=f"Cancelled appointment {appointment.appointment_id}. Reason: {apt.cancellation_reason}."
            )
            messages.warning(request, f"Appointment {appointment.appointment_id} was cancelled.")
            return redirect('appointments:appointment_list')
    else:
        form = AppointmentStatusUpdateForm(instance=appointment)

    return render(request, 'appointments/appointment_cancel.html', {
        'form': form,
        'appointment': appointment,
    })


@login_required
def appointment_schedule_view(request):
    """Daily and weekly agenda view."""
    today = timezone.localdate()
    view_type = request.GET.get('view', 'day')
    selected_date_str = request.GET.get('date', '')

    if selected_date_str:
        try:
            current_date = timezone.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            current_date = today
    else:
        current_date = today

    if view_type == 'week':
        start_of_week = current_date - timedelta(days=current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        appointments = Appointment.objects.select_related('patient', 'doctor').filter(
            appointment_date__range=[start_of_week, end_of_week]
        ).order_by('appointment_date', 'appointment_time')
    else:
        start_of_week = current_date
        end_of_week = current_date
        appointments = Appointment.objects.select_related('patient', 'doctor').filter(
            appointment_date=current_date
        ).order_by('appointment_time')

    doctors = User.objects.filter(role=User.Role.DOCTOR, is_active=True)

    return render(request, 'appointments/schedule_view.html', {
        'appointments': appointments,
        'current_date': current_date,
        'view_type': view_type,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
        'doctors': doctors,
    })
