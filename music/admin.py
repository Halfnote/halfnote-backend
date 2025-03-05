from django.contrib import admin
from .models import Album, Single, Genre

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'release_date', 'average_rating', 'total_ratings')
    search_fields = ('title', 'artist')
    list_filter = ('genres',)

@admin.register(Single)
class SingleAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'release_date', 'average_rating', 'total_ratings')
    search_fields = ('title', 'artist')
    list_filter = ('genres',)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',) 