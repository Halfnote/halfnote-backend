import functools
import logging
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

def handle_api_errors(func):
    """Decorator to handle API errors consistently"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return Response(
                {'error': 'An error occurred processing your request'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return wrapper

def validate_params(*required_params):
    """Decorator to validate required request parameters"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(view_instance, request, *args, **kwargs):
            missing_params = [
                param for param in required_params
                if param not in request.query_params
            ]
            if missing_params:
                return Response(
                    {'error': f'Missing required parameters: {", ".join(missing_params)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return func(view_instance, request, *args, **kwargs)
        return wrapper
    return decorator

def cache_response(timeout=3600):
    """Decorator to cache view responses"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(view_instance, request, *args, **kwargs):
            # Create a cache key based on the function name and request parameters
            cache_key = f"{func.__name__}:{request.query_params.urlencode()}"
            cached_response = cache.get(cache_key)
            
            if cached_response is not None:
                return Response(cached_response)
            
            response = func(view_instance, request, *args, **kwargs)
            if response.status_code == 200:
                cache.set(cache_key, response.data, timeout=timeout)
            
            return response
        return wrapper
    return decorator 