from django.contrib import admin
from .models import Album

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'release_date', 'created_at')
    search_fields = ('title', 'artist')
    list_filter = ('release_date',) 