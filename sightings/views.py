from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import SightingForm

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