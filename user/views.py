from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count, Exists, OuterRef, Value
from django.shortcuts import redirect, render
from django.template.loader import get_template

from sightings.models import Like, Sighting

from .forms import UserRegisterForm


# index view
def index(request):
    qs = Sighting.objects.select_related("bird_species", "user", "user__profile").order_by("-timestamp")
    qs = qs.annotate(like_count=Count("like"))

    if request.user.is_authenticated:
        liked_subquery = Like.objects.filter(user=request.user, sighting=OuterRef("pk"))
        qs = qs.annotate(liked=Exists(liked_subquery))
    else:
        qs = qs.annotate(liked=Value(False))

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
            subject, from_email, to = "Welcome to Bird Alert!", "birdalert2026@gmail.com", email
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
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {username}!!")
            return redirect("index")

        messages.info(request, "Username OR password is incorrect")

    form = AuthenticationForm()
    return render(request, "user/login.html", {"form": form, "title": "Login Here"})


# sightings view
@login_required
def sightings(request):
    return render(request, "user/sightings.html")
