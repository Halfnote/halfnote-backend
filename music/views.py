"""
Halfnote Music Views
Optimized views for music search, reviews, and social features with performance improvements
"""

import re
import logging
import requests
from django.conf import settings
from django.db.models import Avg
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Album, Review, Genre, Activity, ReviewLike, Comment, List, ListItem, ListLike
from .serializers import (
    AlbumSerializer, ReviewSerializer, AlbumSearchResultSerializer, 
    ActivitySerializer, CommentSerializer, GenreSerializer, 
    ListSerializer, ListSummarySerializer, ListItemSerializer
)
from accounts.serializers import UserSerializer
from .services import ExternalMusicService

logger = logging.getLogger(__name__)


# ============================================================================
# SEARCH VIEWS
# ============================================================================

def search_discogs(query):
    """Search Discogs API for albums"""
    response = requests.get(
        f"{settings.DISCOGS_API_URL}/database/search",
        params={
            "q": query,
            "type": "master",
            "per_page": 25,
            "key": settings.DISCOGS_CONSUMER_KEY,
            "secret": settings.DISCOGS_CONSUMER_SECRET
        },
        headers={'User-Agent': 'HalfnoteApp/1.0'},
        timeout=(2, 10)
    )

    if not response.ok:
        logger.error(f"Discogs API error: {response.status_code}")
        return []

    return response.json().get('results', [])


@api_view(['GET'])
@permission_classes([AllowAny])
def search(request):
    """Search for albums using Discogs API"""
    query = request.GET.get('q')
    if not query:
        return Response({'error': 'Query parameter required'}, status=400)
    
    # Check cache first
    cache_key = f'search_{query}'
    cached_results = cache.get(cache_key)
    if cached_results:
        return Response({'results': cached_results, 'cached': True})
    
    try:
        results = search_discogs(query)
        processed_results = []
        
        for result in results:
            title = result.get('title', '')
            artist = 'Various Artists'
            album_title = title
            
            # Parse artist and title from Discogs format
            if ' - ' in title:
                parts = title.split(' - ', 1)
                if len(parts) == 2 and len(parts[0].strip()) < 100:
                    # Clean up disambiguation numbers
                    clean_artist = re.sub(r'\s*\(\d+\)$', '', parts[0].strip())
                    artist = clean_artist or parts[0].strip()
                    album_title = parts[1].strip()
            
            processed_results.append({
                'id': result.get('id'),
                'title': album_title,
                'artist': artist,
                'year': result.get('year'),
                'genre': result.get('genre', []),
                'style': result.get('style', []),
                'cover_image': result.get('cover_image', ''),
                'thumb': result.get('thumb', ''),
            })
        
        # Cache for 15 minutes
        cache.set(cache_key, processed_results, 900)
        
        return Response({'results': processed_results, 'cached': False})
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return Response({'error': 'Search failed'}, status=500)


# ============================================================================
# ALBUM VIEWS
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def album_detail(request, discogs_id):
    """Get album details with reviews"""
    # Check cache
    cache_key = f'album_{discogs_id}'
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response({**cached_data, 'cached': True})
    
    # Check if album exists in database
    album = Album.objects.filter(discogs_id=discogs_id).first()
    
    if album:
        # Get reviews for existing album
        reviews = Review.objects.filter(album=album).select_related('user').order_by('-created_at')
        
        response_data = {
            'album': AlbumSerializer(album).data,
            'reviews': ReviewSerializer(reviews, many=True, context={'request': request}).data,
            'review_count': reviews.count(),
            'average_rating': reviews.aggregate(Avg('rating'))['rating__avg'],
            'exists_in_db': True,
            'cached': False
        }
    else:
        # Fetch from Discogs
        service = ExternalMusicService()
        album_data = service.get_album_details(discogs_id)
        
        if not album_data:
            return Response({'error': 'Album not found'}, status=404)
        
        response_data = {
            'album': album_data,
            'reviews': [],
            'review_count': 0,
            'average_rating': None,
            'exists_in_db': False,
            'cached': False
        }
        
    # Cache for 5 minutes
    cache.set(cache_key, response_data, 300)
    return Response(response_data)


def import_album_from_discogs(discogs_id):
    """Import album from Discogs if it doesn't exist"""
    if Album.objects.filter(discogs_id=discogs_id).exists():
        return Album.objects.get(discogs_id=discogs_id)
    
    service = ExternalMusicService()
    album_data = service.get_album_details(discogs_id)
    
    if album_data:
        album = Album.objects.create(
            discogs_id=discogs_id,
            title=album_data['title'],
            artist=album_data['artist'],
            year=album_data.get('year'),
            cover_url=album_data.get('cover_image', ''),
        )
        return album
    
    return None


# ============================================================================
# REVIEW VIEWS
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, discogs_id):
    """Create a new review for an album"""
    # Import or get album
    album = import_album_from_discogs(discogs_id)
    if not album:
        return Response({'error': 'Album not found'}, status=404)
    
    # Check if user already reviewed this album
    if Review.objects.filter(user=request.user, album=album).exists():
        return Response({'error': 'You have already reviewed this album'}, status=400)
    
    # Create review
    review = Review.objects.create(
        user=request.user,
        album=album,
        rating=request.data.get('rating'),
        content=request.data.get('content', ''),
    )
    
    # Handle genres
    genre_names = request.data.get('genres', [])
    for genre_name in genre_names:
        genre, _ = Genre.objects.get_or_create(name=genre_name)
        review.user_genres.add(genre)
    
    # Create activity
    Activity.objects.create(
        user=request.user,
        activity_type='review_created',
        review=review
    )
    
    # Clear caches
    cache.delete_many([
        f'album_{discogs_id}',
        f'user_reviews_{request.user.username}',
        f'activity_feed_{request.user.id}',
    ])
    
    return Response(ReviewSerializer(review, context={'request': request}).data, status=201)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def review_detail(request, review_id):
    """Get, update, or delete a review"""
    review = get_object_or_404(Review, id=review_id)
    
    if request.method == 'GET':
        return Response(ReviewSerializer(review, context={'request': request}).data)
    
    # Only allow owner to modify
    if review.user != request.user:
        return Response({'error': 'Permission denied'}, status=403)
    
    if request.method == 'PUT':
        # Update review
        review.rating = request.data.get('rating', review.rating)
        review.content = request.data.get('content', review.content)
        review.save()
        
        # Update genres
        genre_names = request.data.get('genres', [])
        review.user_genres.clear()
        for genre_name in genre_names:
            genre, _ = Genre.objects.get_or_create(name=genre_name)
            review.user_genres.add(genre)
        
        # Clear caches
        cache.delete_many([
            f'album_{review.album.discogs_id}',
            f'user_reviews_{request.user.username}',
        ])
        
        return Response(ReviewSerializer(review, context={'request': request}).data)
    
    elif request.method == 'DELETE':
        album_discogs_id = review.album.discogs_id
        review.delete()
        
        # Clear caches
        cache.delete_many([
            f'album_{album_discogs_id}',
            f'user_reviews_{request.user.username}',
        ])
        
        return Response({'message': 'Review deleted'}, status=204)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def toggle_review_like(request, review_id):
    """Like or unlike a review with cache invalidation"""
    review = get_object_or_404(Review.objects.select_related('user'), id=review_id)
    
    like, created = ReviewLike.objects.get_or_create(
        user=request.user,
        review=review
    )
    
    if not created:
        # Unlike
        like.delete()
        action = 'unliked'
    else:
        # Like and create activity
        action = 'liked'
        Activity.objects.create(
            user=request.user,
            activity_type='review_liked',
            review=review
        )
    
    # Clear relevant caches when likes change
    cache.delete_many([
        f'user_reviews_{review.user.username}',
        f'activity_feed_{request.user.id}_friends',
        f'activity_feed_{request.user.id}_you',
        f'user_activity_{review.user.username}',
    ])
    
    return Response({
        'action': action,
        'like_count': ReviewLike.objects.filter(review=review).count()
    })


# ============================================================================
# ACTIVITY VIEWS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_feed(request):
    """Get personalized activity feed with optimized queries"""
    activity_type = request.GET.get('type', 'friends')
    
    # Cache key for this specific feed type and user
    cache_key = f'activity_feed_{request.user.id}_{activity_type}'
    cached_activities = cache.get(cache_key)
    
    if cached_activities:
        return Response(cached_activities)
    
    # Base query with optimal prefetching to avoid N+1 queries
    base_query = Activity.objects.select_related(
        'user', 'target_user', 'review__user', 'review__album', 'comment__user'
    ).prefetch_related(
        'review__user_genres', 'review__likes', 'review__comments'
    )
    
    if activity_type == 'friends':
        # Get activities from followed users
        following_users = request.user.following.values_list('id', flat=True)
        activities = base_query.filter(user__id__in=following_users)
    elif activity_type == 'you':
        # Get user's own activities
        activities = base_query.filter(user=request.user)
    elif activity_type == 'incoming':
        # Get activities where user is mentioned/involved
        activities = base_query.filter(
            review__user=request.user
        ).exclude(user=request.user)
    else:
        activities = Activity.objects.none()
    
    # Pagination with efficient ordering
    offset = int(request.GET.get('offset', 0))
    limit = min(int(request.GET.get('limit', 20)), 50)  # Cap at 50 items
    
    paginated_activities = activities.order_by('-created_at')[offset:offset + limit]
    serializer = ActivitySerializer(paginated_activities, many=True, context={'request': request})
    
    # Cache for 2 minutes (shorter for activity feed freshness)
    cache.set(cache_key, serializer.data, 120)
    
    return Response(serializer.data)


# ============================================================================
# COMMENT VIEWS
# ============================================================================

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def review_comments(request, review_id):
    """Get or create comments for a review"""
    review = get_object_or_404(Review, id=review_id)
    
    if request.method == 'GET':
        comments = Comment.objects.filter(review=review).select_related('user').order_by('created_at')
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response({'comments': serializer.data})
    
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=401)
        
        comment = Comment.objects.create(
            user=request.user,
            review=review,
            content=request.data.get('content', '')
        )
        
        # Create activity
        Activity.objects.create(
            user=request.user,
            activity_type='comment_created',
            review=review,
            comment=comment
        )
        
        return Response(CommentSerializer(comment, context={'request': request}).data, status=201)


# ============================================================================
# LIST VIEWS
# ============================================================================

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def lists_view(request):
    """Get public lists or create a new list"""
    if request.method == 'GET':
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 20))
        
        lists = List.objects.filter(is_public=True).select_related('user').order_by('-updated_at')[offset:offset + limit]
        serializer = ListSummarySerializer(lists, many=True, context={'request': request})
        
        return Response({
            'lists': serializer.data,
            'total_count': List.objects.filter(is_public=True).count(),
            'has_more': List.objects.filter(is_public=True).count() > offset + limit
        })
    
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=401)
        
        list_obj = List.objects.create(
            user=request.user,
            title=request.data.get('title', ''),
            description=request.data.get('description', ''),
            is_public=request.data.get('is_public', True)
        )
        
        return Response(ListSerializer(list_obj, context={'request': request}).data, status=201)


@api_view(['GET'])
@permission_classes([AllowAny])
def user_lists(request, username):
    """Get lists by a specific user"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    user = get_object_or_404(User, username=username)
    
    # Show public lists, or all lists if viewing own profile
    if request.user.is_authenticated and request.user == user:
        lists = List.objects.filter(user=user)
    else:
        lists = List.objects.filter(user=user, is_public=True)
    
    lists = lists.select_related('user').order_by('-updated_at')
    serializer = ListSummarySerializer(lists, many=True, context={'request': request})
    
    return Response(serializer.data)


# ============================================================================
# UTILITY VIEWS
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def genres(request):
    """Get all available genres"""
    genres = Genre.objects.all().order_by('name')
    serializer = GenreSerializer(genres, many=True)
    return Response({'genres': serializer.data})


# ============================================================================
# MISSING VIEWS THAT FRONTEND EXPECTS
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def review_likes(request, review_id):
    """Get users who liked a review"""
    review = get_object_or_404(Review, id=review_id)
    
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))
    include_review = request.GET.get('include_review') == 'true'
    
    likes = ReviewLike.objects.filter(review=review).select_related('user')[offset:offset + limit]

    response_data = {
        'likes': [{'user': UserSerializer(like.user).data} for like in likes],
        'total_count': review.likes.count(),
        'has_more': review.likes.count() > offset + limit
    }
    
    if include_review:
        response_data['review'] = ReviewSerializer(review, context={'request': request}).data
    
    return Response(response_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pin_review(request, review_id):
    """Pin or unpin a review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    # Toggle pin status
    review.is_pinned = not review.is_pinned
    review.save()
    
    return Response({
        'pinned': review.is_pinned,
        'message': 'Review pinned' if review.is_pinned else 'Review unpinned'
    })


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def comment_detail(request, comment_id):
    """Update or delete a comment"""
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    
    if request.method == 'PUT':
        comment.content = request.data.get('content', comment.content)
        comment.save()
        return Response(CommentSerializer(comment, context={'request': request}).data)
    
    elif request.method == 'DELETE':
        comment.delete()
        return Response({'message': 'Comment deleted'}, status=204)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_activity(request, activity_id):
    """Delete an activity (if user owns it)"""
    activity = get_object_or_404(Activity, id=activity_id, user=request.user)
    activity.delete()
    return Response({'message': 'Activity deleted'}, status=204)