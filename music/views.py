from rest_framework import status
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Avg
from .models import Album, Review
from .serializers import AlbumSerializer, ReviewSerializer, AlbumSearchResultSerializer
from .services import ExternalMusicService
import logging
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes

logger = logging.getLogger(__name__)

def search_discogs(query):
    headers = {
        'User-Agent': 'BoomboxdApp/1.0',
        'Authorization': f'Discogs token={settings.DISCOGS_TOKEN}'
    }

    response = requests.get(
        f"{settings.DISCOGS_API_URL}/database/search",
        params={
            "q": query,
            "type": "master",
            "per_page": 10
        },
        headers=headers
    )

    print(f"Discogs API Response Status: {response.status_code}")
    print(f"Discogs API Response: {response.text}")

    if not response.ok:
        logger.error(f"Discogs API error: {response.status_code} - {response.text}")
        return []

    return response.json().get('results', [])

def get_album_from_discogs(discogs_id):
    response = requests.get(
        f"{settings.DISCOGS_API_URL}/releases/{discogs_id}",
        params={"token": settings.DISCOGS_CONSUMER_KEY}
    )
    return response.json()


@api_view(['GET'])
def search(request):
    query = request.GET.get('q')
    if not query:
        return Response({'error': 'Query parameter required'}, status=400)
    try:
        results = search_discogs(query)
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
        
    # Create the album record with only tracklist and credits as new metadata
    album = Album.objects.create(
        title=album_data['title'],
        artist=album_data['artist'],
        year=album_data.get('year'),
        cover_url=album_data.get('cover_image'),
        discogs_id=discogs_id,
        genres=album_data.get('genres', []),
        styles=album_data.get('styles', []),
        tracklist=album_data.get('tracklist', []),
        credits=album_data.get('credits', [])
    )
    
    return album

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
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