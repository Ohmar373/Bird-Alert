"""Data migration to populate bird categories from CSV taxonomy (order → category)."""

from django.db import migrations


# Mapping from taxonomic order to our user-friendly category
ORDER_TO_CATEGORY = {
    # Songbirds (Passeriformes is the largest order — all perching/songbirds)
    'Passeriformes': 'songbird',

    # Waterfowl (ducks, geese, swans)
    'Anseriformes': 'waterfowl',

    # Raptors (hawks, eagles, kites, vultures + falcons)
    'Accipitriformes': 'raptor',
    'Falconiformes': 'raptor',
    'Cathartiformes': 'raptor',   # New World vultures

    # Shorebirds (plovers, sandpipers, gulls, terns, auks — Charadriiformes)
    'Charadriiformes': 'shorebird',

    # Woodpeckers (and toucans, barbets)
    'Piciformes': 'woodpecker',

    # Owls
    'Strigiformes': 'owl',

    # Seabirds
    'Procellariiformes': 'seabird',  # albatrosses, petrels, shearwaters
    'Suliformes': 'seabird',         # boobies, cormorants, frigatebirds
    'Pelecaniformes': 'seabird',     # pelicans, herons, ibises
    'Phaethontiformes': 'seabird',   # tropicbirds
    'Gaviiformes': 'seabird',        # loons
    'Sphenisciformes': 'penguin',    # penguins

    # Hummingbirds (+ swifts — Apodiformes)
    'Apodiformes': 'hummingbird',

    # Gamebirds (chickens, turkeys, quail, pheasants)
    'Galliformes': 'gamebird',

    # Pigeons & Doves
    'Columbiformes': 'pigeon_dove',

    # Parrots
    'Psittaciformes': 'parrot',

    # Flightless birds
    'Struthioniformes': 'flightless',  # ostriches
    'Rheiformes': 'flightless',        # rheas
    'Casuariiformes': 'flightless',    # cassowaries, emu
    'Apterygiformes': 'flightless',    # kiwis
    'Tinamiformes': 'flightless',      # tinamous
}


def populate_categories(apps, schema_editor):
    """Read the CSV to get order for each species, then map to category."""
    import csv
    import os

    BirdSpecies = apps.get_model('sightings', 'BirdSpecies')

    # Build a lookup: scientific_name → order from CSV
    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'bird_alert', 'data', 'BirdSpeciesList.csv'
    )

    sci_to_order = {}
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('category') == 'species':
                    sci_name = row.get('scientific name', '').strip()
                    order = row.get('order', '').strip()
                    if sci_name and order:
                        sci_to_order[sci_name.lower()] = order

    # Update each bird species
    updated = 0
    for bird in BirdSpecies.objects.all():
        order = sci_to_order.get(bird.scientific_name.lower(), '')
        category = ORDER_TO_CATEGORY.get(order, 'other')
        if bird.category != category:
            bird.category = category
            bird.save(update_fields=['category'])
            updated += 1

    print(f'\n  → Updated {updated} birds with categories.')


def reverse_categories(apps, schema_editor):
    BirdSpecies = apps.get_model('sightings', 'BirdSpecies')
    BirdSpecies.objects.all().update(category='other')


class Migration(migrations.Migration):

    dependencies = [
        ('sightings', '0005_add_bird_category'),
    ]

    operations = [
        migrations.RunPython(populate_categories, reverse_categories),
    ]
