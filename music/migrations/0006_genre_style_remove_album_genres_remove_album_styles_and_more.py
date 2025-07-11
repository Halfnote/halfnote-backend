# Generated by Django 5.2.2 on 2025-06-08 22:55

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0005_remove_album_music_album_master__f1574f_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.RemoveField(
            model_name='album',
            name='genres',
        ),
        migrations.RemoveField(
            model_name='album',
            name='styles',
        ),
        migrations.AddField(
            model_name='album',
            name='genres',
            field=models.ManyToManyField(blank=True, related_name='albums', to='music.genre'),
        ),
        migrations.AddField(
            model_name='album',
            name='styles',
            field=models.ManyToManyField(blank=True, related_name='albums', to='music.style'),
        ),
    ]
