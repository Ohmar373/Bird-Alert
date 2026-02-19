from django.urls import path, include
from django.conf import settings
from . import views
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from sightings import views as sightings_views


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.Login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='user/index.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('add-sighting/', sightings_views.add_sighting, name='add_sighting'),
    path('sightings/', views.sightings, name='sightings'),
    path('profile/', include(('user.profile.urls', 'profile'), namespace='profile')),

    # Password reset flow
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='user/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'),
         name='password_reset_complete'),
]