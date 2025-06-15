from rest_framework import serializers
from django.contrib.auth import get_user_model
from music.models import Review

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    pinned_reviews = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'name', 'display_name',
            'bio', 'location', 'avatar', 'favorite_genres', 'follower_count', 
            'following_count', 'review_count', 'pinned_reviews', 'is_following', 'is_staff'
        ]
        read_only_fields = ['id', 'email', 'display_name', 'is_staff']
    
    def get_display_name(self, obj):
        """Return the name if available, otherwise username"""
        return obj.name if obj.name else obj.username
    
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
            pinned_reviews = Review.objects.filter(user=obj, is_pinned=True).order_by('-created_at')[:4]
            return ReviewSerializer(pinned_reviews, many=True, context=self.context).data
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
    
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'bio', 'follower_count', 'following_count', 'review_count']
    
    def get_follower_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()
    
    def get_review_count(self, obj):
        from music.models import Review
        return Review.objects.filter(user=obj).count()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'bio', 'location', 'avatar']
        read_only_fields = ['id', 'email']