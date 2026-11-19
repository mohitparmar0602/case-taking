from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from .models import User


def role_required(*allowed_roles):
    """
    Decorator for views that checks whether a user has one of the allowed roles.
    Admins / superusers are granted access if Role.ADMIN is included or explicitly allowed.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            # Superusers always have admin access
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            messages.error(
                request,
                f"Access denied. Your role ({request.user.get_role_display()}) is not authorized to access this resource."
            )
            return redirect('core:unauthorized')
        return _wrapped_view
    return decorator


def admin_required(view_func):
    return role_required(User.Role.ADMIN)(view_func)


def doctor_required(view_func):
    return role_required(User.Role.DOCTOR, User.Role.ADMIN)(view_func)


def receptionist_required(view_func):
    return role_required(User.Role.RECEPTIONIST, User.Role.ADMIN)(view_func)


def nurse_required(view_func):
    return role_required(User.Role.NURSE, User.Role.ADMIN)(view_func)


def clinical_staff_required(view_func):
    """Accessible by Doctors, Nurses, and Admin"""
    return role_required(User.Role.DOCTOR, User.Role.NURSE, User.Role.ADMIN)(view_func)


def registration_staff_required(view_func):
    """Accessible by Receptionists and Admin (Doctors cannot register or edit patients)"""
    return role_required(User.Role.RECEPTIONIST, User.Role.ADMIN)(view_func)


def patient_directory_required(view_func):
    """Accessible by Receptionists, Nurses, and Admin (Doctors cannot access patient directory)"""
    return role_required(User.Role.RECEPTIONIST, User.Role.NURSE, User.Role.ADMIN)(view_func)


class RoleRequiredMixin(AccessMixin):
    """CBV mixin that verifies user has one of the allowed roles."""
    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.is_superuser or request.user.role in self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)

        messages.error(
            request,
            f"Access denied. Your role ({request.user.get_role_display()}) does not possess authorization for this area."
        )
        return redirect('core:unauthorized')


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = (User.Role.ADMIN,)


class DoctorRequiredMixin(RoleRequiredMixin):
    allowed_roles = (User.Role.DOCTOR, User.Role.ADMIN)


class ClinicalStaffMixin(RoleRequiredMixin):
    allowed_roles = (User.Role.DOCTOR, User.Role.NURSE, User.Role.ADMIN)
