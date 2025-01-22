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
