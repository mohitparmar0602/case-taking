def auth_roles(request):
    """
    Context processor to make user role flags easily accessible in templates.
    """
    user = request.user
    if not user.is_authenticated:
        return {
            'is_admin': False,
            'is_doctor': False,
            'is_receptionist': False,
            'is_nurse': False,
            'user_role': None,
        }
    
    return {
        'is_admin': user.is_admin_user,
        'is_doctor': user.is_doctor_user,
        'is_receptionist': user.is_receptionist_user,
        'is_nurse': user.is_nurse_user,
        'user_role': user.role,
        'user_role_label': user.get_role_display(),
    }
