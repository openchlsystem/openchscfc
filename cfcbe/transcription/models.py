from django.db import models

class AudioFile(models.Model):
    unique_id = models.CharField(max_length=50, unique=True)
    audio_file = models.BinaryField()
    feature_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.file_name

class CaseRecord(models.Model):
    unique_id = models.OneToOneField('AudioFile', on_delete=models.CASCADE)
    date = models.DateTimeField()
    talk_time = models.TimeField()
    case_id = models.CharField(max_length=20)
    narrative = models.TextField()
    plan = models.TextField()
    main_category = models.CharField(max_length=100)
    sub_category = models.CharField(max_length=100)
    gbv = models.BooleanField()
    
    def __str__(self):
        return f"Case {self.case_id} - {self.main_category}"

class ModelVersion(models.Model):
    version = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.version

class ModelTranscription(models.Model):
    audio_id = models.ForeignKey(AudioFile, on_delete=models.CASCADE)
    model_version_id = models.ForeignKey(ModelVersion, on_delete=models.CASCADE)
    predicted_text = models.TextField()
    wer = models.FloatField()
    model_version = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transcription for {self.audio_id.file_name} - {self.model_version}"