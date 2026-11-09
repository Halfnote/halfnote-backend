from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

HEADLINE_MAX = 150
BODY_MAX = 5000

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


class Artist(models.Model):
    """Artist information from Discogs"""

    # Primary identifiers
    discogs_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=255, help_text="Main artist name")
    real_name = models.CharField(max_length=255, blank=True, help_text="Real name if different from stage name")

    # Biography and description
    profile = models.TextField(blank=True, help_text="Artist biography/description from Discogs")

    # Images
    primary_image_url = models.URLField(max_length=500, blank=True, help_text="Primary artist photo")
    images = models.JSONField(default=list, blank=True, help_text="All images from Discogs")

    # Additional info
    name_variations = models.JSONField(default=list, blank=True, help_text="Alternate spellings/names")
    urls = models.JSONField(default=list, blank=True, help_text="Artist websites and social links")
    members = models.JSONField(default=list, blank=True, help_text="Band members (for groups)")

    # Discogs metadata
    discogs_url = models.URLField(max_length=500, blank=True, help_text="Link to Discogs page")
    data_quality = models.CharField(max_length=50, blank=True, help_text="Discogs data quality rating")

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['discogs_id']),
        ]



class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=255)

    # Artist relationship (new)
    artist_rel = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, blank=True, related_name='albums', help_text="Link to Artist model")

    # Legacy artist field (keeping for backwards compatibility during migration)
    artist = models.CharField(max_length=255)

    year = models.IntegerField(null=True, blank=True)
    cover_url = models.URLField(max_length=500, null=True, blank=True)
    artist_photo_url = models.URLField(max_length=500, null=True, blank=True, help_text="URL to artist photo from external API (deprecated, use artist_rel)")
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
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    # The design's two writing areas: up to three serif lines, then an optional body.
    headline = models.CharField(max_length=HEADLINE_MAX, blank=True, default='')
    body = models.TextField(max_length=BODY_MAX, blank=True, default='')
    is_pinned = models.BooleanField(default=False, help_text="Pin this review to profile (max 2)")
    
    # User selects genres for this album when creating review
    user_genres = models.ManyToManyField(Genre, blank=True, related_name='reviews', 
                                        help_text="User-selected genres for this album")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Users may review the same album more than once.
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__isnull=True) | models.Q(rating__gte=1, rating__lte=10),
                name='review_rating_1_to_10'),
            models.CheckConstraint(
                condition=models.Q(rating__isnull=False) | ~models.Q(headline=''),
                name='review_has_rating_or_headline'),
            models.CheckConstraint(
                condition=models.Q(body='') | ~models.Q(headline=''),
                name='review_body_needs_headline'),
        ]

    @property
    def content(self):
        """Headline and body joined, for readers that want one string."""
        return f"{self.headline}\n\n{self.body}" if self.body else self.headline

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
        verbose_name_plural = "Activities"
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['target_user', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
            models.Index(fields=['user', 'activity_type', '-created_at']),  # Compound index for filtered queries
            models.Index(fields=['target_user', 'activity_type', '-created_at']),  # For incoming feeds
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


class List(models.Model):
    """User-created lists of albums"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lists')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, max_length=500)
    albums = models.ManyToManyField(Album, through='ListItem', related_name='lists')
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['is_public', '-updated_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s list: {self.name}"


class ListItem(models.Model):
    """Through model for List-Album relationship with ordering"""
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='items')
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('list', 'album')
        ordering = ['order', 'added_at']
        indexes = [
            models.Index(fields=['list', 'order']),
        ]
    
    def __str__(self):
        return f"{self.album.title} in {self.list.name}"


class ListLike(models.Model):
    """Track likes on lists"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='list_likes')
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user', 'list')
    
    def __str__(self):
        return f"{self.user.username} likes {self.list.name}" 