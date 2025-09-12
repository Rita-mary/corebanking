from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import CustomUser

class UserDeleteTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="login@example.com",
            full_name="Login User",
            password="password123"
        )
        login_url = reverse('login')
        data = {
            'email': 'login@example.com',
            'password':'password123'
        }
        response = self.client.post(login_url,data,format='json')
        self.client.cookies['access_token'] = response.cookies.get('access_token').value
        self.client.cookies['refresh_token'] = response.cookies.get('refresh_token').value
    def test_user_can_delete_account(self):
        delete_url = reverse('profile_delete')
        response = self.client.delete(delete_url)
        self.assertEqual(response.data['message'], 'User Profile Successfuly deleted')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CustomUser.objects.filter(email ='login@example.com').exists())
        self.assertEqual(response.cookies.get('access_token').value,'')
        self.assertEqual(response.cookies.get('refresh_token').value,'')

class UserProfileUpdateTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="login@example.com",
            full_name="Login User",
            password="password123"
        )
        login_url = reverse('login')
        data = {
            'email': 'login@example.com',
            'password':'password123'
        }
        response = self.client.post(login_url,data,format='json')
        self.client.cookies['access_token'] = response.cookies.get('access_token').value
        self.client.cookies['refresh_token'] = response.cookies.get('refresh_token').value
    def test_user_can_update_profile(self):
        update_profile_url = reverse('profile_update')
        data = {
            'full_name': 'Profile User',
            'password':'newpassword123'
        }
        response =self.client.put(update_profile_url,data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'],'Profile User')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

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
