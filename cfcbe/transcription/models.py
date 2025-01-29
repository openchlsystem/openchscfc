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




class CaseRecord(models.Model):
    unique_id = models.CharField(max_length=20, unique=True)
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
