from rest_framework import serializers
from .models import Review
from music.serializers import AlbumSerializer

class ReviewSerializer(serializers.ModelSerializer):
    album = AlbumSerializer(read_only=True)
    user = serializers.StringRelatedField()
    album_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'album', 'album_id', 'rating',
            'text', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        # Album validation now happens in the ViewSet
        return data 