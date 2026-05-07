from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Count, Exists, Min, OuterRef, Value
from django.shortcuts import redirect, render
from django.template.loader import get_template
from django.utils import timezone

from sightings.models import Bookmark, BirdSpecies, Like, Sighting

from .forms import ForgotUsernameForm, UserRegisterForm


# index view
def index(request):
    qs = Sighting.objects.select_related("bird_species", "user", "user__profile").order_by("-timestamp")
    qs = qs.annotate(like_count=Count("like"))

    if request.user.is_authenticated:
        liked_subquery = Like.objects.filter(user=request.user, sighting=OuterRef("pk"))
        bookmarked_subquery = Bookmark.objects.filter(user=request.user, sighting=OuterRef("pk"))
        qs = qs.annotate(liked=Exists(liked_subquery), bookmarked=Exists(bookmarked_subquery))
    else:
        qs = qs.annotate(liked=Value(False), bookmarked=Value(False))

    total_sightings = Sighting.objects.count()
    total_users = User.objects.count()

    trending_species = []
    seasonal_birds = []
    birddex_snapshot = None
    current_month_name = timezone.now().strftime('%B')

    if request.user.is_authenticated:
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        current_month = now.month

        # Trending: most-spotted species in last 30 days
        trending_qs = list(
            Sighting.objects
            .filter(timestamp__gte=thirty_days_ago)
            .values('bird_species__id', 'bird_species__common_name', 'bird_species__category')
            .annotate(spotted_count=Count('id'))
            .order_by('-spotted_count')[:5]
        )
        if trending_qs:
            t_ids = [t['bird_species__id'] for t in trending_qs]
            t_images = {}
            for s in (Sighting.objects.filter(bird_species_id__in=t_ids, image__isnull=False)
                      .exclude(image='').select_related('bird_species').order_by('-timestamp')):
                if s.bird_species_id not in t_images:
                    t_images[s.bird_species_id] = s.image.url
            for t in trending_qs:
                t['image_url'] = t_images.get(t['bird_species__id'], '')
        trending_species = trending_qs

        # Seasonal: most-spotted species in current month across all years
        seasonal_qs = list(
            Sighting.objects
            .filter(timestamp__month=current_month)
            .values('bird_species__id', 'bird_species__common_name', 'bird_species__category')
            .annotate(spotted_count=Count('id'))
            .order_by('-spotted_count')[:5]
        )
        if seasonal_qs:
            s_ids = [s['bird_species__id'] for s in seasonal_qs]
            s_images = {}
            for s in (Sighting.objects.filter(bird_species_id__in=s_ids, image__isnull=False)
                      .exclude(image='').select_related('bird_species').order_by('-timestamp')):
                if s.bird_species_id not in s_images:
                    s_images[s.bird_species_id] = s.image.url
            for sp in seasonal_qs:
                sp['image_url'] = s_images.get(sp['bird_species__id'], '')
        seasonal_birds = seasonal_qs

        # BirddEx snapshot for current user
        species_count = (
            Sighting.objects.filter(user=request.user)
            .values('bird_species').distinct().count()
        )
        total_species = BirdSpecies.objects.count()
        recent_finds = list(
            Sighting.objects.filter(user=request.user)
            .values('bird_species__id', 'bird_species__common_name', 'bird_species__category')
            .annotate(first_seen=Min('timestamp'))
            .order_by('-first_seen')[:3]
        )
        birddex_snapshot = {
            'species_count': species_count,
            'total_species': total_species,
            'recent_finds': recent_finds,
        }

    return render(
        request,
        "user/index.html",
        {
            "title": "BirdAlert - Discover Birds Together",
            "sightings": qs,
            "total_sightings": total_sightings,
            "total_users": total_users,
            "trending_species": trending_species,
            "seasonal_birds": seasonal_birds,
            "birddex_snapshot": birddex_snapshot,
            "current_month_name": current_month_name,
        },
    )


# register view
def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")

            # mailing functionality
            htmly = get_template("user/Email.html")
            d = {"username": username}
            subject, from_email, to = "Welcome to Bird Alert!", settings.DEFAULT_FROM_EMAIL, email
            html_content = htmly.render(d)
            text_content = f"Account created for {username} you can now log in."
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            messages.success(request, f"Account created for {username}!")
            return redirect("login")
    else:
        form = UserRegisterForm()

    return render(request, "user/register.html", {"form": form, "title": "Register Here"})


# login view
def Login(request):
    if request.method == "POST":
        identity = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        username = identity
        matched_user = User.objects.filter(email__iexact=identity).only("username").first()
        if not matched_user:
            matched_user = User.objects.filter(username__iexact=identity).only("username").first()
        if matched_user:
            username = matched_user.username

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {user.username}")
            return redirect("index")

        messages.info(request, "Username OR password is incorrect")

    form = AuthenticationForm()
    forgot_username_form = ForgotUsernameForm()
    return render(
        request,
        "user/login.html",
        {"form": form, "forgot_username_form": forgot_username_form, "title": "Login Here"},
    )


def forgot_username(request):
    if request.method != "POST":
        return redirect("login")

    form = ForgotUsernameForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please enter a valid email address.")
        return redirect("login")

    email = form.cleaned_data["email"].strip()

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        messages.error(request, "No account was found with that email.")
        return redirect("login")
    except MultipleObjectsReturned:
        user = User.objects.filter(email__iexact=email).order_by("id").first()

    subject = "Your Bird Alert Username"
    from_email = settings.DEFAULT_FROM_EMAIL
    text_content = f"Your username is: {user.username}"
    html_content = f"<p>Your Bird Alert username is: <strong>{user.username}</strong></p>"

    msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    messages.success(request, "Your username has been sent to your email.")
    return redirect("login")


# sightings view
@login_required
def sightings(request):
    return render(request, "user/sightings.html")
