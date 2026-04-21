from django.urls import path
from . import views

app_name = 'profile'

urlpatterns = [
    path('', views.profile_view, name='view'),
    path('edit/', views.edit_profile, name='edit'),
    path('<str:username>/', views.user_profile_view, name='user'),
]
