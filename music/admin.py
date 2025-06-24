from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count, Avg
from .models import Album, Review, Genre, Comment, Activity, ReviewLike, List, ListItem, ListLike

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'album_count', 'review_count', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'album_count', 'review_count')
    ordering = ('name',)
    
    def album_count(self, obj):
        return obj.albums.count()
    album_count.short_description = 'Albums'
    
    def review_count(self, obj):
        return obj.reviews.count()
    review_count.short_description = 'Reviews'

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('album_thumbnail', 'title', 'artist', 'year', 'genres_display', 'review_count', 'avg_rating', 'created_at')
    list_filter = ('year', 'genres', 'created_at')
    search_fields = ('title', 'artist', 'discogs_id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'discogs_id', 'album_cover', 'review_count', 'avg_rating', 'total_likes')
    filter_horizontal = ('genres',)
    date_hierarchy = 'created_at'
    
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
        ('Statistics', {
            'fields': ('review_count', 'avg_rating', 'total_likes'),
            'classes': ('collapse',),
            'description': 'Album statistics and metrics'
        }),
        ('System Info', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['export_album_data', 'refresh_cover_art']
    
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
        genres = obj.genres.all()[:3]
        if genres:
            return ", ".join([genre.name for genre in genres])
        return "No genres"
    genres_display.short_description = 'Genres'
    
    def review_count(self, obj):
        """Show number of reviews for this album"""
        return obj.reviews.count()
    review_count.short_description = 'Reviews'
    
    def avg_rating(self, obj):
        """Show average rating for this album"""
        avg = obj.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        if avg:
            return f"{avg:.1f}/10"
        return "No ratings"
    avg_rating.short_description = 'Avg Rating'
    
    def total_likes(self, obj):
        """Total likes across all reviews for this album"""
        return sum(review.likes.count() for review in obj.reviews.all())
    total_likes.short_description = 'Total Likes'
    
    def export_album_data(self, request, queryset):
        """Export selected albums data"""
        # This could be enhanced to actually export data
        self.message_user(request, f'Export functionality for {queryset.count()} albums would be implemented here.')
    export_album_data.short_description = "Export album data"
    
    def refresh_cover_art(self, request, queryset):
        """Refresh cover art for selected albums"""
        self.message_user(request, f'Cover art refresh for {queryset.count()} albums would be implemented here.')
    refresh_cover_art.short_description = "Refresh cover art"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'album_title', 'album_artist', 'rating', 'likes_count', 'comments_count', 'is_pinned', 'created_at')
    list_filter = ('rating', 'is_pinned', 'created_at', 'user_genres')
    search_fields = ('user__username', 'album__title', 'album__artist', 'content')
    readonly_fields = ('created_at', 'updated_at', 'likes_count', 'comments_count')
    raw_id_fields = ('user', 'album')
    filter_horizontal = ('user_genres',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Review Info', {
            'fields': ('user', 'album', 'rating', 'content')
        }),
        ('Settings', {
            'fields': ('is_pinned', 'user_genres'),
            'description': 'Review settings and genre tags'
        }),
        ('Statistics', {
            'fields': ('likes_count', 'comments_count'),
            'classes': ('collapse',),
            'description': 'Engagement metrics'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['pin_reviews', 'unpin_reviews', 'feature_reviews']
    
    def album_title(self, obj):
        return obj.album.title
    album_title.short_description = 'Album'
    
    def album_artist(self, obj):
        return obj.album.artist
    album_artist.short_description = 'Artist'
    
    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'
    
    def comments_count(self, obj):
        return obj.comments.count()
    comments_count.short_description = 'Comments'
    
    def pin_reviews(self, request, queryset):
        """Pin selected reviews"""
        updated = queryset.update(is_pinned=True)
        self.message_user(request, f'{updated} reviews were pinned.')
    pin_reviews.short_description = "Pin selected reviews"
    
    def unpin_reviews(self, request, queryset):
        """Unpin selected reviews"""
        updated = queryset.update(is_pinned=False)
        self.message_user(request, f'{updated} reviews were unpinned.')
    unpin_reviews.short_description = "Unpin selected reviews"
    
    def feature_reviews(self, request, queryset):
        """Feature selected reviews (placeholder for future functionality)"""
        self.message_user(request, f'Feature functionality for {queryset.count()} reviews would be implemented here.')
    feature_reviews.short_description = "Feature selected reviews"

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'review_album', 'review_user', 'content_preview', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'content', 'review__album__title', 'review__user__username')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user', 'review')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Comment Info', {
            'fields': ('user', 'review', 'content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['delete_selected_comments', 'moderate_comments']
    
    def review_album(self, obj):
        return obj.review.album.title
    review_album.short_description = 'Album'
    
    def review_user(self, obj):
        return obj.review.user.username
    review_user.short_description = 'Review By'
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def moderate_comments(self, request, queryset):
        """Moderate selected comments (placeholder for future functionality)"""
        self.message_user(request, f'Moderation functionality for {queryset.count()} comments would be implemented here.')
    moderate_comments.short_description = "Moderate selected comments"

@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'review_album', 'review_user', 'review_rating', 'created_at')
    list_filter = ('created_at', 'review__rating')
    search_fields = ('user__username', 'review__album__title', 'review__user__username')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user', 'review')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    def review_album(self, obj):
        return obj.review.album.title
    review_album.short_description = 'Album'
    
    def review_user(self, obj):
        return obj.review.user.username
    review_user.short_description = 'Review By'
    
    def review_rating(self, obj):
        return f"{obj.review.rating}/10"
    review_rating.short_description = 'Rating'

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'target_user', 'related_content', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'target_user__username')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user', 'target_user', 'review', 'comment')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Activity Info', {
            'fields': ('user', 'activity_type', 'target_user')
        }),
        ('Related Objects', {
            'fields': ('review', 'comment'),
            'description': 'Related review or comment (if applicable)'
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['cleanup_old_activities', 'export_activity_data']
    
    def related_content(self, obj):
        if obj.review:
            return f"Review: {obj.review.album.title}"
        elif obj.comment:
            return f"Comment: {obj.comment.content[:30]}..."
        return "No related content"
    related_content.short_description = 'Related Content'
    
    def cleanup_old_activities(self, request, queryset):
        """Clean up old activities (placeholder for future functionality)"""
        self.message_user(request, f'Cleanup functionality for {queryset.count()} activities would be implemented here.')
    cleanup_old_activities.short_description = "Clean up old activities"
    
    def export_activity_data(self, request, queryset):
        """Export activity data (placeholder for future functionality)"""
        self.message_user(request, f'Export functionality for {queryset.count()} activities would be implemented here.')
    export_activity_data.short_description = "Export activity data"

@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_public', 'created_at', 'updated_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description', 'user__username']

@admin.register(ListItem)
class ListItemAdmin(admin.ModelAdmin):
    list_display = ['list', 'album', 'order', 'added_at']
    list_filter = ['added_at']
    search_fields = ['list__name', 'album__title']

@admin.register(ListLike)
class ListLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'list', 'created_at']
    search_fields = ['user__username', 'list__name']

# Customize admin site headers
admin.site.site_header = "halfnote Administration"
admin.site.site_title = "halfnote Admin"
admin.site.index_title = "Welcome to halfnote Administration" 