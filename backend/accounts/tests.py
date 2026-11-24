from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import AuthUser, Customerprofile, Userprofile


class RegisterAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/accounts/auth/register/'
        self.valid_payload = {
            'username': 'newcustomer',
            'email': 'new@customer.com',
            'first_name': 'Juan',
            'last_name': 'Dela Cruz',
            'password': 'SecurePass123',
            'password_confirm': 'SecurePass123',
            'phone': '09171234567',
            'address': '123 Mandaue City, Cebu',
        }

    def _create_user(self, username, email, password):
        """Helper to create user with proper password hashing."""
        return AuthUser.objects.create(
            username=username,
            email=email,
            first_name='',
            last_name='',
            password=make_password(password),
            is_active=1,
            is_staff=0,
            is_superuser=0,
            date_joined=timezone.now(),
        )

    def test_register_success(self):
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'newcustomer')
        self.assertEqual(response.data['user']['role'], 'customer')

        # Verify profiles created
        user = AuthUser.objects.get(username='newcustomer')
        self.assertTrue(Customerprofile.objects.filter(user=user).exists())
        self.assertTrue(Userprofile.objects.filter(user=user, is_vendor=0).exists())

    def test_register_duplicate_username(self):
        self._create_user('existing', 'e@e.com', 'pass')
        payload = {**self.valid_payload, 'username': 'existing'}
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_duplicate_email(self):
        self._create_user('u1', 'exists@test.com', 'pass')
        payload = {**self.valid_payload, 'email': 'exists@test.com'}
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_register_password_mismatch(self):
        payload = {**self.valid_payload, 'password_confirm': 'DifferentPass123'}
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)

    def test_register_short_password(self):
        payload = {**self.valid_payload, 'password': 'short', 'password_confirm': 'short'}
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_missing_phone(self):
        payload = {**self.valid_payload}
        del payload['phone']
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data)
