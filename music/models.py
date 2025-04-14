from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

# List of allowed genres in the system
ALLOWED_GENRES = [
    'Pop', 'Rock', 'Country', 'Jazz', 'Gospel', 'Funk',
    'Soundtrack', 'Hip-hop', 'Latin', 'Electronic',
    'Reggae', 'Classical', 'Folk', 'World'
]

def validate_genre_name(value):
    """Validates that the genre name is in the list of allowed genres"""
    if value not in ALLOWED_GENRES:
        raise ValidationError(
            f"'{value}' is not a valid genre. Allowed genres are: {', '.join(ALLOWED_GENRES)}"
        )

class Genre(models.Model):
    name = models.CharField(
        max_length=100, 
        unique=True,
        validators=[validate_genre_name]
    )
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Ensures that the name is properly capitalized"""
        if self.name and self.name not in ALLOWED_GENRES:
            # Try to find a case-insensitive match
            for allowed_genre in ALLOWED_GENRES:
                if self.name.lower() == allowed_genre.lower():
                    self.name = allowed_genre
                    return
            # If no match, raise validation error
            raise ValidationError(f"'{self.name}' is not an allowed genre.")

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
    discogs_id = models.CharField(max_length=255, unique=True)
    discogs_url = models.URLField(null=True, blank=True)
    discogs_master_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['title', 'artist']),
        ]

    def __str__(self):
        return f"{self.title} by {self.artist}" 