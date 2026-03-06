from django.db import models

# Create your models here

BIRD_CATEGORY_CHOICES = [
    ('songbird', 'Songbirds'),
    ('waterfowl', 'Waterfowl'),
    ('raptor', 'Raptors'),
    ('shorebird', 'Shorebirds'),
    ('woodpecker', 'Woodpeckers'),
    ('owl', 'Owls'),
    ('seabird', 'Seabirds'),
    ('hummingbird', 'Hummingbirds'),
    ('gamebird', 'Gamebirds'),
    ('pigeon_dove', 'Pigeons & Doves'),
    ('parrot', 'Parrots'),
    ('penguin', 'Penguins'),
    ('flightless', 'Flightless Birds'),
    ('other', 'Other'),
]

class BirdSpecies(models.Model):
    common_name = models.CharField(max_length=100, unique= True)
    scientific_name = models.CharField(max_length=150, unique= True)
    category = models.CharField(max_length=20, choices=BIRD_CATEGORY_CHOICES, default='other', db_index=True)
    
    def __str__(self):
        return self.common_name
    
class Sighting(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    bird_species = models.ForeignKey(BirdSpecies, on_delete=models.CASCADE)
    
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    weather_conditions = models.CharField(max_length=100, help_text = "e.g., Sunny, Cloudy, Rainy")
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='sighting_images/', blank=True, null=True)
    
    location_name = models.CharField(max_length = 200, blank = True, null = True)
    
    def __str__(self):
        return f"{self.bird_species.common_name} sighted by {self.user.username} on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class Like(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    sighting = models.ForeignKey(Sighting, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'sighting')

    def __str__(self):
        return f"{self.user.username} likes {self.sighting.id}"


class Comment(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    sighting = models.ForeignKey(Sighting, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.sighting.id}" 