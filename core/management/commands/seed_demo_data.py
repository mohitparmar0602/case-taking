import random
from datetime import timedelta, date, time
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from accounts.models import User, StaffProfile
from core.models import InstitutionSettings
from patients.models import Patient
from medical_records.models import MedicalHistory, VitalRecord
from appointments.models import Appointment
from consultations.models import Consultation, ConsultationAmendment
from prescriptions.models import Prescription, PrescriptionItem
from audit.models import AuditLog


class Command(BaseCommand):
    help = "Seeds database with realistic fictional healthcare demo data for Smart India Hackathon 2026 (PS ID: SIH26047)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Cleanly reset and re-seed demo data'
        )

    def handle(self, *args, **options):
        reset_requested = options.get('reset', False)
        self.stdout.write(self.style.NOTICE("Initializing SIH 2026 Demo Data Seeding..."))

        with transaction.atomic():
            if reset_requested:
                self.stdout.write("Resetting previous demonstration records...")
                ConsultationAmendment.objects.all().delete()
                PrescriptionItem.objects.all().delete()
                Prescription.objects.all().delete()
                Consultation.objects.all().delete()
                Appointment.objects.all().delete()
                VitalRecord.objects.all().delete()
                MedicalHistory.objects.all().delete()
                Patient.objects.all().delete()
                self.stdout.write(self.style.SUCCESS("[OK] Previous demo records cleaned."))

            # 1. Institution Settings
            institution = InstitutionSettings.get_settings()
            institution.name = "Apex Medical Institute & Research Hospital"
            institution.tagline = "Smart Digital Patient Case-Taking Software | SIH 2026 (PS ID: SIH26047)"
            institution.code = "AIMS-2026"
            institution.email = "contact@apexmedical.org"
            institution.phone = "+91 11 2659 8700"
            institution.emergency_helpline = "108 / 112"
            institution.address = "Sector 14, Institutional Area, Ring Road"
            institution.city = "New Delhi"
            institution.state = "Delhi"
            institution.postal_code = "110029"
            institution.save()

            # 2. Staff Accounts
            # Admin
            admin_user, _ = User.objects.get_or_create(
                username="admin",
                defaults={
                    'first_name': "Super",
                    'last_name': "Admin",
                    'email': "admin@apexmedical.org",
                    'role': User.Role.ADMIN,
                    'is_staff': True,
                    'is_superuser': True,
                    'phone': "+91 98100 11223"
                }
            )
            admin_user.set_password("password123")
            admin_user.save()
            StaffProfile.objects.update_or_create(
                user=admin_user,
                defaults={
                    'employee_id': "ADM-001",
                    'department': "Hospital Administration",
                    'qualification': "MHA, MBA (Healthcare)",
                    'specialization': "Healthcare Informatics"
                }
            )

            # 3 Doctors
            doctors_data = [
                ("dr.sharma", "Rajesh", "Sharma", "rajesh.sharma@apexmedical.org", "General Medicine", "MBBS, MD (Medicine)", "MCI-IND-44210", 600.00),
                ("dr.anita", "Anita", "Verma", "anita.verma@apexmedical.org", "Cardiology", "MBBS, MD, DM (Cardiology)", "MCI-IND-58921", 800.00),
                ("dr.vikram", "Vikram", "Malhotra", "vikram.m@apexmedical.org", "Pulmonology & Chest Medicine", "MBBS, MD (Pulmonology)", "MCI-IND-61204", 700.00),
            ]
            doctors = []
            for username, first, last, email, spec, qual, lic, fee in doctors_data:
                u, _ = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': first,
                        'last_name': last,
                        'email': email,
                        'role': User.Role.DOCTOR,
                        'phone': f"+91 98{random.randint(10000000, 99999999)}"
                    }
                )
                u.set_password("password123")
                u.save()
                StaffProfile.objects.update_or_create(
                    user=u,
                    defaults={
                        'employee_id': f"DOC-{u.id:03d}",
                        'department': spec,
                        'specialization': spec,
                        'qualification': qual,
                        'license_number': lic,
                        'consultation_fee': Decimal(fee)
                    }
                )
                doctors.append(u)

            # 2 Receptionists
            receptionists_data = [
                ("priya.rec", "Priya", "Nair", "priya.nair@apexmedical.org", "Central OPD Reception"),
                ("amit.rec", "Amit", "Singh", "amit.singh@apexmedical.org", "Emergency Triage Desk"),
            ]
            receptionists = []
            for username, first, last, email, dept in receptionists_data:
                u, _ = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': first,
                        'last_name': last,
                        'email': email,
                        'role': User.Role.RECEPTIONIST,
                        'phone': f"+91 97{random.randint(10000000, 99999999)}"
                    }
                )
                u.set_password("password123")
                u.save()
                StaffProfile.objects.update_or_create(
                    user=u,
                    defaults={
                        'employee_id': f"REC-{u.id:03d}",
                        'department': dept,
                        'qualification': "B.Com, Hospital Desk Diploma"
                    }
                )
                receptionists.append(u)

            # 2 Nurses
            nurses_data = [
                ("nurse.sunita", "Sunita", "Devi", "sunita.devi@apexmedical.org", "General OPD Intake"),
                ("nurse.kavita", "Kavita", "Patil", "kavita.patil@apexmedical.org", "Clinical Vitals Assessment"),
            ]
            nurses = []
            for username, first, last, email, dept in nurses_data:
                u, _ = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': first,
                        'last_name': last,
                        'email': email,
                        'role': User.Role.NURSE,
                        'phone': f"+91 96{random.randint(10000000, 99999999)}"
                    }
                )
                u.set_password("password123")
                u.save()
                StaffProfile.objects.update_or_create(
                    user=u,
                    defaults={
                        'employee_id': f"NUR-{u.id:03d}",
                        'department': dept,
                        'qualification': "B.Sc. Nursing, Registered Nurse",
                        'license_number': f"INC-RN-{random.randint(10000, 99999)}"
                    }
                )
                nurses.append(u)

            self.stdout.write(self.style.SUCCESS("[OK] Staff Accounts created (1 Admin, 3 Doctors, 2 Receptionists, 2 Nurses)."))

            # 3. 22 Fictional Patients
            fictional_patients_data = [
                ("Aarav", "Mehta", 32, "MALE", "B+", "9820145678", "aarav.mehta@example.com", "402, Green Park", "New Delhi", "Delhi", "110016", "Sunita Mehta", "9820145679", "Spouse", "MARRIED", "Software Architect"),
                ("Ananya", "Deshmukh", 28, "FEMALE", "O+", "9820256789", "ananya.d@example.com", "Flat 12, Mayur Vihar Ph 1", "New Delhi", "Delhi", "110091", "Ramesh Deshmukh", "9820256780", "Father", "SINGLE", "Graphic Designer"),
                ("Rohan", "Kapoor", 45, "MALE", "A+", "9820367890", "rohan.k@example.com", "B-14, Greater Kailash 1", "New Delhi", "Delhi", "110048", "Pooja Kapoor", "9820367891", "Spouse", "MARRIED", "Civil Contractor"),
                ("Meera", "Iyer", 58, "FEMALE", "AB+", "9820478901", "meera.iyer@example.com", "78, Dwarka Sector 10", "New Delhi", "Delhi", "110075", "Venkat Iyer", "9820478902", "Son", "WIDOWED", "Retired Bank Officer"),
                ("Vikram", "Chauhan", 24, "MALE", "O-", "9820589012", "vikram.c@example.com", "H.No 22, Rohini Sector 7", "New Delhi", "Delhi", "110085", "Suresh Chauhan", "9820589013", "Father", "SINGLE", "Graduate Student"),
                ("Pooja", "Bhatt", 36, "FEMALE", "A-", "9820690123", "pooja.bhatt@example.com", "Tower 4, Saket Court Road", "New Delhi", "Delhi", "110017", "Mahesh Bhatt", "9820690124", "Brother", "MARRIED", "High School Teacher"),
                ("Deepak", "Joshi", 52, "MALE", "B+", "9820701234", "deepak.joshi@example.com", "A-9, Vasant Kunj", "New Delhi", "Delhi", "110070", "Alka Joshi", "9820701235", "Spouse", "MARRIED", "Govt. Officer"),
                ("Sneha", "Kulkarni", 19, "FEMALE", "B-", "9820812345", "sneha.k@example.com", "303, Lajpat Nagar 4", "New Delhi", "Delhi", "110024", "Girish Kulkarni", "9820812346", "Father", "SINGLE", "College Student"),
                ("Arjun", "Reddy", 41, "MALE", "AB-", "9820923456", "arjun.reddy@example.com", "Plot 67, Hauz Khas", "New Delhi", "Delhi", "110016", "Preeti Reddy", "9820923457", "Spouse", "MARRIED", "Financial Analyst"),
                ("Divya", "Sengupta", 63, "FEMALE", "O+", "9821034567", "divya.s@example.com", "C-33, Chittaranjan Park", "New Delhi", "Delhi", "110019", "Anirban Sengupta", "9821034568", "Husband", "MARRIED", "Homemaker"),
                ("Kabir", "Nath", 37, "MALE", "O+", "9821145678", "kabir.n@example.com", "14/B, Karol Bagh", "New Delhi", "Delhi", "110005", "Rashmi Nath", "9821145679", "Sister", "SINGLE", "Retail Merchant"),
                ("Suman", "Agarwal", 70, "FEMALE", "A+", "9821256789", "suman.a@example.com", "88, Civil Lines", "New Delhi", "Delhi", "110054", "Manoj Agarwal", "9821256780", "Son", "WIDOWED", "Retired Principal"),
                ("Mohit", "Singhania", 29, "MALE", "B+", "9821367890", "mohit.s@example.com", "Flat 502, Janakpuri", "New Delhi", "Delhi", "110058", "Neha Singhania", "9821367891", "Spouse", "MARRIED", "Marketing Lead"),
                ("Kavita", "Menon", 48, "FEMALE", "O+", "9821478901", "kavita.m@example.com", "D-12, Defence Colony", "New Delhi", "Delhi", "110024", "Ajay Menon", "9821478902", "Husband", "MARRIED", "HR Director"),
                ("Tarun", "Bansal", 55, "MALE", "A+", "9821589012", "tarun.b@example.com", "Shop 5, Chandni Chowk", "New Delhi", "Delhi", "110006", "Sita Bansal", "9821589013", "Spouse", "MARRIED", "Textile Trader"),
                ("Nisha", "Grover", 22, "FEMALE", "AB+", "9821690123", "nisha.g@example.com", "Block E, Naraina Vihar", "New Delhi", "Delhi", "110028", "Raj Grover", "9821690124", "Father", "SINGLE", "Intern"),
                ("Harish", "Patel", 62, "MALE", "O+", "9821701234", "harish.p@example.com", "45, Patel Nagar East", "New Delhi", "Delhi", "110008", "Kokila Patel", "9821701235", "Spouse", "MARRIED", "Retired Executive"),
                ("Swati", "Trivedi", 34, "FEMALE", "B+", "9821812345", "swati.t@example.com", "101, Paschim Vihar", "New Delhi", "Delhi", "110063", "Amit Trivedi", "9821812346", "Spouse", "MARRIED", "Data Analyst"),
                ("Gaurav", "Saxena", 40, "MALE", "A-", "9821923456", "gaurav.s@example.com", "22, Model Town III", "New Delhi", "Delhi", "110009", "Shalini Saxena", "9821923457", "Spouse", "MARRIED", "Lawyer"),
                ("Geeta", "Pandey", 50, "FEMALE", "O+", "9822034567", "geeta.p@example.com", "H-4, Preet Vihar", "New Delhi", "Delhi", "110092", "Dinesh Pandey", "9822034568", "Husband", "MARRIED", "Government School Teacher"),
                ("Vivek", "Rao", 27, "MALE", "B+", "9822145678", "vivek.rao@example.com", "12, Malviya Nagar", "New Delhi", "Delhi", "110017", "Satish Rao", "9822145679", "Father", "SINGLE", "Journalist"),
                ("Priyanka", "Das", 31, "FEMALE", "AB-", "9822256789", "priyanka.d@example.com", "Flat 8B, Kalkaji", "New Delhi", "Delhi", "110019", "Subhash Das", "9822256780", "Father", "SINGLE", "Biotechnologist"),
            ]

            patients = []
            for idx, p_data in enumerate(fictional_patients_data, 1):
                p_id = f"PAT-2026-{idx:04d}"
                p, created = Patient.objects.get_or_create(
                    patient_id=p_id,
                    defaults={
                        'first_name': p_data[0],
                        'last_name': p_data[1],
                        'age': p_data[2],
                        'date_of_birth': date.today() - timedelta(days=p_data[2] * 365),
                        'gender': p_data[3],
                        'blood_group': p_data[4],
                        'phone_number': p_data[5],
                        'email': p_data[6],
                        'address': p_data[7],
                        'city': p_data[8],
                        'state': p_data[9],
                        'pin_code': p_data[10],
                        'emergency_contact_name': p_data[11],
                        'emergency_contact_number': p_data[12],
                        'emergency_relationship': p_data[13],
                        'marital_status': p_data[14],
                        'occupation': p_data[15],
                        'registered_by': random.choice(receptionists),
                    }
                )
                patients.append(p)

            self.stdout.write(self.style.SUCCESS(f"[OK] {len(patients)} Patients verified / created."))

            # 4. Medical Histories & Vital Records for Patients
            complaints_samples = [
                ("High grade fever with chills and severe body ache", "4 days", "Acute viral prodrome with arthralgia", "Mild childhood asthma", "Father diabetic", "Penicillin allergy", "Paracetamol 650 SOS"),
                ("Exertional chest tightness and shortness of breath", "2 weeks", "Substernal heaviness radiating to left shoulder on climbing stairs", "Hypertension (5 yrs)", "Mother CAD at 62", "None reported", "Amlodipine 5mg OD"),
                ("Productive cough with yellowish sputum and mild wheeze", "5 days", "Began as runny nose, progressed to chest congestion", "Chronic sinusitis", "No hereditary illnesses", "Sulfa drugs (Rash)", "Ambroxol syrup"),
                ("Epigastric burning pain and acidic regurgitation after meals", "3 weeks", "Worse on lying flat and spicy food consumption", "Occasional gastritis", "Non-contributory", "None", "Pantoprazole 40mg before breakfast"),
                ("Persistent headache, posterior neck stiffness and fatigue", "10 days", "Throbbing bilateral temporal pain, blurred vision on exertion", "Essential hypertension", "Father hypertensive, stroke at 71", "None", "Telmisartan 40mg"),
                ("Joint pain with morning stiffness in bilateral knee joints", "6 months", "Difficulty squatting, crepitus on passive knee flexion", "Osteoarthritis grade II", "Mother had OA", "NSAIDs (Dyspepsia)", "Calcium + Vitamin D3"),
            ]

            for idx, p in enumerate(patients):
                cs = complaints_samples[idx % len(complaints_samples)]
                
                # Medical History (get or create)
                MedicalHistory.objects.get_or_create(
                    patient=p,
                    defaults={
                        'recorded_by': random.choice(doctors),
                        'chief_complaint': cs[0],
                        'duration': cs[1],
                        'onset': "Gradual" if "weeks" in cs[1] or "months" in cs[1] else "Sudden onset",
                        'severity': "MODERATE" if idx % 2 == 0 else "SEVERE",
                        'frequency': "Intermittent",
                        'associated_symptoms': "Fatigue, weakness",
                        'hpi_description': cs[2],
                        'previous_illnesses': cs[3],
                        'family_medical_history': cs[4],
                        'known_allergies': cs[5] if cs[5] != "None" else "",
                        'is_allergy_unknown': cs[5] == "None reported" or cs[5] == "None",
                        'current_medications': cs[6],
                        'smoking_history': "NEVER" if idx % 3 != 0 else "FORMER",
                        'alcohol_history': "NONE" if idx % 2 == 0 else "OCCASIONAL",
                        'dietary_habits': "VEGETARIAN" if idx % 2 == 0 else "NON_VEGETARIAN",
                    }
                )

                # Vital Record (create if none exist)
                if not p.vitals.exists():
                    height = Decimal(random.randint(155, 182))
                    weight = Decimal(random.randint(52, 92))
                    sys_bp = random.choice([118, 122, 130, 142, 150, 126, 110])
                    dia_bp = random.choice([76, 80, 84, 90, 94, 78, 70])
                    
                    VitalRecord.objects.create(
                        patient=p,
                        recorded_by=random.choice(nurses),
                        measurement_time=timezone.now() - timedelta(days=random.randint(0, 14), hours=random.randint(1, 8)),
                        temperature_f=Decimal(random.choice([98.4, 98.6, 99.2, 100.4, 101.2, 98.2])),
                        systolic_bp=sys_bp,
                        diastolic_bp=dia_bp,
                        heart_rate=random.randint(68, 104),
                        respiratory_rate=random.randint(14, 22),
                        oxygen_saturation=Decimal(random.randint(95, 99)),
                        height_cm=height,
                        weight_kg=weight,
                        pain_score=random.randint(0, 6),
                        observations="Patient alert, oriented to time, place and person. Intake vitals verified."
                    )

            self.stdout.write(self.style.SUCCESS("[OK] Medical Histories and Vital Records verified / generated."))

            # 5. 16 Appointments (Idempotent: check if slot or appointment already exists)
            appointments = []
            today = timezone.localdate()
            for idx in range(16):
                p = patients[idx % len(patients)]
                d = doctors[idx % len(doctors)]
                # Some past, some today, some upcoming
                day_offset = idx - 8  # from -8 to +7 days
                apt_date = today + timedelta(days=day_offset)
                # Assign unique hour per doctor per day to guarantee no slot overlap
                apt_time = time(hour=9 + (idx % 7), minute=0 if (idx // 7) % 2 == 0 else 30)
                
                status = Appointment.Status.COMPLETED if day_offset < 0 else (Appointment.Status.CONFIRMED if day_offset >= 0 else Appointment.Status.PENDING)
                if idx == 14:
                    status = Appointment.Status.CANCELLED
                elif idx == 15:
                    status = Appointment.Status.PENDING

                # Check if doctor already has an appointment at this time
                existing_apt = Appointment.objects.filter(
                    doctor=d,
                    appointment_date=apt_date,
                    appointment_time=apt_time
                ).first()

                if not existing_apt:
                    apt = Appointment.objects.create(
                        patient=p,
                        doctor=d,
                        appointment_date=apt_date,
                        appointment_time=apt_time,
                        reason=f"Clinical evaluation for {random.choice(['Fever & chills', 'Routine blood pressure check', 'Chest discomfort', 'Persistent cough', 'Follow-up visit'])}",
                        status=status,
                        booked_by=random.choice(receptionists),
                        cancellation_reason="Patient requested rescheduling due to personal travel" if status == Appointment.Status.CANCELLED else ""
                    )
                    appointments.append(apt)
                else:
                    appointments.append(existing_apt)

            self.stdout.write(self.style.SUCCESS(f"[OK] {len(appointments)} Appointments verified / scheduled."))

            # 6. 18 Realistic Consultations (Draft & Finalized)
            med_catalog = [
                ("Paracetamol 650mg", "TABLET", "650 mg", "1-0-1 (Twice daily)", "AFTER_MEALS", "3 days", "Take with warm water if temp > 99 F"),
                ("Amoxicillin + Clavulanic Acid 625mg", "TABLET", "625 mg", "1-0-1 (Twice daily)", "AFTER_MEALS", "5 days", "Complete full antibiotic course"),
                ("Azithromycin 500mg", "TABLET", "500 mg", "1-0-0 (Once daily)", "BEFORE_MEALS", "3 days", "Take 1 hour before breakfast"),
                ("Telmisartan 40mg", "TABLET", "40 mg", "1-0-0 (Morning)", "AFTER_MEALS", "30 days", "Monitor blood pressure weekly"),
                ("Atorvastatin 10mg", "TABLET", "10 mg", "0-0-1 (Bedtime)", "BEDTIME", "30 days", "Take at night"),
                ("Pantoprazole 40mg", "TABLET", "40 mg", "1-0-0 (Empty stomach)", "EMPTY_STOMACH", "14 days", "Take 30 mins before breakfast"),
                ("Levocetirizine 5mg", "TABLET", "5 mg", "0-0-1 (Night)", "AFTER_MEALS", "5 days", "May cause mild drowsiness"),
                ("Cough Expectorant (Ambroxol)", "SYRUP", "10 ml", "1-1-1 (Thrice daily)", "AFTER_MEALS", "5 days", "Shake well before use"),
            ]

            clinical_cases = [
                (
                    "Acute Upper Respiratory Tract Infection (URTI) with Acute Bronchitis",
                    "J20.9 - Acute Bronchitis, unspecified",
                    "Fever, dry irritative cough, throat pain",
                    "Patient presented with throat irritation 3 days back followed by low-grade fever and cough.",
                    "Chest: Bilateral vesicular breath sounds heard, few rhonchi on right middle zone. CVS: S1/S2 audible, no murmurs.",
                    "Hydration, steam inhalation twice daily, oral antibiotics and symptomatic relief.",
                    "CBC, ESR, Chest X-Ray PA view if symptoms persist beyond 4 days."
                ),
                (
                    "Essential Hypertension Stage 1 (Poorly Controlled)",
                    "I10 - Essential (primary) hypertension",
                    "Occasional occipital headache, fatigue, dizziness",
                    "History of high blood pressure for 3 years; irregular medication compliance.",
                    "BP today: 154/96 mmHg. Heart: Regular rate, no S3/S4. Lungs: Clear. No pedal edema.",
                    "Optimize antihypertensive dosage, strict salt restriction (< 5g/day), daily brisk walking for 35 mins.",
                    "Lipid Profile, Serum Creatinine, Urine microalbumin, 12-lead ECG."
                ),
                (
                    "Acute Gastroenteritis with Mild Dehydration",
                    "A09 - Infectious gastroenteritis and colitis",
                    "Watery stools (4-5 episodes), diffuse abdominal cramps, mild nausea",
                    "Ate street food 24 hours back; vomiting stopped, frequent loose stools persist.",
                    "Abdomen soft, diffuse mild epigastric tenderness, no guarding or rigidity. Bowel sounds exaggerated.",
                    "Oral Rehydration Salts (ORS) 200ml after each loose stool, probiotics, light khichdi diet.",
                    "Stool Routine and Microscopy, Serum Electrolytes."
                ),
                (
                    "Type 2 Diabetes Mellitus with Peripheral Neuropathy symptoms",
                    "E11.9 - Type 2 diabetes mellitus without complications",
                    "Burning sensation in bilateral soles, increased thirst, polyuria",
                    "Known diabetic for 6 years on single oral hypoglycemic agent. Last HbA1c 8.4%.",
                    "Foot exam: Diminished vibration sense at great toes, monofilament 8/10 bilaterally. Pulses palpable.",
                    "Dual anti-diabetic therapy, diabetic foot care education, dietary glycemic control.",
                    "Fasting & Postprandial Blood Sugar, HbA1c, Urine Routine, Fundus Examination."
                ),
                (
                    "Chronic Stable Angina — Under Diagnostic Workup",
                    "I20.9 - Angina pectoris, unspecified",
                    "Retro-sternal heaviness on climbing stairs, relieved with 5 minutes rest",
                    "Symptoms noticed for past 3 weeks. No pain at complete rest. No syncope.",
                    "BP: 136/84 mmHg, HR: 74 bpm. Normal heart sounds. No carotid bruits.",
                    "Statin therapy, antiplatelet therapy, avoidance of sudden strenuous exertion.",
                    "Treadmill Test (TMT), 2D Echocardiography, Troponin-I stat, Fasting Lipid Panel."
                )
            ]

            year = timezone.now().strftime('%Y')
            consultations = []
            for idx in range(18):
                p = patients[idx % len(patients)]
                d = doctors[idx % len(doctors)]
                case = clinical_cases[idx % len(clinical_cases)]
                apt = appointments[idx] if idx < len(appointments) else None

                con_id = f"CON-{year}-{idx+1:04d}"
                existing_con = Consultation.objects.filter(consultation_id=con_id).first()

                if not existing_con:
                    is_final = (idx < 15)  # 15 finalized, 3 active drafts for demonstration
                    con_status = Consultation.Status.COMPLETED if is_final else Consultation.Status.IN_PROGRESS

                    con = Consultation.objects.create(
                        consultation_id=con_id,
                        patient=p,
                        doctor=d,
                        appointment=apt,
                        status=con_status,
                        chief_complaints=case[2],
                        history_of_present_illness=case[3],
                        past_history_summary="Relevant chronic medical records and previous prescriptions reviewed.",
                        general_examination="Patient conscious, oriented, no severe distress. No pallor, icterus, cyanosis, clubbing, lymphadenopathy or edema.",
                        systemic_examination=case[4],
                        clinical_observations="Case categorized as moderate severity. Standard clinical care protocol applied.",
                        provisional_diagnosis=case[0],
                        final_diagnosis=case[1] if is_final else "",
                        treatment_plan=case[5],
                        recommended_investigations=case[6],
                        dietary_lifestyle_advice="Low sodium, avoid outside processed foods, adequate hydration, regular sleep schedule.",
                        follow_up_date=today + timedelta(days=7),
                        doctor_private_notes="Patient reassured. Advised to report to emergency if red flag symptoms appear.",
                        is_finalized=is_final,
                        finalized_at=timezone.now() - timedelta(days=15-idx) if is_final else None,
                        finalized_by=d if is_final else None
                    )

                    # Prescription
                    rx = Prescription.objects.create(
                        consultation=con,
                        patient=p,
                        doctor=d,
                        general_advice="Follow medicine schedule strictly. Return for review on follow-up date."
                    )

                    # Add 2-3 items
                    items_to_add = random.sample(med_catalog, random.randint(2, 4))
                    for itm in items_to_add:
                        PrescriptionItem.objects.create(
                            prescription=rx,
                            medicine_name=itm[0],
                            dosage_form=itm[1],
                            strength_dosage=itm[2],
                            frequency=itm[3],
                            timing=itm[4],
                            duration=itm[5],
                            instructions=itm[6]
                        )

                    # Add an Amendment to at least 2 finalized consultations to demonstrate the audit feature
                    if idx in [1, 4]:
                        ConsultationAmendment.objects.create(
                            consultation=con,
                            author=d,
                            amendment_note="Follow-up note: Laboratory reports reviewed. CBC showed mild leukocytosis resolving with therapy. Continue prescribed medication as advised."
                        )
                    consultations.append(con)
                else:
                    consultations.append(existing_con)

            self.stdout.write(self.style.SUCCESS(f"[OK] {len(consultations)} Consultations verified / ready."))

            # 7. Audit Log Events (Idempotent)
            if not AuditLog.objects.filter(description__contains="Administrator logged into healthcare administrative terminal.").exists():
                AuditLog.objects.create(
                    user=admin_user,
                    action=AuditLog.Action.LOGIN,
                    record_type="User",
                    record_id=str(admin_user.id),
                    description="Administrator logged into healthcare administrative terminal.",
                    ip_address="127.0.0.1"
                )
            if not AuditLog.objects.filter(description__contains="finalized and locked clinical case CON-2026-0001.").exists():
                AuditLog.objects.create(
                    user=doctors[0],
                    action=AuditLog.Action.CONSULTATION_FINALIZE,
                    record_type="Consultation",
                    record_id="CON-2026-0001",
                    description="Physician Dr. Rajesh Sharma finalized and locked clinical case CON-2026-0001.",
                    ip_address="127.0.0.1"
                )

            self.stdout.write(self.style.SUCCESS("[OK] Audit Log entries verified."))

        self.stdout.write(self.style.SUCCESS("\n======================================================="))
        self.stdout.write(self.style.SUCCESS("  SIH 2026 DEMO DATABASE SEEDED SUCCESSFULLY!"))
        self.stdout.write(self.style.SUCCESS("======================================================="))
        self.stdout.write("Credentials for Smart India Hackathon Demonstration:")
        self.stdout.write("  - Super Admin:   admin         / password123")
        self.stdout.write("  - Doctor:        dr.sharma     / password123")
        self.stdout.write("  - Doctor:        dr.anita      / password123")
        self.stdout.write("  - Doctor:        dr.vikram     / password123")
        self.stdout.write("  - Receptionist:  priya.rec     / password123")
        self.stdout.write("  - Receptionist:  amit.rec      / password123")
        self.stdout.write("  - Nurse:         nurse.sunita  / password123")
        self.stdout.write("  - Nurse:         nurse.kavita  / password123")
        self.stdout.write("=======================================================\n")
