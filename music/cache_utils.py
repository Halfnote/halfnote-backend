"""
Caching utilities for music app
Optimized for Vercel serverless environment
"""
import hashlib
from django.core.cache import cache
from django.conf import settings
from functools import wraps
import json
from typing import Any, Optional, List


def cache_key_for_user_reviews(username):
    """Generate cache key for user reviews"""
    return f"user_reviews:{username}"


def cache_key_for_album_details(discogs_id):
    """Generate cache key for album details"""
    return f"album_details:{discogs_id}"


def generate_cache_key(*args, **kwargs) -> str:
    """Generate a consistent cache key from arguments"""
    # Create a string representation of all arguments
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    
    # Create a hash for consistent key length
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return f"halfnote:{key_hash}"


def cache_key_for_activity_feed(user_id: int, feed_type: str) -> str:
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


def cache_activity_feed(user_id: int, feed_type: str, data: List[dict], timeout: int = 180) -> None:
    """Cache activity feed data (3 minute timeout by default)"""
    cache_key = cache_key_for_activity_feed(user_id, feed_type)
    cache.set(cache_key, data, timeout)


def get_cached_activity_feed(user_id: int, feed_type: str) -> Optional[List[dict]]:
    """Get cached activity feed data"""
    cache_key = cache_key_for_activity_feed(user_id, feed_type)
    return cache.get(cache_key)


def invalidate_activity_cache(user_id: int) -> None:
    """Invalidate all activity feed caches for a user"""
    feed_types = ['friends', 'you', 'incoming']
    for feed_type in feed_types:
        cache_key = cache_key_for_activity_feed(user_id, feed_type)
        cache.delete(cache_key)


def invalidate_user_related_caches(user_id: int) -> None:
    """Invalidate caches related to a specific user"""
    # Invalidate the user's own activity feeds
    invalidate_activity_cache(user_id)
    
    # Note: In a full implementation, you'd also invalidate feeds of followers
    # For simplicity, we'll let those expire naturally


def cache_user_following(user_id: int, following_ids: List[int], timeout: int = 600) -> None:
    """Cache user's following list (10 minute timeout)"""
    cache_key = f"user_following:{user_id}"
    cache.set(cache_key, following_ids, timeout)


def get_cached_user_following(user_id: int) -> Optional[List[int]]:
    """Get cached user following list"""
    cache_key = f"user_following:{user_id}"
    return cache.get(cache_key)


def cache_review_data(review_id: int, data: dict, timeout: int = 900) -> None:
    """Cache review data (15 minute timeout)"""
    cache_key = f"review:{review_id}"
    cache.set(cache_key, data, timeout)


def get_cached_review_data(review_id: int) -> Optional[dict]:
    """Get cached review data"""
    cache_key = f"review:{review_id}"
    return cache.get(cache_key)


def invalidate_review_cache(review_id: int) -> None:
    """Invalidate review cache"""
    cache_key = f"review:{review_id}"
    cache.delete(cache_key)


def cache_album_data(discogs_id: str, data: dict, timeout: int = 3600) -> None:
    """Cache album data from Discogs (1 hour timeout)"""
    cache_key = f"album:{discogs_id}"
    cache.set(cache_key, data, timeout)


def get_cached_album_data(discogs_id: str) -> Optional[dict]:
    """Get cached album data"""
    cache_key = f"album:{discogs_id}"
    return cache.get(cache_key)


class CacheManager:
    """
    Context manager for batch cache operations
    Useful for Vercel serverless functions where we want to minimize Redis calls
    """
    def __init__(self):
        self.operations = []
    
    def add_set(self, key: str, value: Any, timeout: int = 300):
        """Add a cache set operation"""
        self.operations.append(('set', key, value, timeout))
    
    def add_delete(self, key: str):
        """Add a cache delete operation"""
        self.operations.append(('delete', key))
    
    def execute(self):
        """Execute all cached operations"""
        if not self.operations:
            return

        sets = []
        deletes = []

        # Separate set and delete operations while safely unpacking tuples
        for op in self.operations:
            if op[0] == 'set':
                _, key, value, timeout = op
                sets.append((key, value, timeout))
            elif op[0] == 'delete':
                _, key = op
                deletes.append(key)

        # Execute set operations with individual timeouts
        for key, value, timeout in sets:
            cache.set(key, value, timeout)

        # Execute delete operations
        if deletes:
            cache.delete_many(deletes)

        self.operations.clear()


def smart_cache_activity_feed(user, feed_type: str, force_refresh: bool = False):
    """
    Smart caching for activity feeds with automatic invalidation
    Returns cached data if available and fresh, otherwise fetches and caches new data
    """
    cache_key = cache_key_for_activity_feed(user.id, feed_type)
    
    if not force_refresh:
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
    
    # If no cache hit, we need to generate the data
    # This would be called from the view after optimization
    return None  # View will handle the actual data generation


def setup_cache_table():
    """
    Setup database cache table for environments without Redis
    Run this during deployment
    """
    from django.core.management import call_command
    try:
        call_command('createcachetable')
        print("Cache table created successfully")
    except Exception as e:
        print(f"Cache table setup failed: {e}")


# Decorator for caching expensive operations
def cached_result(cache_key_func, timeout=300):
    """
    Decorator to cache the result of expensive functions
    Usage: @cached_result(lambda x: f"expensive_op:{x}", timeout=600)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = cache_key_func(*args, **kwargs)
            result = cache.get(cache_key)
            
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator 


def invalidate_profile_cache(user_id: int, username: str) -> None:
    """Invalidate all profile-related cache entries for a user"""
    # Invalidate user reviews cache
    cache.delete(cache_key_for_user_reviews(username))
    
    # Invalidate profile-specific cache keys
    cache.delete(f"profile:{user_id}")
    cache.delete(f"profile:{username}")
    cache.delete(f"user_profile:{user_id}")
    cache.delete(f"user_profile:{username}")
    
    # Invalidate user following cache
    cache.delete(f"user_following:{user_id}")
    cache.delete(f"user_followers:{user_id}")


def invalidate_user_related_caches_on_profile_update(user_id: int, username: str) -> None:
    """Comprehensive cache invalidation when a user profile is updated"""
    # Invalidate profile caches
    invalidate_profile_cache(user_id, username)
    
    # Invalidate activity feed caches (user's own feeds and incoming feeds)
    invalidate_activity_cache(user_id)
    
    # Invalidate followers' activity feeds since profile changes affect their feeds
    # Note: This is a simplified approach - in production you might want to be more selective
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        # Invalidate activity feeds of users who follow this user
        follower_ids = user.followers.values_list('id', flat=True)
        for follower_id in follower_ids:
            invalidate_activity_cache(follower_id)
    except User.DoesNotExist:
        pass


def invalidate_on_user_interaction(acting_user_id: int, target_user_id: int = None, review_owner_id: int = None) -> None:
    """
    Comprehensive cache invalidation for any user interaction that affects activity feeds.
    This includes likes, comments, follows, unfollows, etc.
    
    Args:
        acting_user_id: ID of the user performing the action
        target_user_id: ID of the user being targeted (for follows/unfollows)
        review_owner_id: ID of the user who owns the review being liked/commented on
    """
    # Always invalidate the acting user's activity cache
    invalidate_activity_cache(acting_user_id)
    
    # If there's a target user (follow/unfollow), invalidate their incoming feed
    if target_user_id:
        invalidate_activity_cache(target_user_id)
    
    # If there's a review owner (like/comment), invalidate their incoming feed
    if review_owner_id and review_owner_id != acting_user_id:
        invalidate_activity_cache(review_owner_id)
    
    # Invalidate friends' feeds who follow the acting user
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        acting_user = User.objects.get(id=acting_user_id)
        # Invalidate activity feeds of users who follow the acting user
        follower_ids = acting_user.followers.values_list('id', flat=True)
        for follower_id in follower_ids:
            invalidate_activity_cache(follower_id)
    except User.DoesNotExist:
        pass


def invalidate_on_review_action(review_id: int, acting_user_id: int) -> None:
    """
    Cache invalidation specifically for review-related actions (like, unlike, comment)
    
    Args:
        review_id: ID of the review being acted upon
        acting_user_id: ID of the user performing the action
    """
    from music.models import Review
    try:
        review = Review.objects.select_related('user').get(id=review_id)
        review_owner_id = review.user.id
        
        # Use the comprehensive invalidation function
        invalidate_on_user_interaction(
            acting_user_id=acting_user_id,
            review_owner_id=review_owner_id
        )
        
        # Also invalidate the specific review cache
        invalidate_review_cache(review_id)
        
    except Review.DoesNotExist:
        # Still invalidate the acting user's cache even if review not found
        invalidate_activity_cache(acting_user_id)


def invalidate_on_follow_action(acting_user_id: int, target_user_id: int) -> None:
    """
    Cache invalidation specifically for follow/unfollow actions
    
    Args:
        acting_user_id: ID of the user doing the following/unfollowing
        target_user_id: ID of the user being followed/unfollowed
    """
    # Use the comprehensive invalidation function
    invalidate_on_user_interaction(
        acting_user_id=acting_user_id,
        target_user_id=target_user_id
    )
    
    # Also invalidate following/followers caches
    cache.delete(f"user_following:{acting_user_id}")
    cache.delete(f"user_followers:{target_user_id}")


def invalidate_comprehensive_profile_cache(user_id: int, username: str) -> None:
    """
    Most comprehensive profile cache invalidation - use this for any profile-related change
    """
    # Invalidate basic profile caches
    invalidate_profile_cache(user_id, username)
    
    # Invalidate user's own activity feeds
    invalidate_activity_cache(user_id)
    
    # Invalidate all related user caches
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        
        # Invalidate caches for all followers (their friends feed will show updated profile)
        follower_ids = user.followers.values_list('id', flat=True)
        for follower_id in follower_ids:
            invalidate_activity_cache(follower_id)
        
        # Invalidate caches for all users this user follows (their incoming feed)  
        following_ids = user.following.values_list('id', flat=True)
        for following_id in following_ids:
            invalidate_activity_cache(following_id)
            
    except User.DoesNotExist:
        pass 