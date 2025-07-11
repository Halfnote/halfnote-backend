# Generated by Django 5.2 on 2025-06-08 21:46

import accounts.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_favorite_genres'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar_url',
            field=models.URLField(blank=True, null=True, validators=[accounts.validators.validate_avatar_url]),
        ),
        migrations.AlterField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, null=True, validators=[accounts.validators.validate_bio]),
        ),
        migrations.AlterField(
            model_name='user',
            name='favorite_genres',
            field=models.JSONField(blank=True, default=list, validators=[accounts.validators.validate_favorite_genres]),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=30, unique=True, validators=[accounts.validators.validate_username]),
        ),
    ]
