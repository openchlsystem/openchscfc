# Generated by Django 5.1.4 on 2025-01-23 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AudioFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("unique_id", models.CharField(max_length=50, unique=True)),
                ("audio_data", models.BinaryField()),
            ],
        ),
        migrations.CreateModel(
            name="RawData",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("unique_id", models.CharField(max_length=50, unique=True)),
                ("date", models.DateTimeField()),
                ("talk_time", models.TimeField()),
                ("case_id", models.IntegerField()),
                ("narrative", models.TextField()),
                ("plan", models.TextField()),
                ("main_category", models.CharField(max_length=100)),
                ("sub_category", models.CharField(max_length=100)),
                ("gbv", models.BooleanField()),
            ],
        ),
    ]
