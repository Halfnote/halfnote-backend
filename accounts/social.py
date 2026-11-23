import hashlib
import logging
import time
from dataclasses import dataclass

import jwt
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

APPLE_ISSUER = 'https://appleid.apple.com'
GOOGLE_ISSUERS = ['accounts.google.com', 'https://accounts.google.com']

_apple_keys = jwt.PyJWKClient(f'{APPLE_ISSUER}/auth/keys')
_google_keys = jwt.PyJWKClient('https://www.googleapis.com/oauth2/v3/certs')


class InvalidToken(Exception):
    pass


class AppleUnavailable(Exception):
    pass


@dataclass(frozen=True)
class VerifiedIdentity:
    subject: str
    email: str
    email_verified: bool
    name: str


def _decode(token, keys, audience, issuer):
    try:
        key = keys.get_signing_key_from_jwt(token).key
        return jwt.decode(token, key, algorithms=['RS256'], audience=audience, issuer=issuer)
    except jwt.PyJWTError as e:
        raise InvalidToken(str(e)) from e


def _verified(claims):
    # Apple sends email_verified as the string "true"; Google sends a bool.
    return VerifiedIdentity(
        subject=claims['sub'],
        email=(claims.get('email') or '').lower(),
        email_verified=str(claims.get('email_verified')).lower() == 'true',
        # Google puts the name in the token; Apple sends it to the app instead, so the app posts it as `name`.
        name=claims.get('name') or '',
    )


def verify_apple(identity_token, nonce):
    claims = _decode(identity_token, _apple_keys, settings.APPLE_BUNDLE_ID, APPLE_ISSUER)
    # The app hands Apple sha256(nonce) and sends us the raw nonce, so a stolen token can't be replayed with another nonce.
    if claims.get('nonce') != hashlib.sha256(nonce.encode()).hexdigest():
        raise InvalidToken('nonce mismatch')
    return _verified(claims)


def verify_google(id_token):
    claims = _decode(id_token, _google_keys, settings.GOOGLE_CLIENT_IDS, GOOGLE_ISSUERS)
    return _verified(claims)


def _apple_client_secret():
    now = int(time.time())
    return jwt.encode(
        {'iss': settings.APPLE_TEAM_ID, 'iat': now, 'exp': now + 300, 'aud': APPLE_ISSUER, 'sub': settings.APPLE_BUNDLE_ID},
        settings.APPLE_PRIVATE_KEY,
        algorithm='ES256',
        headers={'kid': settings.APPLE_KEY_ID},
    )


def apple_refresh_token(authorization_code):
    """Exchange the one-time code for a refresh token, kept only so account deletion can revoke it."""
    if not settings.APPLE_PRIVATE_KEY:
        return ''
    data = {
        'client_id': settings.APPLE_BUNDLE_ID,
        'client_secret': _apple_client_secret(),
        'code': authorization_code,
        'grant_type': 'authorization_code',
    }
    try:
        response = requests.post(f'{APPLE_ISSUER}/auth/token', data=data, timeout=10)
        response.raise_for_status()
        return response.json().get('refresh_token', '')
    except requests.RequestException as e:
        logger.warning('Apple code exchange failed: %s', e)
        return ''


def revoke_apple(refresh_token):
    """Raises AppleUnavailable when a retry could work; a flat rejection from Apple is only logged."""
    if not (refresh_token and settings.APPLE_PRIVATE_KEY):
        return
    data = {
        'client_id': settings.APPLE_BUNDLE_ID,
        'client_secret': _apple_client_secret(),
        'token': refresh_token,
        'token_type_hint': 'refresh_token',
    }
    try:
        response = requests.post(f'{APPLE_ISSUER}/auth/revoke', data=data, timeout=10)
    except requests.RequestException as e:
        raise AppleUnavailable(str(e)) from e
    if response.status_code == 429 or response.status_code >= 500:
        raise AppleUnavailable(f'Apple returned {response.status_code}')
    if not response.ok:
        logger.warning('Apple token revoke failed: %s %s', response.status_code, response.text)
