from django import forms
from .models import Sighting, BirdSpecies, BEHAVIOR_CHOICES
from .upload_validation import validate_photo_upload

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
            'weather_conditions': forms.TextInput(attrs={'placeholder': 'e.g., Sunny, Cloudy, Rainy'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': "Share what you observed — behavior, surroundings, anything that stood out..."}),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/jpeg,image/png,image/gif,image/webp'}),
            'count': forms.NumberInput(attrs={'min': '1', 'max': '9999', 'placeholder': '1'}),
            'behavior': forms.Select(choices=[('', 'Select behavior…')] + list(BEHAVIOR_CHOICES)),
        }
    
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
