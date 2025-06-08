from django.core.cache import cache
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings
import time

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = 5  # requests per minute
        self.window = 60  # seconds

    def __call__(self, request):
        # Skip rate limiting for non-API routes
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Create cache key
        cache_key = f'ratelimit_{ip}'

        # Get current requests count
        requests = cache.get(cache_key, [])
        now = time.time()

        # Remove old requests
        requests = [req_time for req_time in requests if now - req_time < self.window]

        # Check if rate limit exceeded
        if len(requests) >= self.rate_limit:
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again later.'
            }, status=429)

        # Add current request
        requests.append(now)
        cache.set(cache_key, requests, self.window)

        return self.get_response(request)

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip JWT validation for non-API routes and auth endpoints
        if not request.path.startswith('/api/') or request.path in ['/api/accounts/login/', '/api/accounts/register/']:
            return self.get_response(request)

        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'error': 'Missing or invalid Authorization header'
            }, status=401)

        token = auth_header.split(' ')[1]
        try:
            # Validate token
            AccessToken(token)
        except (InvalidToken, TokenError):
            return JsonResponse({
                'error': 'Invalid or expired token'
            }, status=401)

        return self.get_response(request) 