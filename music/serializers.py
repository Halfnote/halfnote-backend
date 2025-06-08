from rest_framework import serializers
from .models import Album, Review, Genre

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_genres = GenreSerializer(many=True, read_only=True)
    album_title = serializers.CharField(source='album.title', read_only=True)
    album_artist = serializers.CharField(source='album.artist', read_only=True)
    album_cover = serializers.CharField(source='album.cover_url', read_only=True)
    album_year = serializers.IntegerField(source='album.year', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'username', 'rating', 'content', 'user_genres', 'created_at', 
                  'album_title', 'album_artist', 'album_cover', 'album_year']
        read_only_fields = ['id', 'created_at']

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