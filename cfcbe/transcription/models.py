from django.db import models

class AudioFile(models.Model):
    unique_id = models.CharField(max_length=50, unique=True)
    audio_file = models.BinaryField()
    feature_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.unique_id


from django.db import models
# add uuid
import uuid

# Audio File Model (to manage audio files and metadata)
# class AudioFile(models.Model):
#     case_record = models.OneToOneField('CaseRecord', related_name='audio_file', on_delete=models.CASCADE)
#     file = models.FileField(upload_to='audio/')  # Path to the uploaded audio file
#     file_size = models.PositiveIntegerField()  # Size of the audio file in bytes
#     duration = models.FloatField()  # Duration of the audio file in seconds (you could extract this on upload)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"Audio for {self.case_record.case_id}"

# Transcription Model
class Transcription_done(models.Model):
    case_record = models.ForeignKey('CaseRecord', related_name='transcriptions', on_delete=models.CASCADE)
    audio_file = models.ForeignKey('AudioFile', related_name='transcriptions', on_delete=models.SET_NULL, null=True, blank=True)
    true_transcription = models.TextField(blank=True, null=True)
    model_transcription = models.TextField(blank=True, null=True)
    wer = models.FloatField(blank=True, null=True)  # Word Error Rate
    status = models.CharField(max_length=50, choices=[('in-progress', 'In Progress'), ('completed', 'Completed')], default='in-progress')
    started_at = models.DateTimeField(null=True, blank=True)  # Timestamp when transcription starts
    finished_at = models.DateTimeField(null=True, blank=True)  # Timestamp when transcription is finished
    assigned_to = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.SET_NULL)  # Operator assigned to transcription
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transcription {self.id} - WER: {self.wer} - Status: {self.status}"

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
    audio_id = models.ForeignKey(AudioFile, on_delete=models.CASCADE)
    model_version_id = models.ForeignKey(ModelVersion, on_delete=models.CASCADE)
    predicted_text = models.TextField()
    wer = models.FloatField()
    model_version = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transcription for {self.audio_id.file_name} - {self.model_version}"