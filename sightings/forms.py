from django import forms
from .models import Sighting

class SightingForm(forms.ModelForm):
    class Meta:
        model = Sighting
        fields = ['bird_species', 'latitude', 'longitude', 'weather_conditions', 'description']
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'weather_conditions': forms.TextInput(attrs={'placeholder': 'e.g., Sunny, Cloudy, Rainy'}),
        }
