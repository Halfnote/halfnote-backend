import time

from django.core.management.base import BaseCommand

from music.models import Album
from music.services import ExternalMusicService


class Command(BaseCommand):
    help = 'Fill empty album labels from Discogs'

    def handle(self, *args, **options):
        service = ExternalMusicService()
        albums = Album.objects.filter(label='')
        filled = 0
        for album in albums:
            details = service.get_album_details(album.discogs_id)
            if details and details['label']:
                album.label = details['label']
                album.save(update_fields=['label'])
                filled += 1
            time.sleep(2)
        self.stdout.write(f'Filled {filled} of {len(albums)} albums missing a label')
