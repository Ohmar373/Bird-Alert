from django.contrib import admin
from .models import BirdSpecies, Sighting, SightingReport

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
    inlines = []


class SightingReportInline(admin.TabularInline):
    model = SightingReport
    extra = 0
    can_delete = False
    fields = ('reporting_user', 'reason', 'description', 'timestamp', 'resolved')
    readonly_fields = ('reporting_user', 'reason', 'description', 'timestamp', 'resolved')
    show_change_link = True


SightingAdmin.inlines = [SightingReportInline]

@admin.register(SightingReport)
class SightingReportAdmin(admin.ModelAdmin):
    list_display = ('sighting_summary', 'reporting_user', 'reason', 'timestamp', 'resolved')
    list_editable = ('resolved',)
    list_filter = ('resolved', 'reason', 'timestamp')
    search_fields = ('description', 'reporting_user__username', 'sighting__bird_species__common_name', 'sighting__user__username')
    list_select_related = ('sighting__bird_species', 'reporting_user')
    readonly_fields = ('timestamp',)

    @admin.display(description='Sighting')
    def sighting_summary(self, obj):
        return f"{obj.sighting.bird_species.common_name} by {obj.sighting.user.username}"
