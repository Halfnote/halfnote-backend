from rest_framework import serializers
from .models import Album, Review

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'username', 'rating', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = [
            'id', 'title', 'artist', 'year', 'cover_url',
            'discogs_id', 'genres', 'styles', 'tracklist', 'credits',
            'created_at', 'updated_at'
        ]

class AlbumSearchResultSerializer(serializers.Serializer):
    title = serializers.CharField()
    artist = serializers.CharField()
    year = serializers.IntegerField(required=False)
    cover_image = serializers.URLField(required=False)
    discogs_id = serializers.CharField()
    genres = serializers.ListField(child=serializers.CharField(), required=False)
    styles = serializers.ListField(child=serializers.CharField(), required=False) 