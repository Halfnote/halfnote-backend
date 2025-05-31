from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from music.models import Review
from music.serializers import ReviewSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

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
        refresh = RefreshToken.for_user(user)
        return Response({
            'username': user.username,
            'bio': user.bio,
            'avatar_url': user.avatar_url,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        }, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    data = request.data
    user = authenticate(
        username=data.get('username'),
        password=data.get('password')
    )
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'username': user.username,
            'bio': user.bio,
            'avatar_url': user.avatar_url,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        })
    return Response({'error': 'Invalid credentials'}, status=401)

@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == "GET":
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    # PUT
    data = request.data
    request.user.bio = data.get('bio', request.user.bio)
    request.user.avatar_url = data.get('avatar_url', request.user.avatar_url)
    request.user.save()
    return Response({
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, username):
    try:
        user_to_follow = User.objects.get(username=username)
        if user_to_follow == request.user:
            return Response({'error': "Can't follow yourself!"}, status=400)
        request.user.following.add(user_to_follow)
        return Response({'message': f'Now following {username}'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, username):
    try:
        user_to_unfollow = User.objects.get(username=username)
        request.user.following.remove(user_to_unfollow)
        return Response({'message': f'Unfollowed {username}'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_following(request, username):
    try:
        user = User.objects.get(username=username)
        is_following = request.user.following.filter(id=user.id).exists()
        return Response({'is_following': is_following})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def user_followers(request, username):
    try:
        user = User.objects.get(username=username)
        followers = user.followers.all()
        serializer = UserSerializer(followers, many=True)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def user_following(request, username):
    try:
        user = User.objects.get(username=username)
        following = user.following.all()
        serializer = UserSerializer(following, many=True)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_feed(request):
    following_users = request.user.following.all()
    reviews = Review.objects.filter(
        user__in=following_users
    ).order_by('-created_at')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)