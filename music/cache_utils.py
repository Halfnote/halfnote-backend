import hashlib
from django.core.cache import cache
from django.conf import settings
from functools import wraps
import json


def cache_key_for_user_reviews(username):
    """Generate cache key for user reviews"""
    return f"user_reviews:{username}"


def cache_key_for_album_details(discogs_id):
    """Generate cache key for album details"""
    return f"album_details:{discogs_id}"


def cache_key_for_activity_feed(user_id, feed_type):
    """Generate cache key for activity feed"""
    return f"activity_feed:{user_id}:{feed_type}"


def cache_key_for_search_results(query):
    """Generate cache key for search results"""
    query_hash = hashlib.md5(query.encode()).hexdigest()
    return f"search_results:{query_hash}"


def invalidate_user_cache(username):
    """Invalidate all user-related cache entries"""
    cache.delete(cache_key_for_user_reviews(username))
    # Could expand to invalidate other user-related caches


def invalidate_album_cache(discogs_id):
    """Invalidate album-related cache entries"""
    cache.delete(cache_key_for_album_details(discogs_id))


def cached_view(timeout=None):
    """
    Decorator to cache view results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"view:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout or settings.CACHE_TTL)
            return result
        return wrapper
    return decorator


def cache_expensive_query(cache_key, query_func, timeout=None):
    """
    Generic function to cache expensive database queries
    """
    result = cache.get(cache_key)
    if result is not None:
        return result
    
    result = query_func()
    cache.set(cache_key, result, timeout or settings.CACHE_TTL)
    return result 