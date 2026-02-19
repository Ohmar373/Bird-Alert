from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import SightingForm
from sightings import utils
from sightings.utils import get_location_name
from .models import Sighting, BirdSpecies, BIRD_CATEGORY_CHOICES

@login_required
def add_sighting(request):
    return render(request, "sightings/add_sighting.html")

@login_required
def sighting_form(request):
    
    # Get lat/lng from GET or POST
    lat = request.GET.get('lat') or request.POST.get('latitude')
    lng = request.GET.get('lng') or request.POST.get('longitude')
  
    if request.method == "POST":
        form = SightingForm(request.POST, request.FILES)
        if form.is_valid():
            sighting = form.save(commit=False)
            sighting.user = request.user
            sighting.location_name = utils.get_location_name(sighting.latitude, sighting.longitude)
            sighting.save()
            
            return redirect("index")
    else:
        initial_data = {}
        if lat and lng:
            try:
                initial_data = {
                    'latitude': float(lat),
                    'longitude': float(lng),
                }
            except (ValueError, TypeError):
                pass
        
        form = SightingForm(initial=initial_data)
    
    return render(request, "sightings/sighting-form.html", {
        "form": form,
        "lat": lat,
        "lng": lng
    })
    
def search_birds(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    
    if len(query) < 1 and not category:
        return JsonResponse({'results': []})
    
    # Search by common name, optionally filtered by category
    birds = BirdSpecies.objects.all()
    
    if category:
        birds = birds.filter(category=category)
    
    if query:
        birds = birds.filter(common_name__icontains=query)
    
    birds = birds.values('id', 'common_name', 'scientific_name', 'category')[:20]
    
    results = [
        {
            'id': bird['id'],
            'common_name': bird['common_name'],
            'scientific_name': bird['scientific_name'],
            'category': bird['category'],
        }
        for bird in birds
    ]
    
    return JsonResponse({'results': results})


def bird_categories(request):
    """Return the list of bird categories for the filter dropdown."""
    categories = [{'value': val, 'label': label} for val, label in BIRD_CATEGORY_CHOICES]
    return JsonResponse({'categories': categories})


@login_required
def delete_sighting(request, sighting_id):
    sighting = get_object_or_404(Sighting, id=sighting_id)

    if sighting.user != request.user:
        return redirect("index")

    if request.method == "POST":
        sighting.delete()
        return redirect("index")

    return redirect("index")
        