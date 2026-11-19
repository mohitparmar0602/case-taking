import csv
import io
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from patients.models import Patient
from consultations.models import Consultation
from appointments.models import Appointment
from accounts.models import User
from accounts.permissions import admin_required
from core.models import InstitutionSettings
from audit.services import log_audit_event
from audit.models import AuditLog


@login_required
@admin_required
def reports_dashboard_view(request):
    today = timezone.localdate()
    from_date_str = request.GET.get('from_date', '')
    to_date_str = request.GET.get('to_date', '')
    doctor_id = request.GET.get('doctor', '')

    if from_date_str:
        try:
            start_date = timezone.datetime.strptime(from_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = today - timedelta(days=30)
    else:
        start_date = today - timedelta(days=30)

    if to_date_str:
        try:
            end_date = timezone.datetime.strptime(to_date_str, '%Y-%m-%d').date()
        except ValueError:
            end_date = today
    else:
        end_date = today

    # Base QuerySets with Date range
    patients_qs = Patient.objects.filter(created_at__date__range=[start_date, end_date])
    consultations_qs = Consultation.objects.filter(created_at__date__range=[start_date, end_date])
    appointments_qs = Appointment.objects.filter(appointment_date__range=[start_date, end_date])

    if doctor_id:
        consultations_qs = consultations_qs.filter(doctor_id=doctor_id)
        appointments_qs = appointments_qs.filter(doctor_id=doctor_id)

    # Aggregations
    total_reg = patients_qs.count()
    total_con = consultations_qs.count()
    completed_con = consultations_qs.filter(is_finalized=True).count()
    total_apt = appointments_qs.count()
    cancelled_apt = appointments_qs.filter(status=Appointment.Status.CANCELLED).count()

    # Demographics: Gender Breakdown
    gender_stats = patients_qs.values('gender').annotate(count=Count('id'))
    gender_labels = [g['gender'] for g in gender_stats]
    gender_data = [g['count'] for g in gender_stats]

    # Consultations per Doctor
    doc_stats = consultations_qs.values('doctor__first_name', 'doctor__last_name').annotate(count=Count('id')).order_by('-count')
    doc_labels = [f"Dr. {d['doctor__first_name']} {d['doctor__last_name']}".strip() for d in doc_stats]
    doc_data = [d['count'] for d in doc_stats]

    # Appointment Status breakdown
    apt_stats = appointments_qs.values('status').annotate(count=Count('id'))
    apt_labels = [s['status'] for s in apt_stats]
    apt_data = [s['count'] for s in apt_stats]

    doctors = User.objects.filter(role=User.Role.DOCTOR, is_active=True)

    return render(request, 'reports/dashboard.html', {
        'start_date': start_date,
        'end_date': end_date,
        'selected_doctor': doctor_id,
        'doctors': doctors,
        'total_reg': total_reg,
        'total_con': total_con,
        'completed_con': completed_con,
        'total_apt': total_apt,
        'cancelled_apt': cancelled_apt,
        'gender_labels_json': json.dumps(gender_labels),
        'gender_data_json': json.dumps(gender_data),
        'doc_labels_json': json.dumps(doc_labels),
        'doc_data_json': json.dumps(doc_data),
        'apt_labels_json': json.dumps(apt_labels),
        'apt_data_json': json.dumps(apt_data),
        'doc_stats': doc_stats,
    })


@login_required
@admin_required
def export_patients_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Patients_Report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Patient ID', 'First Name', 'Last Name', 'Age', 'Gender', 'Blood Group', 'Phone', 'City', 'State', 'Registration Date', 'Registered By'])

    for p in Patient.objects.all().order_by('-created_at'):
        writer.writerow([
            p.patient_id,
            p.first_name,
            p.last_name,
            p.age,
            p.get_gender_display(),
            p.get_blood_group_display(),
            p.phone_number,
            p.city,
            p.state,
            p.created_at.strftime('%Y-%m-%d %H:%M'),
            p.registered_by.display_title if p.registered_by else "Staff"
        ])

    log_audit_event(
        request=request,
        user=request.user,
        action=AuditLog.Action.DOCUMENT_DOWNLOAD,
        record_type="ReportExport",
        record_id="PatientsCSV",
        description="Exported Patient Registry CSV report."
    )
    return response


@login_required
@admin_required
def export_consultations_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Consultations_Report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Consultation ID', 'Date', 'Patient ID', 'Patient Name', 'Doctor', 'Status', 'Provisional Diagnosis', 'Final Diagnosis', 'Follow-up Date'])

    for c in Consultation.objects.select_related('patient', 'doctor').all().order_by('-created_at'):
        writer.writerow([
            c.consultation_id,
            c.created_at.strftime('%Y-%m-%d %H:%M'),
            c.patient.patient_id,
            c.patient.get_full_name(),
            c.doctor.display_title,
            c.get_status_display(),
            c.provisional_diagnosis,
            c.final_diagnosis,
            c.follow_up_date or "None"
        ])

    log_audit_event(
        request=request,
        user=request.user,
        action=AuditLog.Action.DOCUMENT_DOWNLOAD,
        record_type="ReportExport",
        record_id="ConsultationsCSV",
        description="Exported Consultations Activity CSV report."
    )
    return response


@login_required
@admin_required
def export_executive_summary_pdf(request):
    """Generates comprehensive hospital executive report PDF using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    institution = InstitutionSettings.get_settings()

    title_style = ParagraphStyle(
        'RepTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16,
        textColor=colors.HexColor('#1E3A8A'), alignment=TA_CENTER
    )
    sub_style = ParagraphStyle(
        'RepSub', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5,
        textColor=colors.HexColor('#475569'), alignment=TA_CENTER
    )
    h2_style = ParagraphStyle(
        'RepH2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12,
        textColor=colors.HexColor('#1E3A8A'), spaceBefore=10, spaceAfter=6
    )
    norm = ParagraphStyle('RepNorm', parent=styles['Normal'], fontSize=9, leading=12)
    bold = ParagraphStyle('RepBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12)

    story = []
    story.append(Paragraph(f"{institution.name}", title_style))
    story.append(Paragraph(f"Executive Healthcare Operations & Case-Taking Summary | SIH 2026", sub_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=12))

    # Metrics Summary Table
    t_patients = Patient.objects.count()
    t_consultations = Consultation.objects.count()
    t_appointments = Appointment.objects.count()
    t_doctors = User.objects.filter(role=User.Role.DOCTOR).count()

    summary_data = [
        [Paragraph("<b>Metric</b>", bold), Paragraph("<b>Count / Value</b>", bold), Paragraph("<b>Key Indicator</b>", bold)],
        [Paragraph("Total Registered Patients", norm), Paragraph(str(t_patients), norm), Paragraph("Active digital patient directory", norm)],
        [Paragraph("Total Clinical Consultations", norm), Paragraph(str(t_consultations), norm), Paragraph("Digitized structured case sheets", norm)],
        [Paragraph("Total Appointments Managed", norm), Paragraph(str(t_appointments), norm), Paragraph("Scheduled patient visits", norm)],
        [Paragraph("Active Medical Doctors", norm), Paragraph(str(t_doctors), norm), Paragraph("Consultant clinical faculty", norm)],
    ]
    sum_table = Table(summary_data, colWidths=[180, 100, 240])
    sum_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EFF6FF')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(Paragraph("1. Executive Key Performance Indicators", h2_style))
    story.append(sum_table)
    story.append(Spacer(1, 10))

    # Doctor Performance Table
    story.append(Paragraph("2. Consultations Breakdown by Clinical Practitioner", h2_style))
    doc_data = [[
        Paragraph("<b>Physician Name</b>", bold),
        Paragraph("<b>Specialization</b>", bold),
        Paragraph("<b>Total Consultations</b>", bold)
    ]]
    for doc_user in User.objects.filter(role=User.Role.DOCTOR):
        cnt = Consultation.objects.filter(doctor=doc_user).count()
        spec = doc_user.profile.specialization if hasattr(doc_user, 'profile') else "General"
        doc_data.append([
            Paragraph(doc_user.display_title, norm),
            Paragraph(spec, norm),
            Paragraph(str(cnt), norm)
        ])

    doc_table = Table(doc_data, colWidths=[200, 200, 120])
    doc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(doc_table)

    story.append(Spacer(1, 25))
    story.append(Paragraph(f"Generated on {timezone.now().strftime('%d-%b-%Y %I:%M %p')} by Administrator: {request.user.display_title}", norm))

    doc.build(story)
    buffer.seek(0)

    log_audit_event(
        request=request,
        user=request.user,
        action=AuditLog.Action.DOCUMENT_DOWNLOAD,
        record_type="ReportExport",
        record_id="ExecutiveSummaryPDF",
        description="Generated Executive Operations Summary PDF report."
    )

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Executive_Clinical_Summary.pdf"'
    return response
