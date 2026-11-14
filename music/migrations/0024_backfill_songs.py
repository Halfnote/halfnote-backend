from django.db import migrations

from music.models import fill_songs


def backfill(apps, schema_editor):
    Song = apps.get_model('music', 'Song')
    for album in apps.get_model('music', 'Album').objects.iterator():
        fill_songs(Song, album)


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0023_song'),
    ]

    operations = [
        migrations.RunPython(backfill, migrations.RunPython.noop),
    ]
