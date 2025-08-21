"""
Halfnote Core Views
Simple views for serving the React frontend and API root
"""

import os
from django.http import HttpResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


def frontend(request):
    """Serve the React frontend application"""
    # Find the React build index.html file
    possible_paths = []
    
    if settings.STATIC_ROOT:
        possible_paths.append(os.path.join(settings.STATIC_ROOT, 'index.html'))
    
    if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
        for static_dir in settings.STATICFILES_DIRS:
            possible_paths.append(os.path.join(static_dir, 'index.html'))
    
    # Fallback paths
    possible_paths.extend([
        os.path.join(settings.BASE_DIR, 'staticfiles', 'index.html'),
        os.path.join(settings.BASE_DIR, 'frontend', 'build', 'index.html'),
    ])
    
    for index_file_path in possible_paths:
        try:
            with open(index_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return HttpResponse(html_content, content_type='text/html')
        except FileNotFoundError:
            continue
    
    return HttpResponse(
        "React app not found. Please run 'npm run build' to build the frontend.",
        status=500
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint with available endpoints"""
    return Response({
        'status': 'ok',
        'message': 'Halfnote API - Music review platform',
        'version': '1.0.0',
        'endpoints': {
            'authentication': {
                'register': '/api/accounts/register/',
                'login': '/api/accounts/login/',
                'profile': '/api/accounts/profile/',
            },
            'music': {
                'search': '/api/music/search/',
                'album_detail': '/api/music/albums/{discogs_id}/',
                'create_review': '/api/music/albums/{discogs_id}/review/',
                'activity_feed': '/api/music/activity/',
                'reviews': '/api/music/reviews/',
            },
            'users': {
                'user_reviews': '/api/accounts/users/{username}/reviews/',
                'user_profile': '/api/accounts/users/{username}/',
                'follow_user': '/api/accounts/users/{username}/follow/',
            }
        }
    })