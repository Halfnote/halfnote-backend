from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Album, Review, Genre

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'album_count', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'album_count')
    
    def album_count(self, obj):
        return obj.albums.count()
    album_count.short_description = 'Albums'



@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('album_thumbnail', 'title', 'artist', 'year', 'genres_display', 'review_count', 'created_at')
    list_filter = ('year', 'genres', 'created_at')
    search_fields = ('title', 'artist', 'discogs_id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'discogs_id', 'album_cover', 'review_count')
    filter_horizontal = ('genres',)  # Nice interface for many-to-many
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'artist', 'year', 'discogs_id')
        }),
        ('Cover Art', {
            'fields': ('cover_url', 'album_cover'),
            'description': 'Album artwork and thumbnail'
        }),
        ('User Genres', {
            'fields': ('genres',),
            'description': 'User-assigned genres (from reviews)'
        }),
        ('Discogs Data', {
            'fields': ('discogs_genres', 'discogs_styles'),
            'description': 'Original genre/style data from Discogs',
            'classes': ('collapse',)
        }),
        ('Additional Data', {
            'fields': ('tracklist', 'credits'),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('id', 'created_at', 'updated_at', 'review_count'),
            'classes': ('collapse',)
        }),
    )
    
    def album_thumbnail(self, obj):
        """Display small thumbnail in list view"""
        if obj.cover_url:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.cover_url
            )
        return "No image"
    album_thumbnail.short_description = 'Cover'
    
    def album_cover(self, obj):
        """Display larger cover in detail view"""
        if obj.cover_url:
            return format_html(
                '<img src="{}" width="200" height="200" style="object-fit: cover; border-radius: 8px;" />',
                obj.cover_url
            )
        return "No cover available"
    album_cover.short_description = 'Album Cover'
    
    def genres_display(self, obj):
        """Display genres as a readable string"""
        genres = obj.genres.all()[:3]  # Show first 3 genres
        if genres:
            return ", ".join([genre.name for genre in genres])
        return "No genres"
    genres_display.short_description = 'Genres'
    
    def review_count(self, obj):
        """Show number of reviews for this album"""
        return obj.reviews.count()
    review_count.short_description = 'Reviews'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'album', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'album__title', 'album__artist', 'content')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user', 'album')  # Makes it easier to select users/albums 