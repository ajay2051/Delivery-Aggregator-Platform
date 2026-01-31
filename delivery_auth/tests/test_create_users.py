from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import datetime, timedelta

from delivery_auth.models import AuthUser


class CreateUserViewTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.url = reverse('create_user')

        self.valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'Password123!',
            'user_number': '+9779852314785',
            'country': 'Nepal',
            'date_of_birth': (datetime.now().date() - timedelta(days=365*20)).strftime('%Y-%m-%d'),
            'role': 'partner'
        }

    def test_create_user_success(self):
        """Test successful user creation"""
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)

        # Verify user was created
        user = AuthUser.objects.filter(email=self.valid_data['email']).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')

    def test_create_user_missing_required_field(self):
        """Test user creation without required field"""
        invalid_data = self.valid_data.copy()
        del invalid_data['email']

        response = self.client.post(self.url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email"""
        # Create first user
        self.client.post(self.url, self.valid_data, format='json')

        # Try to create second user with same email
        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_invalid_email(self):
        """Test user creation with invalid email"""
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid-email'

        response = self.client.post(self.url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_weak_password(self):
        """Test user creation with weak password"""
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = 'weak'

        response = self.client.post(self.url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)