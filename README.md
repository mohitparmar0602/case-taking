# Patient Case-Taking Software
## Smart India Hackathon 2026 | Problem Statement ID: SIH26047

A complete, modern, secure, responsive, and fully functional digital healthcare record-management and clinical case-taking platform developed for **Smart India Hackathon 2026**.

This software replaces traditional paper-based case-taking with a centralized, auditable, and role-governed digital platform. It assists healthcare institutions in registering patients, capturing structured clinical narratives, monitoring longitudinal vital signs, conducting tabbed clinical consultations, issuing prescriptions, managing appointments, and exporting verified medical summaries.

> **Clinical Governance Notice:** The application is designed for clinical documentation and administrative healthcare management. It strictly does not provide unverified automated diagnoses or algorithmic prescribing.

---

## 1. System Architecture & Tech Stack

- **Backend Framework:** Django 6.1+ (Python 3.14 / 3.x)
- **Database:** SQLite (development / local demo) / PostgreSQL-ready ORM
- **Authentication & RBAC:** Django Session-Based Authentication with Custom User Model (`accounts.User`) & granular Role-Based Access Control
- **Frontend & UI/UX:** HTML5, CSS3, JavaScript, Bootstrap 5.3, Bootstrap Icons 1.11, Chart.js 4.4
- **PDF Engine:** ReportLab 5.1 (generating professional institutional consultation summaries & executive operational reports)
- **Data Export:** Built-in Python CSV writer & OpenPyXL

### Modular Django Application Layout
```
patient_care/            # Project core configuration (settings, root URLs, wsgi)
├── accounts/            # Custom User, StaffProfile, RBAC decorators & mixins
├── core/                # InstitutionSettings, dynamic dashboards, router
├── patients/            # Patient demographics, auto ID (PAT-YYYY-XXXX), search
├── medical_records/     # Structured medical histories (Sections A-H) & Vitals intake
├── consultations/       # Digital case-taking, finalization locks, amendments, PDF engine
├── prescriptions/       # Prescription & PrescriptionItem formset management
├── appointments/        # Clinic scheduling, conflict prevention, calendar agenda
├── documents/           # Medical document repository with permission-checked downloads
├── audit/               # Immutable security audit trail & administrative viewer
├── reports/             # Operational analytics, demographic charts, CSV & PDF reports
├── static/              # Healthcare SaaS CSS styling, custom JS (live BMI calculation)
└── templates/           # Bootstrap 5 responsive templates with reusable includes
```

---

## 2. Role-Based Access Control (RBAC) Matrix

| Capability / Resource | Super Admin | Doctor | Receptionist | Nurse |
|:---|:---:|:---:|:---:|:---:|
| **Executive Dashboard & KPIs** | Yes | Role View | Role View | Role View |
| **Patient Registration & Demographics** | Yes | Yes | Yes | Read-Only |
| **Schedule & Manage Appointments** | Yes | View / Update | Yes | View Queue |
| **Record Vital Signs & Measurements** | Yes | Yes | No | Yes |
| **Record Medical History (HPI/Past/Allergy)** | Yes | Yes | No | Yes |
| **Start Clinical Case-Taking Consultation** | Yes | Yes | No | No |
| **Prescribe Medications (Rx)** | Yes | Yes | No | No |
| **Finalize & Lock Consultation Records** | Yes | Yes | No | No |
| **Append Audited Post-Lock Addenda** | Yes | Yes | No | No |
| **Upload / Download Medical Test Documents** | Yes | Yes | Restrict Download | Yes |
| **Hospital Staff & User Account Management** | Yes | No | No | No |
| **Analytics, CSV & PDF Reports Export** | Yes | No | No | No |
| **System Audit Trail Logs** | Yes | No | No | No |

---

## 3. Implemented Modules

1. **Authentication & User Management:** Custom user model supporting 4 distinct hospital roles, secure session management, profile updating, and administrative account toggling.
2. **Dynamic Dashboards:** Dynamic calculations directly from ORM for all 4 roles. Live 7-day intake activity charts via Chart.js.
3. **Patient Registration:** Unique auto-generated Patient IDs (`PAT-YYYY-XXXX`), duplicate detection, calculated age, blood group badges, emergency contact details.
4. **Structured Medical History:** Comprehensive 8-section capture (Chief Complaints, HPI narrative, Past Medical, Past Surgical, Family History, Personal/Social Habits, Allergies, Routine Medications).
5. **Vital Signs Management:** Intake logging for BP, Pulse, Temp, SpO2, Resp Rate, Height, Weight, Pain Scale (0-10), and client/server auto-computed BMI. Trend charts over time.
6. **Consultation & Case-Taking (Core Module):** Tabbed clinical workflow (Presentation, Examination, Diagnosis, Prescription, Private Notes). Finalization lock mechanism preventing silent overwrites and supporting audited amendments.
7. **Appointment Scheduling:** Doctor conflict detection (prevents overlapping bookings), daily & weekly agenda calendar.
8. **Comprehensive Patient Profile:** 9 distinct tabs (Overview, Personal Info, Medical History, Vitals, Consultations, Diagnoses, Prescriptions, Appointments, Documents) plus an activity timeline.
9. **Document Repository:** Secure upload of lab test reports, radiology, and scans. Protected download view validating role permissions.
10. **System Audit Trail:** Automated event logging capturing actors, IP addresses, target records, and descriptions.
11. **Reporting & Analytics:** Date-range and doctor filters, gender and doctor workload charts, CSV data exports, and ReportLab executive PDF summaries.

---

## 4. Quick Demonstration Credentials

All fictional test accounts are configured with the development password: **`password123`**

| Role | Username | Password | Full Name & Title |
|:---|:---|:---|:---|
| **Super Admin** | `admin` | `password123` | Super Admin (Healthcare Administration) |
| **Doctor** | `dr.sharma` | `password123` | Dr. Rajesh Sharma, MD (General Medicine) |
| **Doctor** | `dr.anita` | `password123` | Dr. Anita Verma, DM (Cardiology) |
| **Doctor** | `dr.vikram` | `password123` | Dr. Vikram Malhotra, MD (Pulmonology) |
| **Receptionist** | `priya.rec` | `password123` | Priya Nair (Central OPD Reception) |
| **Receptionist** | `amit.rec` | `password123` | Amit Singh (Emergency Intake Desk) |
| **Nurse** | `nurse.sunita` | `password123` | Sunita Devi, RN (OPD Triage Station) |
| **Nurse** | `nurse.kavita` | `password123` | Kavita Patil, RN (Clinical Vitals Station) |

---

## 5. SIH 2026 End-to-End Live Demonstration Workflow

To demonstrate the full clinical lifecycle during the SIH evaluation:

### Step 1 — Receptionist (`priya.rec`)
1. Log in to the terminal as `priya.rec`.
2. Navigate to **Register Patient**. Enter details for a walk-in patient (e.g., "Arun Kumar", 34 yrs, B+).
3. The platform validates against duplicates, generates an ID (e.g., `PAT-2026-0023`), and redirects to the patient profile.
4. Click **Book Appointment** and schedule a consultation slot with `dr.sharma`.

### Step 2 — Nurse (`nurse.sunita`)
1. Log in as `nurse.sunita`. Open the **Nursing Intake Station**.
2. Locate the patient in the queue and click **Record Vitals**.
3. Input BP (e.g., `130/85`), Pulse (`78`), Temp (`99.1`), SpO2 (`98%`), Height (`172 cm`), and Weight (`70 kg`).
4. Notice the live BMI auto-calculation (`23.66 - Normal`). Save the record.

### Step 3 — Doctor (`dr.sharma`)
1. Log in as `dr.sharma`. The physician dashboard displays today's appointment queue and active drafts.
2. Click **Examine / Consult** for the patient.
3. Review the patient's vitals and allergy alerts in the right-hand reference sidebar.
4. Fill in the tabbed consultation sheet:
   - **History:** Chief complaint and narrative.
   - **Examination:** General and systemic findings.
   - **Diagnosis:** Provisional and confirmed diagnoses.
   - **Rx:** Add prescribed medications via the inline prescription form.
5. Click **Finalize & Sign Case Record**. The case sheet is locked with a cryptographic status badge.

### Step 4 — Clinical Summary & Reports
1. On the finalized case sheet, click **Download PDF Report** to view the ReportLab-generated medical case summary.
2. Try amending the finalized case by adding an audited clinical addendum.

### Step 5 — Super Administrator (`admin`)
1. Log in as `admin`.
2. Review the hospital KPI metrics, 7-day intake charts, and real-time operational feeds.
3. Open **System Audit Trail** to view the tamper-evident log of all clinical actions.
4. Open **Analytics & Reports** to download CSV exports or generate the Executive Summary PDF.

---

## 6. Setup & Execution Commands

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Pip

### 1. Install Dependencies
```bash
python -m pip install django pillow reportlab openpyxl
```

### 2. Apply Database Migrations
```bash
python manage.py migrate
```

### 3. Seed Realistic Demonstration Data
Populates 1 Super Admin, 3 Doctors, 2 Receptionists, 2 Nurses, 22 Patients, Vitals, Histories, 16 Appointments, and 18 Consultations:
```bash
python manage.py seed_demo_data
```

### 4. Run the Automated Test Suite
Executes 25 comprehensive tests across authentication, RBAC, clinical case finalization, vitals, scheduling, and reports:
```bash
python manage.py test
```

### 5. Start the Development Server
```bash
python manage.py runserver
```
Access the application at `http://127.0.0.1:8000/`.
