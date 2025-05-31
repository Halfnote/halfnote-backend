from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    year = models.IntegerField(null=True, blank=True)
    cover_url = models.URLField(max_length=500, null=True, blank=True)
    discogs_id = models.CharField(max_length=50, unique=True)
    genres = models.JSONField(default=list, blank=True)
    styles = models.JSONField(default=list, blank=True)
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
    genres = models.JSONField(default=list, blank=True)  # Store list of genre strings
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('album', 'user')  # One review per album per user

    def __str__(self):
        return f"{self.user.username}'s review of {self.album.title}" 