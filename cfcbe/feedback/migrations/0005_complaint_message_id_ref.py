# Generated by Django 5.1.4 on 2025-01-08 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("feedback", "0004_complaint_session_id_complaint_timestamp"),
    ]

    operations = [
        migrations.AddField(
            model_name="complaint",
            name="message_id_ref",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
