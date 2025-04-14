from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.cache import cache
from django.db.models import Q
from .models import Album, Genre, Artist
from .serializers import AlbumSerializer, AlbumSearchResultSerializer
from .services.discogs import DiscogsClient
from .services.spotify import SpotifyClient
from rest_framework.exceptions import APIException
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
import uuid
import logging

logger = logging.getLogger(__name__)

class ExternalAPIError(APIException):
    status_code = 503
    default_detail = 'External service temporarily unavailable.'
    default_code = 'service_unavailable'

class MusicViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ['release_date', 'average_rating', 'total_ratings', 'created_at', 'title']
    ordering = ['-created_at']  # Default ordering

    def get_object(self):
        obj = super().get_object()
        cache_key = f'{self.cache_prefix}:{obj.id}'
        cache.set(cache_key, obj, timeout=3600)
        return obj

    def _search_external_apis(self, query):
        discogs_client = DiscogsClient()
        spotify_client = SpotifyClient()
        
        # Search Discogs first
        discogs_results = discogs_client.search_album(query)
        
        logger.info(f"Found {len(discogs_results)} albums on Discogs for '{query}'")
        
        results = []
        
        for discogs_item in discogs_results:
            # Get or create the artist
            artist_name = discogs_item['artist']
            artist, _ = Artist.objects.get_or_create(name=artist_name)
            
            # Get Spotify data (cover art, preview, etc.)
            spotify_data = spotify_client.search_album(discogs_item['title'], artist_name)
            
            # Process genres and styles
            genre_objects = []
            
            # Map Discogs genres and styles to our supported genres
            mapped_genre_names = discogs_client.map_genres(
                discogs_item.get('genres', []),
                discogs_item.get('styles', [])
            )
            
            # Create Genre objects from the mapped names
            for genre_name in mapped_genre_names:
                genre, _ = Genre.objects.get_or_create(name=genre_name)
                genre_objects.append(genre)
            
            # Extract year from the date string
            release_date = discogs_item.get('release_date')
            if not release_date:
                release_date = '1970-01-01'  # Default date
            
            # Prepare data for Album creation
            item_data = {
                'id': uuid.uuid4(),
                'title': discogs_item['title'],
                'artist': artist,
                'release_date': release_date,
                'cover_art_url': discogs_item.get('cover_art_url') or (spotify_data['cover_art_url'] if spotify_data else None),
                'spotify_url': spotify_data['spotify_url'] if spotify_data else None,
                'spotify_embed_url': spotify_data['spotify_embed_url'] if spotify_data else None,
                'discogs_id': discogs_item['id'],
                'discogs_url': discogs_item.get('discogs_url'),
            }
            
            # Add master ID for albums if available
            if 'master_id' in discogs_item:
                item_data['discogs_master_id'] = discogs_item['master_id']
            
            # Create the Album instance
            item = self.queryset.model.objects.create(**item_data)
            
            # Add genres
            if genre_objects:
                item.genres.set(genre_objects)
            
            # Get serialized data for the response
            results.append(self.get_serializer(item).data)

        return results

    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        Search for albums using Discogs API
        """
        query = request.query_params.get("q", "")
        if not query:
            return Response({"detail": "Query parameter 'q' is required"}, status=400)
            
        limit = int(request.query_params.get("limit", 10))
        
        cache_key = f"album_search_{query}_{limit}"
        cached_results = cache.get(cache_key)
        
        if cached_results:
            logger.info(f"Using cached results for query: {query}")
            return Response(cached_results)
        
        try:
            discogs_client = DiscogsClient()
            search_results = discogs_client.search_album(query)
            
            # Limit results based on the limit parameter
            search_results = search_results[:limit]
            
            # Need to serialize the data before caching to avoid ContentNotRenderedError
            serialized_results = AlbumSearchResultSerializer(search_results, many=True).data
            
            # Cache the serialized data, not the Response object
            cache.set(cache_key, serialized_results, timeout=3600)  # Cache for 1 hour
            
            return Response(serialized_results)
        except Exception as e:
            logger.error(f"Error searching albums: {str(e)}")
            return Response(
                {"detail": "An error occurred while searching for albums"},
                status=500,
            )

    @action(detail=False, methods=["post"])
    def save_to_library(self, request):
        """
        Save an album from Discogs to the local database
        Required fields in request body:
        - discogs_id: The ID of the album on Discogs
        - title: Album title
        - artist: Artist name
        - release_date: Release date (YYYY-MM-DD)
        - cover_art_url: URL to album cover art
        """
        # Require authentication for this endpoint
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            # Extract data from request
            discogs_id = request.data.get('discogs_id')
            title = request.data.get('title')
            artist_name = request.data.get('artist')
            release_date = request.data.get('release_date', '1970-01-01')
            cover_art_url = request.data.get('cover_art_url')
            
            # Validate required fields
            if not discogs_id or not title or not artist_name:
                return Response(
                    {"detail": "discogs_id, title, and artist are required fields"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Check if album already exists
            if Album.objects.filter(discogs_id=discogs_id).exists():
                album = Album.objects.get(discogs_id=discogs_id)
                return Response(
                    {"detail": "Album already exists in library", "album": self.get_serializer(album).data},
                    status=status.HTTP_200_OK
                )
                
            # Get or create the artist
            artist, _ = Artist.objects.get_or_create(name=artist_name)
            
            # Create the album
            album = Album.objects.create(
                id=uuid.uuid4(),
                title=title,
                artist=artist,
                release_date=release_date,
                cover_art_url=cover_art_url,
                discogs_id=discogs_id,
                discogs_url=request.data.get('discogs_url'),
                discogs_master_id=request.data.get('master_id') 
            )
            
            # Add genres if provided
            genres = request.data.get('genres', [])
            styles = request.data.get('styles', [])
            
            all_genres = []
            for genre_name in genres + styles:
                if genre_name:
                    genre, _ = Genre.objects.get_or_create(name=genre_name)
                    all_genres.append(genre)
                    
            if all_genres:
                album.genres.set(all_genres)
                
            return Response(
                {"detail": "Album saved to library", "album": self.get_serializer(album).data},
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Error saving album to library: {str(e)}")
            return Response(
                {"detail": "An error occurred while saving the album"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
    
    @action(detail=False, methods=['get'])
    def by_genre(self, request):
        """Get albums by genre name"""
        genre_name = request.query_params.get('name')
        if not genre_name:
            return Response({"detail": "Genre name parameter is required"}, status=400)
        
        try:
            albums = self.get_queryset().filter(genres__name__iexact=genre_name)
            page = self.paginate_queryset(albums)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(albums, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching albums by genre: {str(e)}")
            return Response(
                {"detail": "An error occurred while fetching albums by genre"},
                status=500
            ) 