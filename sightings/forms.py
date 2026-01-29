from django import forms
from .models import Sighting

class SightingForm(forms.ModelForm):
    class Meta:
        model = Sighting
        fields = ['bird_species', 'latitude', 'longitude', 'weather_conditions', 'description']
        widgets = {
            'latitude': forms.NumberInput(attrs={'type': 'hidden'}),
            'longitude': forms.NumberInput(attrs={'type': 'hidden'}),
            'weather_conditions': forms.TextInput(attrs={'placeholder': 'e.g., Sunny, Cloudy, Rainy'}),
        }