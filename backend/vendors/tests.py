from accounts.models import AuthUser, Userprofile
from catalog.models import Vendor
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from vendors.models import PosVendor


class AdminVendorAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Market Admin user
        self.admin = AuthUser.objects.create(
            username='marketadmin',
            email='admin@market.com',
            first_name='Market',
            last_name='Admin',
            password=make_password('adminpass123'),
            is_active=1,
            is_staff=1,
            is_superuser=0,
            date_joined=timezone.now(),
        )
        Userprofile.objects.create(
            user=self.admin,
            is_vendor=0,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        # Create regular customer
        self.customer = AuthUser.objects.create(
            username='customer1',
            email='cust@test.com',
            first_name='Customer',
            last_name='One',
            password=make_password('custpass123'),
            is_active=1,
            is_staff=0,
            is_superuser=0,
            date_joined=timezone.now(),
        )
        Userprofile.objects.create(
            user=self.customer,
            is_vendor=0,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        self.list_url = '/api/vendors/admin/'
        self.create_url = '/api/vendors/admin/create/'

        self.valid_vendor_data = {
            'username': 'vendor_rosa',
            'email': 'rosa@vendor.com',
            'first_name': 'Rosa',
            'last_name': 'Vegetables',
            'password': 'VendorPass123',
            'name': "Rosa's Fresh Vegetables",
            'stall_location': 'Stall A-12',
            'market_section': 'Vegetables Section',
            'contact_phone': '09171112233',
            'contact_email': 'rosa@stall.com',
        }

    def authenticate_admin(self):
        self.client.force_authenticate(user=self.admin)

    def authenticate_customer(self):
        self.client.force_authenticate(user=self.customer)

    def test_admin_can_list_vendors(self):
        self.authenticate_admin()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_customer_cannot_list_vendors(self):
        self.authenticate_customer()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_list_vendors(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_create_vendor(self):
        self.authenticate_admin()
        response = self.client.post(self.create_url, self.valid_vendor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], "Rosa's Fresh Vegetables")
        self.assertEqual(response.data['user']['username'], 'vendor_rosa')

        # Verify all models created
        vendor = Vendor.objects.get(name="Rosa's Fresh Vegetables")
        self.assertEqual(vendor.user.username, 'vendor_rosa')
        self.assertTrue(Userprofile.objects.filter(user=vendor.user, is_vendor=1).exists())
        self.assertTrue(PosVendor.objects.filter(catalog_vendor=vendor).exists())

    def test_admin_create_vendor_duplicate_username(self):
        self.authenticate_admin()
        # Create once
        self.client.post(self.create_url, self.valid_vendor_data, format='json')
        # Try again
        response = self.client.post(self.create_url, self.valid_vendor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_admin_create_vendor_duplicate_email(self):
        self.authenticate_admin()
        self.client.post(self.create_url, self.valid_vendor_data, format='json')
        # Different username, same email
        data = {**self.valid_vendor_data, 'username': 'vendor_rosa2'}
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_customer_cannot_create_vendor(self):
        self.authenticate_customer()
        response = self.client.post(self.create_url, self.valid_vendor_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_deactivate_vendor(self):
        self.authenticate_admin()
        create_resp = self.client.post(self.create_url, self.valid_vendor_data, format='json')
        vendor_id = create_resp.data['id']

        deactivate_url = f'/api/vendors/admin/{vendor_id}/deactivate/'
        response = self.client.post(deactivate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        vendor = Vendor.objects.get(id=vendor_id)
        self.assertEqual(vendor.is_active, 0)
        self.assertEqual(vendor.user.is_active, 0)
