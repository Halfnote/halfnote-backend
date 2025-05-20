from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
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
                'import': '/api/albums/import/<discogs_id>/',
                'detail': '/api/albums/<album_id>/',
                'reviews': '/api/albums/<album_id>/reviews/',
            },
            'users': {
                'reviews': '/api/users/<username>/reviews/',
            }
        }
    }) 