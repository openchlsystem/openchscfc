# Generated by Django 5.1.4 on 2025-01-08 09:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("feedback", "0003_notification"),
    ]

    operations = [
        migrations.AddField(
            model_name="complaint",
            name="session_id",
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="complaint",
            name="timestamp",
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime.datetime(
                    2025, 1, 8, 9, 39, 53, 339603, tzinfo=datetime.timezone.utc
                ),
            ),
            preserve_default=False,
        ),
    ]
