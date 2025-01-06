from django.db import models
import uuid

# Enum choices for categorizing complaints
class ComplaintCategory(models.TextChoices):
    ABUSE = 'ABUSE', 'Abuse'
    HARASSMENT = 'HARASSMENT', 'Harassment'
    FRAUD = 'FRAUD', 'Fraud'
    NEGLECT = 'NEGLECT', 'Neglect'
    OTHER = 'OTHER', 'Other'

# Model to represent a Complaint
class Complaint(models.Model):
    complaint_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    reporter_nickname = models.CharField(max_length=100, null=True, blank=True)  # Anonymous reporter
    case_category = models.CharField(max_length=50, choices=ComplaintCategory.choices, default=ComplaintCategory.OTHER)
    complaint_text = models.TextField(blank=True, null=True)  # The text version of the complaint
    complaint_audio = models.BinaryField(blank=True, null=True)  # The audio version of the complaint
    created_at = models.DateTimeField(auto_now_add=True)

    # Victim and perpetrator information
    victim = models.ForeignKey('Person', related_name='victims', on_delete=models.CASCADE, null=True, blank=True)
    perpetrator = models.ForeignKey('Person', related_name='perpetrators', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Complaint {self.complaint_id} by {self.reporter_nickname}"

# Model for storing information about Victims or Perpetrators
class Person(models.Model):
    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    additional_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# Model for Case Notes (to document updates or notes related to the case)
class CaseNote(models.Model):
    complaint = models.ForeignKey(Complaint, related_name='case_notes', on_delete=models.CASCADE)
    note_text = models.TextField()
    note_audio = models.BinaryField(blank=True, null=True)  # Optional audio note
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255)  # This could be an agent's name or system

    def __str__(self):
        return f"CaseNote for {self.complaint.complaint_id} on {self.created_at}"

# Model for storing the status of a complaint (e.g., Under Investigation, Resolved, etc.)
class ComplaintStatus(models.Model):
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255)  # This could be an agent's name or system

    def __str__(self):
        return f"Status for Complaint {self.complaint.complaint_id}: {self.status}"
