from django.db import models

class AudioFile(models.Model):
    unique_id = models.CharField(max_length=255, unique=True)
    audio_file = models.FileField(upload_to='audio_files/')

    def __str__(self):
        return self.unique_id

class ModelVersion(models.Model):
    version = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.version

class ModelTranscription(models.Model):
    audio_id = models.ForeignKey(AudioFile, on_delete=models.CASCADE)
    model_version_id = models.ForeignKey(ModelVersion, on_delete=models.CASCADE)
    predicted_text = models.TextField()
    wer = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Transcription for {self.audio_id.unique_id} by {self.model_version_id.version}"

class AudioFileChunkQuerySet(models.QuerySet):
    def total_chunks(self):
        return self.count()

    def total_transcribed_chunks(self):
        return self.filter(true_transcription__isnull=False).exclude(true_transcription='').count()

    def total_untranscribed_chunks(self):
        return self.filter(true_transcription__isnull=True).count()

    def total_rejected_chunks(self):
        return self.filter(is_rejected=True).count()

    def with_transcriptions(self):
        return self.filter(true_transcription__isnull=False).exclude(true_transcription='')

    def without_transcriptions(self):
        return self.filter(true_transcription__isnull=True)

    def rejected_chunks(self):
        return self.filter(is_rejected=True)

class AudioFileChunk(models.Model):
    parent_audio = models.ForeignKey(AudioFile, on_delete=models.CASCADE, related_name='chunks')
    true_transcription = models.TextField(null=True, blank=True)
    is_rejected = models.BooleanField(default=False)

    objects = AudioFileChunkQuerySet.as_manager()

    def __str__(self):
        return f"Chunk for {self.parent_audio.unique_id}"

class CaseRecord(models.Model):
    unique_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.unique_id
