from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.cache import cache
from django.db.models import Q
from .models import Album, Single, Genre
from .serializers import AlbumSerializer, SingleSerializer
from .services.musicbrainz import MusicBrainzClient
from .services.spotify import SpotifyClient
from rest_framework.exceptions import APIException
from rest_framework.filters import OrderingFilter
import uuid
import logging

logger = logging.getLogger(__name__)

class ExternalAPIError(APIException):
    status_code = 503
    default_detail = 'External service temporarily unavailable.'
    default_code = 'service_unavailable'

class MusicViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [OrderingFilter]
    ordering_fields = ['release_date', 'average_rating', 'total_ratings']

    def get_object(self):
        obj = super().get_object()
        cache_key = f'{self.cache_prefix}:{obj.id}'
        cache.set(cache_key, obj, timeout=3600)
        return obj

    def _search_external_apis(self, query, is_album=True):
        mb_client = MusicBrainzClient()
        spotify_client = SpotifyClient()

        try:
            mb_results = mb_client.search_album(query) if is_album else mb_client.search_single(query)
            if not mb_results:
                return Response({'message': 'No results found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"MusicBrainz API error: {str(e)}")
            raise ExternalAPIError()

        results = []
        for mb_item in mb_results:
            spotify_data = (spotify_client.search_album(mb_item['title'], mb_item['artist']) 
                          if is_album else 
                          spotify_client.search_track(mb_item['title'], mb_item['artist']))
            
            genre_objects = []
            if spotify_data and spotify_data.get('genres'):
                for genre_name in spotify_data['genres']:
                    genre, _ = Genre.objects.get_or_create(name=genre_name)
                    genre_objects.append(genre)
            
            item_data = {
                'id': uuid.uuid4(),
                'title': mb_item['title'],
                'artist': mb_item['artist'],
                'release_date': mb_item['release_date'],
                'cover_art_url': spotify_data['cover_art_url'] if spotify_data else mb_item.get('cover_art_url'),
                'spotify_url': spotify_data['spotify_url'] if spotify_data else None,
                'spotify_embed_url': spotify_data['spotify_embed_url'] if spotify_data else None,
                'musicbrainz_id': mb_item['id'],
            }
            
            item = self.queryset.model.objects.create(**item_data)
            if genre_objects:
                item.genres.set(genre_objects)
            
            results.append(self.get_serializer(item).data)

        return results

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Query parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        cache_key = f'search:{self.cache_prefix}:{query}'
        cached_results = cache.get(cache_key)
        if cached_results:
            return Response(cached_results)

        db_results = self.queryset.filter(
            Q(title__icontains=query) | Q(artist__icontains=query)
        )[:5]
        
        if db_results:
            serializer = self.get_serializer(db_results, many=True)
            cache.set(cache_key, serializer.data, timeout=3600)
            return Response(serializer.data)

        results = self._search_external_apis(query, is_album=self.cache_prefix == 'album')
        cache.set(cache_key, results, timeout=3600)
        return Response(results)

class AlbumViewSet(MusicViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    cache_prefix = 'album'

class SingleViewSet(MusicViewSet):
    queryset = Single.objects.all()
    serializer_class = SingleSerializer
    cache_prefix = 'single' 