from rest_framework import serializers
from .models import Album, Review

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'username', 'rating', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

class AlbumSerializer(serializers.ModelSerializer):
    review_count = serializers.IntegerField(read_only=True, required=False)
    average_rating = serializers.FloatField(read_only=True, required=False)
    
    class Meta:
        model = Album
        fields = [
            'id', 'title', 'artist', 'year', 'cover_url',
            'discogs_id', 'genres', 'styles', 'review_count',
            'average_rating', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class AlbumSearchResultSerializer(serializers.Serializer):
    discogs_id = serializers.CharField()
    title = serializers.CharField()
    artist = serializers.CharField()
    year = serializers.IntegerField(required=False, allow_null=True)
    cover_image = serializers.URLField(required=False, allow_null=True)
    genres = serializers.ListField(child=serializers.CharField(), required=False)
    styles = serializers.ListField(child=serializers.CharField(), required=False) 