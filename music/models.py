from django.db import models
import uuid

class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    year = models.IntegerField(null=True, blank=True)
    cover_url = models.URLField(blank=True)
    discogs_id = models.IntegerField(unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.artist} - {self.title} ({self.year})"

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['artist']),
            models.Index(fields=['discogs_id']),
        ] 