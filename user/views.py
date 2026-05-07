from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Count, Exists, OuterRef, Value
from django.shortcuts import redirect, render
from django.template.loader import get_template

from sightings.models import Bookmark, Like, Sighting

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

    return render(
        request,
        "user/index.html",
        {
            "title": "BirdAlert - Discover Birds Together",
            "sightings": qs,
            "total_sightings": total_sightings,
            "total_users": total_users,
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
