from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django.conf import settings
from .serializers import UserSerializer
from rest_framework.decorators import action
from .models import UserProfile
from .serializers import UserProfileSerializer, ListSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import List, ListItem
from music.models import Album
from reviews.models import Review
from reviews.serializers import ReviewSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": serializer.data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Set access token
            response.set_cookie(
                settings.SIMPLE_JWT['AUTH_COOKIE'],
                response.data['access'],
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
                httponly=True,
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
            )
            # Set refresh token
            response.set_cookie(
                settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                response.data['refresh'],
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
                httponly=True,
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
            )
            # Remove tokens from response body
            del response.data['access']
            del response.data['refresh']
            response.data['message'] = 'Login successful'
        return response

class RefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        if refresh_token:
            request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            response.set_cookie(
                settings.SIMPLE_JWT['AUTH_COOKIE'],
                response.data['access'],
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
                httponly=True,
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
            )
            del response.data['access']
            response.data['message'] = 'Token refresh successful'
        return response

class LogoutView(generics.GenericAPIView):
    def post(self, request):
        response = Response({'message': 'Logout successful'})
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        return response

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'user__username'  # Use username for lookup
    lookup_url_kwarg = 'username'
    
    def get_queryset(self):
        return UserProfile.objects.select_related('user')
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, username=None):
        """Get all reviews by a user"""
        profile = self.get_object()
        reviews = Review.objects.filter(user=profile.user).order_by('-created_at')
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def favorites(self, request, username=None):
        """Get user's favorite albums"""
        profile = self.get_object()
        albums = profile.favorite_albums.all()
        from music.serializers import AlbumSerializer
        serializer = AlbumSerializer(albums, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def follow(self, request, username=None):
        """Follow a user"""
        target_profile = self.get_object()
        user_profile = request.user.profile
        
        if target_profile == user_profile:
            return Response(
                {"detail": "You cannot follow yourself"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_profile.following.add(target_profile)
        return Response({"detail": "User followed successfully"})
    
    @action(detail=True, methods=['post'])
    def unfollow(self, request, username=None):
        """Unfollow a user"""
        target_profile = self.get_object()
        user_profile = request.user.profile
        
        if target_profile == user_profile:
            return Response(
                {"detail": "You cannot unfollow yourself"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_profile.following.remove(target_profile)
        return Response({"detail": "User unfollowed successfully"})
    
    @action(detail=True, methods=['get'])
    def followers(self, request, username=None):
        """Get users following this profile"""
        profile = self.get_object()
        followers = profile.followers.all()
        serializer = UserProfileSerializer(followers, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def following(self, request, username=None):
        """Get users this profile is following"""
        profile = self.get_object()
        following = profile.following.all()
        serializer = UserProfileSerializer(following, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = UserProfileSerializer(request.user.profile, context={'request': request})
        return Response(serializer.data)

class ListViewSet(viewsets.ModelViewSet):
    queryset = List.objects.all()
    serializer_class = ListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = List.objects.all()
        
        # If not authenticated or not requesting own lists, only show public lists
        if not self.request.user.is_authenticated:
            return queryset.filter(list_type='public')
            
        username = self.request.query_params.get('username', None)
        if username:
            if username == self.request.user.username:
                # Show all own lists
                return queryset.filter(user__username=username)
            else:
                # Show only public lists for other users
                return queryset.filter(user__username=username, list_type='public')
                
        # Default: show public lists from all users and all own lists
        return queryset.filter(
            list_type='public'
        ) | queryset.filter(user=self.request.user)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == 'retrieve':
            context['detailed'] = True
        return context
    
    @action(detail=True, methods=['post'])
    def add_album(self, request, pk=None):
        """Add an album to a list"""
        album_list = self.get_object()
        
        # Check if user is the owner of the list
        if album_list.user != request.user:
            return Response(
                {"detail": "You can only add albums to your own lists"}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        album_id = request.data.get('album_id')
        if not album_id:
            return Response(
                {"detail": "album_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            album = Album.objects.get(id=album_id)
        except Album.DoesNotExist:
            return Response(
                {"detail": f"Album with ID {album_id} not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Get the highest order value for the list
        last_item = ListItem.objects.filter(list=album_list).order_by('-order').first()
        order = (last_item.order + 1) if last_item else 1
        
        # Create a new list item
        list_item = ListItem.objects.create(
            list=album_list,
            album=album,
            order=order,
            notes=request.data.get('notes', '')
        )
        
        serializer = ListItemSerializer(list_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def remove_album(self, request, pk=None):
        """Remove an album from a list"""
        album_list = self.get_object()
        
        # Check if user is the owner of the list
        if album_list.user != request.user:
            return Response(
                {"detail": "You can only remove albums from your own lists"}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        album_id = request.query_params.get('album_id')
        if not album_id:
            return Response(
                {"detail": "album_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            list_item = ListItem.objects.get(list=album_list, album_id=album_id)
            list_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ListItem.DoesNotExist:
            return Response(
                {"detail": "Album not found in this list"}, 
                status=status.HTTP_404_NOT_FOUND
            ) 