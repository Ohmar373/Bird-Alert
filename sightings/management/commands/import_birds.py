from django.core.management.base import BaseCommand
from sightings.models import BirdSpecies
import csv

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
                
                # Skip rows without proper names or species entries
                if not common_name or not scientific_name or row.get('category') != 'species':
                    skipped += 1
                    continue
                
                # Truncate scientific name if it exceeds max length
                if len(scientific_name) > 150:
                    scientific_name = scientific_name[:150]
                
                try:
                    # Check if bird already exists
                    if BirdSpecies.objects.filter(common_name=common_name).exists():
                        skipped += 1
                        continue
                    
                    # Create new bird
                    BirdSpecies.objects.create(
                        common_name=common_name,
                        scientific_name=scientific_name
                    )
                    imported += 1
                    
                    if imported % 100 == 0:
                        self.stdout.write(f"Progress: {imported} imported...")
                        
                except Exception as e:
                    self.stdout.write(f"Error importing {common_name}: {str(e)}")
                    skipped += 1
        
        self.stdout.write(self.style.SUCCESS(f"\n✓ Successfully imported {imported} birds"))
        self.stdout.write(f"Skipped {skipped} entries")