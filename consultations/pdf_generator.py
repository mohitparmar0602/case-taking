import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from core.models import InstitutionSettings


def generate_consultation_pdf(consultation):
    """
    Generates a professional hospital-grade Medical Consultation Report PDF using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    institution = InstitutionSettings.get_settings()
    styles = getSampleStyleSheet()

    # Custom styles
    header_title = ParagraphStyle(
        'HospitalTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#1E3A8A'),
        alignment=TA_CENTER
    )
    header_sub = ParagraphStyle(
        'HospitalSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#475569'),
        alignment=TA_CENTER
    )
    section_head = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=8,
        spaceAfter=4
    )
    normal_text = ParagraphStyle(
        'ReportNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1E293B')
    )
    bold_label = ParagraphStyle(
        'ReportBoldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # 1. Hospital Header
    story.append(Paragraph(institution.name, header_title))
    tagline_text = f"{institution.tagline}<br/>{institution.address}, {institution.city}, {institution.state} - {institution.postal_code} | Tel: {institution.phone}"
    story.append(Paragraph(tagline_text, header_sub))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=10))

    # 2. Patient & Consultation Demographics Box
    patient = consultation.patient
    doctor = consultation.doctor
    doctor_spec = doctor.profile.specialization if hasattr(doctor, 'profile') else "Consultant Physician"

    info_data = [
        [
            Paragraph(f"<b>Patient ID:</b> {patient.patient_id}", normal_text),
            Paragraph(f"<b>Consultation ID:</b> {consultation.consultation_id}", normal_text),
            Paragraph(f"<b>Date:</b> {consultation.created_at.strftime('%d-%b-%Y %I:%M %p')}", normal_text),
        ],
        [
            Paragraph(f"<b>Name:</b> {patient.get_full_name()}", normal_text),
            Paragraph(f"<b>Age / Sex:</b> {patient.age} Yrs / {patient.get_gender_display()}", normal_text),
            Paragraph(f"<b>Blood Group:</b> {patient.get_blood_group_display()}", normal_text),
        ],
        [
            Paragraph(f"<b>Contact:</b> {patient.phone_number}", normal_text),
            Paragraph(f"<b>Doctor:</b> {doctor.display_title}", normal_text),
            Paragraph(f"<b>Specialty:</b> {doctor_spec}", normal_text),
        ],
    ]

    info_table = Table(info_data, colWidths=[175, 175, 175])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))

    # 3. Latest Vitals Strip (if available)
    latest_vital = patient.vitals.first()
    if latest_vital:
        vitals_data = [[
            Paragraph(f"<b>BP:</b> {latest_vital.blood_pressure_display}", normal_text),
            Paragraph(f"<b>Pulse:</b> {latest_vital.heart_rate or '—'} bpm", normal_text),
            Paragraph(f"<b>Temp:</b> {latest_vital.temperature_f or '—'} °F", normal_text),
            Paragraph(f"<b>SpO2:</b> {latest_vital.oxygen_saturation or '—'}%", normal_text),
            Paragraph(f"<b>BMI:</b> {latest_vital.bmi or '—'}", normal_text),
        ]]
        vitals_table = Table(vitals_data, colWidths=[105, 105, 105, 105, 105])
        vitals_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EFF6FF')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#93C5FD')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(vitals_table)
        story.append(Spacer(1, 8))

    # 4. Chief Complaints & HPI
    story.append(Paragraph("1. Chief Complaints & Clinical Presentation", section_head))
    story.append(Paragraph(consultation.chief_complaints or "None documented", normal_text))
    story.append(Spacer(1, 6))

    if consultation.history_of_present_illness:
        story.append(Paragraph("<b>History of Present Illness:</b>", bold_label))
        story.append(Paragraph(consultation.history_of_present_illness, normal_text))
        story.append(Spacer(1, 6))

    # 5. Clinical Examination Findings
    if consultation.general_examination or consultation.systemic_examination:
        story.append(Paragraph("2. Clinical Examination", section_head))
        if consultation.general_examination:
            story.append(Paragraph(f"<b>General Examination:</b> {consultation.general_examination}", normal_text))
        if consultation.systemic_examination:
            story.append(Paragraph(f"<b>Systemic Examination:</b> {consultation.systemic_examination}", normal_text))
        story.append(Spacer(1, 6))

    # 6. Diagnosis
    story.append(Paragraph("3. Diagnosis", section_head))
    if consultation.final_diagnosis:
        story.append(Paragraph(f"<b>Final Diagnosis:</b> {consultation.final_diagnosis}", normal_text))
    if consultation.provisional_diagnosis:
        story.append(Paragraph(f"<b>Provisional Diagnosis:</b> {consultation.provisional_diagnosis}", normal_text))
    story.append(Spacer(1, 6))

    # 7. Prescriptions (Rx)
    has_prescription = hasattr(consultation, 'prescription') and consultation.prescription.items.exists()
    if has_prescription:
        story.append(Paragraph("4. Rx — Prescribed Medications", section_head))
        rx_header = [
            Paragraph("<b>#</b>", bold_label),
            Paragraph("<b>Medicine Name</b>", bold_label),
            Paragraph("<b>Dosage / Strength</b>", bold_label),
            Paragraph("<b>Frequency</b>", bold_label),
            Paragraph("<b>Duration</b>", bold_label),
            Paragraph("<b>Instructions</b>", bold_label),
        ]
        rx_rows = [rx_header]
        for idx, item in enumerate(consultation.prescription.items.all(), 1):
            rx_rows.append([
                Paragraph(str(idx), normal_text),
                Paragraph(f"{item.medicine_name} ({item.get_dosage_form_display()})", normal_text),
                Paragraph(item.strength_dosage, normal_text),
                Paragraph(f"{item.frequency} - {item.get_timing_display()}", normal_text),
                Paragraph(item.duration, normal_text),
                Paragraph(item.instructions or "—", normal_text),
            ])

        rx_table = Table(rx_rows, colWidths=[25, 140, 90, 110, 60, 100])
        rx_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(rx_table)
        story.append(Spacer(1, 6))

        if consultation.prescription.general_advice:
            story.append(Paragraph(f"<b>Prescription Advice:</b> {consultation.prescription.general_advice}", normal_text))
            story.append(Spacer(1, 6))

    # 8. Treatment Plan & Recommended Investigations
    if consultation.treatment_plan or consultation.recommended_investigations:
        story.append(Paragraph("5. Management & Investigations", section_head))
        if consultation.treatment_plan:
            story.append(Paragraph(f"<b>Treatment Plan:</b> {consultation.treatment_plan}", normal_text))
        if consultation.recommended_investigations:
            story.append(Paragraph(f"<b>Recommended Investigations / Labs:</b> {consultation.recommended_investigations}", normal_text))
        if consultation.dietary_lifestyle_advice:
            story.append(Paragraph(f"<b>Diet & Lifestyle Advice:</b> {consultation.dietary_lifestyle_advice}", normal_text))
        story.append(Spacer(1, 6))

    # 9. Follow-up & Footer
    if consultation.follow_up_date:
        story.append(Paragraph(f"<b>Follow-up Date:</b> {consultation.follow_up_date.strftime('%d-%b-%Y')}", bold_label))
        story.append(Spacer(1, 10))

    # Amendments (if any)
    if consultation.amendments.exists():
        story.append(Paragraph("Audited Addenda / Amendments", section_head))
        for amend in consultation.amendments.all():
            amend_text = f"<b>[{amend.created_at.strftime('%d-%b-%Y %H:%M')} by {amend.author.display_title}]:</b> {amend.amendment_note}"
            story.append(Paragraph(amend_text, normal_text))
        story.append(Spacer(1, 10))

    # Sign-off box
    story.append(Spacer(1, 25))
    sign_data = [
        [
            Paragraph("<i>Verified & Finalized Clinically</i><br/>Status: Finalized & Locked" if consultation.is_finalized else "<i>Draft Record — Not Finalized</i>", normal_text),
            Paragraph(f"<b>{doctor.display_title}</b><br/>{doctor_spec}<br/>License: {doctor.profile.license_number if hasattr(doctor, 'profile') else 'N/A'}", ParagraphStyle('RightDoc', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=9, leading=12))
        ]
    ]
    sign_table = Table(sign_data, colWidths=[260, 265])
    sign_table.setStyle(TableStyle([
        ('LINEABOVE', (1, 0), (1, 0), 1, colors.HexColor('#475569')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(sign_table)

    # Disclaimer
    story.append(Spacer(1, 15))
    disclaimer = Paragraph(
        "Notice: This digital case-taking record is generated for institutional clinical and administrative documentation (SIH 2026 | PS ID: SIH26047).",
        ParagraphStyle('Disc', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7, textColor=colors.HexColor('#94A3B8'), alignment=TA_CENTER)
    )
    story.append(disclaimer)

    doc.build(story)
    buffer.seek(0)
    return buffer
