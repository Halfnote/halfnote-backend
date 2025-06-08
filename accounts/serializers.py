from rest_framework import serializers
from django.contrib.auth import get_user_model
from music.models import Review

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'bio', 'avatar_url',
            'favorite_genres', 'followers_count', 'following_count',
            'review_count'
        ]
        read_only_fields = ['id', 'email']
    
    def get_followers_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()
    
    def get_review_count(self, obj):
        return Review.objects.filter(user=obj).count()

class UserFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar_url']