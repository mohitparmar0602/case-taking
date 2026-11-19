# PythonAnywhere Deployment Guide
## Patient Case-Taking Software (Carevia Healthcare)
### SIH 2026 (SIH26047) · INT253 Academic Project

Follow these exact steps to host this Django project on [PythonAnywhere](https://www.pythonanywhere.com/) (Free or Paid tier).

---

## Prerequisites
1. A **PythonAnywhere account** ([Sign up here](https://www.pythonanywhere.com/registration/register/beginner/)).
   - Your site URL will be: `https://<your-username>.pythonanywhere.com`
2. Your project pushed to a Git repository (e.g. GitHub) **OR** zipped as an archive.

---

## Step 1: Open a Bash Console on PythonAnywhere
1. Log in to your PythonAnywhere dashboard.
2. In the **Consoles** tab, click **Bash** under "Start a new console".

---

## Step 2: Clone or Upload Your Project
In the Bash console, clone your repository into your home directory:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL> django-carevia
cd django-carevia
```

*(Note: If you uploaded a `.zip` file via the Files tab, run `unzip django.zip -d django-carevia` and `cd django-carevia`)*

---

## Step 3: Create & Activate Virtual Environment
Use PythonAnywhere's `virtualenvwrapper` to create an isolated Python 3.11 or 3.12 environment:

```bash
mkvirtualenv --python=python3.11 carevia-env
```

Install all required project dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 4: Run Migrations, Seed Demo Data & Collect Static Files
While still inside `~/django-carevia` with the virtualenv active:

```bash
# 1. Apply database migrations
python manage.py migrate

# 2. Seed pre-configured clinical roles and demo data
python manage.py seed_demo_data

# 3. Collect static files for web server delivery
python manage.py collectstatic --noinput
```

---

## Step 5: Configure the Web App on PythonAnywhere
1. Go to the **Web** tab in your PythonAnywhere dashboard.
2. Click **"Add a new web app"**.
3. When prompted:
   - Click **Next** on the domain name screen (`<your-username>.pythonanywhere.com`).
   - Select **"Manual configuration"** *(Do NOT select "Django", as manual configuration allows you to connect your existing code and virtualenv directly)*.
   - Choose **Python 3.11** (matching your virtualenv).
   - Click **Next**.

---

## Step 6: Configure Paths & Virtualenv
On your Web tab configuration page, configure the following:

### 1. Code Section
- **Source code:** `/home/<your-username>/django-carevia`
- **Working directory:** `/home/<your-username>/django-carevia`

### 2. Virtualenv Section
- Enter the path to your created virtual environment:
  `/home/<your-username>/.virtualenvs/carevia-env`
  *(Click the blue checkmark to save)*

### 3. Static Files Section
Add two URL-to-Directory mappings:

| URL | Directory |
| :--- | :--- |
| `/static/` | `/home/<your-username>/django-carevia/staticfiles` |
| `/media/` | `/home/<your-username>/django-carevia/media` |

---

## Step 7: Configure the WSGI File
1. Under the **Code** section on the Web tab, click the link to edit the **WSGI configuration file**:
   `/var/www/<your-username>_pythonanywhere_com_wsgi.py`
2. Delete everything inside the file and replace it with:

```python
import os
import sys

# Replace <your-username> with your actual PythonAnywhere username:
path = '/home/<your-username>/django-carevia'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'patient_care.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

3. Click the **Save** button in the top right.

---

## Step 8: Reload & Access Your Live Application
1. Return to the **Web** tab.
2. Click the green button: **"Reload <your-username>.pythonanywhere.com"**.
3. Open `https://<your-username>.pythonanywhere.com` in your browser!

---

## Pre-Configured Demo Credentials

All test accounts use the password: **`password123`**

| Role | Username | Password | Workstation Function |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin` | `password123` | Institutional settings, staff management, audit trail |
| **Doctor** | `dr.sharma` | `password123` | Clinical case-taking chamber, Rx pad, PDF discharge |
| **Doctor** | `dr.anita` | `password123` | Clinical examination & vitals telemetry review |
| **Receptionist** | `priya.rec` | `password123` | Patient intake, deterministic PID stamping, queue |
| **Nurse** | `nurse.sunita` | `password123` | Vitals intake, automated BMI calculation, allergy logging |
