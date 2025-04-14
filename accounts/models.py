from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from music.models import Album

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    avatar_url = models.URLField(blank=True, null=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    favorite_albums = models.ManyToManyField(Album, related_name='favorited_by', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
        
    @property
    def followers_count(self):
        return self.followers.count()
        
    @property
    def following_count(self):
        return self.following.count()
        
    @property
    def reviews_count(self):
        return self.user.review_set.count()


class List(models.Model):
    LIST_TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lists')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    albums = models.ManyToManyField(Album, through='ListItem', related_name='lists')
    list_type = models.CharField(max_length=10, choices=LIST_TYPE_CHOICES, default='public')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} by {self.user.username}"


class ListItem(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['list', 'album']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile automatically when a User is created"""
    if created:
        UserProfile.objects.create(user=instance) 