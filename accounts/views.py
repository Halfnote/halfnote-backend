from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import os
from django.db import models

from .serializers import UserProfileSerializer, UserFollowSerializer, UserSerializer
from music.models import Review, Genre
from music.serializers import ReviewSerializer

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user.
    
    POST parameters:
    - username: Required. The username for the new account
    - password: Required. The password for the new account
    - bio: Optional. A short bio for the user
    - avatar_url: Optional. URL to the user's avatar image
    """
    try:
        user = User.objects.create_user(
            username=request.data['username'],
            password=request.data['password'],
            bio=request.data.get('bio', '')
        )
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            user.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'username': user.username,
            'bio': user.bio,
            'avatar': user.avatar.url if user.avatar else None,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        }, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    data = request.data
    user = authenticate(
        username=data.get('username'),
        password=data.get('password')
    )
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'username': user.username,
            'bio': user.bio,
            'avatar': user.avatar.url if user.avatar else None,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        })
    return Response({'error': 'Invalid credentials'}, status=401)

@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == "GET":
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    # PUT - Handle both JSON and form data
    data = {}
    
    # Copy basic fields
    if 'bio' in request.data:
        data['bio'] = request.data['bio']
    if 'name' in request.data:
        data['name'] = request.data['name']
    if 'location' in request.data:
        data['location'] = request.data['location']
    
    # Handle favorite_genres - can be JSON string or list
    if 'favorite_genres' in request.data:
        try:
            import json
            raw_genres = request.data['favorite_genres']
            
            # Handle both JSON string and direct list
            if isinstance(raw_genres, str):
                genre_names = json.loads(raw_genres)
            elif isinstance(raw_genres, list):
                genre_names = raw_genres
            else:
                genre_names = []
            
            # Keep as list of strings - the serializer expects strings, not objects
            data['favorite_genres'] = [name for name in genre_names if isinstance(name, str)]
        except (json.JSONDecodeError, TypeError, ValueError):
            data['favorite_genres'] = []
    
    # Handle avatar file upload
    if 'avatar' in request.FILES:
        data['avatar'] = request.FILES['avatar']
    
    serializer = UserProfileSerializer(request.user, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        
        # Comprehensive cache invalidation for profile updates
        from music.cache_utils import invalidate_comprehensive_profile_cache
        invalidate_comprehensive_profile_cache(request.user.id, request.user.username)
        
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def user_reviews(request, username):
    """Get all reviews by a specific user - with caching optimization"""
    try:
        # Try to get cached reviews first
        from music.cache_utils import cache_key_for_user_reviews, cache_expensive_query
        
        cache_key = cache_key_for_user_reviews(username)
        
        def get_user_reviews():
            user = User.objects.get(username=username)
            reviews = Review.objects.filter(user=user).select_related('album', 'user').order_by('-created_at')
            serializer = ReviewSerializer(reviews, many=True, context={'request': request})
            return serializer.data
        
        # Cache for 10 minutes (600 seconds) - balance between freshness and performance
        cached_data = cache_expensive_query(cache_key, get_user_reviews, timeout=600)
        
        return Response(cached_data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_profile(request, username=None):
    """Get user profile information"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    serializer = UserProfileSerializer(user, context={'request': request})
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile information"""
    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        
        # Comprehensive cache invalidation for profile updates
        from music.cache_utils import invalidate_comprehensive_profile_cache
        invalidate_comprehensive_profile_cache(request.user.id, request.user.username)
        
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, username):
    """Follow a user"""
    user_to_follow = get_object_or_404(User, username=username)
    
    if user_to_follow == request.user:
        return Response(
            {'error': 'You cannot follow yourself'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if already following
    if not request.user.following.filter(id=user_to_follow.id).exists():
        request.user.following.add(user_to_follow)
        
        # Create activity for following
        from music.models import Activity
        Activity.objects.create(
            user=request.user,
            activity_type='user_followed',
            target_user=user_to_follow
        )
        
        # Comprehensive cache invalidation for follow actions
        from music.cache_utils import invalidate_on_follow_action
        invalidate_on_follow_action(request.user.id, user_to_follow.id)
    
    return Response({'status': 'following'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, username):
    """Unfollow a user"""
    user_to_unfollow = get_object_or_404(User, username=username)
    request.user.following.remove(user_to_unfollow)
    
    # Remove the follow activity from the feed
    from music.models import Activity
    Activity.objects.filter(
        user=request.user,
        activity_type='user_followed',
        target_user=user_to_unfollow
    ).delete()
    
    # Comprehensive cache invalidation for unfollow actions
    from music.cache_utils import invalidate_on_follow_action
    invalidate_on_follow_action(request.user.id, user_to_unfollow.id)
    
    return Response({'status': 'unfollowed'})

@api_view(['GET'])
@permission_classes([AllowAny])
def get_followers(request, username):
    """Get list of user's followers"""
    user = get_object_or_404(User, username=username)
    followers = user.followers.all()
    serializer = UserFollowSerializer(followers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_following(request, username):
    """Get list of users that the user is following"""
    user = get_object_or_404(User, username=username)
    following = user.following.all()
    serializer = UserFollowSerializer(following, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_feed(request):
    following_users = request.user.following.all()
    reviews = Review.objects.filter(
        user__in=following_users
    ).order_by('-created_at')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def search_users(request):
    """Search for users by username"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return Response({'error': 'Query parameter required'}, status=400)
    
    # Search for users whose username contains the query (case-insensitive)
    users_query = User.objects.filter(username__icontains=query)
    
    # Only exclude current user if authenticated
    if request.user.is_authenticated:
        users_query = users_query.exclude(id=request.user.id)
    
    users = users_query[:10]  # Limit to 10 results
    
    # Get users that the current user is already following (only if authenticated)
    following_usernames = set()
    if request.user.is_authenticated:
        following_usernames = set(request.user.following.values_list('username', flat=True))
    
    results = []
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'bio': user.bio or '',
            'avatar': user.avatar.url if user.avatar else None,
            'is_following': user.username in following_usernames,
            'is_verified': user.is_verified,
        }
        results.append(user_data)
    
    return Response({'users': results})

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_cloudinary(request):
    """Debug endpoint to check Cloudinary configuration"""
    from django.conf import settings
    import cloudinary
    
    config = cloudinary.config()
    return Response({
        'cloudinary_configured': hasattr(settings, 'DEFAULT_FILE_STORAGE') and 'cloudinary' in settings.DEFAULT_FILE_STORAGE.lower(),
        'cloud_name': config.cloud_name if config.cloud_name else 'Not set',
        'api_key_present': bool(config.api_key),
        'api_secret_present': bool(config.api_secret),
        'default_storage': getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_storage(request):
    """Debug endpoint to check storage configuration"""
    from django.conf import settings
    from django.core.files.storage import default_storage
    import cloudinary
    
    try:
        config = cloudinary.config()
        cloudinary_configured = bool(config.cloud_name and config.api_key and config.api_secret)
    except:
        cloudinary_configured = False
        config = None
    
    return Response({
        'default_file_storage_setting': getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set'),
        'actual_storage_class': str(type(default_storage)),
        'cloudinary_configured': cloudinary_configured,
        'cloudinary_cloud_name': config.cloud_name if config and config.cloud_name else 'Not set',
        'cloudinary_api_key_present': bool(config and config.api_key) if config else False,
        'environment_vars': {
            'CLOUDINARY_CLOUD_NAME': bool(os.getenv('CLOUDINARY_CLOUD_NAME')),
            'CLOUDINARY_API_KEY': bool(os.getenv('CLOUDINARY_API_KEY')),
            'CLOUDINARY_API_SECRET': bool(os.getenv('CLOUDINARY_API_SECRET')),
        }
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_avatar(request):
    """Remove user's avatar and delete from Cloudinary"""
    user = request.user
    
    if user.avatar:
        # Delete from Cloudinary if it's not the default avatar
        try:
            import cloudinary.uploader
            # Extract public_id from the avatar URL
            avatar_url = str(user.avatar)
            if 'cloudinary.com' in avatar_url:
                # Extract public_id from Cloudinary URL
                # URL format: https://res.cloudinary.com/cloud_name/image/upload/v1234567890/public_id.ext
                parts = avatar_url.split('/')
                if len(parts) > 0:
                    # Get the filename with extension and remove extension to get public_id
                    filename_with_ext = parts[-1]
                    public_id = filename_with_ext.split('.')[0]
                    
                    # Delete from Cloudinary
                    cloudinary.uploader.destroy(public_id)
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Error deleting from Cloudinary: {e}")
        
        # Clear the avatar field
        user.avatar = None
        user.save()
        
        # Comprehensive cache invalidation for avatar removal (profile update)
        from music.cache_utils import invalidate_comprehensive_profile_cache
        invalidate_comprehensive_profile_cache(user.id, user.username)
    
    return Response({'message': 'Avatar removed successfully'})

@api_view(['GET'])
@permission_classes([AllowAny])
def user_genre_stats(request, username):
    """Get user's most reviewed genres"""
    user = get_object_or_404(User, username=username)
    
    # Get genres from user's reviews with counts
    from music.models import Genre
    from django.db.models import Count
    
    genre_stats = Genre.objects.filter(
        reviews__user=user
    ).annotate(
        review_count=Count('reviews', filter=models.Q(reviews__user=user))
    ).order_by('-review_count')[:10]  # Top 10 genres
    
    stats_data = [
        {
            'name': genre.name,
            'count': genre.review_count
        }
        for genre in genre_stats
    ]
    
    return Response({
        'username': username,
        'genres': stats_data,
        'total_reviews': user.album_reviews.count()
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_profile(request, username):
    """Debug endpoint to test profile serialization"""
    user = get_object_or_404(User, username=username)
    
    # Raw user data
    raw_data = {
        'username': user.username,
        'favorite_genres_raw': user.favorite_genres,
        'favorite_genres_type': type(user.favorite_genres).__name__,
    }
    
    # Serialized data
    serializer = UserProfileSerializer(user, context={'request': request})
    
    return Response({
        'raw_data': raw_data,
        'serialized_data': serializer.data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def user_activity_feed(request, username):
    """Get activity feed for a specific user's profile page"""
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get user's activities (their reviews, likes, follows, comments)
    # Exclude internal activities like pinned reviews for cleaner profile feed
    from music.models import Activity
    from music.serializers import ActivitySerializer
    
    activities = Activity.objects.filter(user=user).exclude(
        activity_type='review_pinned'  # Exclude pinned activities from profile feed
    ).select_related(
        'user',
        'target_user',
        'comment'
    ).prefetch_related(
        'review__album',
        'review__user',
        'review__user_genres'
    ).order_by('-created_at')[:50]
    
    serializer = ActivitySerializer(activities, many=True, context={'request': request, 'feed_type': 'profile'})
    return Response(serializer.data)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorite_albums(request):
    """Manage user's favorite albums (max 5)"""
    user = request.user
    
    if request.method == 'GET':
        # Get user's favorite albums
        from .serializers import UserProfileSerializer
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response({'favorite_albums': serializer.data['favorite_albums']})
    
    elif request.method == 'POST':
        # Add album to favorites
        album_id = request.data.get('album_id')
        discogs_id = request.data.get('discogs_id')
        
        if not album_id and not discogs_id:
            return Response({"error": "album_id or discogs_id is required"}, status=400)
        
        try:
            from music.models import Album
            if album_id:
                # Check if album_id looks like a UUID or a discogs_id
                try:
                    # Try to parse as UUID first
                    import uuid
                    uuid.UUID(album_id)
                    album = Album.objects.get(id=album_id)
                except (ValueError, TypeError):
                    # If not a valid UUID, treat as discogs_id
                    album = Album.objects.get(discogs_id=album_id)
            else:
                # Import album from Discogs if needed
                from music.views import import_album_from_discogs
                album = import_album_from_discogs(discogs_id)
                if not album:
                    return Response({"error": "Album not found on Discogs"}, status=404)
            
            # Check if already in favorites
            if user.favorite_albums.filter(id=album.id).exists():
                return Response({"error": "Album already in favorites"}, status=400)
            
            # Check limit
            if user.favorite_albums.count() >= 5:
                return Response({"error": "You can only have up to 5 favorite albums"}, status=400)
            
            # Add to favorites
            user.favorite_albums.add(album)
            
            # Invalidate profile cache
            from music.cache_utils import invalidate_profile_cache
            invalidate_profile_cache(user.id, user.username)
            
            return Response({"message": "Album added to favorites"}, status=201)
            
        except Album.DoesNotExist:
            return Response({"error": "Album not found"}, status=404)
    
    elif request.method == 'DELETE':
        # Remove album from favorites
        album_id = request.data.get('album_id')
        discogs_id = request.data.get('discogs_id')
        
        if not album_id and not discogs_id:
            return Response({"error": "album_id or discogs_id is required"}, status=400)
        
        try:
            from music.models import Album
            if album_id:
                # Check if album_id looks like a UUID or a discogs_id
                try:
                    # Try to parse as UUID first
                    import uuid
                    uuid.UUID(album_id)
                    album = Album.objects.get(id=album_id)
                except (ValueError, TypeError):
                    # If not a valid UUID, treat as discogs_id
                    album = Album.objects.get(discogs_id=album_id)
            else:
                album = Album.objects.get(discogs_id=discogs_id)
            
            # Remove from favorites
            if user.favorite_albums.filter(id=album.id).exists():
                user.favorite_albums.remove(album)
                
                # Invalidate profile cache
                from music.cache_utils import invalidate_profile_cache
                invalidate_profile_cache(user.id, user.username)
                
                return Response({"message": "Album removed from favorites"}, status=200)
            else:
                return Response({"error": "Album not in favorites"}, status=404)
                
        except Album.DoesNotExist:
            return Response({"error": "Album not found"}, status=404)