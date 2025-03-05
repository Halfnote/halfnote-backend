from rest_framework import serializers
from .models import Album, Single, Genre

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

class AlbumSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = [
            'id', 'title', 'artist', 'release_date',
            'cover_art_url', 'spotify_url', 'spotify_embed_url',
            'genres', 'average_rating', 'total_ratings',
            'created_at'
        ]

class SingleSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Single
        fields = [
            'id', 'title', 'artist', 'release_date',
            'cover_art_url', 'spotify_url', 'spotify_embed_url',
            'genres', 'average_rating', 'total_ratings',
            'created_at'
        ] 