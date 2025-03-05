from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.db.models import F
from .models import Review
from .serializers import ReviewSerializer
from music.models import Album, Single

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        album_id = self.request.data.get('album_id')
        single_id = self.request.data.get('single_id')
        
        if album_id:
            album = Album.objects.get(id=album_id)
            album.total_ratings = F('total_ratings') + 1
            album.average_rating = (F('average_rating') * F('total_ratings') + 
                                  self.request.data['rating']) / (F('total_ratings') + 1)
            album.save()
            serializer.save(user=self.request.user, album=album)
        elif single_id:
            single = Single.objects.get(id=single_id)
            single.total_ratings = F('total_ratings') + 1
            single.average_rating = (F('average_rating') * F('total_ratings') + 
                                   self.request.data['rating']) / (F('total_ratings') + 1)
            single.save()
            serializer.save(user=self.request.user, single=single)
        else:
            return Response({'error': 'Either album_id or single_id is required'}, 
                          status=status.HTTP_400_BAD_REQUEST) 