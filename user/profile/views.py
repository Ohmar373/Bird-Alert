from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import UserForm, ProfileForm


@login_required
def edit_profile(request):
    try:
        profile = request.user.profile
    except Exception:
        profile = None

    password_form = None

    if request.method == 'POST':
        u_form = UserForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=profile)
        password_form = PasswordChangeForm(user=request.user, data=request.POST)

        # profile/username update
        if 'save_profile' in request.POST:
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('profile:edit')

        # password change
        if 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')
                return redirect('profile:edit')
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        u_form = UserForm(instance=request.user)
        p_form = ProfileForm(instance=profile)
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'user/profile_edit.html', {
        'u_form': u_form,
        'p_form': p_form,
        'password_form': password_form,
    })
