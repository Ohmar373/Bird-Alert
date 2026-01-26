from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render

# Create your views here.

# index view
def index(request):
    return render(request, 'user/index.html', {'title': 'index'})

# register view
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            # mailing functionality
            htmly = get_template('user/Email.html')
            d = {'username': username}
            subject, from_email, to = 'Welcome to Bird Alert!', 'birdalert2026@gmail.com', email
            html_content = htmly.render(d)
            text_content = f'Account created for {username} you can now log in.'
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form, 'title': 'Register Here'})

# login view
def Login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            form = login(request, user)
            messages.success(request, f'Welcome {username}!!')
            return redirect('index')
        else:
            messages.info(request, f'Username OR password is incorrect')
        form = AuthenticationForm()
        return render(request, 'user/login.html', {'form': form, 'title': 'Login Here'})
    else:
        form = AuthenticationForm()
        return render(request, 'user/login.html', {'form': form, 'title': 'Login Here'})

# map view
def map_view(request):
    return render(request, "user/map.html")
