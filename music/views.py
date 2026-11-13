"""
Halfnote Music Views
Optimized views for music search, reviews, and social features with performance improvements
"""

import re
import logging
import requests
from concurrent.futures import ThreadPoolExecutor
from django.conf import settings
from django.core.cache import cache
from django.db.models import Max, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import latest_rated_average, RecentlyViewedAlbum, Album, Review, Genre, Activity, ReviewLike, Comment, List, ListItem, ListLike, Artist
from .serializers import (
    AlbumSerializer, ReviewSerializer, ReviewWriteSerializer, AlbumSearchResultSerializer,
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


def get_artist_photo(artist_name):
    """Fetch artist photo from Discogs API"""
    try:
        response = requests.get(
            f"{settings.DISCOGS_API_URL}/database/search",
            params={
                "q": artist_name,
                "type": "artist",
                "per_page": 1,
                "key": settings.DISCOGS_CONSUMER_KEY,
                "secret": settings.DISCOGS_CONSUMER_SECRET
            },
            headers={'User-Agent': 'HalfnoteApp/1.0'},
            timeout=(2, 5)
        )
        if not response.ok:
            return None

        results = response.json().get('results', [])
        if not results:
            return None
            
        # Details of first artist result
        artist_id = results[0].get('id')
        if not artist_id:
            return None

        detail_response = requests.get(
            f"{settings.DISCOGS_API_URL}/artists/{artist_id}",
            params={
                "key": settings.DISCOGS_CONSUMER_KEY,
                "secret": settings.DISCOGS_CONSUMER_SECRET
            },
            headers={'User-Agent': 'HalfnoteApp/1.0'},
            timeout=(2, 5)
        )
        
        if detail_response.ok:
            artist_data = detail_response.json()
            images = artist_data.get('images', [])
            if images:
                return images[0].get('uri')
                
    except Exception as e:
        logger.error(f"Error fetching artist photo for {artist_name}: {e}")
        
    return None


ARTIST_PHOTO_TTL = 60 * 60 * 24
PHOTO_RESULTS_LIMIT = 10


def get_artist_photos(artist_names):
    keys = {name: f'artist_photo_{name}' for name in artist_names}
    cached = cache.get_many(keys.values())
    photos = {name: cached[key] for name, key in keys.items() if key in cached}
    missing = [name for name in artist_names if name not in photos]
    if missing:
        with ThreadPoolExecutor(max_workers=len(missing)) as pool:
            fetched = dict(zip(missing, pool.map(get_artist_photo, missing)))
        cache.set_many({keys[name]: url for name, url in fetched.items() if url}, ARTIST_PHOTO_TTL)
        photos.update(fetched)
    return photos


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
                'artist_photo_url': None,
                'thumb': result.get('thumb', ''),
            })
        
        artists = {r['artist'] for r in processed_results[:PHOTO_RESULTS_LIMIT] if r['artist'] != 'Various Artists'}
        photos = get_artist_photos(artists)
        for r in processed_results[:PHOTO_RESULTS_LIMIT]:
            r['artist_photo_url'] = photos.get(r['artist'])

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
    album = import_album_from_discogs(discogs_id)
    if not album:
        return Response({'error': 'Album not found'}, status=404)

    reviews = list(Review.objects.filter(album=album).select_related('user').prefetch_related('likes', 'comments', 'user_genres').order_by('-created_at'))

    return Response({
        'album': AlbumSerializer(album).data,
        'reviews': ReviewSerializer(reviews, many=True, context={'request': request}).data,
        'review_count': len({r.user_id for r in reviews}),
        'average_rating': latest_rated_average(reviews),
        'exists_in_db': True,
        'cached': False
    })


def get_or_create_artist(artist_name):
    """
    Get or create an Artist object from Discogs.
    Returns the Artist instance or None if not found.
    """
    if not artist_name or artist_name == 'Various Artists':
        return None

    service = ExternalMusicService()

    # Try to find existing artist by name first
    existing_artist = Artist.objects.filter(name=artist_name).first()
    if existing_artist:
        logger.info(f"Found existing artist: {artist_name}")
        return existing_artist

    # Search for artist on Discogs
    artist_id = service.search_artist(artist_name)
    if not artist_id:
        logger.warning(f"Could not find artist on Discogs: {artist_name}")
        return None

    # Check if we already have this artist by discogs_id
    existing_artist = Artist.objects.filter(discogs_id=artist_id).first()
    if existing_artist:
        logger.info(f"Found existing artist by Discogs ID: {artist_id}")
        return existing_artist

    # Fetch full artist details
    artist_data = service.get_artist_details(artist_id)
    if not artist_data:
        logger.error(f"Failed to fetch artist details for ID: {artist_id}")
        return None

    # Create new artist
    try:
        artist = Artist.objects.create(
            discogs_id=artist_data['discogs_id'],
            name=artist_data['name'],
            real_name=artist_data.get('real_name', ''),
            profile=artist_data.get('profile', ''),
            primary_image_url=artist_data.get('primary_image_url', ''),
            images=artist_data.get('images', []),
            name_variations=artist_data.get('name_variations', []),
            urls=artist_data.get('urls', []),
            members=artist_data.get('members', []),
            discogs_url=artist_data.get('discogs_url', ''),
            data_quality=artist_data.get('data_quality', '')
        )
        logger.info(f"Created new artist: {artist.name} (ID: {artist.discogs_id})")
        return artist
    except Exception as e:
        logger.error(f"Error creating artist {artist_name}: {str(e)}")
        return None


def import_album_from_discogs(discogs_id):
    """Import album from Discogs if it doesn't exist"""
    album = Album.objects.filter(discogs_id=discogs_id).first()
    if album:
        return album

    album_data = ExternalMusicService().get_album_details(discogs_id)
    if not album_data:
        return None

    artist = get_or_create_artist(album_data['artist'])
    album, _ = Album.objects.get_or_create(discogs_id=discogs_id, defaults={
        'title': album_data['title'],
        'artist': album_data['artist'],
        'artist_rel': artist,
        'year': album_data.get('year') or None,
        'cover_url': album_data.get('cover_image', ''),
        'artist_photo_url': artist.primary_image_url if artist else None,
        'discogs_genres': album_data.get('genres', []),
        'discogs_styles': album_data.get('styles', []),
        'tracklist': album_data.get('tracklist', []),
        'credits': album_data.get('credits', []),
    })
    return album


# ============================================================================
# REVIEW VIEWS
# ============================================================================

def validation_error(errors):
    """Contract shape: one message in `error`, the first problem per field in `fields`."""
    fields = {name: str(msgs[0]) for name, msgs in errors.items() if name != 'non_field_errors'}
    first = errors.get('non_field_errors') or next(iter(errors.values()))
    return Response({'error': str(first[0]), 'fields': fields}, status=400)


def set_genres(review, genre_names):
    review.user_genres.set([Genre.objects.get_or_create(name=name)[0] for name in genre_names])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request, discogs_id):
    """Create a review. A user may review the same album more than once."""
    album = import_album_from_discogs(discogs_id)
    if not album:
        return Response({'error': 'Album not found'}, status=404)

    serializer = ReviewWriteSerializer(data=request.data)
    if not serializer.is_valid():
        return validation_error(serializer.errors)
    review = serializer.save(user=request.user, album=album)
    set_genres(review, request.data.get('genres', []))

    Activity.objects.create(
        user=request.user,
        activity_type='review_created',
        review=review
    )

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
        # Partial: keys left out keep their values.
        serializer = ReviewWriteSerializer(review, data=request.data, partial=True)
        if not serializer.is_valid():
            return validation_error(serializer.errors)
        review = serializer.save()
        if 'genres' in request.data:
            set_genres(review, request.data['genres'])
        return Response(ReviewSerializer(review, context={'request': request}).data)
    
    elif request.method == 'DELETE':
        review.delete()
        return Response({'message': 'Review deleted'}, status=204)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def toggle_review_like(request, review_id):
    """Like or unlike a review"""
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
    
    return Response({
        'action': action,
        'like_count': ReviewLike.objects.filter(review=review).count()
    })


RECENTLY_VIEWED_LIMIT = 10


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def recently_viewed(request):
    """GET the user's last 10 albums tapped from search; POST {discogs_id} to record a tap."""
    if request.method == 'POST':
        discogs_id = request.data.get('discogs_id') if isinstance(request.data, dict) else None
        if not discogs_id:
            return Response({'error': 'discogs_id is required'}, status=400)
        album = import_album_from_discogs(str(discogs_id))
        if not album:
            return Response({'error': 'Album not found'}, status=404)
        RecentlyViewedAlbum.objects.update_or_create(
            user=request.user, album=album, defaults={'viewed_at': timezone.now()})
        return Response(status=204)

    rows = (RecentlyViewedAlbum.objects.filter(user=request.user)
            .select_related('album').order_by('-viewed_at')[:RECENTLY_VIEWED_LIMIT])
    # Same item shape as /music/search/ so the composer renders both lists with one row.
    return Response({'results': [{
        'id': int(row.album.discogs_id) if row.album.discogs_id.isdigit() else row.album.discogs_id,
        'title': row.album.title,
        'artist': row.album.artist,
        'year': row.album.year,
        'cover_image': row.album.cover_url or '',
        'viewed_at': row.viewed_at,
    } for row in rows]})


# ============================================================================
# ACTIVITY VIEWS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_feed(request):
    """Get personalized activity feed with optimized queries"""
    activity_type = request.GET.get('type', 'friends')
    
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
    return Response(serializer.data)


class FeedPagination(CursorPagination):
    page_size = 20
    ordering = ('-latest_at', '-id')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feed(request):
    """One card per review, ordered by its newest counted activity (see activity-contract.md)."""
    me = request.user
    # Filter before annotate so MAX only sees the counted activity rows.
    reviews = (Review.objects
               .filter(Q(activity__user=me) | Q(activity__user__in=me.following.all()) | Q(user=me))
               .annotate(latest_at=Max('activity__created_at'))
               .filter(latest_at__isnull=False))
    paginator = FeedPagination()
    page = paginator.paginate_queryset(reviews, request)
    return paginator.get_paginated_response([{'review': {'id': r.id}} for r in page])


# ============================================================================
# COMMENT VIEWS
# ============================================================================

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def review_comments(request, review_id):
    """Get or create comments for a review"""
    review = get_object_or_404(Review, id=review_id)
    
    if request.method == 'GET':
        # Cache GET requests for comments
        cache_key = f'review_comments_{review_id}'
        cached_comments = cache.get(cache_key)
        
        if cached_comments:
            return Response({'comments': cached_comments})
        
        comments = Comment.objects.filter(review=review).select_related('user').order_by('created_at')
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        
        # Cache for 2 minutes (comments change frequently)
        cache.set(cache_key, serializer.data, 120)
        
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
        
        cache.delete(f'review_comments_{review_id}')
        
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
            name=request.data.get('name', ''),
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


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def list_detail(request, list_id):
    """Get, update, or delete a specific list"""
    list_obj = get_object_or_404(List, id=list_id)
    
    # Check permissions for non-public lists
    if not list_obj.is_public and (not request.user.is_authenticated or request.user != list_obj.user):
        return Response({'error': 'List not found'}, status=404)
    
    if request.method == 'GET':
        # Cache for GET requests only
        cache_key = f'list_detail_{list_id}_{request.user.id if request.user.is_authenticated else "anon"}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        serializer = ListSerializer(list_obj, context={'request': request})
        
        # Cache for 5 minutes (lists change moderately)
        cache.set(cache_key, serializer.data, 300)
        
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Only owner can update
        if not request.user.is_authenticated or request.user != list_obj.user:
            return Response({'error': 'Permission denied'}, status=403)
        
        list_obj.name = request.data.get('name', list_obj.name)
        list_obj.description = request.data.get('description', list_obj.description)
        list_obj.is_public = request.data.get('is_public', list_obj.is_public)
        list_obj.save()
        
        # Clear relevant caches
        cache_keys = [
            f'list_detail_{list_id}_anon',
            f'list_detail_{list_id}_{request.user.id}',
            f'user_lists_{list_obj.user.username}',
        ]
        
        # Clear list likes cache for different pagination combinations
        for offset in [0, 20, 40]:
            for limit in [20, 50]:
                cache_keys.append(f'list_likes_{list_id}_{offset}_{limit}')
        
        cache.delete_many(cache_keys)
        
        serializer = ListSerializer(list_obj, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        # Only owner can delete
        if not request.user.is_authenticated or request.user != list_obj.user:
            return Response({'error': 'Permission denied'}, status=403)
        
        list_obj.delete()
        return Response({'message': 'List deleted'}, status=204)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_likes(request, list_id):
    """Get users who liked a list with caching"""
    list_obj = get_object_or_404(List, id=list_id)
    
    # Check permissions for non-public lists
    if not list_obj.is_public and (not request.user.is_authenticated or request.user != list_obj.user):
        return Response({'error': 'List not found'}, status=404)
    
    offset = int(request.GET.get('offset', 0))
    limit = min(int(request.GET.get('limit', 20)), 50)

    # Cache key includes pagination
    cache_key = f'list_likes_{list_id}_{offset}_{limit}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return Response(cached_data)

    likes = ListLike.objects.filter(list=list_obj).select_related('user')[offset:offset + limit]
    
    users_data = []
    for like in likes:
        users_data.append({
            'id': like.user.id,
            'username': like.user.username,
            'avatar': like.user.avatar.url if like.user.avatar else None,
            'is_staff': like.user.is_staff
        })
    
    total_count = ListLike.objects.filter(list=list_obj).count()

    response_data = {
        'users': users_data,
        'total_count': total_count,
        'has_more': total_count > offset + limit,
        'next_offset': offset + limit if total_count > offset + limit else None
    }
    
    # Cache for 3 minutes (likes change frequently)
    cache.set(cache_key, response_data, 180)

    return Response(response_data)


# ============================================================================
# UTILITY VIEWS
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def search_artists(request):
    """Search for artists"""
    query = request.GET.get('q', '')

    if not query:
        return Response({'results': []})

    # Search local Artist database
    artists = Artist.objects.filter(name__icontains=query)[:10]

    from .serializers import ArtistSerializer
    serializer = ArtistSerializer(artists, many=True)

    return Response({'results': serializer.data})


@api_view(['GET'])
@permission_classes([AllowAny])
def artist_detail(request, artist_id):
    """Get detailed information about a specific artist"""
    try:
        # Try to find by primary key first
        artist = Artist.objects.get(pk=artist_id)
    except (Artist.DoesNotExist, ValueError):
        # If not found by PK, try by discogs_id
        artist = get_object_or_404(Artist, discogs_id=artist_id)

    from .serializers import ArtistSerializer
    serializer = ArtistSerializer(artist)

    # Also include related albums
    albums = Album.objects.filter(artist_rel=artist).select_related('artist_rel')
    album_data = AlbumSerializer(albums, many=True).data

    return Response({
        'artist': serializer.data,
        'albums': album_data,
        'album_count': albums.count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def genres(request):
    """Get all available genres with caching"""
    cache_key = 'all_genres'
    cached_genres = cache.get(cache_key)

    if cached_genres:
        return Response({'genres': cached_genres})

    genres = Genre.objects.all().order_by('name')
    serializer = GenreSerializer(genres, many=True)

    # Cache for 1 hour (genres don't change often)
    cache.set(cache_key, serializer.data, 3600)

    return Response({'genres': serializer.data})

@api_view(['GET'])
@permission_classes([AllowAny])
def review_likes(request, review_id):
    """Get users who liked a review"""
    review = get_object_or_404(Review, id=review_id)
    
    offset = int(request.GET.get('offset', 0))
    limit = min(int(request.GET.get('limit', 20)), 50)
    include_review = request.GET.get('include_review') == 'true'
    
    likes = ReviewLike.objects.filter(review=review).select_related('user')[offset:offset + limit]
    total_count = review.likes.count()

    # Format users array as expected by frontend
    users_data = []
    for like in likes:
        users_data.append({
            'id': like.user.id,
            'username': like.user.username,
            'avatar': like.user.avatar.url if like.user.avatar else None,
            'is_staff': like.user.is_staff
        })

    response_data = {
        'users': users_data,
        'total_count': total_count,
        'has_more': total_count > offset + limit,
        'next_offset': offset + limit if total_count > offset + limit else None
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