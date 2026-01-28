from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import SightingForm

@login_required
def add_sighting(request):
    return render(request, "sightings/add_sighting.html")

@login_required
def sighting_form(request):
  
    if request.method == "POST":
        form = SightingForm(request.POST, request.FILES)
        if form.is_valid():
            sighting = form.save(commit=False)
            sighting.user = request.user  
            sighting.save()
            
            return redirect("index")
    else:
        
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        
        initial_data = {}
        if lat and lng:
            initial_data = {
                'latitude': lat,
                'longitude': lng,
            }
        
        form = SightingForm(initial=initial_data)
    
    return render(request, "sightings/sighting-form.html", {"form": form})