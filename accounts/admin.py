from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Enhanced fieldsets with better organization
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Profile', {
            'fields': ('bio', 'avatar', 'avatar_preview', 'favorite_genres'),
            'description': 'User profile information and preferences'
        }),
        ('Social', {
            'fields': ('following', 'followers_count', 'following_count'),
            'description': 'Social connections and follower information'
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('review_count', 'total_likes_received'),
            'classes': ('collapse',),
            'description': 'User activity statistics'
        }),
    )
    
    # Enhanced list display with more useful information
    list_display = (
        'username', 'email', 'full_name', 'avatar_thumbnail', 
        'review_count', 'followers_count', 'following_count',
        'is_staff', 'is_active', 'date_joined'
    )
    
    # Enhanced filters for better navigation
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'date_joined',
        'groups', 'favorite_genres'
    )
    
    # Enhanced search functionality
    search_fields = ('username', 'email', 'first_name', 'last_name', 'bio')
    
    # Better interface for many-to-many fields
    filter_horizontal = ('following', 'groups', 'user_permissions')
    
    # Read-only fields for calculated values
    readonly_fields = (
        'avatar_preview', 'followers_count', 'following_count', 
        'review_count', 'total_likes_received', 'last_login', 'date_joined'
    )
    
    # Ordering
    ordering = ('-date_joined',)
    
    # Custom methods for enhanced display
    def avatar_thumbnail(self, obj):
        """Display user avatar thumbnail in list view"""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 50%;" />',
                obj.avatar.url
            )
        return "No avatar"
    avatar_thumbnail.short_description = 'Avatar'
    
    def avatar_preview(self, obj):
        """Display larger avatar in detail view"""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 50%;" />',
                obj.avatar.url
            )
        return "No avatar uploaded"
    avatar_preview.short_description = 'Avatar Preview'
    
    def full_name(self, obj):
        """Display full name or username if no name provided"""
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return obj.username
    full_name.short_description = 'Name'
    
    def followers_count(self, obj):
        """Count of followers"""
        return obj.followers.count()
    followers_count.short_description = 'Followers'
    
    def following_count(self, obj):
        """Count of users being followed"""
        return obj.following.count()
    following_count.short_description = 'Following'
    
    def review_count(self, obj):
        """Count of reviews written"""
        return obj.album_reviews.count()
    review_count.short_description = 'Reviews'
    
    def total_likes_received(self, obj):
        """Total likes received on all reviews"""
        return sum(review.likes.count() for review in obj.album_reviews.all())
    total_likes_received.short_description = 'Total Likes'
    
    # Custom actions
    actions = ['make_staff', 'remove_staff', 'activate_users', 'deactivate_users']
    
    def make_staff(self, request, queryset):
        """Make selected users staff members"""
        updated = queryset.update(is_staff=True)
        self.message_user(request, f'{updated} users were successfully made staff members.')
    make_staff.short_description = "Make selected users staff"
    
    def remove_staff(self, request, queryset):
        """Remove staff status from selected users"""
        updated = queryset.update(is_staff=False)
        self.message_user(request, f'{updated} users had staff status removed.')
    remove_staff.short_description = "Remove staff status from selected users"
    
    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users were successfully activated.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users were successfully deactivated.')
    deactivate_users.short_description = "Deactivate selected users" 