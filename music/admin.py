from django.contrib import admin
from .models import Album

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'year')
    list_filter = ('year',)
    search_fields = ('title', 'artist') 