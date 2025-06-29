# Generated by Django 5.2.2 on 2025-06-11 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_user_avatar_url_alter_user_bio_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='avatar_url',
        ),
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, help_text='Profile picture', null=True, upload_to='avatars/'),
        ),
    ]
