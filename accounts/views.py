from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from music.models import Review
from music.serializers import ReviewSerializer
from django.http import status

User = get_user_model()

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user.
    
    POST parameters:
    - username: Required. The username for the new account
    - password: Required. The password for the new account
    - bio: Optional. A short bio for the user
    - avatar_url: Optional. URL to the user's avatar image
    """
    try:
        user = User.objects.create_user(
            username=request.data['username'],
            password=request.data['password'],
            bio=request.data.get('bio', ''),
            avatar_url=request.data.get('avatar_url', '')
        )
        return Response({
            'username': user.username,
            'bio': user.bio,
            'avatar_url': user.avatar_url
        }, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
@permission_classes([AllowAny])
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
@permission_classes([IsAuthenticated])
def profile(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not logged in'}, status=401)
        
    if request.method == "GET":
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
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

@api_view(['GET'])
@permission_classes([AllowAny])
def user_reviews(request, username):
    """Get all reviews by a specific user"""
    try:
        user = User.objects.get(username=username)
        reviews = Review.objects.filter(user=user).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND) 