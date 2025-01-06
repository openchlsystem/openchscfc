from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User model


# Categories
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# Complaints
class Complaint(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    text = models.TextField(blank=True)
    audio_url = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=50)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='low')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Audio Files
class AudioFile(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    file_path = models.TextField()
    transcription = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

# Translations
class Translation(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    source_language = models.CharField(max_length=50)
    target_language = models.CharField(max_length=50)
    translated_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# Feedback
class Feedback(models.Model):
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # Rating out of 5
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# Metrics
class Metric(models.Model):
    METRIC_TYPE_CHOICES = [
        ('response_time', 'Response Time'),
        ('resolution_time', 'Resolution Time'),
    ]
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPE_CHOICES)
    value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

# Triage Logs
class TriageLog(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    severity = models.CharField(max_length=20, choices=Complaint.SEVERITY_CHOICES)
    keywords_detected = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# Caseworker Actions
class CaseworkerAction(models.Model):

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

# Notifications
class Notification(models.Model):
    message = models.TextField()
    read_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
