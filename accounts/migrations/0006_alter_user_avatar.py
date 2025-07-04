# Generated by Django 5.2.2 on 2025-06-12 22:15

import cloudinary_storage.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_remove_user_avatar_url_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, help_text='Profile picture', null=True, storage=cloudinary_storage.storage.MediaCloudinaryStorage(), upload_to='avatars/'),
        ),
    ]
