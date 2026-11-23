from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from cloudinary_storage.storage import MediaCloudinaryStorage
from .storage import SimpleCloudinaryStorage
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
    banner = models.ImageField(
        upload_to='banners/',
        blank=True,
        null=True,
        help_text='Profile banner image',
        storage=SimpleCloudinaryStorage()
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
        help_text='Favorite albums (max 4)'
    )
    following = models.ManyToManyField(
        'self',
        related_name='followers',
        symmetrical=False,
        blank=True
    )
    onboarded_at = models.DateTimeField(null=True, blank=True)
    AVATAR_PRESETS = [(k, k.title()) for k in ['cat', 'bear', 'ghost', 'fox', 'dog', 'mushroom', 'vinyl', 'robot']]
    avatar_preset = models.CharField(max_length=20, null=True, blank=True, choices=AVATAR_PRESETS)

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        constraints = [
            models.UniqueConstraint(Lower('email'), condition=~Q(email=''), name='accounts_user_email_unique'),
        ]


class Identity(models.Model):
    """A Sign in with Apple / Google account linked to a Halfnote user."""
    PROVIDERS = [('apple', 'Apple'), ('google', 'Google')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='identities')
    provider = models.CharField(max_length=10, choices=PROVIDERS)
    subject = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    apple_refresh_token = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['provider', 'subject'], name='accounts_identity_provider_subject_unique'),
        ]
