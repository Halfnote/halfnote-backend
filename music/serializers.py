from rest_framework import serializers
from .models import Album, Review, Genre, ReviewLike, Activity, Comment

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'username', 'user_avatar', 'content', 'created_at']
        read_only_fields = ['id', 'username', 'user_avatar', 'created_at']
    
    def get_user_avatar(self, obj):
        if obj.user.avatar:
            return obj.user.avatar.url
        return None


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    user_is_staff = serializers.BooleanField(source='user.is_staff', read_only=True)
    user_genres = GenreSerializer(many=True, read_only=True)
    album_title = serializers.CharField(source='album.title', read_only=True)
    album_artist = serializers.CharField(source='album.artist', read_only=True)
    album_cover = serializers.CharField(source='album.cover_url', read_only=True)
    album_year = serializers.IntegerField(source='album.year', read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'username', 'user_avatar', 'user_is_staff', 'rating', 'content', 'user_genres', 'created_at', 
                  'album_title', 'album_artist', 'album_cover', 'album_year', 'is_pinned',
                  'likes_count', 'is_liked_by_user', 'comments_count']
        read_only_fields = ['id', 'created_at']
    
    def get_user_avatar(self, obj):
        if obj.user.avatar:
            return obj.user.avatar.url
        return None
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_comments_count(self, obj):
        return obj.comments.count()

class AlbumSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    
    class Meta:
        model = Album
        fields = [
            'id', 'title', 'artist', 'year', 'cover_url',
            'discogs_id', 'genres', 'discogs_genres', 'discogs_styles', 
            'tracklist', 'credits', 'created_at', 'updated_at'
        ]

class AlbumSearchResultSerializer(serializers.Serializer):
    title = serializers.CharField()
    artist = serializers.CharField(required=False)
    year = serializers.IntegerField(required=False)
    cover_image = serializers.URLField(required=False)
    discogs_id = serializers.CharField(source='id')
    genres = serializers.ListField(child=serializers.CharField(), required=False, source='genre')
    styles = serializers.ListField(child=serializers.CharField(), required=False, source='style')


class ActivitySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    target_user = serializers.SerializerMethodField()
    
    # Review details if activity is review-related
    review_details = serializers.SerializerMethodField()
    comment_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Activity
        fields = ['id', 'user', 'activity_type', 'target_user', 
                  'review_details', 'comment_details', 'created_at']
    
    def get_user(self, obj):
        return {
            'username': obj.user.username,
            'avatar': obj.user.avatar.url if obj.user.avatar else None,
            'is_staff': obj.user.is_staff
        }
    
    def get_target_user(self, obj):
        if obj.target_user:
            return {
                'username': obj.target_user.username,
                'avatar': obj.target_user.avatar.url if obj.target_user.avatar else None,
                'is_staff': obj.target_user.is_staff
            }
        return None
    
    def get_review_details(self, obj):
        if obj.review:
            return {
                'id': obj.review.id,
                'rating': obj.review.rating,
                'content': obj.review.content[:100] + '...' if len(obj.review.content) > 100 else obj.review.content,
                'album': {
                    'title': obj.review.album.title,
                    'artist': obj.review.album.artist,
                    'year': obj.review.album.year,
                    'cover_url': obj.review.album.cover_url,
                },
                'user': {
                    'username': obj.review.user.username,
                    'avatar': obj.review.user.avatar.url if obj.review.user.avatar else None,
                    'is_staff': obj.review.user.is_staff
                }
            }
        return None
    
    def get_comment_details(self, obj):
        if obj.comment:
            return {
                'id': obj.comment.id,
                'content': obj.comment.content,
                'created_at': obj.comment.created_at,
            }
        return None 