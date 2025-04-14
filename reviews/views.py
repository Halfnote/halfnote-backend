from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.db.models import F
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Review
from .serializers import ReviewSerializer
from music.models import Album

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        'user__username': ['exact'],
        'album__id': ['exact'],
        'album__title': ['icontains'],
        'album__artist__name': ['exact', 'icontains'],
        'rating': ['exact', 'gte', 'lte'],
        'created_at': ['gte', 'lte'],
    }
    search_fields = ['text', 'album__title', 'album__artist__name']
    ordering_fields = ['created_at', 'rating', 'album__title']
    ordering = ['-created_at']  # Default ordering

    def perform_create(self, serializer):
        album_id = self.request.data.get('album_id')
        rating = float(self.request.data.get('rating'))
        
        if album_id:
            try:
                album = Album.objects.get(id=album_id)
                
                # Update album rating (without using F expressions in calculations)
                current_total = album.total_ratings
                current_avg = album.average_rating
                
                # Calculate new average
                if current_total == 0:
                    new_avg = rating
                else:
                    new_avg = ((current_avg * current_total) + rating) / (current_total + 1)
                
                # Update the album
                album.total_ratings = current_total + 1
                album.average_rating = new_avg
                album.save()
                
                # Save the review
                serializer.save(user=self.request.user, album=album)
                
            except Album.DoesNotExist:
                return Response(
                    {"status": "error", "detail": f"Album with ID {album_id} not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {"status": "error", "detail": str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"status": "error", "detail": "album_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            ) 