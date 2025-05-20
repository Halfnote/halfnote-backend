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
                'register': '/api/accounts/register/',
                'login': '/api/accounts/login/',
                'profile': '/api/accounts/profile/',
            },
            'music': {
                'search': '/api/music/search/',
                'detail': '/api/music/albums/{discogs_id}/',
                'create_review': '/api/music/albums/{discogs_id}/review/',
            },
            'users': {
                'reviews': '/api/accounts/users/{username}/reviews/',
            }
        }
    }) 