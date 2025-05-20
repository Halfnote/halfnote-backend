from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def api_root(request):
    return Response({
        'status': 'ok',
        'message': 'Boomboxd API is running',
        'version': '1.0.0',
        'endpoints': {
            'auth': {
                'register': '/api/register/',
                'login': '/api/login/',
                'profile': '/api/profile/',
            },
            'albums': {
                'search': '/api/albums/search/',
                'import': '/api/albums/import/{discogs_id}/',
                'detail': '/api/albums/{album_id}/',
                'reviews': '/api/albums/{album_id}/reviews/',
                'create_review': '/api/albums/{album_id}/review/',
            },
            'users': {
                'reviews': '/api/users/{username}/reviews/',
            }
        }
    }) 