from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import CustomUser

class UserRegistrationTest(APITestCase):
    def test_user_can_register(self):
        url = reverse('register')
        data = {
            'email':'register@gmail.com',
            'full_name':'Registering User',
            'password':'registerpass',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().email, 'register@gmail.com')

class LoginTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="login@example.com",
            full_name="Login User",
            password="password123"
        )

    def test_user_can_login(self):
        url = reverse('login')
        data = {
            'email': 'login@example.com',
            'password':'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Login successful")
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)


class UserProfileTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            full_name="Test User",
            password="testpass123"
        )

        # Login to get tokens in cookies
        url = reverse("login")
        data = {"email": "test@example.com", "password": "testpass123"}
        response = self.client.post(url, data, format="json")

        # Manually set cookies for subsequent requests
        self.client.cookies["access_token"] = response.cookies["access_token"].value

    def test_authenticated_user_can_view_profile(self):
        url = reverse("profile")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "test@example.com")
class UserLogoutTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            full_name="Test User",
            password="testpass123"
        )

        # Login to get tokens in cookies
        self.login_url = reverse("login")
        data = {"email": "test@example.com", "password": "testpass123"}
        response = self.client.post(self.login_url, data, format="json")

        # Simulate browser: client stores the cookie from login response
        self.client.cookies['access_token'] = response.cookies['access_token'].value
        self.client.cookies['refresh_token'] = response.cookies['refresh_token'].value
    def test_user_can_logout(self):
        logout_url = reverse("logout")
        response = self.client.post(logout_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "User successfully logged out")

        # After logout, cookies should be cleared
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)
        self.assertEqual(response.cookies["access_token"]["max-age"], 0)
        self.assertEqual(response.cookies["refresh_token"]["max-age"], 0)
