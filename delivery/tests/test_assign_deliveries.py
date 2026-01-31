from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from datetime import datetime, timedelta

from delivery.models import Delivery
from delivery_auth.models import AuthUser


class AssignDeliveriesTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create super admin user
        self.super_admin = AuthUser.objects.create_user(
            email='superadmin@test.com',
            password='testpass123',
            role='super_admin',
            first_name='Super',
            last_name='Admin'
        )

        # Create admin user
        self.admin_user = AuthUser.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            role='admin',
            first_name='Admin',
            last_name='User'
        )

        # Create non-admin user
        self.partner_user = AuthUser.objects.create_user(
            email='partner@test.com',
            password='testpass123',
            role='partner',
            first_name='Partner',
            last_name='User'
        )

        # Create delivery with required fields
        self.delivery = Delivery.objects.create(
            product_name='Test Product',
            status='PENDING',
            delivery_date=datetime.now().date() + timedelta(days=7)
            # Add other required fields here if needed
        )

        self.url = reverse('assign_deliveries', kwargs={'pk': self.delivery.id})

    def test_assign_delivery_success(self):
        """Test successful delivery assignment"""
        self.client.force_authenticate(user=self.super_admin)

        data = {'assigned_to': self.admin_user.id}
        response = self.client.patch(self.url, data, format='json')

        def test_assign_delivery_success(self):
            """Test successful delivery assignment"""
            self.client.force_authenticate(user=self.super_admin)

            data = {'assigned_to': self.admin_user.id}
            response = self.client.patch(self.url, data, format='json')

            print(f"Status: {response.status_code}")
            print(f"Response: {response.data}")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['message'], 'Delivery assigned to admin successfully')

            self.delivery.refresh_from_db()
            self.assertEqual(self.delivery.assigned_to.id, self.admin_user.id)
            self.assertEqual(self.delivery.status, 'ASSIGNED')

    def test_assign_delivery_missing_assigned_to(self):
        """Test assignment without assigned_to field"""
        self.client.force_authenticate(user=self.super_admin)

        response = self.client.patch(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'assigned_to field is required')

    def test_assign_delivery_not_found(self):
        """Test assignment to non-existent delivery"""
        self.client.force_authenticate(user=self.super_admin)

        url = reverse('assign_deliveries', kwargs={'pk': 9999})
        data = {'assigned_to': self.admin_user.id}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Delivery not found')

    def test_assign_delivery_user_not_found(self):
        """Test assignment to non-existent user"""
        self.client.force_authenticate(user=self.super_admin)

        data = {'assigned_to': 9999}
        response = self.client.patch(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'User not found')

    def test_assign_delivery_to_non_admin(self):
        """Test assignment to non-admin user"""
        self.client.force_authenticate(user=self.super_admin)

        data = {'assigned_to': self.partner_user.id}
        response = self.client.patch(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'User is not an admin')