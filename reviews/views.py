from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Review
from music.models import Album

ALLOWED_GENRES = [
    'Pop', 'Rock', 'Hip-Hop', 'Jazz', 'Electronic', 
    'Classical', 'Folk', 'Country', 'Metal', 'Other'
]

@csrf_exempt
@require_http_methods(["POST"])
def create_review(request, album_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    
    try:
        data = json.loads(request.body)
        album = Album.objects.get(id=album_id)
        
        # Validate rating
        rating = int(data.get('rating', 0))
        if not (1 <= rating <= 5):
            return JsonResponse({'error': 'Rating must be between 1 and 5'}, status=400)
            
        # Validate genres
        genres = data.get('genres', [])
        if not all(g in ALLOWED_GENRES for g in genres):
            return JsonResponse({'error': 'Invalid genres'}, status=400)
            
        review = Review.objects.create(
            user=request.user,
            album=album,
            rating=rating,
            text=data.get('text', ''),
            genres=genres
        )
        return JsonResponse(review_to_dict(review), status=201)
    except Album.DoesNotExist:
        return JsonResponse({'error': 'Album not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def album_reviews(request, album_id):
    try:
        reviews = Review.objects.filter(album_id=album_id).order_by('-created_at')
        return JsonResponse({
            'reviews': [review_to_dict(r) for r in reviews]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def user_reviews(request, username):
    reviews = Review.objects.filter(user__username=username).order_by('-created_at')
    return JsonResponse({
        'reviews': [review_to_dict(r) for r in reviews]
    })

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