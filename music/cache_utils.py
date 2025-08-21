"""
Halfnote Cache Utils
Simple caching utilities for improved performance
"""

from django.core.cache import cache


def cache_key_for_user_reviews(username):
    """Generate cache key for user reviews"""
    return f"user_reviews_{username}"


def cache_key_for_album_details(discogs_id):
    """Generate cache key for album details"""
    return f"album_details_{discogs_id}"


def cache_key_for_activity_feed(user_id):
    """Generate cache key for activity feed"""
    return f"activity_feed_{user_id}"


def cache_key_for_search_results(query):
    """Generate cache key for search results"""
    # Simple hash of query for cache key
    import hashlib
    query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
    return f"search_{query_hash}"


def invalidate_user_cache(username):
    """Clear user-related caches"""
    cache.delete_many([
        f"user_reviews_{username}",
        f"user_profile_{username}",
        f"user_lists_{username}",
    ])


def invalidate_album_cache(discogs_id):
    """Clear album-related caches"""
    cache.delete(f"album_details_{discogs_id}")


def cache_expensive_query(cache_key, query_func, timeout=300):
    """Cache the result of an expensive query"""
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    result = query_func()
    cache.set(cache_key, result, timeout)
    return result