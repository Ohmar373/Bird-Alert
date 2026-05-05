from functools import lru_cache
from urllib.parse import quote

import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from sightings import utils
from sightings.bird_detection import identify_bird_species

from .forms import SightingForm
from .models import BIRD_CATEGORY_CHOICES, BirdSpecies, Comment, Like, Sighting


@login_required
def discover(request):
    """Render the Discover page (map + search + filters)."""
    return render(request, "sightings/discover.html")


@login_required
def sighting_form(request):
    # Get lat/lng from GET or POST
    lat = request.GET.get("lat") or request.POST.get("latitude")
    lng = request.GET.get("lng") or request.POST.get("longitude")

    if request.method == "POST":
        form = SightingForm(request.POST, request.FILES)
        if form.is_valid():
            sighting = form.save(commit=False)
            sighting.user = request.user
            if sighting.latitude and sighting.longitude:
                sighting.location_name = utils.get_location_name(sighting.latitude, sighting.longitude)
            sighting.save()
            return redirect("index")
    else:
        initial_data = {}
        if lat and lng:
            try:
                initial_data = {
                    "latitude": float(lat),
                    "longitude": float(lng),
                }
            except (ValueError, TypeError):
                pass

        form = SightingForm(initial=initial_data)

    return render(
        request,
        "sightings/sighting-form.html",
        {
            "form": form,
            "lat": lat,
            "lng": lng,
        },
    )


def search_birds(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()

    if len(query) < 1 and not category:
        return JsonResponse({"results": []})

    birds = BirdSpecies.objects.all()

    if category:
        birds = birds.filter(category=category)

    if query:
        birds = birds.filter(common_name__icontains=query)

    birds = birds.values("id", "common_name", "scientific_name", "category")[:20]

    results = [
        {
            "id": bird["id"],
            "common_name": bird["common_name"],
            "scientific_name": bird["scientific_name"],
            "category": bird["category"],
        }
        for bird in birds
    ]

    return JsonResponse({"results": results})


def bird_categories(request):
    """Return the list of bird categories for the filter dropdown."""
    categories = [{"value": val, "label": label} for val, label in BIRD_CATEGORY_CHOICES]
    return JsonResponse({"categories": categories})


def list_birds(request):
    """Return a short list of bird species for populating filters/selects."""
    birds = BirdSpecies.objects.all().values("id", "common_name")[:500]
    results = [{"id": b["id"], "common_name": b["common_name"]} for b in birds]
    return JsonResponse({"results": results})


def search_sightings(request):
    """Return sightings matching a query or species id."""
    q = request.GET.get("q", "").strip()
    species_id = request.GET.get("species_id")

    sightings_qs = Sighting.objects.select_related("bird_species", "user").all()

    if species_id:
        try:
            sightings_qs = sightings_qs.filter(bird_species__id=int(species_id))
        except (ValueError, TypeError):
            sightings_qs = sightings_qs.none()
    elif q:
        sightings_qs = sightings_qs.filter(bird_species__common_name__icontains=q)
    else:
        sightings_qs = sightings_qs.order_by("-timestamp")[:200]

    data = [
        {
            "id": s.id,
            "lat": s.latitude,
            "lng": s.longitude,
            "common_name": s.bird_species.common_name,
            "timestamp": s.timestamp.isoformat(),
            "user": s.user.username,
        }
        for s in sightings_qs[:500]
    ]

    return JsonResponse({"results": data})


@login_required
@require_POST
def like_sighting(request, sighting_id):
    sighting = get_object_or_404(Sighting, id=sighting_id)
    user = request.user

    existing = Like.objects.filter(user=user, sighting=sighting)
    if existing.exists():
        existing.delete()
        liked = False
    else:
        Like.objects.create(user=user, sighting=sighting)
        liked = True

    count = Like.objects.filter(sighting=sighting).count()
    return JsonResponse({"liked": liked, "count": count})


def get_comments(request, sighting_id):
    sighting = get_object_or_404(Sighting, id=sighting_id)
    comments = (
        Comment.objects.filter(sighting=sighting)
        .select_related("user")
        .order_by("-timestamp")[:50]
    )
    data = [
        {
            "user": c.user.username,
            "text": c.text,
            "timestamp": c.timestamp.isoformat(),
        }
        for c in comments
    ]
    return JsonResponse({"results": data})


@login_required
@require_POST
def add_comment(request, sighting_id):
    sighting = get_object_or_404(Sighting, id=sighting_id)
    text = request.POST.get("text", "").strip()
    if not text:
        return JsonResponse({"error": "Empty comment"}, status=400)

    comment = Comment.objects.create(user=request.user, sighting=sighting, text=text)

    return JsonResponse(
        {
            "user": comment.user.username,
            "text": comment.text,
            "timestamp": comment.timestamp.isoformat(),
        }
    )


@login_required
def camera_detection(request):
    """Render the bird detection camera page."""
    return render(request, "sightings/camera_detection.html")


@lru_cache(maxsize=256)
def get_bird_example_image(common_name, scientific_name=""):
    """Return a representative bird image from Wikipedia, if one exists."""
    candidates = [common_name, scientific_name]

    for name in candidates:
        if not name:
            continue

        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(name)}"
            response = requests.get(
                url,
                headers={"User-Agent": "BirdAlert/1.0"},
                timeout=3,
            )
            if response.status_code != 200:
                continue

            data = response.json()
            original_image = data.get("originalimage") or {}
            thumbnail = data.get("thumbnail") or {}
            image_url = original_image.get("source") or thumbnail.get("source")
            if image_url:
                return image_url
        except requests.RequestException:
            continue
        except ValueError:
            continue

    return ""


@login_required
@require_POST
def detect_bird_species(request):
    """
    API endpoint for bird species detection from uploaded image.
    
    Receives an image file and returns likely bird species matches.
    
    Args:
        image: Uploaded image file
        
    Returns:
        JSON response with detected species:
        {
            'success': bool,
            'species': [
                {
                    'id': int,
                    'common_name': str,
                    'scientific_name': str,
                    'category': str,
                    'confidence': float
                }
            ],
            'error': str (if applicable)
        }
    """
    
    if 'image' not in request.FILES:
        return JsonResponse({
            'success': False,
            'error': 'No image provided'
        }, status=400)
    
    try:
        image_file = request.FILES['image']
        
        # Identify bird species from image
        species_list = identify_bird_species(image_file)
        if species_list:
            species_list = species_list[:1]
            for species in species_list:
                species["example_image_url"] = get_bird_example_image(
                    species.get("common_name", ""),
                    species.get("scientific_name", ""),
                )
        
        return JsonResponse({
            'success': True,
            'species': species_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error processing image: {str(e)}'
        }, status=500)


@login_required
def delete_sighting(request, sighting_id):
    sighting = get_object_or_404(Sighting, id=sighting_id)

    if sighting.user != request.user:
        return redirect("index")

    if request.method == "POST":
        sighting.delete()
        return redirect("index")

    return redirect("index")
