# Generated by Django 5.2.2 on 2025-06-11 05:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0012_add_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='comment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='music.comment'),
        ),
    ]
