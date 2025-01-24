from django.db import models


class Transcription(models.Model):
    audio_file = models.FileField(upload_to="uploads/")
    transcript = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
