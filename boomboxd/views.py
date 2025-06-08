from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import render

def frontend(request):
    """Serve the frontend interface"""
    return render(request, 'index.html')

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'status': 'ok',
        'message': 'Halfnote API is running',
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