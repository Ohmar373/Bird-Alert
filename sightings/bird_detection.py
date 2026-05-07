"""
Bird species identification service using multiple detection strategies.
Supports:
1. Gemini Vision AI (primary — highest accuracy, 1,500 free requests/day)
2. Google Cloud Vision API (fallback, 1,000 free requests/month)
3. Image colour analysis + database matching (free, no API needed)
"""

from PIL import Image
import io
import os
import random
import math
import colorsys
from collections import Counter
from .models import BirdSpecies

# Try to import Gemini - optional
try:
    from google import genai as google_genai
    from google.genai import types as genai_types
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# Try to import Google Vision - optional
try:
    from google.cloud import vision
    HAS_GOOGLE_VISION = True
except ImportError:
    HAS_GOOGLE_VISION = False


# ---------------------------------------------------------------------------
# HSV Hue → Bird Category mapping
# Using HSV (Hue-Saturation-Value) color space is far more reliable than RGB
# averaging because hue is independent of lighting/brightness.
# Hue ranges are in degrees 0–360.
# ---------------------------------------------------------------------------
HSV_HUE_MAP = [
    # (hue_min, hue_max, categories, confidence_weight)
    (0,   20,  ['songbird'],                   0.88),  # Red          → cardinal, tanager
    (20,  55,  ['songbird'],                   0.92),  # Orange/amber → oriole, robin
    (55,  75,  ['songbird'],                   0.87),  # Yellow       → warbler, goldfinch
    (75,  155, ['parrot'],                     0.90),  # Green        → parrot, parakeet
    (155, 205, ['seabird', 'shorebird'],       0.80),  # Cyan/teal    → heron, kingfisher
    (205, 255, ['songbird'],                   0.85),  # Blue         → blue jay, bluebird
    (255, 295, ['hummingbird'],                0.88),  # Purple       → hummingbird, sunbird
    (295, 340, ['shorebird', 'seabird'],       0.76),  # Pink/magenta → spoonbill, flamingo
    (340, 360, ['songbird'],                   0.83),  # Red-pink     → house finch
]

# ---------------------------------------------------------------------------
# Well-known, frequently-photographed species per category.
# These are surfaced first so results contain recognisable birds even when
# the detection method cannot identify the exact species.
# ---------------------------------------------------------------------------
COMMON_PHOTOGRAPHED_BIRDS = {
    'songbird': [
        'Altamira Oriole', 'Baltimore Oriole', "Bullock's Oriole", 'Streak-backed Oriole',
        'Northern Cardinal', 'Scarlet Tanager', 'Western Tanager', 'Summer Tanager',
        'American Robin', 'Blue Jay', 'American Goldfinch', 'Yellow Warbler',
        'Painted Bunting', 'Indigo Bunting', 'Rose-breasted Grosbeak',
        'American Redstart', 'Eastern Bluebird', 'Barn Swallow',
        'Black-capped Chickadee', 'House Finch', 'Purple Finch',
    ],
    'raptor': [
        'Bald Eagle', 'Golden Eagle', 'Red-tailed Hawk', 'Osprey',
        'Peregrine Falcon', "Cooper's Hawk", 'Sharp-shinned Hawk',
        'American Kestrel', 'Ferruginous Hawk', 'Rough-legged Hawk',
    ],
    'owl': [
        'Great Horned Owl', 'Barred Owl', 'Barn Owl', 'Snowy Owl',
        'Great Gray Owl', 'Burrowing Owl', 'Eastern Screech-Owl',
    ],
    'waterfowl': [
        'Mallard', 'Canada Goose', 'Wood Duck', 'Northern Pintail',
        'American Black Duck', 'Canvasback', 'Ring-necked Duck', 'Trumpeter Swan',
    ],
    'hummingbird': [
        'Ruby-throated Hummingbird', "Anna's Hummingbird", 'Broad-tailed Hummingbird',
        'Rufous Hummingbird', 'Black-chinned Hummingbird', 'Calliope Hummingbird',
        'Broad-billed Hummingbird',
    ],
    'parrot': [
        'Scarlet Macaw', 'Blue-and-yellow Macaw', 'Rose-ringed Parakeet',
        'Monk Parakeet', 'Green Parakeet', 'Red-crowned Parrot',
    ],
    'seabird': [
        'Herring Gull', 'Laughing Gull', 'Brown Pelican', 'Atlantic Puffin',
        'Double-crested Cormorant', "Forster's Tern",
    ],
    'shorebird': [
        'American Avocet', 'Black-necked Stilt', 'Roseate Spoonbill',
        'Greater Flamingo', 'Long-billed Curlew', 'Killdeer', 'Willet',
    ],
    'woodpecker': [
        'Downy Woodpecker', 'Hairy Woodpecker', 'Pileated Woodpecker',
        'Red-headed Woodpecker', 'Northern Flicker', 'Red-bellied Woodpecker',
    ],
    'pigeon_dove': [
        'Mourning Dove', 'Rock Pigeon', 'White-winged Dove',
        'Eurasian Collared-Dove', 'Inca Dove',
    ],
    'gamebird': [
        'Wild Turkey', 'Ring-necked Pheasant', 'Northern Bobwhite',
        'California Quail', 'Ruffed Grouse',
    ],
    'penguin': [
        'Emperor Penguin', 'Gentoo Penguin', 'Magellanic Penguin',
        'African Penguin', 'Little Penguin',
    ],
    'flightless': [
        'Common Ostrich', 'Emu', 'Greater Rhea', 'Southern Cassowary',
    ],
}


def detect_with_gemini(image_file):
    """
    Identify bird species using Gemini Vision AI.
    Asks Gemini directly: "What species of bird is this?"
    Returns top 5 matches looked up in the database.
    Free tier: 1,500 requests/day.
    """
    if not HAS_GEMINI:
        return None

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None

    try:
        client = google_genai.Client(api_key=api_key)

        image_file.seek(0)
        image_bytes = image_file.read()

        prompt = (
            "You are an expert ornithologist. Look at this bird photo and identify the species.\n"
            "List the top 5 most likely bird species in this image, in order of confidence.\n"
            "Format your response EXACTLY like this (one per line, nothing else):\n"
            "1. Common Name (Scientific Name)\n"
            "2. Common Name (Scientific Name)\n"
            "3. Common Name (Scientific Name)\n"
            "4. Common Name (Scientific Name)\n"
            "5. Common Name (Scientific Name)\n"
            "If it is clearly not a bird, reply only with: NOT A BIRD"
        )

        # Try models in order of capability, falling back if quota is exhausted
        last_error = None
        response = None
        model_candidates = [
            ('gemini-2.5-flash', {'thinking_config': {'thinking_budget': 0}}),
            ('gemini-2.0-flash', {}),
            ('gemini-2.0-flash-lite', {}),
        ]
        for model_name, extra_config in model_candidates:
            try:
                kwargs = dict(
                    model=model_name,
                    contents=[
                        genai_types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                        prompt,
                    ],
                )
                if extra_config:
                    kwargs['config'] = extra_config
                response = client.models.generate_content(**kwargs)
                break
            except Exception as model_err:
                print(f'Gemini model {model_name} failed: {model_err}')
                last_error = model_err
                continue
        if response is None:
            raise last_error
        text = response.text.strip()

        if 'NOT A BIRD' in text.upper():
            return []

        results = []
        confidence_steps = [0.97, 0.93, 0.88, 0.83, 0.78]

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            # Strip leading "1. ", "2. " etc.
            import re
            line = re.sub(r'^\d+\.\s*', '', line)

            # Extract common name (everything before the parenthesis)
            common = re.sub(r'\s*\(.*?\)', '', line).strip()
            # Extract scientific name from parentheses
            sci_match = re.search(r'\(([^)]+)\)', line)
            scientific = sci_match.group(1).strip() if sci_match else ''

            if not common:
                continue

            # Look up in database — try common name first, then scientific
            bird = BirdSpecies.objects.filter(common_name__iexact=common).first()
            if not bird and scientific:
                bird = BirdSpecies.objects.filter(scientific_name__iexact=scientific).first()
            if not bird:
                # Fuzzy match as last resort
                matches = fuzzy_match_bird_name(common, BirdSpecies.objects.all(), threshold=0.75)
                if matches:
                    bird = matches[0]['bird']

            idx = len(results)
            conf = confidence_steps[idx] if idx < len(confidence_steps) else 0.70

            if bird:
                results.append({
                    'id': bird.id,
                    'common_name': bird.common_name,
                    'scientific_name': bird.scientific_name,
                    'category': bird.category,
                    'confidence': conf,
                    'source': 'gemini',
                })
            else:
                # Bird not in DB but Gemini identified it — show Gemini's answer
                results.append({
                    'id': None,
                    'common_name': common,
                    'scientific_name': scientific,
                    'category': 'unknown',
                    'confidence': conf,
                    'source': 'gemini',
                })

            if len(results) == 5:
                break

        return results if results else None

    except Exception as e:
        print(f"Gemini error: {e}")
        return None


# Generic Vision labels that are never bird species names — skip these
# so they don't fuzzy-match to unrelated species.
_GENERIC_LABELS = {
    'bird', 'wildlife', 'animal', 'vertebrate', 'organism', 'fauna',
    'nature', 'natural', 'wild', 'feather', 'beak', 'wing', 'claw',
    'sky', 'tree', 'branch', 'leaf', 'water', 'blue', 'green', 'red',
    'yellow', 'white', 'black', 'brown', 'grey', 'gray', 'orange',
    'purple', 'pink', 'terrestrial', 'avian', 'passerine', 'raptor',
    'songbird', 'perching', 'flight', 'flying', 'sitting', 'standing',
    'close', 'stock', 'photo', 'image', 'photograph',
}


def _match_label_to_bird(label, confidence, source_tag):
    """
    Try to match a Google Vision label to a bird species in the database.

    Match priority (affects final sort order via confidence bonus):
      1. Exact common name  → confidence kept as-is        (highest rank)
      2. Exact scientific name → -1 % penalty
      3. Fuzzy match (≥0.80) → -10 % penalty               (lowest rank)

    Generic non-species labels are rejected before matching.
    """
    label_lower = label.lower().strip()

    # Reject single words that are clearly not species names
    if label_lower in _GENERIC_LABELS:
        return None
    # Also skip anything shorter than 4 chars — too generic to be a species
    if len(label_lower) < 4:
        return None

    # ── Exact common name ──────────────────────────────────────────────
    bird = BirdSpecies.objects.filter(common_name__iexact=label_lower).first()
    if bird:
        return {
            'id': bird.id,
            'common_name': bird.common_name,
            'scientific_name': bird.scientific_name,
            'category': bird.category,
            'confidence': round(min(confidence, 0.99), 2),
            'source': source_tag,
            '_exact': True,   # used for tie-breaking sort
        }

    # ── Exact scientific name ──────────────────────────────────────────
    bird = BirdSpecies.objects.filter(scientific_name__iexact=label_lower).first()
    if bird:
        return {
            'id': bird.id,
            'common_name': bird.common_name,
            'scientific_name': bird.scientific_name,
            'category': bird.category,
            'confidence': round(min(confidence * 0.99, 0.99), 2),
            'source': source_tag,
            '_exact': True,
        }

    # ── Fuzzy match — only multi-word labels (e.g. "blue jay", "bald eagle") ──
    # Single generic words like "eagle" or "jay" would match too broadly.
    if ' ' not in label_lower:
        return None

    matches = fuzzy_match_bird_name(label_lower, BirdSpecies.objects.all(), threshold=0.80)
    if matches:
        bird = matches[0]['bird']
        return {
            'id': bird.id,
            'common_name': bird.common_name,
            'scientific_name': bird.scientific_name,
            'category': bird.category,
            'confidence': round(min(confidence * 0.90, 0.99), 2),
            'source': source_tag + '_fuzzy',
            '_exact': False,
        }
    return None


def detect_with_google_vision(image_file):
    """
    Detect bird species using Google Cloud Vision API.

    Uses two annotation types for maximum accuracy:
    1. label_detection  — Google's trained image classifiers (best for species ID)
    2. web_detection    — visually similar web images (catches species names not
                          in label_detection's vocabulary)

    Results from both are merged, deduplicated by bird ID, and sorted by
    confidence before returning the top 5.
    """
    if not HAS_GOOGLE_VISION:
        return None

    try:
        if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            return None

        client = vision.ImageAnnotatorClient()

        image_file.seek(0)
        content = image_file.read()
        image = vision.Image(content=content)

        # web_detection does reverse image search → more accurate for specific species.
        # label_detection uses image classifiers → good for visual similarity but
        # may return related-looking species (e.g. Mountain Bluebird for a Blue Jay).
        #
        # Scoring:
        #   web_detection match  → confidence + 0.05 bonus (primary source)
        #   label_detection only → confidence as-is        (secondary source)
        #   appears in both      → gets the web bonus (already applied) + stays #1

        detected_birds = {}   # bird_id → result dict

        # ── 1. Web detection (primary — reverse image search) ───────────
        web_response = client.web_detection(image=image)
        for entity in web_response.web_detection.web_entities:
            if entity.score < 0.5:
                continue
            result = _match_label_to_bird(entity.description, entity.score, 'google_vision')
            if result:
                result['confidence'] = round(min(result['confidence'] + 0.05, 0.99), 2)
                if result['id'] not in detected_birds:
                    detected_birds[result['id']] = result

        # ── 2. Label detection (secondary — fills gaps web missed) ──────
        label_response = client.label_detection(image=image)
        for label in label_response.label_annotations:
            if label.score < 0.5:
                continue
            result = _match_label_to_bird(label.description, label.score, 'google_vision')
            if result and result['id'] not in detected_birds:
                detected_birds[result['id']] = result

        if not detected_birds:
            return None

        sorted_birds = sorted(
            detected_birds.values(),
            key=lambda x: (x.pop('_exact', False), x['confidence']),
            reverse=True,
        )
        return sorted_birds[:5]

    except Exception as e:
        print(f"Google Vision error: {str(e)}")
        return None


def _analyze_image_colors(image_file):
    """
    Analyse the dominant bird colour using HSV color space.

    Key improvements:
    - Centre-crop (middle 60%) to focus on the photographic subject.
    - High saturation threshold (0.55) to skip typical blurred/grey backgrounds.
    - Modal hue histogram (most common vivid hue bucket) rather than circular
      mean, so a large dull background can't pull the result away from a small
      vivid bird.
    - Separate achromatic path for white/black/grey birds.

    Returns {'categories': [...], 'confidence': float} or None.
    """
    try:
        image_file.seek(0)
        img = Image.open(image_file).convert('RGB')

        # Centre-crop to the middle 60%
        w, h = img.size
        mx, my = int(w * 0.2), int(h * 0.2)
        img = img.crop((mx, my, w - mx, h - my)).resize((80, 80))
        pixels = list(img.getdata())
        n = len(pixels)

        # Hue histogram: 18 buckets of 20° each (indices 0-17)
        BUCKET_SIZE = 20
        NUM_BUCKETS = 18
        hue_weights = [0.0] * NUM_BUCKETS
        achromatic = {'white': 0, 'black': 0, 'grey': 0}
        vivid_count = 0

        SAT_THRESHOLD = 0.55   # skip dull/background pixels
        VAL_MIN, VAL_MAX = 0.12, 0.96

        for r, g, b in pixels:
            hue, sat, val = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

            if sat < 0.18 or not (VAL_MIN <= val <= VAL_MAX):
                # Achromatic
                if val > 0.80:
                    achromatic['white'] += 1
                elif val < 0.22:
                    achromatic['black'] += 1
                else:
                    achromatic['grey'] += 1
                continue

            if sat < SAT_THRESHOLD:
                continue  # low-saturation background — skip

            vivid_count += 1
            bucket = int((hue * 360) / BUCKET_SIZE) % NUM_BUCKETS
            hue_weights[bucket] += sat  # weight vivid pixels by saturation

        # ── Achromatic bird? ──────────────────────────────────────────────
        if vivid_count < n * 0.06:
            if achromatic['white'] >= achromatic['black']:
                return {'categories': ['seabird', 'waterfowl'], 'confidence': 0.70}
            elif achromatic['black'] > achromatic['grey']:
                return {'categories': ['songbird'], 'confidence': 0.72}   # crow/raven
            else:
                return {'categories': ['raptor', 'owl', 'pigeon_dove'], 'confidence': 0.68}

        # ── Modal hue bucket ───────────────────────────────────────────────
        peak_bucket = max(range(NUM_BUCKETS), key=lambda i: hue_weights[i])
        peak_hue_deg = peak_bucket * BUCKET_SIZE  # representative degree of bucket

        for hue_min, hue_max, categories, weight in HSV_HUE_MAP:
            if hue_min <= peak_hue_deg < hue_max:
                return {'categories': categories, 'confidence': weight}

        return None

    except Exception as e:
        print(f"Color analysis error: {e}")
        return None


def _get_birds_from_db(categories, confidence_base, limit=5):
    """
    Return `limit` birds from the database for the given categories.

    Priority order:
    1. Well-known / frequently-photographed species from COMMON_PHOTOGRAPHED_BIRDS
       (so results contain recognisable names even without exact species ID).
    2. Random birds from the matched categories to fill remaining slots.
    3. Random birds from all categories if none found for supplied categories.
    """
    from django.db.models import Q

    # ── 1. Priority: well-known photogenic species ─────────────────────────
    priority_names = []
    for cat in categories:
        priority_names.extend(COMMON_PHOTOGRAPHED_BIRDS.get(cat, []))

    results = []
    used_ids = set()

    if priority_names:
        q = Q()
        for name in priority_names:
            q |= Q(common_name__iexact=name)
        priority_qs = list(BirdSpecies.objects.filter(q, category__in=categories))
        random.shuffle(priority_qs)
        for i, bird in enumerate(priority_qs[:limit]):
            conf = round(max(0.30, confidence_base - i * 0.04), 2)
            results.append({
                'id': bird.id,
                'common_name': bird.common_name,
                'scientific_name': bird.scientific_name,
                'category': bird.category,
                'confidence': conf,
                'source': 'local_database',
            })
            used_ids.add(bird.id)

    # ── 2. Fill remaining slots with random category birds ─────────────────
    if len(results) < limit:
        extra_qs = list(
            BirdSpecies.objects.filter(category__in=categories)
            .exclude(id__in=used_ids)
        )
        random.shuffle(extra_qs)
        for i, bird in enumerate(extra_qs[: limit - len(results)]):
            conf = round(max(0.30, confidence_base - (len(results) + i) * 0.04), 2)
            results.append({
                'id': bird.id,
                'common_name': bird.common_name,
                'scientific_name': bird.scientific_name,
                'category': bird.category,
                'confidence': conf,
                'source': 'local_database',
            })
            used_ids.add(bird.id)

    # ── 3. Fallback: pull from any category ────────────────────────────
    if not results:
        qs = list(BirdSpecies.objects.all())
        random.shuffle(qs)
        for i, bird in enumerate(qs[:limit]):
            conf = round(max(0.30, confidence_base - i * 0.04), 2)
            results.append({
                'id': bird.id,
                'common_name': bird.common_name,
                'scientific_name': bird.scientific_name,
                'category': bird.category,
                'confidence': conf,
                'source': 'local_database',
            })

    return results


def identify_bird_species(image_file):
    """
    Identify bird species from an image file.

    Strategy (in order):
    1. Google Cloud Vision API  — highest accuracy, requires credentials
    2. Image colour analysis    — maps dominant pixel colour to bird category,
                                  then queries the full 11,000+ bird database
    3. Random database fallback — returns random birds from DB when colour
                                  analysis yields no clear category match

    Returns:
        List of dicts: [{'id', 'common_name', 'scientific_name',
                         'category', 'confidence', 'source'}, ...]
    """
    try:
        # Validate file is a readable image
        image_file.seek(0)
        img = Image.open(image_file)
        img.verify()
        image_file.seek(0)

        # ── 1. Gemini Vision AI (primary — most accurate) ───────────────
        results = detect_with_gemini(image_file)
        if results is not None:   # empty list = confirmed not a bird
            if not results:
                return []         # Gemini said NOT A BIRD
            return results

        # ── 2. Google Vision API (fallback) ────────────────────────────
        results = detect_with_google_vision(image_file)
        if results:
            return results

        # ── 2. Colour analysis + DB query ───────────────────────────────
        image_file.seek(0)
        colour_match = _analyze_image_colors(image_file)
        if colour_match:
            return _get_birds_from_db(
                colour_match['categories'],
                colour_match['confidence'],
            )

        # ── 3. Fallback: random birds from the full database ─────────────
        return _get_birds_from_db(
            list(BirdSpecies.objects.values_list('category', flat=True).distinct()),
            confidence_base=0.45,
        )

    except Exception as e:
        print(f"Error identifying bird: {e}")
        return []





def fuzzy_match_bird_name(query, birds, threshold=0.6):
    """
    Fuzzy match query string against bird names.
    
    Args:
        query: String to match
        birds: List of BirdSpecies objects or names
        threshold: Minimum similarity score (0-1)
        
    Returns:
        List of matching birds with similarity scores
    """
    from difflib import SequenceMatcher
    
    results = []
    query_lower = query.lower().strip()
    
    for bird in birds:
        if isinstance(bird, BirdSpecies):
            name = bird.common_name.lower()
        else:
            name = str(bird).lower()
        
        similarity = SequenceMatcher(None, query_lower, name).ratio()
        
        if similarity >= threshold:
            results.append({
                'bird': bird,
                'similarity': similarity,
                'name': name
            })
    
    # Sort by similarity descending
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    return results

