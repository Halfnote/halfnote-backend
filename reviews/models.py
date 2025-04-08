from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from music.models import Album, Single

User = get_user_model()

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True)
    single = models.ForeignKey(Single, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(album__isnull=False, single__isnull=True) |
                    models.Q(album__isnull=True, single__isnull=False)
                ),
                name='review_either_album_or_single'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['album', 'created_at']),
            models.Index(fields=['single', 'created_at']),
        ]

    def __str__(self):
        return f"Review by {self.user.username} for {self.album or self.single}" 