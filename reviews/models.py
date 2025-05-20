from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from music.models import Album

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField(blank=True)
    genres = models.JSONField(default=list)  # Store list of genre strings
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'album']  # One review per album per user

    def __str__(self):
        return f"{self.user.username}'s review of {self.album.title}" 