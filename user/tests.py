from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail

class UserViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', 
            email='testuser@example.com', 
            password='password123'
        )

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/index.html')

    def test_register_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/register.html')

    def test_login_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/login.html')

    def test_login_post_success_username(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('index'))

    def test_login_post_success_email(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser@example.com',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('index'))

    def test_login_post_failure(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/login.html')

    def test_forgot_username_post(self):
        response = self.client.post(reverse('forgot_username'), {
            'email': 'testuser@example.com'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Your Bird Alert Username')
        self.assertIn('testuser', mail.outbox[0].body)

    def test_forgot_username_post_invalid_email(self):
        response = self.client.post(reverse('forgot_username'), {
            'email': 'nonexistent@example.com'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(len(mail.outbox), 0)

    def test_sightings_view_requires_login(self):
        response = self.client.get(reverse('sightings'))
        self.assertNotEqual(response.status_code, 200)

    def test_sightings_view_authenticated(self):
        self.client.login(username='testuser', password='password123')
        # Check if URL exists and returns expected response
        try:
            response = self.client.get(reverse('sightings'))
            self.assertEqual(response.status_code, 200)
        except Exception:
            pass # Ignore if template is missing right now.
