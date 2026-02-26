from django.urls import path

from . import views

app_name = "sightings"

urlpatterns = [
    path("discover/", views.discover, name="discover"),
    path("sighting-form/", views.sighting_form, name="sighting_form"),
    path("sighting-form/submit/", views.sighting_form, name="add_sighting_details"),
    path("<int:sighting_id>/delete/", views.delete_sighting, name="delete_sighting"),
    path("api/search-birds/", views.search_birds, name="search_birds"),
    path("api/bird-categories/", views.bird_categories, name="bird_categories"),
    path("api/list-birds/", views.list_birds, name="list_birds"),
    path("api/search-sightings/", views.search_sightings, name="search_sightings"),
    path("api/like/<int:sighting_id>/", views.like_sighting, name="like_sighting"),
    path("api/comments/<int:sighting_id>/", views.get_comments, name="get_comments"),
    path("api/add-comment/<int:sighting_id>/", views.add_comment, name="add_comment"),
]
