from django.core.management.base import BaseCommand
from sightings.models import BirdSpecies
import csv

# Mapping from taxonomic order to our user-friendly category
ORDER_TO_CATEGORY = {
    'Passeriformes': 'songbird',
    'Anseriformes': 'waterfowl',
    'Accipitriformes': 'raptor',
    'Falconiformes': 'raptor',
    'Cathartiformes': 'raptor',
    'Charadriiformes': 'shorebird',
    'Piciformes': 'woodpecker',
    'Strigiformes': 'owl',
    'Procellariiformes': 'seabird',
    'Suliformes': 'seabird',
    'Pelecaniformes': 'seabird',
    'Phaethontiformes': 'seabird',
    'Gaviiformes': 'seabird',
    'Sphenisciformes': 'penguin',
    'Apodiformes': 'hummingbird',
    'Galliformes': 'gamebird',
    'Columbiformes': 'pigeon_dove',
    'Psittaciformes': 'parrot',
    'Struthioniformes': 'flightless',
    'Rheiformes': 'flightless',
    'Casuariiformes': 'flightless',
    'Apterygiformes': 'flightless',
    'Tinamiformes': 'flightless',
}


class Command(BaseCommand):
    help = 'Import birds from CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)
    
    def handle(self, *args, **options):
        csv_path = options['csv_file']
        imported = 0
        skipped = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                common_name = row.get('English name', '').strip()
                scientific_name = row.get('scientific name', '').strip()
                order = row.get('order', '').strip()
                
                # Skip rows without proper names or species entries
                if not common_name or not scientific_name or row.get('category') != 'species':
                    skipped += 1
                    continue
                
                # Truncate scientific name if it exceeds max length
                if len(scientific_name) > 150:
                    scientific_name = scientific_name[:150]
                
                # Determine category from taxonomic order
                bird_category = ORDER_TO_CATEGORY.get(order, 'other')
                
                try:
                    # Check if bird already exists
                    if BirdSpecies.objects.filter(common_name=common_name).exists():
                        skipped += 1
                        continue
                    
                    # Create new bird
                    BirdSpecies.objects.create(
                        common_name=common_name,
                        scientific_name=scientific_name,
                        category=bird_category
                    )
                    imported += 1
                    
                    if imported % 100 == 0:
                        self.stdout.write(f"Progress: {imported} imported...")
                        
                except Exception as e:
                    self.stdout.write(f"Error importing {common_name}: {str(e)}")
                    skipped += 1
        
        self.stdout.write(self.style.SUCCESS(f"\n✓ Successfully imported {imported} birds"))
        self.stdout.write(f"Skipped {skipped} entries")