from .models import InstitutionSettings
from accounts.models import User


def institution_settings(request):
    try:
        settings = InstitutionSettings.get_settings()
    except Exception:
        settings = None

    try:
        doctors = User.objects.filter(role=User.Role.DOCTOR, is_active=True).select_related('profile')
    except Exception:
        doctors = []

    return {
        'institution': settings,
        'doctors': doctors,
    }

