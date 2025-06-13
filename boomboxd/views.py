from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
import requests
from django.contrib.auth import get_user_model
import os

User = get_user_model()

def frontend(request):
    """Serve the React frontend"""
    from django.conf import settings
    
    # Try multiple locations for the index.html file
    possible_paths = []
    
    # Add STATIC_ROOT path if it exists (production)
    if settings.STATIC_ROOT:
        possible_paths.append(os.path.join(settings.STATIC_ROOT, 'index.html'))
    
    # Add STATICFILES_DIRS paths (development)
    if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
        for static_dir in settings.STATICFILES_DIRS:
            possible_paths.append(os.path.join(static_dir, 'index.html'))
    
    # Add fallback paths
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
    
    return HttpResponse("React app not found. Please run 'npm run build' to build the frontend.", status=500)

def legacy_frontend(request):
    """Serve the legacy Django template interface"""
    return render(request, 'legacy/index.html')

def activity_page(request):
    """Display the activity feed page"""
    return render(request, 'activity.html')

def user_profile(request, username):
    """Display a user's profile page - the main profile view like Letterboxd"""
    user = get_object_or_404(User, username=username)
    
    # Check if the current user is viewing their own profile
    is_own_profile = request.user.is_authenticated and request.user.username == username
    
    # Get basic stats
    review_count = user.album_reviews.count()
    follower_count = user.followers.count()
    following_count = user.following.count()
    
    return render(request, 'user_profile.html', {
        'profile_user': user,
        'username': username,
        'is_own_profile': is_own_profile,
        'review_count': review_count,
        'follower_count': follower_count,
        'following_count': following_count,
    })

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

def search_results(request):
    """Dedicated search results page"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return render(request, 'search_results.html', {
            'query': '',
            'albums': [],
            'users': [],
            'total_results': 0
        })
    
    albums = []
    users = []
    
    try:
        # Search albums using our existing Discogs search
        from music.views import search_discogs
        
        discogs_results = search_discogs(query)
        
        # Process results similar to how music/views.py does it
        albums = []
        for result in discogs_results:
            # Parse artist and title more intelligently
            title = result.get('title', '')
            artist = 'Various Artists'  # Default fallback
            album_title = title
            
            # Try to extract artist - but don't assume format
            if ' - ' in title:
                parts = title.split(' - ', 1)
                if len(parts) == 2:
                    potential_artist, potential_title = parts
                    # Only use if the first part looks like an artist (not too long)
                    if len(potential_artist.strip()) < 100:
                        # Clean up Discogs disambiguation numbers like (2), (3)
                        import re
                        clean_artist = re.sub(r'\s*\(\d+\)$', '', potential_artist.strip()).strip()
                        artist = clean_artist if clean_artist else potential_artist.strip()
                        album_title = potential_title.strip()
            
            albums.append({
                'id': result.get('id'),
                'title': album_title,
                'artist': artist,
                'year': result.get('year'),
                'genre': result.get('genre', []),
                'style': result.get('style', []),
                'cover_image': result.get('cover_image', ''),
                'thumb': result.get('thumb', ''),
            })
    except Exception as e:
        print(f"Album search error: {e}")
        pass  # Continue even if album search fails
    
    try:
        # Search users from our database
        users_queryset = User.objects.filter(
            username__icontains=query
        )[:10]
        
        users = []
        for user in users_queryset:
            # Handle avatar - use avatar.url if exists, otherwise default
            avatar_url = ''
            if user.avatar:
                try:
                    avatar_url = user.avatar.url
                except:
                    avatar_url = ''
            
            users.append({
                'id': user.id,
                'username': user.username,
                'bio': user.bio or '',
                'avatar_url': avatar_url,
                'is_following': False  # We'll need authentication context for this
            })
    except Exception as e:
        print(f"User search error: {e}")
        pass  # Continue even if user search fails
    
    total_results = len(albums) + len(users)
    
    return render(request, 'search_results.html', {
        'query': query,
        'albums': albums,
        'users': users,
        'total_results': total_results
    })

def followers_page(request, username):
    """Followers page for a specific user"""
    try:
        profile_user = User.objects.get(username=username)
        return render(request, 'followers.html', {
            'username': username,
            'profile_user': profile_user
        })
    except User.DoesNotExist:
        return render(request, '404.html', status=404)

def following_page(request, username):
    """Following page for a specific user"""
    try:
        profile_user = User.objects.get(username=username)
        return render(request, 'following.html', {
            'username': username,
            'profile_user': profile_user
        })
    except User.DoesNotExist:
        return render(request, '404.html', status=404)

def review_detail(request, review_id):
    """Individual review detail page - like Letterboxd's review pages"""
    from music.models import Review
    
    try:
        review = Review.objects.select_related('user', 'album').get(id=review_id)
        
        # Check if current user is the review author
        is_own_review = request.user.is_authenticated and request.user == review.user
        
        return render(request, 'review_detail.html', {
            'review': review,
            'is_own_review': is_own_review,
        })
    except Review.DoesNotExist:
        return render(request, '404.html', status=404) 