from django import forms
from .models import Sighting, BirdSpecies, BEHAVIOR_CHOICES
from .upload_validation import validate_photo_upload

WEATHER_CHOICES = [
    ('', 'Select conditions…'),
    ('Clear', 'Clear'),
    ('Sunny', 'Sunny'),
    ('Partly Cloudy', 'Partly Cloudy'),
    ('Overcast', 'Overcast'),
    ('Foggy / Misty', 'Foggy / Misty'),
    ('Windy', 'Windy'),
    ('Drizzle', 'Drizzle'),
    ('Light Rain', 'Light Rain'),
    ('Heavy Rain', 'Heavy Rain'),
    ('Thunderstorm', 'Thunderstorm'),
    ('Hot & Humid', 'Hot & Humid'),
    ('Snowy', 'Snowy'),
    ('Hazy', 'Hazy'),
]

MAX_BIRD_COUNT = 9999

class SightingForm(forms.ModelForm):
    bird_species = forms.CharField(
        label='Bird',
        widget=forms.TextInput(attrs={
            'id': 'bird_species_input',
            'autocomplete': 'off',
            'placeholder': 'Search bird species...'
        })
    )

    class Meta:
        model = Sighting
        fields = ['bird_species', 'latitude', 'longitude', 'weather_conditions', 'description', 'image', 'count', 'behavior']
        widgets = {
            'latitude': forms.NumberInput(attrs={'type': 'hidden'}),
            'longitude': forms.NumberInput(attrs={'type': 'hidden'}),
            'weather_conditions': forms.Select(choices=WEATHER_CHOICES),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': "Share what you observed — behavior, surroundings, anything that stood out..."}),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/jpeg,image/png,image/gif,image/webp'}),
            'count': forms.NumberInput(attrs={'min': '1', 'max': '9999', 'placeholder': '1'}),
            'behavior': forms.Select(choices=[('', 'Select behavior…')] + list(BEHAVIOR_CHOICES)),
        }
    
    def clean_count(self):
        count = self.cleaned_data.get('count')
        if count is not None and count > MAX_BIRD_COUNT:
            raise forms.ValidationError(f"Count cannot exceed {MAX_BIRD_COUNT:,}.")
        if count is not None and count < 1:
            raise forms.ValidationError("Count must be at least 1.")
        return count

    def clean_bird_species(self):
        bird_name = self.cleaned_data['bird_species'].strip()
        try:
            # Try to find the bird by common name
            bird = BirdSpecies.objects.get(common_name__iexact=bird_name)
            return bird
        except BirdSpecies.DoesNotExist:
            raise forms.ValidationError(f"Bird species '{bird_name}' not found in database.")
        except BirdSpecies.MultipleObjectsReturned:
            raise forms.ValidationError("Multiple species found. Please be more specific.")

    def clean_image(self):
        image = self.cleaned_data.get('image')
        validate_photo_upload(image)
        return image
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # bird_species is already a BirdSpecies object from clean_bird_species
        if commit:
            instance.save()
        return instance
