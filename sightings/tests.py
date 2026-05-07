from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import SightingForm
from .models import BirdSpecies, Bookmark, Sighting, Like, Comment

class ModelUnitTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.bird, created = BirdSpecies.objects.get_or_create(
            scientific_name='Turdus migratorius',
            defaults={
                'common_name': 'American Robin',
                'category': 'songbird'
            }
        )
        self.sighting = Sighting.objects.create(
            user=self.user,
            bird_species=self.bird,
            latitude=40.7128,
            longitude=-74.0060,
            weather_conditions='Sunny',
            description='Saw it in the park tree!'
        )

    def test_bird_species_str(self):
        self.assertEqual(str(self.bird), 'American Robin')

    def test_sighting_creation(self):
        self.assertEqual(self.sighting.user.username, 'testuser')
        self.assertEqual(self.sighting.bird_species.common_name, 'American Robin')
        self.assertIsNotNone(self.sighting.timestamp)

    def test_like_creation(self):
        like = Like.objects.create(user=self.user, sighting=self.sighting)
        self.assertEqual(Like.objects.count(), 1)
        self.assertTrue('likes' in str(like))

    def test_comment_creation(self):
        comment = Comment.objects.create(user=self.user, sighting=self.sighting, text='Great photo!')
        self.assertEqual(Comment.objects.count(), 1)
        self.assertTrue('Comment by testuser' in str(comment))


class SightingFormTests(TestCase):
    def setUp(self):
        self.bird, created = BirdSpecies.objects.get_or_create(
            scientific_name='Cardinalis cardinalis',
            defaults={
                'common_name': 'Northern Cardinal',
                'category': 'songbird'
            }
        )

    def test_rejects_non_photo_upload(self):
        upload = SimpleUploadedFile(
            'payload.txt',
            b'<script>alert("not a photo")</script>',
            content_type='text/plain'
        )
        form = SightingForm(
            data={
                'bird_species': self.bird.common_name,
                'latitude': '35.2271',
                'longitude': '-80.8431',
                'count': '1',
                'behavior': '',
            },
            files={'image': upload}
        )

        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)


class ViewIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.bird, created = BirdSpecies.objects.get_or_create(
            scientific_name='Cardinalis cardinalis',
            defaults={
                'common_name': 'Northern Cardinal',
                'category': 'songbird'
            }
        )
        self.sighting = Sighting.objects.create(
            user=self.user,
            bird_species=self.bird,
            latitude=35.2271,
            longitude=-80.8431,
            weather_conditions='Cloudy'
        )

    def test_discover_view_redirects_if_not_logged_in(self):
        response = self.client.get(reverse('sightings:discover'))
        self.assertNotEqual(response.status_code, 200)

    def test_search_birds_api(self):
        # Search api shouldn't need auth based on views.py
        response = self.client.get(reverse('sightings:search_birds'), {'q': 'Cardinal'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"results": [{"id": self.bird.id, "common_name": "Northern Cardinal", "scientific_name": "Cardinalis cardinalis", "category": "songbird"}]}
        )

    def test_search_sightings_api(self):
        response = self.client.get(reverse('sightings:search_sightings'), {'q': 'Cardinal'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['common_name'], 'Northern Cardinal')

    def test_like_sighting_api(self):
        self.client.login(username='testuser', password='password123')
        url = reverse('sightings:like_sighting', args=[self.sighting.id])
        
        # Like
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['liked'])
        self.assertEqual(response.json()['count'], 1)

        # Unlike
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['liked'])
        self.assertEqual(response.json()['count'], 0)

    def test_add_comment_api(self):
        self.client.login(username='testuser', password='password123')
        url = reverse('sightings:add_comment', args=[self.sighting.id])
        
        response = self.client.post(url, {'text': 'Awesome bird!'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['text'], 'Awesome bird!')
        self.assertEqual(Comment.objects.count(), 1)

    def test_bookmark_sighting_api(self):
        self.client.login(username='testuser', password='password123')
        url = reverse('sightings:bookmark_sighting', args=[self.sighting.id])

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['bookmarked'])
        self.assertTrue(Bookmark.objects.filter(user=self.user, sighting=self.sighting).exists())

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['bookmarked'])
        self.assertFalse(Bookmark.objects.filter(user=self.user, sighting=self.sighting).exists())

    def test_profile_shows_bookmarked_sightings_for_owner(self):
        Bookmark.objects.create(user=self.user, sighting=self.sighting)
        self.client.login(username='testuser', password='password123')

        response = self.client.get(reverse('profile:view'))

        self.assertContains(response, 'data-panel="saved"')
        self.assertContains(response, self.sighting.bird_species.common_name)
        self.assertContains(response, 'Saved')

    def test_sighting_detail_view(self):
        self.client.login(username='testuser', password='password123')
        Bookmark.objects.create(user=self.user, sighting=self.sighting)
        Like.objects.create(user=self.user, sighting=self.sighting)

        response = self.client.get(reverse('sightings:sighting_detail', args=[self.sighting.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.sighting.bird_species.common_name)
        self.assertContains(response, 'sd-icon-btn bookmarked')
        self.assertContains(response, 'Back to testuser')
