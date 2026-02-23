from django.contrib import admin
from .models import BirdSpecies, Sighting

@admin.register(BirdSpecies)
class BirdSpeciesAdmin(admin.ModelAdmin):
    list_display = ('common_name', 'scientific_name', 'category')
    list_filter = ('category',)
    search_fields = ('common_name', 'scientific_name')

@admin.register(Sighting)
class SightingAdmin(admin.ModelAdmin):
    list_display = ('bird_species', 'user', 'location_name', 'timestamp')
    list_filter = ('bird_species__category',)
    search_fields = ('bird_species__common_name', 'user__username')
