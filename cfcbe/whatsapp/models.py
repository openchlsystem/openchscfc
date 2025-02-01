from django.db import models

class WhatsAppMessage(models.Model):
    MESSAGE_TYPES = [
        ("text", "Text"),
        ("image", "Image"),
        ("video", "Video"),
        ("audio", "Audio"),
        ("document", "Document"),
    ]

    sender = models.CharField(max_length=255, help_text="WhatsApp number of the sender")
    recipient = models.CharField(max_length=255, help_text="WhatsApp number of the recipient")
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPES, default="text", help_text="Type of the message")
    content = models.TextField(blank=True, null=True, help_text="Text content of the message, if applicable")
    caption = models.TextField(blank=True, null=True, help_text="Caption for media messages, if applicable")  # New field
    media_url = models.URLField(blank=True, null=True, help_text="URL of the media file, if applicable")
    media_base64 = models.TextField(blank=True, null=True, help_text="Base64-encoded representation of the media")
    media_mime_type = models.CharField(max_length=100, blank=True, null=True, help_text="MIME type of the media, e.g., image/jpeg")
    timestamp = models.DateTimeField(help_text="Timestamp of when the message was received")
    is_forwarded_to_main_system = models.BooleanField(default=False, help_text="Flag to track if the message was forwarded to the main system")

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient} ({self.message_type})"



from django.db import models

# from accounts.models import MyUser


class IncomingMessage(models.Model):
    contact_wa_id = models.CharField(max_length=100)
    message_text = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.contact_wa_id} at {self.received_at.strftime('%Y-%m-%d %H:%M:%S')}"

class OutgoingMessage(models.Model):
    contact_wa_id = models.CharField(max_length=100)
    message_text = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    was_successful = models.BooleanField(default=False)

    def __str__(self):
        return f"To {self.contact_wa_id} at {self.sent_at.strftime('%Y-%m-%d %H:%M:%S')}"

class WhatsAppMessage(models.Model):
    messaging_product = models.CharField(max_length=50)
    display_phone_number = models.CharField(max_length=15)
    phone_number_id = models.CharField(max_length=50)
    contact_name = models.CharField(max_length=255)
    contact_wa_id = models.CharField(max_length=15)
    message_from = models.CharField(max_length=15)
    message_id = models.CharField(max_length=255)
    message_timestamp = models.DateTimeField()
    message_text = models.TextField()

    def get_responses(self):
        return self.whatsappresponse_set.all()

class WhatsAppResponse(models.Model):
    message = models.ForeignKey(WhatsAppMessage, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_message(self):
        return self.message


class WhatsAppConversation(models.Model):
    messages = models.ManyToManyField(WhatsAppMessage)
    responses = models.ManyToManyField(WhatsAppResponse)
    
    

# models.py

from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    # sender = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='inapp_sent_messages')
    # receiver = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='inapp_received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
