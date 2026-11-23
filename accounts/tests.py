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


import hashlib
import time
from types import SimpleNamespace
from unittest import mock

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from django.test import override_settings
from django.utils import timezone

from accounts import social

SIGNING_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
APPLE_P8 = ec.generate_private_key(ec.SECP256R1()).private_bytes(
    serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
).decode()
NONCE = 'raw-nonce'


def id_token(issuer, audience, sub, **claims):
    now = int(time.time())
    return jwt.encode({'iss': issuer, 'aud': audience, 'sub': sub, 'iat': now, 'exp': now + 600, **claims}, SIGNING_KEY, algorithm='RS256')


def apple_token(sub, audience='com.halfnote.test', nonce=NONCE, **claims):
    return id_token(social.APPLE_ISSUER, audience, sub, nonce=hashlib.sha256(nonce.encode()).hexdigest(), **claims)


def google_token(sub, **claims):
    return id_token('https://accounts.google.com', 'google-ios-client', sub, **claims)


def apple_http(*args, **kwargs):
    return SimpleNamespace(ok=True, json=lambda: {'refresh_token': 'apple-refresh'}, status_code=200, text='')


@override_settings(
    APPLE_BUNDLE_ID='com.halfnote.test', APPLE_TEAM_ID='TEAM', APPLE_KEY_ID='KEY', APPLE_PRIVATE_KEY=APPLE_P8,
    GOOGLE_CLIENT_IDS=['google-ios-client'],
)
class SignInTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        public = SimpleNamespace(key=SIGNING_KEY.public_key())
        for keys in (social._apple_keys, social._google_keys):
            patcher = mock.patch.object(keys, 'get_signing_key_from_jwt', return_value=public)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.apple_http = mock.patch('accounts.social.requests.post', side_effect=apple_http).start()
        self.addCleanup(mock.patch.stopall)

    def apple(self, token, **extra):
        body = {'identity_token': token, 'authorization_code': 'code', 'nonce': NONCE, **extra}
        return self.client.post('/api/accounts/auth/apple/', body, format='json')

    def google(self, token):
        return self.client.post('/api/accounts/auth/google/', {'id_token': token}, format='json')

    def test_register_with_email_then_login_by_email(self):
        response = self.client.post('/api/accounts/register/', {'email': 'Dee@Example.com', 'password': 'Pw1234567!'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['needs_onboarding'])
        self.assertTrue(response.data['user']['username'].isalnum())

        login = self.client.post('/api/accounts/login/', {'login': 'dee@example.com', 'password': 'Pw1234567!'}, format='json')
        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.data['user']['id'], response.data['user']['id'])

    def test_register_rejects_weak_password(self):
        response = self.client.post('/api/accounts/register/', {'email': 'dee@example.com', 'password': 'password'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data['fields'])

    def test_google_prefills_name_from_token(self):
        response = self.google(google_token('g-2', name='Dee Dee'))
        self.assertEqual(response.data['user']['name'], 'Dee Dee')

    def test_register_rejects_taken_email_case_insensitively(self):
        User.objects.create_user(username='dee', email='dee@example.com', password='x')
        response = self.client.post('/api/accounts/register/', {'email': 'DEE@example.com', 'password': 'Pw1234567!'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['fields'], {'email': 'taken'})

    def test_existing_username_login_still_works(self):
        User.objects.create_user(username='olduser', password='pw', onboarded_at=timezone.now())
        response = self.client.post('/api/accounts/login/', {'username': 'OldUser', 'password': 'pw'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['needs_onboarding'])
        self.assertEqual(self.client.post('/api/accounts/login/', {'login': 'olduser', 'password': 'no'}, format='json').status_code, 401)

    def test_apple_creates_then_logs_in_same_user(self):
        first = self.apple(apple_token('apple-1', email='a@privaterelay.appleid.com', email_verified='true'), name='Dee')
        self.assertEqual(first.status_code, 201)
        self.assertTrue(first.data['needs_onboarding'])
        self.assertEqual(first.data['user']['name'], 'Dee')

        again = self.apple(apple_token('apple-1'))
        self.assertEqual(again.status_code, 200)
        self.assertEqual(again.data['user']['id'], first.data['user']['id'])
        self.assertEqual(User.objects.count(), 1)

    def test_apple_rejects_wrong_nonce_and_wrong_audience(self):
        self.assertEqual(self.apple(apple_token('apple-1', nonce='other')).status_code, 401)
        self.assertEqual(self.apple(apple_token('apple-1', audience='com.someone.else')).status_code, 401)
        self.assertEqual(User.objects.count(), 0)

    def test_google_links_to_existing_account_on_verified_email(self):
        existing = User.objects.create_user(username='dee', email='dee@example.com', password='x', onboarded_at=timezone.now())
        response = self.google(google_token('g-1', email='Dee@example.com', email_verified=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['id'], existing.id)
        self.assertFalse(response.data['needs_onboarding'])

    def test_google_unverified_email_never_links(self):
        User.objects.create_user(username='dee', email='dee@example.com', password='x')
        response = self.google(google_token('g-1', email='dee@example.com', email_verified=False))
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data['user']['username'], 'dee')

    def test_delete_me_revokes_apple_token_and_removes_user(self):
        token = self.apple(apple_token('apple-1')).data['access_token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.apple_http.reset_mock()

        self.assertEqual(self.client.delete('/api/accounts/me/').status_code, 204)
        self.assertEqual(User.objects.count(), 0)
        revoke = self.apple_http.call_args
        self.assertTrue(revoke.args[0].endswith('/auth/revoke'))
        self.assertEqual(revoke.kwargs['data']['token'], 'apple-refresh')


from music.models import Album
from music.onboarding import ONBOARDING_DISCOGS_IDS


class OnboardingStepTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='user00000000', email='new@example.com', password='x')
        self.client.force_authenticate(self.user)
        for i in range(5):
            Album.objects.create(title=f'A{i}', artist='X', discogs_id=str(i))

    def put_profile(self, body):
        return self.client.put('/api/accounts/profile/', body, format='json')

    def put_favorites(self, ids):
        return self.client.put('/api/accounts/favorite-albums/', {'discogs_ids': ids}, format='json')

    def test_full_onboarding_then_login_skips_it(self):
        self.assertEqual(self.put_profile({'name': 'Dee', 'username': 'ddd'}).status_code, 200)
        self.assertEqual(self.put_favorites(['0', '1', '2', '3']).status_code, 200)
        self.assertEqual(self.put_profile({'avatar_preset': 'cat', 'onboarded': True}).status_code, 200)

        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.onboarded_at)
        self.assertEqual(self.user.avatar_preset, 'cat')
        self.assertEqual(self.user.favorite_albums.count(), 4)

    def test_taken_username_and_unknown_face_are_field_errors(self):
        User.objects.create_user(username='ddd', password='x')
        self.assertIn('username', self.put_profile({'username': 'ddd'}).data['fields'])
        self.assertIn('avatar_preset', self.put_profile({'avatar_preset': 'dragon'}).data['fields'])

    def test_unfinished_users_are_hidden_publicly(self):
        anon = APIClient()
        self.assertEqual(anon.get('/api/accounts/users/user00000000/').status_code, 404)
        self.assertEqual(anon.get('/api/accounts/users/search/?q=user0').data['users'], [])

        self.put_profile({'onboarded': True})
        public = anon.get('/api/accounts/users/user00000000/')
        self.assertEqual(public.status_code, 200)
        self.assertNotIn('email', public.data)

    def test_favorites_put_replaces_set_and_caps_at_four(self):
        self.put_favorites(['0', '1'])
        self.assertEqual(self.put_favorites(['2']).status_code, 200)
        self.assertEqual(list(self.user.favorite_albums.values_list('discogs_id', flat=True)), ['2'])
        self.assertEqual(self.put_favorites(['0', '1', '2', '3', '4']).status_code, 400)
        self.assertEqual(self.put_favorites([]).status_code, 200)
        self.assertEqual(self.user.favorite_albums.count(), 0)

    def test_favorites_post_caps_at_four(self):
        self.put_favorites(['0', '1', '2', '3'])
        response = self.client.post('/api/accounts/favorite-albums/', {'discogs_id': '4'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.user.favorite_albums.count(), 4)

    @mock.patch('music.views.ExternalMusicService.get_album_details', return_value=None)
    def test_unknown_album_is_rejected_without_saving(self, _):
        self.put_favorites(['0'])
        self.assertEqual(self.put_favorites(['0', 'nope']).status_code, 400)
        self.assertEqual(list(self.user.favorite_albums.values_list('discogs_id', flat=True)), ['0'])

    def test_onboarding_albums_lists_only_the_hand_picked_set(self):
        Album.objects.create(title='Melodrama', artist='Lorde', discogs_id=ONBOARDING_DISCOGS_IDS[0])
        albums = APIClient().get('/api/music/onboarding/albums/').data['albums']
        self.assertEqual([a['discogs_id'] for a in albums], [ONBOARDING_DISCOGS_IDS[0]])
        self.assertEqual(set(albums[0]), {'discogs_id', 'title', 'artist', 'year', 'cover_url'})
