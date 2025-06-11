from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import os

from .serializers import UserProfileSerializer, UserFollowSerializer, UserSerializer
from music.models import Review
from music.serializers import ReviewSerializer

User = get_user_model()

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
            bio=request.data.get('bio', '')
        )
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            user.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'username': user.username,
            'bio': user.bio,
            'avatar': user.avatar.url if user.avatar else None,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        }, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

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
            'avatar': user.avatar.url if user.avatar else None,
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh)
        })
    return Response({'error': 'Invalid credentials'}, status=401)

@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def profile(request):
    if request.method == "GET":
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    # PUT - Handle both JSON and form data
    data = request.data.copy()
    
    # Handle favorite_genres if it's JSON string
    if 'favorite_genres' in data and isinstance(data['favorite_genres'], str):
        try:
            import json
            data['favorite_genres'] = json.loads(data['favorite_genres'])
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Handle avatar file upload
    if 'avatar' in request.FILES:
        data['avatar'] = request.FILES['avatar']
    
    serializer = UserProfileSerializer(request.user, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(['GET'])
@permission_classes([AllowAny])
def get_profile(request, username=None):
    """Get user profile information"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    serializer = UserProfileSerializer(user)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile information"""
    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, username):
    """Follow a user"""
    user_to_follow = get_object_or_404(User, username=username)
    
    if user_to_follow == request.user:
        return Response(
            {'error': 'You cannot follow yourself'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if already following
    if not request.user.following.filter(id=user_to_follow.id).exists():
        request.user.following.add(user_to_follow)
        
        # Create activity for following
        from music.models import Activity
        Activity.objects.create(
            user=request.user,
            activity_type='user_followed',
            target_user=user_to_follow
        )
    
    return Response({'status': 'following'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, username):
    """Unfollow a user"""
    user_to_unfollow = get_object_or_404(User, username=username)
    request.user.following.remove(user_to_unfollow)
    return Response({'status': 'unfollowed'})

@api_view(['GET'])
@permission_classes([AllowAny])
def get_followers(request, username):
    """Get list of user's followers"""
    user = get_object_or_404(User, username=username)
    followers = user.followers.all()
    serializer = UserFollowSerializer(followers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_following(request, username):
    """Get list of users that the user is following"""
    user = get_object_or_404(User, username=username)
    following = user.following.all()
    serializer = UserFollowSerializer(following, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_feed(request):
    following_users = request.user.following.all()
    reviews = Review.objects.filter(
        user__in=following_users
    ).order_by('-created_at')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    """Search for users by username"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return Response({'error': 'Query parameter required'}, status=400)
    
    # Search for users whose username contains the query (case-insensitive)
    users = User.objects.filter(
        username__icontains=query
    ).exclude(
        id=request.user.id  # Exclude the current user from results
    )[:10]  # Limit to 10 results
    
    # Get users that the current user is already following
    following_usernames = set(request.user.following.values_list('username', flat=True))
    
    results = []
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'bio': user.bio or '',
            'avatar': user.avatar.url if user.avatar else None,
            'is_following': user.username in following_usernames,
        }
        results.append(user_data)
    
    return Response({'users': results})

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_cloudinary(request):
    """Debug endpoint to check Cloudinary configuration"""
    from django.conf import settings
    import cloudinary
    
    config = cloudinary.config()
    return Response({
        'cloudinary_configured': hasattr(settings, 'DEFAULT_FILE_STORAGE') and 'cloudinary' in settings.DEFAULT_FILE_STORAGE.lower(),
        'cloud_name': config.cloud_name if config.cloud_name else 'Not set',
        'api_key_present': bool(config.api_key),
        'api_secret_present': bool(config.api_secret),
        'default_storage': getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_storage(request):
    """Debug endpoint to check storage configuration"""
    from django.conf import settings
    from django.core.files.storage import default_storage
    import cloudinary
    
    try:
        config = cloudinary.config()
        cloudinary_configured = bool(config.cloud_name and config.api_key and config.api_secret)
    except:
        cloudinary_configured = False
        config = None
    
    return Response({
        'default_file_storage_setting': getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set'),
        'actual_storage_class': str(type(default_storage)),
        'cloudinary_configured': cloudinary_configured,
        'cloudinary_cloud_name': config.cloud_name if config and config.cloud_name else 'Not set',
        'cloudinary_api_key_present': bool(config and config.api_key) if config else False,
        'environment_vars': {
            'CLOUDINARY_CLOUD_NAME': bool(os.getenv('CLOUDINARY_CLOUD_NAME')),
            'CLOUDINARY_API_KEY': bool(os.getenv('CLOUDINARY_API_KEY')),
            'CLOUDINARY_API_SECRET': bool(os.getenv('CLOUDINARY_API_SECRET')),
        }
    })