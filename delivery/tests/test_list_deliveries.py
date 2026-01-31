from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import datetime, timedelta

from delivery.models import Delivery
from delivery_auth.models import AuthUser


class ListDeliveriesTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create admin user
        self.admin_user = AuthUser.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            role='admin',
            first_name='Admin',
            last_name='User'
        )

        # Create partner user
        self.partner_user = AuthUser.objects.create_user(
            email='partner@test.com',
            password='testpass123',
            role='partner',
            first_name='Partner',
            last_name='User'
        )

        # Create deliveries created by partner
        self.delivery1 = Delivery.objects.create(
            product_name='Laptop',
            status='PENDING',
            delivery_date=datetime.now().date() + timedelta(days=7),
            delivery_address='123 Main St',
            created_by=self.partner_user
        )

        # Create delivery assigned to admin
        self.delivery2 = Delivery.objects.create(
            product_name='Phone',
            status='ASSIGNED',
            delivery_date=datetime.now().date() + timedelta(days=5),
            delivery_address='456 Oak Ave',
            created_by=self.partner_user,
            assigned_to=self.admin_user
        )

        self.url = reverse('list_deliveries')

    def test_list_deliveries_without_role(self):
        """Test listing deliveries without role parameter"""
        self.client.force_authenticate(user=self.partner_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Please select a role')

    def test_list_deliveries_invalid_role(self):
        """Test listing deliveries with invalid role"""
        self.client.force_authenticate(user=self.partner_user)

        response = self.client.get(self.url, {'role': 'invalid'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "Invalid role. Must be 'partner' or 'admin'")

    def test_list_deliveries_as_partner(self):
        """Test partner viewing their created deliveries"""
        self.client.force_authenticate(user=self.partner_user)

        response = self.client.get(self.url, {'role': 'partner'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_deliveries_as_admin(self):
        """Test admin viewing assigned deliveries"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.url, {'role': 'admin'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['product_name'], 'Phone')

    def test_list_deliveries_with_search(self):
        """Test searching deliveries"""
        self.client.force_authenticate(user=self.partner_user)

        response = self.client.get(self.url, {'role': 'partner', 'search': 'Laptop'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['product_name'], 'Laptop')

    def test_list_deliveries_unauthenticated(self):
        """Test listing deliveries without authentication"""
        response = self.client.get(self.url, {'role': 'partner'})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)