from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Artist(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

class Album(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    release_date = models.DateField()
    cover_art_url = models.URLField(null=True, blank=True)
    spotify_url = models.URLField(null=True, blank=True)
    spotify_embed_url = models.URLField(null=True, blank=True)
    genres = models.ManyToManyField(Genre)
    average_rating = models.FloatField(
        default=0,
        validators=[MinValueValidator(1.0), MaxValueValidator(10.0)]
    )
    total_ratings = models.IntegerField(default=0)
    musicbrainz_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['title', 'artist']),
        ]

    def __str__(self):
        return f"{self.title} by {self.artist}"

class Single(models.Model):
    id = models.UUIDField(primary_key=True)
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    release_date = models.DateField()
    cover_art_url = models.URLField(null=True, blank=True)
    spotify_url = models.URLField(null=True, blank=True)
    spotify_embed_url = models.URLField(null=True, blank=True)
    genres = models.ManyToManyField(Genre)
    average_rating = models.FloatField(
        default=0,
        validators=[MinValueValidator(1.0), MaxValueValidator(10.0)]
    )
    total_ratings = models.IntegerField(default=0)
    musicbrainz_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['title', 'artist']),
        ]

    def __str__(self):
        return f"{self.title} by {self.artist}" 