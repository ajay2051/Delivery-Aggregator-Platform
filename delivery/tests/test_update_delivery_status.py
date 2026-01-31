from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import datetime, timedelta

from delivery.models import Delivery
from delivery_auth.models import AuthUser


class UpdateDeliveryStatusTestCase(TestCase):
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

        # Create delivery in CREATED status
        self.delivery_created = Delivery.objects.create(
            product_name='Laptop',
            status='CREATED',
            delivery_date=datetime.now().date() + timedelta(days=7),
            delivery_address='123 Main St',
            created_by=self.partner_user
        )

        # Create delivery in ASSIGNED status
        self.delivery_assigned = Delivery.objects.create(
            product_name='Phone',
            status='ASSIGNED',
            delivery_date=datetime.now().date() + timedelta(days=5),
            delivery_address='456 Oak Ave',
            created_by=self.partner_user,
            assigned_to=self.admin_user
        )

        # Create delivery in COMPLETED status (terminal state)
        self.delivery_completed = Delivery.objects.create(
            product_name='Tablet',
            status='COMPLETED',
            delivery_date=datetime.now().date() + timedelta(days=3),
            delivery_address='789 Pine Rd',
            created_by=self.partner_user,
            assigned_to=self.admin_user
        )

    def test_update_status_success_assigned_to_in_transit(self):
        """Test valid transition from ASSIGNED to IN_TRANSIT"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('update_deliveries', kwargs={'pk': self.delivery_assigned.id})
        data = {'status': 'IN_TRANSIT'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.delivery_assigned.refresh_from_db()
        self.assertEqual(self.delivery_assigned.status, 'IN_TRANSIT')

    def test_update_status_missing_status_field(self):
        """Test update without status field"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('update_deliveries', kwargs={'pk': self.delivery_created.id})
        response = self.client.patch(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'status field is required')

    def test_update_status_invalid_transition(self):
        """Test invalid transition from CREATED to COMPLETED"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('update_deliveries', kwargs={'pk': self.delivery_created.id})
        data = {'status': 'COMPLETED'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)

    def test_update_status_terminal_state(self):
        """Test updating delivery in terminal state"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('update_deliveries', kwargs={'pk': self.delivery_completed.id})
        data = {'status': 'IN_TRANSIT'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('terminal state', response.data['message'].lower())

    def test_update_status_delivery_not_found(self):
        """Test updating non-existent delivery"""
        self.client.force_authenticate(user=self.admin_user)

        url = reverse('update_deliveries', kwargs={'pk': 9999})
        data = {'status': 'ASSIGNED'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Delivery not found')

    def test_update_status_unauthenticated(self):
        """Test unauthenticated user cannot update status"""
        url = reverse('update_deliveries', kwargs={'pk': self.delivery_created.id})
        data = {'status': 'ASSIGNED'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)