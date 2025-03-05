from rest_framework import serializers
from .models import Review
from music.serializers import AlbumSerializer, SingleSerializer

class ReviewSerializer(serializers.ModelSerializer):
    album = AlbumSerializer(read_only=True)
    single = SingleSerializer(read_only=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'album', 'single', 'rating',
            'text', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        if not data.get('album') and not data.get('single'):
            raise serializers.ValidationError("Either album or single must be provided")
        if data.get('album') and data.get('single'):
            raise serializers.ValidationError("Cannot review both album and single")
        return data 