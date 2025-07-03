from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary_storage.storage import MediaCloudinaryStorage
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
    name = models.CharField(
        max_length=100, 
        blank=True,
        help_text='Your full name'
    )
    bio = models.TextField(
        blank=True,
        null=True,
        validators=[validate_bio]
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Your location (city, country, etc.)'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text='Profile picture',
        storage=MediaCloudinaryStorage()
    )
    favorite_genres = models.JSONField(
        default=list,
        blank=True,
        validators=[validate_favorite_genres]
    )
    favorite_albums = models.ManyToManyField(
        'music.Album',
        related_name='favorited_by',
        blank=True,
        help_text='Favorite albums (max 5)'
    )
    following = models.ManyToManyField(
        'self',
        related_name='followers',
        symmetrical=False,
        blank=True
    )
    is_verified = models.BooleanField(
        default=False,
        help_text='Verified checkmark for trusted users'
    )

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL' 