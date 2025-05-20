from rest_framework import serializers
from .models import Review, GENRES
from music.serializers import AlbumSerializer

class ReviewSerializer(serializers.ModelSerializer):
    album = AlbumSerializer(read_only=True)
    user = serializers.StringRelatedField()
    album_id = serializers.UUIDField(write_only=True)
    genres = serializers.MultipleChoiceField(choices=[(g, g) for g in GENRES], required=False)

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'album', 'album_id', 'rating',
            'text', 'genres', 'created_at', 'updated_at'
        ]

    def validate_genres(self, value):
        """Validate that all genres are from the allowed list"""
        if not all(genre in GENRES for genre in value):
            raise serializers.ValidationError("Invalid genre specified")
        return value

    def validate(self, data):
        # Album validation now happens in the ViewSet
        return data 