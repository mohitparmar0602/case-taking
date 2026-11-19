from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import User, StaffProfile
from .forms import (
    UserLoginForm,
    StaffCreationForm,
    StaffUpdateForm,
    ProfileEditForm,
    CustomPasswordChangeForm,
)
from .permissions import admin_required
from audit.services import log_audit_event
from audit.models import AuditLog


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard_router')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, "This account has been deactivated. Please contact the administrator.")
                return render(request, 'accounts/login.html', {'form': form})
            
            login(request, user)
            log_audit_event(
                request=request,
                user=user,
                action=AuditLog.Action.LOGIN,
                record_type="User",
                record_id=str(user.id),
                description=f"User {user.username} ({user.get_role_display()}) logged in successfully."
            )
            messages.success(request, f"Welcome back, {user.display_title}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('core:dashboard_router')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        user = request.user
        log_audit_event(
            request=request,
            user=user,
            action=AuditLog.Action.LOGOUT,
            record_type="User",
            record_id=str(user.id),
            description=f"User {user.username} logged out."
        )
        logout(request)
        messages.info(request, "You have been securely logged out.")
    return redirect('accounts:login')


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            form = ProfileEditForm(request.POST, instance=user)
            pwd_form = CustomPasswordChangeForm(user=user)
            if form.is_valid():
                form.save()
                log_audit_event(
                    request=request,
                    user=user,
                    action=AuditLog.Action.STAFF_UPDATE,
                    record_type="User",
                    record_id=str(user.id),
                    description="User updated their personal profile details."
                )
                messages.success(request, "Profile information updated successfully.")
                return redirect('accounts:profile')
        elif 'change_password' in request.POST:
            form = ProfileEditForm(instance=user)
            pwd_form = CustomPasswordChangeForm(user=user, data=request.POST)
            if pwd_form.is_valid():
                pwd_user = pwd_form.save()
                update_session_auth_hash(request, pwd_user)
                log_audit_event(
                    request=request,
                    user=user,
                    action=AuditLog.Action.STAFF_UPDATE,
                    record_type="User",
                    record_id=str(user.id),
                    description="User changed their password."
                )
                messages.success(request, "Password changed successfully!")
                return redirect('accounts:profile')
            else:
                messages.error(request, "Please correct the errors in the password form.")
    else:
        form = ProfileEditForm(instance=user)
        pwd_form = CustomPasswordChangeForm(user=user)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'pwd_form': pwd_form,
        'staff_profile': getattr(user, 'profile', None),
    })


@admin_required
def staff_list_view(request):
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '').strip()

    staff_qs = User.objects.select_related('profile').all().order_by('role', 'first_name')

    if role_filter:
        staff_qs = staff_qs.filter(role=role_filter)
    if status_filter == 'active':
        staff_qs = staff_qs.filter(is_active=True)
    elif status_filter == 'inactive':
        staff_qs = staff_qs.filter(is_active=False)
    if query:
        staff_qs = staff_qs.filter(
            first_name__icontains=query
        ) | staff_qs.filter(
            last_name__icontains=query
        ) | staff_qs.filter(
            username__icontains=query
        ) | staff_qs.filter(
            profile__employee_id__icontains=query
        )

    return render(request, 'accounts/staff_list.html', {
        'staff_members': staff_qs,
        'selected_role': role_filter,
        'selected_status': status_filter,
        'query': query,
        'roles': User.Role.choices,
    })


@admin_required
def staff_create_view(request):
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                new_user = form.save()
            log_audit_event(
                request=request,
                user=request.user,
                action=AuditLog.Action.STAFF_UPDATE,
                record_type="User",
                record_id=str(new_user.id),
                description=f"Admin created new staff account: {new_user.username} ({new_user.get_role_display()})."
            )
            messages.success(request, f"Staff account for {new_user.display_title} successfully created.")
            return redirect('accounts:staff_list')
        else:
            messages.error(request, "Failed to create staff account. Please review form errors.")
    else:
        form = StaffCreationForm()

    return render(request, 'accounts/staff_form.html', {
        'form': form,
        'is_edit': False,
    })


@admin_required
def staff_edit_view(request, pk):
    target_user = get_object_or_404(User.objects.select_related('profile'), pk=pk)
    profile, _ = StaffProfile.objects.get_or_create(
        user=target_user,
        defaults={'employee_id': f"EMP-{target_user.id:04d}"}
    )

    if request.method == 'POST':
        form = StaffUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            target_user.first_name = form.cleaned_data['first_name']
            target_user.last_name = form.cleaned_data['last_name']
            target_user.email = form.cleaned_data['email']
            target_user.phone = form.cleaned_data.get('phone', '')
            target_user.role = form.cleaned_data['role']
            target_user.is_active = form.cleaned_data['is_active']
            target_user.save()
            form.save()

            log_audit_event(
                request=request,
                user=request.user,
                action=AuditLog.Action.STAFF_UPDATE,
                record_type="User",
                record_id=str(target_user.id),
                description=f"Admin updated details for staff {target_user.username}."
            )
            messages.success(request, f"Staff details for {target_user.display_title} updated.")
            return redirect('accounts:staff_list')
    else:
        initial_data = {
            'first_name': target_user.first_name,
            'last_name': target_user.last_name,
            'email': target_user.email,
            'phone': target_user.phone,
            'role': target_user.role,
            'is_active': target_user.is_active,
        }
        form = StaffUpdateForm(instance=profile, initial=initial_data)

    return render(request, 'accounts/staff_form.html', {
        'form': form,
        'is_edit': True,
        'target_user': target_user,
    })


@admin_required
def staff_toggle_status_view(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    if target_user == request.user:
        messages.error(request, "You cannot deactivate your own administrative account.")
        return redirect('accounts:staff_list')

    target_user.is_active = not target_user.is_active
    target_user.save()

    status_str = "activated" if target_user.is_active else "deactivated"
    log_audit_event(
        request=request,
        user=request.user,
        action=AuditLog.Action.STAFF_UPDATE,
        record_type="User",
        record_id=str(target_user.id),
        description=f"Staff account {target_user.username} was {status_str}."
    )
    messages.info(request, f"Account for {target_user.display_title} has been {status_str}.")
    return redirect('accounts:staff_list')
