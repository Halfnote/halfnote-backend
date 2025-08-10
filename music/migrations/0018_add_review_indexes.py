# Generated manually to add performance-friendly indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0017_add_favorite_albums'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['user', '-created_at'], name='music_review_user_created_idx'),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['album', '-created_at'], name='music_review_album_created_idx'),
        ),
        migrations.AddIndex(
            model_name='reviewlike',
            index=models.Index(fields=['review', '-created_at'], name='music_reviewlike_review_created_idx'),
        ),
    ]

