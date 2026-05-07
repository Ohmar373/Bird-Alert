from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from sightings.models import Bookmark, Comment, Like, Sighting

from .forms import UserForm, ProfileForm
from .models import Profile


def _build_profile_context(profile_user):
    profile, _ = Profile.objects.get_or_create(user=profile_user)

    sightings = (
        Sighting.objects.filter(user=profile_user)
        .select_related("bird_species")
        .annotate(
            like_count=Count("like", distinct=True),
            comment_count=Count("comment", distinct=True),
        )
        .order_by("-timestamp")
    )

    stats = {
        "post_count": sightings.count(),
        "species_count": sightings.values("bird_species_id").distinct().count(),
        "likes_received": Like.objects.filter(sighting__user=profile_user).count(),
        "comments_received": Comment.objects.filter(sighting__user=profile_user).count(),
    }

    bookmarked_sightings = Sighting.objects.none()
    if profile_user.is_authenticated:
        bookmarked_sightings = (
            Sighting.objects.filter(bookmark__user=profile_user)
            .select_related("bird_species", "user")
            .annotate(
                like_count=Count("like", distinct=True),
                comment_count=Count("comment", distinct=True),
            )
            .order_by("-bookmark__timestamp")
        )
        stats["bookmark_count"] = bookmarked_sightings.count()

    return {
        "profile": profile,
        "profile_user": profile_user,
        "sightings": sightings,
        "bookmarked_sightings": bookmarked_sightings,
        "stats": stats,
    }


@login_required
def profile_view(request):
    context = _build_profile_context(request.user)
    context["is_owner"] = True
    return render(request, "user/profile.html", context)


@login_required
def user_profile_view(request, username):
    user_model = get_user_model()
    profile_user = get_object_or_404(user_model, username__iexact=username)

    if profile_user == request.user:
        return redirect("profile:view")

    context = _build_profile_context(profile_user)
    context["is_owner"] = False
    return render(request, "user/profile.html", context)


@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

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
                return redirect('profile:view')

        # password change
        if 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')
                return redirect('profile:view')
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
