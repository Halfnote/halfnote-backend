import logging
import requests

from django.conf import settings
from django.db.models import Avg
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Album, Review, Genre
from .serializers import AlbumSerializer, ReviewSerializer, AlbumSearchResultSerializer
from .services import ExternalMusicService

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
def search(request):
    query = request.GET.get('q')
    if not query:
        return Response({'error': 'Query parameter required'}, status=400)
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
        return Response({'results': serializer.data})
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return Response({'error': 'Search failed', 'details': str(e)}, status=500)



@api_view(['GET'])
def unified_album_view(request, discogs_id):
    """
    Unified view for album details - handles both database albums and Discogs preview
    """
    # First, check if album exists in our database
    album = Album.objects.filter(discogs_id=discogs_id).first()
    
    if album:
        # Album exists in our database
        reviews = Review.objects.filter(album=album).order_by('-created_at')
        
        return Response({
            'album': AlbumSerializer(album).data,
            'reviews': ReviewSerializer(reviews, many=True).data,
            'review_count': reviews.count(),
            'average_rating': reviews.aggregate(Avg('rating'))['rating__avg'],
            'exists_in_db': True
        })
    else:
        # Album doesn't exist - fetch from Discogs
        service = ExternalMusicService()
        album_data = service.get_album_details(discogs_id)
        
        if not album_data:
            return Response({'error': 'Album not found'}, status=404)
        
        return Response({
            'album': album_data,
            'reviews': [],
            'review_count': 0,
            'average_rating': None,
            'exists_in_db': False
        })

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
                
            # Return info about genre validation
            response_data = ReviewSerializer(review).data
            if invalid_genres:
                response_data['warnings'] = {
                    'invalid_genres': invalid_genres,
                    'valid_genres_accepted': valid_genres
                }
            return Response(response_data, status=201)
        
        return Response(ReviewSerializer(review).data, status=201)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(['PUT', 'DELETE'])
def edit_review(request, review_id):
    """Edit or delete a review - only by the review author"""
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=401)
    
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response({"error": "Review not found"}, status=404)
    
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
            
            # Return response with warnings if needed
            response_data = ReviewSerializer(review).data
            if invalid_genres:
                response_data['warnings'] = {
                    'invalid_genres': invalid_genres,
                    'valid_genres_accepted': valid_genres
                }
            return Response(response_data)
        
        return Response(ReviewSerializer(review).data)
    
    elif request.method == 'DELETE':
        # Delete the review
        album = review.album
        review.delete()
        
        # Update album's genres after deletion
        album.genres.clear()
        all_review_genres = Genre.objects.filter(reviews__album=album).distinct()
        album.genres.set(all_review_genres)
        
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
    return Response({
        "message": f"Review {action} successfully",
        "is_pinned": review.is_pinned,
        "review": ReviewSerializer(review).data
    }) 