from django.db import models

class AudioFile(models.Model):
    unique_id = models.CharField(max_length=50, unique=True)
    audio_file = models.FileField(upload_to="")
    feature_text = models.TextField(blank=True, null=True)
    file_size = models.PositiveIntegerField(null=True)
    duration = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.unique_id
    
# Case Record Model
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
    audio_id = models.ForeignKey(AudioFile, on_delete=models.DO_NOTHING)
    model_version_id = models.ForeignKey(ModelVersion, on_delete=models.DO_NOTHING)
    predicted_text = models.TextField()
    wer = models.FloatField()
    status = models.CharField(max_length=50, choices=[('in-progress', 'In Progress'), ('completed', 'Completed')], default='in-progress')
    started_at = models.DateTimeField(null=True, blank=True)  # Timestamp when transcription starts
    finished_at = models.DateTimeField(null=True, blank=True)  # Timestamp when transcription is finished
    assigned_to = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL)  # Operator assigned to transcription
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transcription for {self.audio_id.file_name} - {self.model_version_id.version}"