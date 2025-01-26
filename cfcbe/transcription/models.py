from django.db import models

class Transcription(models.Model):
    audio_file = models.FileField(upload_to="uploads/")
    true_transcription = models.TextField(blank=True, null=True)
    model_transcription = models.TextField(blank=True, null=True)
    wer = models.FloatField(blank=True, null=True)  # Word Error Rate
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transcription {self.id} - WER: {self.wer}"
