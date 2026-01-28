from django.urls import path
from . import views

app_name = 'sightings'

urlpatterns = [
    path('add/', views.add_sighting, name='add_sighting'),
    path('sighting-form/', views.sighting_form, name='sighting_form'),
    path('sighting-form/submit/', views.add_sighting_details, name = 'add_sighting_details'),
]