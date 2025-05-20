from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Album
from .serializers import AlbumSerializer, AlbumSearchResultSerializer
from .services import ExternalMusicService
from .decorators import handle_api_errors, validate_params, cache_response
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
import uuid
import logging
import re
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import requests
from django.conf import settings

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

@csrf_exempt
@api_view(['GET'])
def search(request):
    query = request.GET.get('q')
    if not query:
        return Response({'error': 'Query parameter required'}, status=400)
    
    try:
        service = ExternalMusicService()
        cache_key = f'discogs_search:{query}'
        results = service.search_discogs(query, cache_key)
        return Response({'results': results})
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return Response({'error': 'Search failed', 'details': str(e)}, status=500)

@csrf_exempt
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

class AlbumViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing albums.
    """
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for albums on Discogs.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {'error': 'Search query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ExternalMusicService()
        cache_key = f'discogs_search:{query}'
        results = service.search_discogs(query, cache_key)
        serializer = AlbumSearchResultSerializer(results, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def import_from_discogs(self, request):
        """
        Import an album from Discogs using its ID.
        """
        discogs_id = request.data.get('discogs_id')
        if not discogs_id:
            return Response(
                {'error': 'Discogs ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if album already exists
        existing_album = Album.objects.filter(discogs_id=discogs_id).first()
        if existing_album:
            serializer = self.get_serializer(existing_album)
            return Response(serializer.data)

        # Get album data from Discogs service
        service = ExternalMusicService()
        album_data = service._make_request(f"masters/{discogs_id}")
        if not album_data:
            return Response(
                {'error': 'Album not found on Discogs'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Format album data
        formatted_data = {
            'title': album_data.get('title'),
            'artist': album_data.get('artists', [{}])[0].get('name', 'Unknown Artist'),
            'release_date': album_data.get('year'),
            'cover_image_url': album_data.get('images', [{}])[0].get('uri'),
            'discogs_id': discogs_id
        }

        # Create new album
        serializer = self.get_serializer(data=formatted_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_object(self):
        obj = super().get_object()
        cache_key = f'{self.cache_prefix}:{obj.id}'
        cache.set(cache_key, self.get_serializer(obj).data, timeout=3600)
        return obj

    @handle_api_errors
    @validate_params('q')
    @cache_response(timeout=3600)
    @action(detail=False, methods=["get"])
    def search_discogs(self, request):
        """Search for albums using Discogs"""
        query = request.query_params['q']
        limit = int(request.query_params.get("limit", 10))
        
        service = ExternalMusicService()
        cache_key = f'discogs_search:{query}'
        results = service.search_discogs(query, cache_key)[:limit]
        
        return Response(AlbumSearchResultSerializer(results, many=True).data)

    @handle_api_errors
    @action(detail=True, methods=["post"])
    def set_spotify_url(self, request, pk=None):
        """Set Spotify URL for an album"""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        spotify_url = request.data.get('spotify_url', '').strip()
        if not spotify_url:
            return Response(
                {"detail": "spotify_url is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Extract Spotify ID from URL
        spotify_id = None
        patterns = [
            r'spotify.com/album/([a-zA-Z0-9]{22})',  # Web URL
            r'spotify:album:([a-zA-Z0-9]{22})',      # URI
            r'^([a-zA-Z0-9]{22})$'                   # Just the ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, spotify_url)
            if match:
                spotify_id = match.group(1)
                break
                
        if not spotify_id:
            return Response(
                {"detail": "Invalid Spotify URL format"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        album = self.get_object()
        album.spotify_id = spotify_id
        album.spotify_url = f"https://open.spotify.com/album/{spotify_id}"
        album.spotify_embed_url = f"https://open.spotify.com/embed/album/{spotify_id}"
        album.save()
        
        return Response(self.get_serializer(album).data)

    @handle_api_errors
    @action(detail=False, methods=["post"])
    def save_to_library(self, request):
        """Save an album to the local database"""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        required_fields = ['discogs_id', 'title', 'artist']
        if not all(field in request.data for field in required_fields):
            return Response(
                {"detail": f"Required fields: {', '.join(required_fields)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if album already exists
        if Album.objects.filter(discogs_id=request.data['discogs_id']).exists():
            album = Album.objects.get(discogs_id=request.data['discogs_id'])
            return Response(
                {"detail": "Album already exists in library", "album": self.get_serializer(album).data},
                status=status.HTTP_200_OK
            )

        # Get or create artist
        artist, _ = Artist.objects.get_or_create(name=request.data['artist'])

        # Create album
        album = Album.objects.create(
            id=uuid.uuid4(),
            title=request.data['title'],
            artist=artist,
            release_date=request.data.get('release_date', '1970-01-01'),
            cover_art_url=request.data.get('cover_art_url'),
            discogs_id=request.data['discogs_id'],
            discogs_url=request.data.get('discogs_url'),
            discogs_master_id=request.data.get('master_id'),
            spotify_url=request.data.get('spotify_url'),
            spotify_embed_url=request.data.get('spotify_embed_url')
        )

        return Response(self.get_serializer(album).data, status=status.HTTP_201_CREATED)

    cache_prefix = 'album'
    filterset_fields = {
        'title': ['exact', 'icontains'],
        'artist__name': ['exact', 'icontains'],
        'release_date': ['exact', 'year', 'year__gte', 'year__lte'],
        'average_rating': ['gte', 'lte'],
    }
    search_fields = ['title', 'artist__name'] 