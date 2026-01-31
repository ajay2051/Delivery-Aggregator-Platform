from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import datetime, timedelta

from delivery.models import Delivery
from delivery_auth.models import AuthUser


class RequestDeliveriesTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create partner user
        self.partner_user = AuthUser.objects.create_user(
            email='partner@test.com',
            password='testpass123',
            role='partner',
            first_name='Partner',
            last_name='User'
        )

        # Create admin user (non-partner)
        self.admin_user = AuthUser.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            role='admin',
            first_name='Admin',
            last_name='User'
        )

        self.url = reverse('request_deliveries')

        self.valid_data = {
            'delivery_date': (datetime.now().date() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'product_name': 'Test Product',
            'delivery_address': '123 Test St',
            'status': 'CREATED'
        }

    def test_request_delivery_success(self):
        """Test successful delivery request"""
        self.client.force_authenticate(user=self.partner_user)

        response = self.client.post(self.url, self.valid_data, format='json')

        print(f"Status: {response.status_code}")
        print(f"Response: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Delivery Request Success...🤗🤗')
        self.assertIn('data', response.data)

        # Verify delivery was created
        delivery = Delivery.objects.filter(created_by=self.partner_user).first()
        self.assertIsNotNone(delivery)
        self.assertEqual(delivery.product_name, 'Test Product')

    def test_request_delivery_missing_required_field(self):
        """Test delivery request without required field"""
        self.client.force_authenticate(user=self.partner_user)

        invalid_data = self.valid_data.copy()
        del invalid_data['delivery_date']

        response = self.client.post(self.url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_delivery_duplicate_request(self):
        """Test duplicate delivery request"""
        self.client.force_authenticate(user=self.partner_user)

        # First request
        response1 = self.client.post(self.url, self.valid_data, format='json')

        print(f"First request status: {response1.status_code}")
        print(f"First request response: {response1.data}")

        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Duplicate request with same data
        response2 = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response2.data['message'], 'Duplicate request detected...👿👿')

    def test_request_delivery_non_partner_forbidden(self):
        """Test non-partner user cannot request delivery"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_request_delivery_unauthenticated(self):
        """Test unauthenticated user cannot request delivery"""
        response = self.client.post(self.url, self.valid_data, format='json')

        # Permission classes check authentication first, so it returns 403 instead of 401
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)