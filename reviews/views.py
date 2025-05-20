from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from .models import Review
from music.models import Album

ALLOWED_GENRES = [
    'Pop', 'Rock', 'Hip-Hop', 'Jazz', 'Electronic', 
    'Classical', 'Folk', 'Country', 'Metal', 'Other'
]

@csrf_exempt
@api_view(['POST'])
def create_review(request, album_id):
    if not request.user.is_authenticated:
        return Response({'error': 'Login required'}, status=401)
    
    try:
        album = Album.objects.get(id=album_id)
        
        # Validate rating
        rating = int(request.data.get('rating', 0))
        if not (1 <= rating <= 10):
            return Response({'error': 'Rating must be between 1 and 10'}, status=400)
            
        # Validate genres
        genres = request.data.get('genres', [])
        if not all(g in ALLOWED_GENRES for g in genres):
            return Response({'error': 'Invalid genres'}, status=400)
            
        review = Review.objects.create(
            user=request.user,
            album=album,
            rating=rating,
            text=request.data.get('text', ''),
            genres=genres
        )
        return Response(review_to_dict(review), status=201)
    except Album.DoesNotExist:
        return Response({'error': 'Album not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['GET'])
def album_reviews(request, album_id):
    try:
        reviews = Review.objects.filter(album_id=album_id).order_by('-created_at')
        return Response({
            'reviews': [review_to_dict(r) for r in reviews]
        })
    except Exception as e:
        return Response({'error': str(e)}, status=400)

def review_to_dict(review):
    return {
        'user': review.user.username,
        'album': {
            'id': str(review.album.id),
            'title': review.album.title,
            'artist': review.album.artist,
            'cover_url': review.album.cover_url
        },
        'rating': review.rating,
        'text': review.text,
        'genres': review.genres,
        'created_at': review.created_at.isoformat()
    } 