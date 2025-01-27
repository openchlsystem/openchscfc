# Generated by Django 5.1.4 on 2025-01-22 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("whatsapp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="whatsappmessage",
            name="caption",
            field=models.TextField(
                blank=True,
                help_text="Caption for media messages, if applicable",
                null=True,
            ),
        ),
    ]
