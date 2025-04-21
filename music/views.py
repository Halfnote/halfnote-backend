from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.cache import cache
from django.db.models import Q
from .models import Album, Genre, Artist
from .serializers import AlbumSerializer, AlbumSearchResultSerializer
from .services import ExternalMusicService
from .decorators import handle_api_errors, validate_params, cache_response
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
import uuid
import logging
import re

logger = logging.getLogger(__name__)

class MusicViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ['release_date', 'average_rating', 'total_ratings', 'created_at', 'title']
    ordering = ['-created_at']

    def get_object(self):
        obj = super().get_object()
        cache_key = f'{self.cache_prefix}:{obj.id}'
        cache.set(cache_key, self.get_serializer(obj).data, timeout=3600)
        return obj

    @handle_api_errors
    @validate_params('q')
    @cache_response(timeout=3600)
    @action(detail=False, methods=["get"])
    def search(self, request):
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

        # Process genres
        genres = request.data.get('genres', []) + request.data.get('styles', [])
        genre_objects = []
        for genre_name in genres:
            genre, _ = Genre.objects.get_or_create(name=genre_name)
            genre_objects.append(genre)
        
        if genre_objects:
            album.genres.set(genre_objects)

        return Response(self.get_serializer(album).data, status=status.HTTP_201_CREATED)

class AlbumViewSet(MusicViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    cache_prefix = 'album'
    filterset_fields = {
        'title': ['exact', 'icontains'],
        'artist__name': ['exact', 'icontains'],
        'genres__name': ['exact'],
        'release_date': ['exact', 'year', 'year__gte', 'year__lte'],
        'average_rating': ['gte', 'lte'],
    }
    search_fields = ['title', 'artist__name', 'genres__name']

    @handle_api_errors
    @cache_response(timeout=3600)
    @action(detail=False, methods=['get'])
    def by_genre(self, request):
        """Get albums filtered by genre"""
        genre = request.query_params.get('genre')
        if not genre:
            return Response(
                {"detail": "Genre parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        albums = self.queryset.filter(genres__name__iexact=genre)
        return Response(self.get_serializer(albums, many=True).data) 