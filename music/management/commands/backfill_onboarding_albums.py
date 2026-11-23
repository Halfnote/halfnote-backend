import time

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from music.models import Album
from music.onboarding import ONBOARDING_DISCOGS_IDS
from music.views import import_album_from_discogs


class Command(BaseCommand):
    help = 'Import the onboarding album grid from Discogs; all or nothing, skips albums already stored'

    def handle(self, *args, **options):
        existing = set(Album.objects.filter(discogs_id__in=ONBOARDING_DISCOGS_IDS).values_list('discogs_id', flat=True))
        missing = [i for i in ONBOARDING_DISCOGS_IDS if i not in existing]
        self.stdout.write(f'{len(existing)} already stored, importing {len(missing)}')

        with transaction.atomic():
            for discogs_id in missing:
                album = import_album_from_discogs(discogs_id)
                if album is None:
                    raise CommandError(f'Discogs import failed for {discogs_id}; rolled back the whole batch')
                self.stdout.write(f'  {discogs_id}  {album.artist} – {album.title}')
                # One import makes several Discogs calls (album, release, artist); stay under 60/min.
                time.sleep(3)

        self.stdout.write(self.style.SUCCESS(f'Done: {len(ONBOARDING_DISCOGS_IDS)} onboarding albums in the database'))
