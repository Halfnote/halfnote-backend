from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL' 