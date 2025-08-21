from rest_framework import serializers
from django.contrib.auth import get_user_model
from music.models import Review
from django.db.models import Count

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    pinned_reviews = serializers.SerializerMethodField()
    favorite_albums = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    most_reviewed_genres = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'name', 'display_name',
            'bio', 'location', 'avatar', 'banner', 'favorite_genres', 'most_reviewed_genres',
            'follower_count', 'following_count', 'review_count', 'pinned_reviews', 
            'favorite_albums', 'is_following', 'is_staff'
        ]
        read_only_fields = ['id', 'email', 'display_name', 'is_staff']
    
    def get_display_name(self, obj):
        """Return the name if available, otherwise username"""
        return obj.name if obj.name else obj.username
    
    def get_most_reviewed_genres(self, obj):
        """Get user's most reviewed genres with counts"""
        from music.models import Genre
        from django.db.models import Q
        
        genre_stats = Genre.objects.filter(
            reviews__user=obj
        ).annotate(
            review_count=Count('reviews', filter=Q(reviews__user=obj))
        ).order_by('-review_count')[:10]  # Top 10 genres
        
        return [
            {
                'id': genre.id,
                'name': genre.name,
                'count': genre.review_count
            }
            for genre in genre_stats
        ]
    
    def to_representation(self, instance):
        """Convert favorite_genres from list of strings to list of objects for frontend"""
        data = super().to_representation(instance)
        if data.get('favorite_genres'):
            data['favorite_genres'] = [
                {'id': hash(genre) % 1000000, 'name': genre}
                for genre in data['favorite_genres']
            ]
        else:
            data['favorite_genres'] = []
        return data
    
    def update(self, instance, validated_data):
        """Handle favorite_genres conversion from objects to strings"""
        if 'favorite_genres' in validated_data:
            genres_data = validated_data['favorite_genres']
            if genres_data and isinstance(genres_data[0], dict):
                # Convert from objects to strings for database storage
                validated_data['favorite_genres'] = [g['name'] for g in genres_data]
            elif genres_data is None or genres_data == []:
                # Handle empty list or None (user cleared all genres)
                validated_data['favorite_genres'] = []
        return super().update(instance, validated_data)
    
    def get_follower_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()
    
    def get_review_count(self, obj):
        return Review.objects.filter(user=obj).count()
    
    def get_pinned_reviews(self, obj):
        try:
            from music.serializers import ReviewSerializer
            pinned_reviews = Review.objects.filter(user=obj, is_pinned=True).order_by('-created_at')[:2]
            return ReviewSerializer(pinned_reviews, many=True, context=self.context).data
        except Exception as e:
            # Return empty list if there's any issue to prevent profile page from breaking
            return []
    
    def get_favorite_albums(self, obj):
        """Get user's favorite albums with album details and user review info"""
        try:
            from music.models import Review
            favorite_albums = obj.favorite_albums.all()[:7]  # Limit to 7
            
            albums_data = []
            for album in favorite_albums:
                album_data = {
                    'id': str(album.id),
                    'title': album.title,
                    'artist': album.artist,
                    'year': album.year,
                    'cover_url': album.cover_url,
                    'discogs_id': album.discogs_id
                }
                
                # Add user's review info if they reviewed this album
                user_review = Review.objects.filter(album=album, user=obj).first()
                if user_review:
                    album_data['user_review_id'] = user_review.id
                    album_data['user_rating'] = user_review.rating
                    album_data['user_review_content'] = user_review.content[:100] + '...' if len(user_review.content) > 100 else user_review.content
                
                albums_data.append(album_data)
            
            return albums_data
        except Exception as e:
            # Return empty list if there's any issue to prevent profile page from breaking
            return []
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj:
            return request.user.following.filter(id=obj.id).exists()
        return False

class UserFollowSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'avatar', 'bio', 'follower_count', 'following_count', 'review_count', 'is_following', 'is_staff']
    
    def get_display_name(self, obj):
        """Return the name if available, otherwise username"""
        return obj.name if obj.name else obj.username
    
    def get_follower_count(self, obj):
        # Use prefetched data if available, otherwise count
        if hasattr(obj, 'prefetched_follower_count'):
            return obj.prefetched_follower_count
        return obj.followers.count()
    
    def get_following_count(self, obj):
        # Use prefetched data if available, otherwise count
        if hasattr(obj, 'prefetched_following_count'):
            return obj.prefetched_following_count
        return obj.following.count()
    
    def get_review_count(self, obj):
        # Use prefetched data if available, otherwise count
        if hasattr(obj, 'prefetched_review_count'):
            return obj.prefetched_review_count
        from music.models import Review
        return Review.objects.filter(user=obj).count()
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj:
            # Use prefetched data if available
            if hasattr(obj, 'prefetched_is_following'):
                return obj.prefetched_is_following
            return request.user.following.filter(id=obj.id).exists()
        return False

class UserSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'bio', 'location', 'avatar', 'follower_count', 'following_count', 'review_count', 'is_staff']
        read_only_fields = ['id', 'email', 'is_staff']
    
    def get_follower_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()
    
    def get_review_count(self, obj):
        from music.models import Review
        return Review.objects.filter(user=obj).count()