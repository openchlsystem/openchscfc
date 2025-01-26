# Generated by Django 5.1.4 on 2025-01-25 11:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai", "0003_alter_rawdata_unique_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rawdata",
            name="unique_id",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="ai.audiofile"
            ),
        ),
    ]
