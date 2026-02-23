from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import SightingForm
from sightings import utils
from sightings.utils import get_location_name
from .models import Sighting, BirdSpecies
from .models import Like, Comment
from django.views.decorators.http import require_POST
from django.utils import timezone

@login_required
def discover(request):
    """Render the Discover page (map + search + filters)."""
    return render(request, "sightings/discover.html")

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
    
    if len(query) < 1:
        return JsonResponse({'results': []})
    
    # Search by common name
    birds = BirdSpecies.objects.filter(
        common_name__icontains=query
    ).values('id', 'common_name', 'scientific_name')[:20]
    
    results = [
        {
            'id': bird['id'],
            'common_name': bird['common_name'],
            'scientific_name': bird['scientific_name']
        }
        for bird in birds
    ]
    
    return JsonResponse({'results': results})

def list_birds(request):
    """Return a short list of bird species for populating filters/selects."""
    birds = BirdSpecies.objects.all().values('id', 'common_name')[:500]
    results = [{'id': b['id'], 'common_name': b['common_name']} for b in birds]
    return JsonResponse({'results': results})

def search_sightings(request):
    """API: Return sightings matching a query or species id.

    Params:
      q - partial common_name match
      species_id - exact BirdSpecies id
    """
    q = request.GET.get('q', '').strip()
    species_id = request.GET.get('species_id')

    sightings_qs = Sighting.objects.select_related('bird_species', 'user').all()

    if species_id:
        try:
            sightings_qs = sightings_qs.filter(bird_species__id=int(species_id))
        except (ValueError, TypeError):
            sightings_qs = sightings_qs.none()
    elif q:
        sightings_qs = sightings_qs.filter(bird_species__common_name__icontains=q)
    else:
        # If no filter provided, return recent sightings
        sightings_qs = sightings_qs.order_by('-timestamp')[:200]

    data = [
        {
            'id': s.id,
            'lat': s.latitude,
            'lng': s.longitude,
            'common_name': s.bird_species.common_name,
            'timestamp': s.timestamp.isoformat(),
            'user': s.user.username,
        }
        for s in sightings_qs[:500]
    ]

    return JsonResponse({'results': data})


@login_required
@require_POST
def like_sighting(request, sighting_id):
    sighting = get_object_or_404(Sighting, id=sighting_id)
    user = request.user

    liked = False
    existing = Like.objects.filter(user=user, sighting=sighting)
    if existing.exists():
        existing.delete()
        liked = False
    else:
        Like.objects.create(user=user, sighting=sighting)
        liked = True

    count = Like.objects.filter(sighting=sighting).count()
    return JsonResponse({'liked': liked, 'count': count})


def get_comments(request, sighting_id):
    sighting = get_object_or_404(Sighting, id=sighting_id)
    comments = Comment.objects.filter(sighting=sighting).select_related('user').order_by('-timestamp')[:50]
    data = [
        {'user': c.user.username, 'text': c.text, 'timestamp': c.timestamp.isoformat()}
        for c in comments
    ]
    return JsonResponse({'results': data})


@login_required
@require_POST
def add_comment(request, sighting_id):
    sighting = get_object_or_404(Sighting, id=sighting_id)
    text = request.POST.get('text', '').strip()
    if not text:
        return JsonResponse({'error': 'Empty comment'}, status=400)

    comment = Comment.objects.create(user=request.user, sighting=sighting, text=text, timestamp=timezone.now())

    return JsonResponse({'user': comment.user.username, 'text': comment.text, 'timestamp': comment.timestamp.isoformat()})

@login_required
def delete_sighting(request, sighting_id):
    sighting = get_object_or_404(Sighting, id=sighting_id)

    if sighting.user != request.user:
        return redirect("index")

    if request.method == "POST":
        sighting.delete()
        return redirect("index")

    return redirect("index")
        