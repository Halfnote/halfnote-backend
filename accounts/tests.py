from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

TOKEN_REFRESH_URL = '/api/accounts/token/refresh/'


class TokenRefreshTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='refreshuser', password='testpass123')
        self.refresh = RefreshToken.for_user(self.user)

    def test_valid_refresh_token_returns_new_token_pair(self):
        response = self.client.post(TOKEN_REFRESH_URL, {'refresh': str(self.refresh)}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data), {'access', 'refresh'})

    def test_invalid_refresh_token_is_rejected(self):
        response = self.client.post(TOKEN_REFRESH_URL, {'refresh': 'not-a-real-token'}, format='json')
        self.assertEqual(response.status_code, 401)
