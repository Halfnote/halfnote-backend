from rest_framework import serializers
from .models import Album, Review, Genre, ReviewLike, Activity, Comment, List, ListItem, ListLike

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
    album_discogs_id = serializers.CharField(source='album.discogs_id', read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'username', 'user_avatar', 'user_is_staff', 'rating', 'content', 'user_genres', 'created_at', 
                  'album_title', 'album_artist', 'album_cover', 'album_year', 'album_discogs_id', 'is_pinned',
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
            request = self.context.get('request')
            feed_type = self.context.get('feed_type', 'friends')
            is_liked_by_user = False
            if request and request.user.is_authenticated:
                is_liked_by_user = obj.review.likes.filter(user=request.user).exists()
            
            review_data = {
                'id': obj.review.id,
                'rating': obj.review.rating,
                'content': obj.review.content[:100] + '...' if len(obj.review.content) > 100 else obj.review.content,
                'is_liked_by_user': is_liked_by_user,
                'user_genres': [{'id': g.id, 'name': g.name} for g in obj.review.user_genres.all()],
                'album': {
                    'title': obj.review.album.title,
                    'artist': obj.review.album.artist,
                    'year': obj.review.album.year,
                    'cover_url': obj.review.album.cover_url,
                    'discogs_id': obj.review.album.discogs_id,
                },
                'user': {
                    'username': obj.review.user.username,
                    'avatar': obj.review.user.avatar.url if obj.review.user.avatar else None,
                    'is_staff': obj.review.user.is_staff
                }
            }
            
            # Always include counts for all feed types (needed for proper UI rendering)
            review_data['likes_count'] = obj.review.likes.count()
            review_data['comments_count'] = obj.review.comments.count()
            
            return review_data
        return None
    
    def get_comment_details(self, obj):
        if obj.comment:
            return {
                'id': obj.comment.id,
                'content': obj.comment.content,
                'created_at': obj.comment.created_at,
            }
        return None


class ListItemSerializer(serializers.ModelSerializer):
    album = serializers.SerializerMethodField()
    album_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = ListItem
        fields = ['id', 'album', 'album_id', 'order', 'added_at']
        read_only_fields = ['id', 'added_at']
    
    def get_album(self, obj):
        album_data = AlbumSerializer(obj.album).data
        
        # Add user review information if available
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_review = Review.objects.filter(
                album=obj.album, 
                user=request.user
            ).first()
            if user_review:
                album_data['user_review_id'] = user_review.id
                album_data['user_rating'] = user_review.rating
        
        return album_data


class ListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    items = ListItemSerializer(many=True, read_only=True)
    album_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    
    class Meta:
        model = List
        fields = ['id', 'name', 'description', 'is_public', 'created_at', 'updated_at',
                  'user', 'items', 'album_count', 'likes_count', 'is_liked_by_user']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user(self, obj):
        return {
            'username': obj.user.username,
            'avatar': obj.user.avatar.url if obj.user.avatar else None,
            'is_staff': obj.user.is_staff
        }
    
    def get_album_count(self, obj):
        return obj.items.count()
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class ListSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for list previews"""
    user = serializers.SerializerMethodField()
    album_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    first_albums = serializers.SerializerMethodField()
    
    class Meta:
        model = List
        fields = ['id', 'name', 'description', 'created_at', 'updated_at',
                  'user', 'album_count', 'likes_count', 'first_albums']
    
    def get_user(self, obj):
        return {
            'username': obj.user.username,
            'avatar': obj.user.avatar.url if obj.user.avatar else None,
            'is_staff': obj.user.is_staff
        }
    
    def get_album_count(self, obj):
        return obj.items.count()
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_first_albums(self, obj):
        # Return first 4 album covers for preview
        first_items = obj.items.select_related('album')[:4]
        return [{
            'id': item.album.id,
            'title': item.album.title,
            'artist': item.album.artist,
            'cover_url': item.album.cover_url
        } for item in first_items] 