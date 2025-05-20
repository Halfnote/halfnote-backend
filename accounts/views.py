from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User

@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    data = json.loads(request.body)
    try:
        user = User.objects.create_user(
            username=data['username'],
            password=data['password'],
            bio=data.get('bio', ''),
            avatar_url=data.get('avatar_url', '')
        )
        return JsonResponse({
            'username': user.username,
            'bio': user.bio,
            'avatar_url': user.avatar_url
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    data = json.loads(request.body)
    user = authenticate(
        username=data.get('username'),
        password=data.get('password')
    )
    if user:
        auth_login(request, user)
        return JsonResponse({
            'username': user.username,
            'bio': user.bio,
            'avatar_url': user.avatar_url
        })
    return JsonResponse({'error': 'Invalid credentials'}, status=401)

@require_http_methods(["GET", "PUT"])
def profile(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not logged in'}, status=401)
        
    if request.method == "GET":
        return JsonResponse({
            'username': request.user.username,
            'bio': request.user.bio,
            'avatar_url': request.user.avatar_url
        })
    
    # PUT request
    data = json.loads(request.body)
    request.user.bio = data.get('bio', request.user.bio)
    request.user.avatar_url = data.get('avatar_url', request.user.avatar_url)
    request.user.save()
    return JsonResponse({
        'username': request.user.username,
        'bio': request.user.bio,
        'avatar_url': request.user.avatar_url
    }) 