from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Avg
from .models import Album, Review
from .serializers import AlbumSerializer, ReviewSerializer, AlbumSearchResultSerializer
from .services import ExternalMusicService
import logging

logger = logging.getLogger(__name__)

DISCOGS_URL = "https://api.discogs.com"

def search_discogs(query):
    headers = {
        'User-Agent': 'BoomboxdApp/1.0'
    }
    
    response = requests.get(
        f"{DISCOGS_URL}/database/search",
        params={
            "q": query,
            "type": "master",  # Changed to master instead of release
            "token": settings.DISCOGS_CONSUMER_KEY,
            "per_page": 10
        },
        headers=headers
    )
    
    # Print response for debugging
    print(f"Discogs API Response Status: {response.status_code}")
    print(f"Discogs API Response: {response.text}")
    
    if not response.ok:
        logger.error(f"Discogs API error: {response.status_code} - {response.text}")
        return []
        
    try:
        data = response.json()
        if 'results' not in data:
            logger.error(f"Unexpected Discogs API response format: {data}")
            return []
            
        # Transform the results to match our expected format
        transformed_results = []
        for result in data['results'][:10]:
            transformed_results.append({
                'title': result.get('title', ''),
                'artist': result.get('artist', ''),
                'year': result.get('year', ''),
                'cover_image': result.get('cover_image', ''),
                'master_id': result.get('master_id', ''),
                'id': result.get('id', '')
            })
        return transformed_results
    except Exception as e:
        logger.error(f"Error parsing Discogs response: {str(e)}")
        return []

def get_album_from_discogs(discogs_id):
    response = requests.get(
        f"{DISCOGS_URL}/releases/{discogs_id}",
        params={"token": settings.DISCOGS_CONSUMER_KEY}
    )
    return response.json()

@api_view(['GET'])
def search(request):
    """Search for albums on Discogs"""
    query = request.GET.get('q')
    if not query:
        return Response({'error': 'Query parameter required'}, status=400)
    
    try:
        service = ExternalMusicService()
        results = service.search_discogs(query)
        serializer = AlbumSearchResultSerializer(results, many=True)
        return Response({'results': serializer.data})
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return Response({'error': 'Search failed', 'details': str(e)}, status=500)

@api_view(['GET', 'POST'])
def import_album(request, discogs_id):
    try:
        # Check if already imported
        album = Album.objects.filter(discogs_id=discogs_id).first()
        if album:
            return Response(album_to_dict(album))
            
        # Get from Discogs and create
        data = get_album_from_discogs(discogs_id)
        album = Album.objects.create(
            title=data['title'],
            artist=data['artists'][0]['name'],
            year=data.get('year'),
            cover_url=data.get('images', [{}])[0].get('uri', ''),
            discogs_id=discogs_id
        )
        return Response(album_to_dict(album), status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['GET'])
def album_detail(request, album_id):
    try:
        album = Album.objects.get(id=album_id)
        return Response(album_to_dict(album))
    except Album.DoesNotExist:
        return Response({'error': 'Album not found'}, status=404)

def album_to_dict(album):
    return {
        'id': str(album.id),
        'title': album.title,
        'artist': album.artist,
        'year': album.year,
        'cover_url': album.cover_url,
        'discogs_id': album.discogs_id
    }

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
        
    # Create the album record
    album = Album.objects.create(
        title=album_data['title'],
        artist=album_data['artist'],
        year=album_data.get('year'),
        cover_url=album_data.get('cover_image'),
        discogs_id=discogs_id,
        genres=album_data.get('genres', []),
        styles=album_data.get('styles', [])
    )
    
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
        
        return Response(ReviewSerializer(review).data, status=201)
    except Exception as e:
        return Response({"error": str(e)}, status=400) 