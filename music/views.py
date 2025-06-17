import logging
import requests

from django.conf import settings
from django.db.models import Avg, Prefetch
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Album, Review, Genre, Activity, ReviewLike, Comment
from .serializers import AlbumSerializer, ReviewSerializer, AlbumSearchResultSerializer, ActivitySerializer, CommentSerializer, GenreSerializer
from .services import ExternalMusicService
from .cache_utils import (
    cache_key_for_user_reviews, cache_key_for_album_details, 
    cache_key_for_activity_feed, cache_key_for_search_results,
    invalidate_user_cache, invalidate_album_cache, cache_expensive_query
)

logger = logging.getLogger(__name__)

def search_discogs(query):
    headers = {
                        'User-Agent': 'HalfnoteApp/1.0'
    }

    response = requests.get(
        f"{settings.DISCOGS_API_URL}/database/search",
        params={
            "q": query,
            "type": "master",
            "per_page": 10,
            "key": settings.DISCOGS_CONSUMER_KEY,
            "secret": settings.DISCOGS_CONSUMER_SECRET
        },
        headers=headers
    )

    if not response.ok:
        logger.error(f"Discogs API error: {response.status_code} - {response.text}")
        return []

    return response.json().get('results', [])


@api_view(['GET'])
@permission_classes([AllowAny])
def search(request):
    query = request.GET.get('q')
    if not query:
        return Response({'error': 'Query parameter required'}, status=400)
    
    # Check cache first
    cache_key = cache_key_for_search_results(query)
    cached_results = cache.get(cache_key)
    if cached_results:
        return Response({'results': cached_results, 'cached': True})
    
    try:
        results = search_discogs(query)
        
        # Process results for album search - keep it simple
        processed_results = []
        for result in results:
            # Parse artist and title more intelligently
            title = result.get('title', '')
            artist = 'Various Artists'  # Default fallback
            album_title = title
            
            # Try to extract artist - but don't assume format
            if ' - ' in title:
                parts = title.split(' - ', 1)
                if len(parts) == 2:
                    potential_artist, potential_title = parts
                    # Only use if the first part looks like an artist (not too long)
                    if len(potential_artist.strip()) < 100:
                        # Clean up Discogs disambiguation numbers like (2), (3)
                        import re
                        clean_artist = re.sub(r'\s*\(\d+\)$', '', potential_artist.strip()).strip()
                        artist = clean_artist if clean_artist else potential_artist.strip()
                        album_title = potential_title.strip()
            
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
        
        serializer = AlbumSearchResultSerializer(processed_results, many=True)
        
        # Cache results for 10 minutes
        cache.set(cache_key, serializer.data, 600)
        
        return Response({'results': serializer.data, 'cached': False})
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return Response({'error': 'Search failed', 'details': str(e)}, status=500)





@api_view(['GET'])
def unified_album_view(request, discogs_id):
    """
    Unified view for album details - handles both database albums and Discogs preview
    """
    # Check cache first
    cache_key = cache_key_for_album_details(discogs_id)
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response({**cached_data, 'cached': True})
    
    # First, check if album exists in our database
    album = Album.objects.filter(discogs_id=discogs_id).first()
    
    if album:
        # Album exists in our database - use optimized queries
        reviews = Review.objects.filter(album=album).select_related('user').prefetch_related(
            'user_genres', 'likes', 'comments'
        ).order_by('-created_at')
        
        response_data = {
            'album': AlbumSerializer(album).data,
            'reviews': ReviewSerializer(reviews, many=True, context={'request': request}).data,
            'review_count': reviews.count(),
            'average_rating': reviews.aggregate(Avg('rating'))['rating__avg'],
            'exists_in_db': True,
            'cached': False
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, response_data, 300)
        return Response(response_data)
    else:
        # Album doesn't exist - fetch from Discogs
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
        
        # Cache for 15 minutes (longer since it's from external API)
        cache.set(cache_key, response_data, 900)
        return Response(response_data)

def import_album_from_discogs(discogs_id):
    """Import an album from Discogs if it doesn't exist in the database"""
    # Check if already imported
    album = Album.objects.filter(discogs_id=discogs_id).first()
    if album:
        return album
    
    # Fetch from Discogs and create
    service = ExternalMusicService()
    album_data = service.get_album_details(discogs_id)
    
    if not album_data:
        return None
        
    # Create the album record with Discogs metadata
    album = Album.objects.create(
        title=album_data['title'],
        artist=album_data['artist'],
        year=album_data.get('year'),
        cover_url=album_data.get('cover_image'),
        discogs_id=discogs_id,
        discogs_genres=album_data.get('genres', []),
        discogs_styles=album_data.get('styles', []),
        tracklist=album_data.get('tracklist', []),
        credits=album_data.get('credits', [])
    )
    
    # Note: User genres will be assigned when creating reviews
    
    return album

@api_view(['POST'])
def create_review(request, discogs_id):
    """Create a review for an album, importing the album if needed"""
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)
    
    # Get or import the album
    album = import_album_from_discogs(discogs_id)
    
    if not album:
        return Response({"error": "Album not found on Discogs"}, status=404)
    
    # Create the review
    try:
        review = Review.objects.create(
            album=album,
            user=request.user,
            rating=request.data.get('rating'),
            content=request.data.get('content', '')
        )
        
        # Handle user-selected genres for this review
        user_genres = request.data.get('genres', [])
        if user_genres:
            valid_genres = []
            invalid_genres = []
            
            for genre_name in user_genres:
                try:
                    genre = Genre.objects.get(name=genre_name)
                    review.user_genres.add(genre)
                    # Also add to album's genres (aggregate from all reviews)
                    album.genres.add(genre)
                    valid_genres.append(genre_name)
                except Genre.DoesNotExist:
                    invalid_genres.append(genre_name)
            
            # Log invalid genres for debugging
            if invalid_genres:
                logger.warning(f"Invalid genres submitted: {invalid_genres}. Valid genres: {[g.name for g in Genre.objects.all()]}")
        
        # Create activity for new review
        create_activity('review_created', request.user, review=review)
        
        # Comprehensive cache invalidation for new reviews
        from .cache_utils import invalidate_on_user_interaction
        invalidate_on_user_interaction(acting_user_id=request.user.id)
        
        # Invalidate relevant caches
        invalidate_album_cache(discogs_id)
        invalidate_user_cache(request.user.username)
        
        # Return info about genre validation
        response_data = ReviewSerializer(review, context={'request': request}).data
        if user_genres and invalid_genres:
            response_data['warnings'] = {
                'invalid_genres': invalid_genres,
                'valid_genres_accepted': valid_genres if user_genres else []
            }
        return Response(response_data, status=201)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def edit_review(request, review_id):
    """Get, edit or delete a review"""
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response({"error": "Review not found"}, status=404)
    
    if request.method == 'GET':
        # Anyone can view a review
        return Response(ReviewSerializer(review, context={'request': request}).data)
    
    # For PUT and DELETE, require authentication and ownership
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)
    
    # Check if user owns this review
    if review.user != request.user:
        return Response({"error": "You can only edit your own reviews"}, status=403)
    
    if request.method == 'PUT':
        # Update the review
        review.rating = request.data.get('rating', review.rating)
        review.content = request.data.get('content', review.content)
        review.save()
        
        # Handle genre updates
        user_genres = request.data.get('genres', [])
        if user_genres is not None:  # Allow empty list to clear genres
            # Clear existing genres
            review.user_genres.clear()
            
            # Add new genres
            valid_genres = []
            invalid_genres = []
            
            for genre_name in user_genres:
                try:
                    genre = Genre.objects.get(name=genre_name)
                    review.user_genres.add(genre)
                    valid_genres.append(genre_name)
                except Genre.DoesNotExist:
                    invalid_genres.append(genre_name)
            
            # Update album's genres (reaggregate from all reviews)
            album = review.album
            album.genres.clear()
            all_review_genres = Genre.objects.filter(reviews__album=album).distinct()
            album.genres.set(all_review_genres)
            
            # Comprehensive cache invalidation for review updates
            from .cache_utils import invalidate_on_user_interaction
            invalidate_on_user_interaction(acting_user_id=request.user.id)
            
            # Return response with warnings if needed
            response_data = ReviewSerializer(review).data
            if invalid_genres:
                response_data['warnings'] = {
                    'invalid_genres': invalid_genres,
                    'valid_genres_accepted': valid_genres
                }
            return Response(response_data)
        
        # Comprehensive cache invalidation for review updates
        from .cache_utils import invalidate_on_user_interaction
        invalidate_on_user_interaction(acting_user_id=request.user.id)
        
        return Response(ReviewSerializer(review, context={'request': request}).data)
    
    elif request.method == 'DELETE':
        # Delete the review
        album = review.album
        review.delete()
        
        # Update album's genres after deletion
        album.genres.clear()
        all_review_genres = Genre.objects.filter(reviews__album=album).distinct()
        album.genres.set(all_review_genres)
        
        # Comprehensive cache invalidation for review deletion
        from .cache_utils import invalidate_on_user_interaction
        invalidate_on_user_interaction(acting_user_id=request.user.id)
        
        return Response({"message": "Review deleted successfully"}, status=200)

@api_view(['POST'])
def pin_review(request, review_id):
    """Pin or unpin a review - only by the review author"""
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)
    
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response({"error": "Review not found"}, status=404)
    
    # Check if user owns this review
    if review.user != request.user:
        return Response({"error": "You can only pin your own reviews"}, status=403)
    
    # Check if trying to pin and already at limit
    if not review.is_pinned:
        pinned_count = Review.objects.filter(user=request.user, is_pinned=True).count()
        if pinned_count >= 4:
            return Response({"error": "You can only pin up to 4 reviews"}, status=400)
    
    # Toggle pin status
    review.is_pinned = not review.is_pinned
    review.save()
    
    action = "pinned" if review.is_pinned else "unpinned"
    
    # Create activity for pinning
    if review.is_pinned:
        create_activity('review_pinned', request.user, review=review)
    
    # Comprehensive cache invalidation for review pinning
    from .cache_utils import invalidate_on_user_interaction
    invalidate_on_user_interaction(acting_user_id=request.user.id)
    
    return Response({
        "message": f"Review {action} successfully",
        "is_pinned": review.is_pinned,
        "review": ReviewSerializer(review, context={'request': request}).data
    })


# Activity utility functions
def create_activity(activity_type, user, target_user=None, review=None):
    """Create an activity record and invalidate related caches"""
    Activity.objects.create(
        user=user,
        activity_type=activity_type,
        target_user=target_user,
        review=review
    )
    
    # Invalidate activity feed caches
    from .cache_utils import invalidate_activity_cache
    
    # Invalidate the user's own activity cache
    invalidate_activity_cache(user.id)
    
    # Invalidate target user's incoming activity cache if applicable
    if target_user:
        invalidate_activity_cache(target_user.id)


@api_view(['POST'])
def like_review(request, review_id):
    """Like or unlike a review"""
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)
    
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response({"error": "Review not found"}, status=404)
    
    # Check if already liked
    like, created = ReviewLike.objects.get_or_create(
        user=request.user,
        review=review
    )
    
    if not created:
        # Unlike - delete the like
        like.delete()
        action = "unliked"
        
        # Remove the like activity from the feed
        Activity.objects.filter(
            user=request.user,
            activity_type='review_liked',
            review=review
        ).delete()
    else:
        # Create activity for liking
        create_activity('review_liked', request.user, target_user=review.user, review=review)
        action = "liked"
    
    # Comprehensive cache invalidation for review interactions
    from .cache_utils import invalidate_on_review_action
    invalidate_on_review_action(review_id, request.user.id)
    
    return Response({
        "message": f"Review {action} successfully",
        "is_liked": created,
        "likes_count": review.likes.count()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def review_likes(request, review_id):
    """Get users who liked a review with optional pagination and review details"""
    try:
        review = Review.objects.select_related('user', 'album').get(id=review_id)
    except Review.DoesNotExist:
        return Response({"error": "Review not found"}, status=404)

    # Get pagination parameters
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))
    include_review = request.GET.get('include_review', 'false').lower() == 'true'

    # Get users who liked this review with pagination
    likes = ReviewLike.objects.filter(review=review).select_related('user').order_by('-created_at')
    total_likes = likes.count()
    
    # Apply pagination if offset/limit provided
    if offset > 0 or limit < total_likes:
        paginated_likes = likes[offset:offset + limit]
    else:
        paginated_likes = likes

    # Serialize user data
    from accounts.serializers import UserSerializer
    users = [like.user for like in paginated_likes]
    users_data = UserSerializer(users, many=True).data

    response_data = {
        'users': users_data,
        'total_count': total_likes,
        'has_more': total_likes > offset + limit,
        'next_offset': offset + limit if total_likes > offset + limit else None
    }

    # Include review details if requested
    if include_review:
        response_data['review'] = {
            'id': review.id,
            'username': review.user.username,
            'album_title': review.album.title,
            'album_artist': review.album.artist,
            'album_cover': review.album.cover_url,
            'rating': review.rating,
            'content': review.content,
            'created_at': review.created_at
        }

    return Response(response_data)


@api_view(['GET'])
def activity_feed(request):
    """Get activity feed based on type - with caching optimization"""
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)
    
    feed_type = request.GET.get('type', 'friends')  # friends, you, incoming
    
    # Try to get cached data first
    from .cache_utils import get_cached_activity_feed, cache_activity_feed
    cached_data = get_cached_activity_feed(request.user.id, feed_type)
    
    if cached_data is not None:
        return Response(cached_data)
    
    # Build base queryset with optimized select_related and prefetch_related
    base_queryset = Activity.objects.select_related(
        'user',  # Always fetch the user who performed the activity
        'target_user',  # Fetch the target user if applicable
        'comment'  # Fetch comment details if applicable
    ).prefetch_related(
        'review__album',  # Prefetch review and its album
        'review__user',   # Prefetch review owner
        'review__user_genres'  # Prefetch review genres
    )
    
    if feed_type == 'you':
        # User's own activities (exclude pinned reviews)
        activities = base_queryset.filter(user=request.user).exclude(activity_type='review_pinned')[:50]
    elif feed_type == 'incoming':
        # Activities targeting the current user (exclude pinned reviews)
        activities = base_queryset.filter(target_user=request.user).exclude(activity_type='review_pinned')[:50]
    else:  # friends
        # Activities from people the user follows (exclude pinned reviews)
        following_users = request.user.following.all()
        activities = base_queryset.filter(user__in=following_users).exclude(activity_type='review_pinned')[:50]
    
    serializer = ActivitySerializer(activities, many=True, context={'request': request, 'feed_type': feed_type})
    serialized_data = serializer.data
    
    # Cache the result for 3 minutes (activity feeds change frequently)
    cache_activity_feed(request.user.id, feed_type, serialized_data, timeout=180)
    
    return Response(serialized_data)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def review_comments(request, review_id):
    """Get comments for a review or add a new comment"""
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response({"error": "Review not found"}, status=404)
    
    if request.method == 'GET':
        # Get comments for this review with pagination
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 10))
        
        total_comments = Comment.objects.filter(review=review).count()
        comments = Comment.objects.filter(review=review).order_by('created_at')[offset:offset + limit]
        serializer = CommentSerializer(comments, many=True)
        
        return Response({
            'comments': serializer.data,
            'total_count': total_comments,
            'has_more': total_comments > offset + limit,
            'next_offset': offset + limit if total_comments > offset + limit else None
        })
    
    elif request.method == 'POST':
        # Add a new comment
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)
        
        content = request.data.get('content', '').strip()
        if not content:
            return Response({"error": "Comment content is required"}, status=400)
        
        comment = Comment.objects.create(
            review=review,
            user=request.user,
            content=content
        )
        
        # Create activity for comment
        Activity.objects.create(
            user=request.user,
            activity_type='comment_created',
            target_user=review.user,
            review=review,
            comment=comment
        )
        
        # Comprehensive cache invalidation for review interactions
        from .cache_utils import invalidate_on_review_action
        invalidate_on_review_action(review.id, request.user.id)
        
        return Response(CommentSerializer(comment).data, status=201)


@api_view(['PUT', 'DELETE'])
def edit_comment(request, comment_id):
    """Edit or delete a comment - only by the comment author"""
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)
    
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=404)
    
    # Check if user owns this comment
    if comment.user != request.user:
        return Response({"error": "You can only edit your own comments"}, status=403)
    
    if request.method == 'PUT':
        content = request.data.get('content', '').strip()
        if not content:
            return Response({"error": "Comment content is required"}, status=400)
        
        comment.content = content
        comment.save()
        
        # Comprehensive cache invalidation for comment updates
        from .cache_utils import invalidate_on_review_action
        invalidate_on_review_action(comment.review.id, request.user.id)
        
        return Response(CommentSerializer(comment).data)
    
    elif request.method == 'DELETE':
        review_id = comment.review.id
        
        # Remove the comment activity from the feed
        Activity.objects.filter(
            user=request.user,
            activity_type='comment_created',
            comment=comment
        ).delete()
        
        comment.delete()
        
        # Comprehensive cache invalidation for comment deletion
        from .cache_utils import invalidate_on_review_action
        invalidate_on_review_action(review_id, request.user.id)
        
        return Response({"message": "Comment deleted successfully"}, status=200)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_activity(request, activity_id):
    """Delete an activity - only by the activity creator"""
    try:
        activity = Activity.objects.get(id=activity_id)
    except Activity.DoesNotExist:
        return Response({"error": "Activity not found"}, status=404)
    
    # Check if user owns this activity
    if activity.user != request.user:
        return Response({"error": "You can only delete your own activities"}, status=403)
    
    # Handle different activity types and their effects
    if activity.activity_type == 'user_followed' and activity.target_user:
        # Unfollow the user
        request.user.following.remove(activity.target_user)
    elif activity.activity_type == 'review_liked' and activity.review:
        # Unlike the review
        ReviewLike.objects.filter(user=request.user, review=activity.review).delete()
    elif activity.activity_type == 'comment_created' and activity.comment:
        # Delete the comment
        activity.comment.delete()
    elif activity.activity_type == 'review_created' and activity.review:
        # Delete the review
        activity.review.delete()
    
    # Delete the activity
    activity.delete()
    
    return Response({"message": "Activity deleted successfully"}, status=200)

 