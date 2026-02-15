from django.urls import path
from . import views

app_name = 'profile'

urlpatterns = [
    path('', views.edit_profile, name='edit'),
    path('edit/', views.edit_profile, name='edit'),
]
