from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class Genre(models.Model):
    # Simple predefined genres list
    PREDEFINED_GENRES = [
        'Pop', 'Hip-Hop', 'Rock', 'Latin', 'Country', 'Electronic', 
        'Jazz', 'Reggae', 'Gospel', 'Classical', 'Funk', 'Folk', 
        'Soundtrack', 'World'
    ]
    
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']



class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    year = models.IntegerField(null=True, blank=True)
    cover_url = models.URLField(max_length=500, null=True, blank=True)
    discogs_id = models.CharField(max_length=50, unique=True)
    
    # User-assigned genres (from predefined list)
    genres = models.ManyToManyField(Genre, blank=True, related_name='albums')
    
    # Discogs metadata (for reference)
    discogs_genres = models.JSONField(default=list, blank=True, help_text="Original genres from Discogs")
    discogs_styles = models.JSONField(default=list, blank=True, help_text="Original styles from Discogs")
    
    tracklist = models.JSONField(default=list, blank=True)
    credits = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.artist} - {self.title}"

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['artist']),
            models.Index(fields=['discogs_id']),
        ]

class Review(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='album_reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    content = models.TextField(blank=True)
    is_pinned = models.BooleanField(default=False, help_text="Pin this review to profile (max 4)")
    
    # User selects genres for this album when creating review
    user_genres = models.ManyToManyField(Genre, blank=True, related_name='reviews', 
                                        help_text="User-selected genres for this album")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('album', 'user')  # One review per album per user

    def __str__(self):
        return f"{self.user.username}'s review of {self.album.title}"


class ReviewLike(models.Model):
    """Track likes on reviews"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_likes')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user', 'review')  # One like per user per review
    
    def __str__(self):
        return f"{self.user.username} likes {self.review.user.username}'s review"


class Activity(models.Model):
    """Track user activities for the activity feed"""
    ACTIVITY_TYPES = [
        ('review_created', 'Review Created'),
        ('review_liked', 'Review Liked'),
        ('review_pinned', 'Review Pinned'),
        ('user_followed', 'User Followed'),
        ('comment_created', 'Comment Created'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    
    # Related objects (nullable for flexibility)
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                   related_name='targeted_activities', null=True, blank=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"


class Comment(models.Model):
    """Comments on reviews"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['review', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} commented on {self.review.user.username}'s review" 