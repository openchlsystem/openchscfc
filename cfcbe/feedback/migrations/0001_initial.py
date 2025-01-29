# Generated by Django 5.1.4 on 2025-01-29 15:12

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Complaint",
            fields=[
                (
                    "complaint_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "session_id",
                    models.UUIDField(blank=True, default=uuid.uuid4, null=True),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "reporter_nickname",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "case_category",
                    models.CharField(
                        blank=True, default="Not Specified", max_length=255, null=True
                    ),
                ),
                ("complaint_text", models.TextField(blank=True, null=True)),
                ("complaint_audio", models.BinaryField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "message_id_ref",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Person",
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
                ("name", models.CharField(max_length=255)),
                ("age", models.PositiveIntegerField(blank=True, null=True)),
                ("gender", models.CharField(blank=True, max_length=50, null=True)),
                ("additional_info", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="CaseNote",
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
                ("note_text", models.TextField()),
                ("note_audio", models.BinaryField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.CharField(max_length=255)),
                (
                    "complaint",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="case_notes",
                        to="feedback.complaint",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ComplaintStatus",
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
                ("status", models.CharField(max_length=100)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("updated_by", models.CharField(max_length=255)),
                (
                    "complaint",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="feedback.complaint",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "notification_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("message", models.TextField()),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "complaint",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="feedback.complaint",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="complaint",
            name="perpetrator",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="perpetrators",
                to="feedback.person",
            ),
        ),
        migrations.AddField(
            model_name="complaint",
            name="victim",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="victims",
                to="feedback.person",
            ),
        ),
    ]
