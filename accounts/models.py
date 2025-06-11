from django.contrib.auth.models import AbstractUser
from django.db import models
from .validators import (
    validate_username, validate_bio,
    validate_favorite_genres
)

class User(AbstractUser):
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[validate_username]
    )
    bio = models.TextField(
        blank=True,
        null=True,
        validators=[validate_bio]
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text='Profile picture'
    )
    favorite_genres = models.JSONField(
        default=list,
        blank=True,
        validators=[validate_favorite_genres]
    )
    following = models.ManyToManyField(
        'self',
        related_name='followers',
        symmetrical=False,
        blank=True
    )

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL' 