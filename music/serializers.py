from rest_framework import serializers
from .models import Album, Genre, Artist

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name']

class AlbumSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    artist = ArtistSerializer(read_only=True)
    artist_id = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(),
        source='artist',
        write_only=True,
        required=False
    )

    class Meta:
        model = Album
        fields = [
            'id', 'title', 'artist', 'artist_id', 'release_date',
            'cover_art_url', 'spotify_url', 'spotify_embed_url',
            'genres', 'average_rating', 'total_ratings',
            'created_at'
        ]

class AlbumSearchResultSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    artist = serializers.CharField()
    release_date = serializers.DateField(required=False, allow_null=True)
    cover_art_url = serializers.URLField(required=False, allow_null=True)
    thumb_url = serializers.URLField(required=False, allow_null=True)
    genres = serializers.ListField(child=serializers.CharField(), required=False)
    styles = serializers.ListField(child=serializers.CharField(), required=False)
    discogs_url = serializers.URLField(required=False, allow_null=True)
    master_id = serializers.CharField(required=False, allow_null=True)
    master_url = serializers.URLField(required=False, allow_null=True)
    country = serializers.CharField(required=False, allow_null=True) 