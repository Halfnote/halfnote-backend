"""
Halfnote Accounts Views
Simplified user authentication and profile management
"""

from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserProfileSerializer, UserFollowSerializer, UserSerializer
from music.models import Review
from music.serializers import ReviewSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user"""
    try:
        user = User.objects.create_user(
            username=request.data['username'].lower(),
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
    """Login user and return tokens"""
    user = authenticate(
        username=request.data.get('username', '').lower(),
        password=request.data.get('password', '')
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


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get or update user profile"""
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    # Handle profile updates
    data = request.data.copy()
    
    # Handle file uploads
    if 'avatar' in request.FILES:
        data['avatar'] = request.FILES['avatar']
    if 'banner' in request.FILES:
        data['banner'] = request.FILES['banner']
    
    serializer = UserProfileSerializer(request.user, data=data, partial=True)
    if serializer.is_valid():
        try:
            serializer.save()
            
            # Clear user caches
            cache_keys = [
                f'user_profile_{request.user.username}',
                f'user_reviews_{request.user.username}',
                f'activity_feed_{request.user.id}',
            ]
            cache.delete_many(cache_keys)
            
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': f'Profile update failed: {str(e)}'}, status=500)
    
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
def user_reviews(request, username):
    """Get reviews by a specific user"""
    user = get_object_or_404(User, username=username)
    
    # Check cache first
    cache_key = f'user_reviews_{username}'
    cached_reviews = cache.get(cache_key)
    
    if cached_reviews:
        return Response({'reviews': cached_reviews, 'cached': True})
    
    # Get reviews with related data
    reviews = Review.objects.filter(user=user).select_related('album', 'user').prefetch_related(
        'user_genres', 'likes', 'comments'
    ).order_by('-created_at')
    
    # Pagination
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))
    
    paginated_reviews = reviews[offset:offset + limit]
    serializer = ReviewSerializer(paginated_reviews, many=True, context={'request': request})
    
    response_data = {
        'reviews': serializer.data,
        'total_count': reviews.count(),
        'has_more': reviews.count() > offset + limit,
        'next_offset': offset + limit if reviews.count() > offset + limit else None,
        'cached': False
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, serializer.data, 300)
    
    return Response(response_data)


@api_view(['GET'])
@permission_classes([AllowAny])
def user_profile(request, username):
    """Get public user profile"""
    user = get_object_or_404(User, username=username)
    
    # Check cache
    cache_key = f'user_profile_{username}'
    cached_profile = cache.get(cache_key)
    
    if cached_profile:
        return Response({**cached_profile, 'cached': True})
    
    serializer = UserSerializer(user, context={'request': request})
    profile_data = serializer.data
    
    # Cache for 10 minutes
    cache.set(cache_key, profile_data, 600)
    
    return Response({**profile_data, 'cached': False})


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def follow_user(request, username):
    """Follow or unfollow a user"""
    target_user = get_object_or_404(User, username=username)
    
    if target_user == request.user:
        return Response({'error': 'Cannot follow yourself'}, status=400)
    
    if request.method == 'POST':
        request.user.following.add(target_user)
        action = 'followed'
    else:  # DELETE
        request.user.following.remove(target_user)
        action = 'unfollowed'
    
    # Clear relevant caches
    cache_keys = [
        f'user_profile_{username}',
        f'user_profile_{request.user.username}',
        f'activity_feed_{request.user.id}',
    ]
    cache.delete_many(cache_keys)
    
    return Response({
        'action': action,
        'target_user': username,
        'following_count': request.user.following.count(),
        'followers_count': target_user.followers.count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def user_followers(request, username):
    """Get user's followers"""
    user = get_object_or_404(User, username=username)
    
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))
    
    followers = user.followers.all()[offset:offset + limit]
    serializer = UserFollowSerializer(followers, many=True, context={'request': request})
    
    return Response({
        'followers': serializer.data,
        'total_count': user.followers.count(),
        'has_more': user.followers.count() > offset + limit,
        'next_offset': offset + limit if user.followers.count() > offset + limit else None
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def user_following(request, username):
    """Get users that this user follows"""
    user = get_object_or_404(User, username=username)
    
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))
    
    following = user.following.all()[offset:offset + limit]
    serializer = UserFollowSerializer(following, many=True, context={'request': request})
    
    return Response({
        'following': serializer.data,
        'total_count': user.following.count(),
        'has_more': user.following.count() > offset + limit,
        'next_offset': offset + limit if user.following.count() > offset + limit else None
    })


# ============================================================================
# MISSING VIEWS THAT FRONTEND EXPECTS
# ============================================================================

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, username):
    """Unfollow a user (same as DELETE on follow_user)"""
    return follow_user(request, username)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_users(request):
    """Search for users"""
    query = request.GET.get('q', '')
    if not query:
        return Response({'users': []})
    
    users = User.objects.filter(username__icontains=query)[:20]
    serializer = UserSerializer(users, many=True, context={'request': request})
    
    return Response({'users': serializer.data})


@api_view(['GET'])
@permission_classes([AllowAny])
def user_genre_stats(request, username):
    """Get genre statistics for a user"""
    user = get_object_or_404(User, username=username)
    
    # This would typically aggregate genre data from user's reviews
    # For now, return a simple response
    return Response({
        'user': username,
        'genres': [],
        'message': 'Genre stats not implemented yet'
    })


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorite_albums(request):
    """Manage user's favorite albums"""
    if request.method == 'GET':
        # Get user's favorite albums
        favorite_albums = request.user.favorite_albums.all()
        from music.serializers import AlbumSerializer
        serializer = AlbumSerializer(favorite_albums, many=True)
        return Response({'albums': serializer.data})
    
    elif request.method == 'POST':
        # Add album to favorites
        discogs_id = request.data.get('discogs_id')
        if not discogs_id:
            return Response({'error': 'discogs_id required'}, status=400)
        
        from music.models import Album
        album = get_object_or_404(Album, discogs_id=discogs_id)
        request.user.favorite_albums.add(album)
        
        return Response({'message': 'Album added to favorites'})
    
    elif request.method == 'DELETE':
        # Remove album from favorites
        discogs_id = request.data.get('discogs_id')
        if not discogs_id:
            return Response({'error': 'discogs_id required'}, status=400)
        
        from music.models import Album
        album = get_object_or_404(Album, discogs_id=discogs_id)
        request.user.favorite_albums.remove(album)
        
        return Response({'message': 'Album removed from favorites'})