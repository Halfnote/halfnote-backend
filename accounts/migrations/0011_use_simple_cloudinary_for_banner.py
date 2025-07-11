# Generated by Django 5.2.3 on 2025-07-07 02:30

import accounts.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_add_banner_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='banner',
            field=models.ImageField(blank=True, help_text='Profile banner image', null=True, storage=accounts.storage.SimpleCloudinaryStorage(), upload_to='banners/'),
        ),
    ]
