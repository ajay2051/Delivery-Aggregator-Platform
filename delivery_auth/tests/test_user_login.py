from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import datetime, timedelta

from delivery_auth.models import AuthUser


class UserLoginViewTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.url = reverse('login')

        # Create a verified user
        self.user = AuthUser.objects.create_user(
            email='test@example.com',
            password='Password123!',
            first_name='Test',
            last_name='User',
            role='partner',
            is_verified=True
        )

        # Create an unverified user
        self.unverified_user = AuthUser.objects.create_user(
            email='unverified@example.com',
            password='Password123!',
            first_name='Unverified',
            last_name='User',
            role='partner',
            is_verified=False
        )

        self.valid_credentials = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }

    def test_login_success(self):
        """Test successful user login"""
        response = self.client.post(self.url, self.valid_credentials, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['message'], 'Successfully Logged In...🙂🙂')
        self.assertEqual(response.data['user']['email'], 'test@example.com')

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        invalid_credentials = {
            'email': 'test@example.com',
            'password': 'WrongPassword123!'
        }

        response = self.client.post(self.url, invalid_credentials, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        nonexistent_credentials = {
            'email': 'nonexistent@example.com',
            'password': 'Password123!'
        }

        response = self.client.post(self.url, nonexistent_credentials, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unverified_user(self):
        """Test login with unverified user"""
        unverified_credentials = {
            'email': 'unverified@example.com',
            'password': 'Password123!'
        }

        response = self.client.post(self.url, unverified_credentials, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_email(self):
        """Test login without email"""
        invalid_data = {
            'password': 'Password123!'
        }

        response = self.client.post(self.url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_password(self):
        """Test login without password"""
        invalid_data = {
            'email': 'test@example.com'
        }

        response = self.client.post(self.url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)