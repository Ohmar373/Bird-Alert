from django.urls import path
from . import views

app_name = 'sightings'

urlpatterns = [
    path('add/', views.add_sighting, name='add_sighting'),
    path('sighting-form/', views.sighting_form, name='sighting_form'),
    path('sighting-form/submit/', views.sighting_form, name='add_sighting_details'),
    path('<int:sighting_id>/delete/', views.delete_sighting, name='delete_sighting'),
    path('api/search-birds/', views.search_birds, name='search_birds'),
    path('api/bird-categories/', views.bird_categories, name='bird_categories'),
]