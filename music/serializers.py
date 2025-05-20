from rest_framework import serializers
from .models import Album

class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = [
            'id', 'title', 'artist', 'release_date',
            'cover_image_url', 'discogs_id',
            'created_at', 'updated_at'
        ]

class AlbumSearchResultSerializer(serializers.Serializer):
    discogs_id = serializers.IntegerField()
    title = serializers.CharField()
    artist = serializers.CharField()
    year = serializers.IntegerField(required=False, allow_null=True)
    cover_image_url = serializers.URLField(required=False, allow_null=True) 