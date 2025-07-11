# Generated by Django 5.2.3 on 2025-07-07 02:09

import cloudinary_storage.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_add_verified_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='banner',
            field=models.ImageField(blank=True, help_text='Profile banner image', null=True, storage=cloudinary_storage.storage.MediaCloudinaryStorage(), upload_to='banners/'),
        ),
    ]
