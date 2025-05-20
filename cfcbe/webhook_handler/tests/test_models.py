import uuid
import json
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from webhook_handler.models import (
    # Core Gateway Models
    Conversation, WebhookMessage,
    # Authentication Models
    Organization, EmailVerification,
    # Webform Models
    Person, Complaint, CaseNote, ComplaintStatus, Notification, Voicenote,
    # WhatsApp Models
    Contact, WhatsAppMedia, WhatsAppMessage, WhatsAppResponse, WhatsAppCredential
)


class ConversationModelTests(TestCase):
    def setUp(self):
        self.conversation = Conversation.objects.create(
            conversation_id="test_conversation_123",
            sender_id="test_sender_123",
            platform="whatsapp",
            metadata={"test_key": "test_value"}
        )

    def test_conversation_creation(self):
        """Test Conversation model can be created."""
        self.assertEqual(self.conversation.conversation_id, "test_conversation_123")
        self.assertEqual(self.conversation.sender_id, "test_sender_123")
        self.assertEqual(self.conversation.platform, "whatsapp")
        self.assertTrue(self.conversation.is_active)
        self.assertIsNotNone(self.conversation.last_activity)
        self.assertEqual(self.conversation.metadata, {"test_key": "test_value"})

    def test_conversation_string_representation(self):
        """Test Conversation string representation."""
        self.assertEqual(str(self.conversation), "whatsapp conversation with test_sender_123")


class WebhookMessageModelTests(TestCase):
    def setUp(self):
        self.conversation = Conversation.objects.create(
            conversation_id="test_conversation_123",
            sender_id="test_sender_123",
            platform="whatsapp"
        )
        self.message = WebhookMessage.objects.create(
            message_id="test_message_123",
            conversation=self.conversation,
            sender_id="test_sender_123",
            platform="whatsapp",
            content="Test message content",
            media_url="https://example.com/test.jpg",
            message_type="text",
            metadata={"test_key": "test_value"}
        )

    def test_webhook_message_creation(self):
        """Test WebhookMessage model can be created."""
        self.assertEqual(self.message.message_id, "test_message_123")
        self.assertEqual(self.message.conversation, self.conversation)
        self.assertEqual(self.message.sender_id, "test_sender_123")
        self.assertEqual(self.message.platform, "whatsapp")
        self.assertEqual(self.message.content, "Test message content")
        self.assertEqual(self.message.media_url, "https://example.com/test.jpg")
        self.assertEqual(self.message.message_type, "text")
        self.assertIsNotNone(self.message.timestamp)
        self.assertEqual(self.message.metadata, {"test_key": "test_value"})

    def test_webhook_message_string_representation(self):
        """Test WebhookMessage string representation."""
        self.assertEqual(str(self.message), "Message from test_sender_123 on whatsapp")


class OrganizationModelTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            email="test@example.com",
            phone="1234567890"
        )

    def test_organization_creation(self):
        """Test Organization model can be created."""
        self.assertEqual(self.organization.name, "Test Organization")
        self.assertEqual(self.organization.email, "test@example.com")
        self.assertEqual(self.organization.phone, "1234567890")
        self.assertTrue(self.organization.is_active)
        self.assertIsNotNone(self.organization.created_at)
        self.assertIsNotNone(self.organization.updated_at)

    def test_organization_string_representation(self):
        """Test Organization string representation."""
        self.assertEqual(str(self.organization), "Test Organization")

    def test_organization_uuid(self):
        """Test that organization ID is a valid UUID."""
        self.assertIsInstance(self.organization.id, uuid.UUID)


class EmailVerificationModelTests(TestCase):
    def setUp(self):
        self.verification = EmailVerification.create_verification("test@example.com")

    def test_email_verification_creation(self):
        """Test EmailVerification model can be created."""
        self.assertEqual(self.verification.email, "test@example.com")
        self.assertEqual(len(self.verification.otp), 6)
        self.assertFalse(self.verification.is_verified)
        self.assertIsNotNone(self.verification.expires_at)
        self.assertIsNotNone(self.verification.created_at)

    def test_otp_generation(self):
        """Test OTP generation."""
        otp = EmailVerification.generate_otp()
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())

    def test_is_valid_method(self):
        """Test is_valid method."""
        # New verification should be valid
        self.assertTrue(self.verification.is_valid())
        
        # Expired verification should not be valid
        self.verification.expires_at = timezone.now() - timedelta(minutes=1)
        self.verification.save()
        self.assertFalse(self.verification.is_valid())
        
        # Verified verification should not be valid
        self.verification.expires_at = timezone.now() + timedelta(minutes=10)
        self.verification.is_verified = True
        self.verification.save()
        self.assertFalse(self.verification.is_valid())

    def test_create_verification_replaces_existing(self):
        """Test that creating a new verification for the same email invalidates previous ones."""
        old_otp = self.verification.otp
        new_verification = EmailVerification.create_verification("test@example.com")
        
        self.verification.refresh_from_db()
        self.assertFalse(self.verification.is_verified)
        self.assertNotEqual(old_otp, new_verification.otp)


class PersonModelTests(TestCase):
    def setUp(self):
        self.person = Person.objects.create(
            name="Test Person",
            age=30,
            gender="Male",
            additional_info="Test additional info"
        )

    def test_person_creation(self):
        """Test Person model can be created."""
        self.assertEqual(self.person.name, "Test Person")
        self.assertEqual(self.person.age, 30)
        self.assertEqual(self.person.gender, "Male")
        self.assertEqual(self.person.additional_info, "Test additional info")

    def test_person_string_representation(self):
        """Test Person string representation."""
        self.assertEqual(str(self.person), "Test Person")


class ComplaintModelTests(TestCase):
    def setUp(self):
        self.conversation = Conversation.objects.create(
            conversation_id="test_conversation_123",
            sender_id="test_sender_123",
            platform="webform"
        )
        self.organization = Organization.objects.create(
            name="Test Organization",
            email="test@example.com"
        )
        self.victim = Person.objects.create(
            name="Test Victim",
            age=25,
            gender="Female"
        )
        self.perpetrator = Person.objects.create(
            name="Test Perpetrator",
            age=40,
            gender="Male"
        )
        # Create a mock image file
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',  # Empty content for test
            content_type='image/jpeg'
        )
        self.complaint = Complaint.objects.create(
            session_id=uuid.uuid4(),
            conversation=self.conversation,
            organization=self.organization,
            reporter_nickname="Anonymous",
            case_category="Harassment",
            complaint_text="Test complaint text",
            complaint_image=self.test_image,
            message_id_ref="ref123",
            victim=self.victim,
            perpetrator=self.perpetrator
        )

    def test_complaint_creation(self):
        """Test Complaint model can be created."""
        self.assertIsInstance(self.complaint.complaint_id, uuid.UUID)
        self.assertIsInstance(self.complaint.session_id, uuid.UUID)
        self.assertEqual(self.complaint.conversation, self.conversation)
        self.assertEqual(self.complaint.organization, self.organization)
        self.assertEqual(self.complaint.reporter_nickname, "Anonymous")
        self.assertEqual(self.complaint.case_category, "Harassment")
        self.assertEqual(self.complaint.complaint_text, "Test complaint text")
        self.assertIsNotNone(self.complaint.complaint_image)
        self.assertEqual(self.complaint.message_id_ref, "ref123")
        self.assertEqual(self.complaint.victim, self.victim)
        self.assertEqual(self.complaint.perpetrator, self.perpetrator)
        self.assertIsNotNone(self.complaint.created_at)

    def test_complaint_string_representation(self):
        """Test Complaint string representation."""
        expected = f"Complaint {self.complaint.complaint_id} by Anonymous"
        self.assertEqual(str(self.complaint), expected)


class CaseNoteModelTests(TestCase):
    def setUp(self):
        self.complaint = Complaint.objects.create(
            reporter_nickname="Anonymous",
            complaint_text="Test complaint text"
        )
        self.case_note = CaseNote.objects.create(
            complaint=self.complaint,
            note_text="Test note text",
            created_by="Test Agent"
        )

    def test_case_note_creation(self):
        """Test CaseNote model can be created."""
        self.assertEqual(self.case_note.complaint, self.complaint)
        self.assertEqual(self.case_note.note_text, "Test note text")
        self.assertIsNone(self.case_note.note_audio)
        self.assertEqual(self.case_note.created_by, "Test Agent")
        self.assertIsNotNone(self.case_note.created_at)

    def test_case_note_string_representation(self):
        """Test CaseNote string representation."""
        expected = f"CaseNote for {self.complaint.complaint_id} on {self.case_note.created_at}"
        self.assertEqual(str(self.case_note), expected)


class ComplaintStatusModelTests(TestCase):
    def setUp(self):
        self.complaint = Complaint.objects.create(
            reporter_nickname="Anonymous",
            complaint_text="Test complaint text"
        )
        self.status = ComplaintStatus.objects.create(
            complaint=self.complaint,
            status="In Progress",
            updated_by="Test Agent"
        )

    def test_complaint_status_creation(self):
        """Test ComplaintStatus model can be created."""
        self.assertEqual(self.status.complaint, self.complaint)
        self.assertEqual(self.status.status, "In Progress")
        self.assertEqual(self.status.updated_by, "Test Agent")
        self.assertIsNotNone(self.status.updated_at)

    def test_complaint_status_string_representation(self):
        """Test ComplaintStatus string representation."""
        expected = f"Status for Complaint {self.complaint.complaint_id}: In Progress"
        self.assertEqual(str(self.status), expected)


class NotificationModelTests(TestCase):
    def setUp(self):
        self.complaint = Complaint.objects.create(
            reporter_nickname="Anonymous",
            complaint_text="Test complaint text"
        )
        self.notification = Notification.objects.create(
            complaint=self.complaint,
            message="Test notification message"
        )

    def test_notification_creation(self):
        """Test Notification model can be created."""
        self.assertIsInstance(self.notification.notification_id, uuid.UUID)
        self.assertEqual(self.notification.complaint, self.complaint)
        self.assertEqual(self.notification.message, "Test notification message")
        self.assertFalse(self.notification.is_read)
        self.assertIsNotNone(self.notification.created_at)

    def test_notification_string_representation(self):
        """Test Notification string representation."""
        expected = f"Notification for Complaint {self.complaint.complaint_id}"
        self.assertEqual(str(self.notification), expected)


class VoicenoteModelTests(TestCase):
    def setUp(self):
        self.complaint = Complaint.objects.create(
            reporter_nickname="Anonymous",
            complaint_text="Test complaint text"
        )
        self.voicenote = Voicenote.objects.create(
            complaint=self.complaint,
            voicenote=b'test audio data'
        )

    def test_voicenote_creation(self):
        """Test Voicenote model can be created."""
        self.assertEqual(self.voicenote.complaint, self.complaint)
        self.assertEqual(self.voicenote.voicenote, b'test audio data')
        self.assertIsNotNone(self.voicenote.created_at)

    def test_voicenote_string_representation(self):
        """Test Voicenote string representation."""
        expected = f"Voicenote for Complaint {self.complaint.complaint_id}"
        self.assertEqual(str(self.voicenote), expected)
        
    def test_voicenote_without_complaint(self):
        """Test Voicenote model without complaint."""
        voicenote_no_complaint = Voicenote.objects.create(
            voicenote=b'test audio data without complaint'
        )
        expected = "Voicenote for Complaint No complaint"
        self.assertEqual(str(voicenote_no_complaint), expected)


class ContactModelTests(TestCase):
    def setUp(self):
        self.conversation = Conversation.objects.create(
            conversation_id="test_conversation_123",
            sender_id="test_sender_123",
            platform="whatsapp"
        )
        self.contact = Contact.objects.create(
            wa_id="1234567890",
            name="Test Contact",
            display_phone_number="+1234567890",
            conversation=self.conversation
        )

    def test_contact_creation(self):
        """Test Contact model can be created."""
        self.assertEqual(self.contact.wa_id, "1234567890")
        self.assertEqual(self.contact.name, "Test Contact")
        self.assertEqual(self.contact.display_phone_number, "+1234567890")
        self.assertEqual(self.contact.conversation, self.conversation)

    def test_contact_string_representation_with_name(self):
        """Test Contact string representation with name."""
        self.assertEqual(str(self.contact), "Test Contact")

    def test_contact_string_representation_without_name(self):
        """Test Contact string representation without name."""
        self.contact.name = None
        self.contact.save()
        self.assertEqual(str(self.contact), "1234567890")


class WhatsAppMediaModelTests(TestCase):
    def setUp(self):
        # Create a mock media file
        self.test_file = SimpleUploadedFile(
            name='test_media.jpg',
            content=b'',  # Empty content for test
            content_type='image/jpeg'
        )
        self.media = WhatsAppMedia.objects.create(
            media_type="image",
            media_url="https://example.com/test.jpg",
            media_file=self.test_file,
            media_mime_type="image/jpeg"
        )

    def test_whatsapp_media_creation(self):
        """Test WhatsAppMedia model can be created."""
        self.assertEqual(self.media.media_type, "image")
        self.assertEqual(self.media.media_url, "https://example.com/test.jpg")
        self.assertIsNotNone(self.media.media_file)
        self.assertEqual(self.media.media_mime_type, "image/jpeg")

    def test_whatsapp_media_string_representation_with_url(self):
        """Test WhatsAppMedia string representation with URL."""
        self.assertEqual(str(self.media), "Media (image) - https://example.com/test.jpg")

    def test_whatsapp_media_string_representation_with_file(self):
        """Test WhatsAppMedia string representation with file."""
        self.media.media_url = None
        self.media.save()
        self.assertTrue(str(self.media).startswith("Media (image) - "))


class WhatsAppMessageModelTests(TestCase):
    def setUp(self):
        self.conversation = Conversation.objects.create(
            conversation_id="test_conversation_123",
            sender_id="test_sender_123",
            platform="whatsapp"
        )
        self.webhook_message = WebhookMessage.objects.create(
            message_id="test_message_123",
            conversation=self.conversation,
            sender_id="test_sender_123",
            platform="whatsapp",
            content="Test message content"
        )
        self.contact = Contact.objects.create(
            wa_id="1234567890",
            name="Test Contact"
        )
        self.media = WhatsAppMedia.objects.create(
            media_type="image",
            media_url="https://example.com/test.jpg"
        )
        self.message = WhatsAppMessage.objects.create(
            sender="9876543210",
            recipient=self.contact,
            conversation=self.conversation,
            webhook_message=self.webhook_message,
            message_type="image",
            content="Test message content",
            caption="Test caption",
            media=self.media,
            status="sent"
        )

    def test_whatsapp_message_creation(self):
        """Test WhatsAppMessage model can be created."""
        self.assertEqual(self.message.sender, "9876543210")
        self.assertEqual(self.message.recipient, self.contact)
        self.assertEqual(self.message.conversation, self.conversation)
        self.assertEqual(self.message.webhook_message, self.webhook_message)
        self.assertEqual(self.message.message_type, "image")
        self.assertEqual(self.message.content, "Test message content")
        self.assertEqual(self.message.caption, "Test caption")
        self.assertEqual(self.message.media, self.media)
        self.assertEqual(self.message.status, "sent")
        self.assertFalse(self.message.is_forwarded_to_main_system)
        self.assertIsNotNone(self.message.timestamp)

    def test_whatsapp_message_string_representation(self):
        """Test WhatsAppMessage string representation."""
        expected = f"Message from 9876543210 to {self.contact} (image, sent)"
        self.assertEqual(str(self.message), expected)

    def test_mark_as_sent_method(self):
        """Test mark_as_sent method."""
        self.message.status = "pending"
        self.message.save()
        self.message.mark_as_sent()
        self.assertEqual(self.message.status, "sent")

    def test_mark_as_failed_method(self):
        """Test mark_as_failed method."""
        self.message.status = "pending"
        self.message.save()
        self.message.mark_as_failed()
        self.assertEqual(self.message.status, "failed")

    def test_mark_as_delivered_method(self):
        """Test mark_as_delivered method."""
        self.message.status = "sent"
        self.message.save()
        self.message.mark_as_delivered()
        self.assertEqual(self.message.status, "delivered")

    def test_mark_as_read_method(self):
        """Test mark_as_read method."""
        self.message.status = "delivered"
        self.message.save()
        self.message.mark_as_read()
        self.assertEqual(self.message.status, "read")


class WhatsAppResponseModelTests(TestCase):
    def setUp(self):
        self.conversation = Conversation.objects.create(
            conversation_id="test_conversation_123",
            sender_id="test_sender_123",
            platform="whatsapp"
        )
        self.webhook_message = WebhookMessage.objects.create(
            message_id="test_message_123",
            conversation=self.conversation,
            sender_id="test_sender_123",
            platform="whatsapp",
            content="Test message content"
        )
        self.message = WhatsAppMessage.objects.create(
            sender="9876543210",
            conversation=self.conversation,
            webhook_message=self.webhook_message,
            message_type="text",
            content="Test message content"
        )
        self.response_webhook = WebhookMessage.objects.create(
            message_id="test_response_123",
            conversation=self.conversation,
            sender_id="system",
            platform="whatsapp",
            content="Test response content"
        )
        self.response = WhatsAppResponse.objects.create(
            message=self.message,
            content="Test response content",
            webhook_message=self.response_webhook
        )

    def test_whatsapp_response_creation(self):
        """Test WhatsAppResponse model can be created."""
        self.assertEqual(self.response.message, self.message)
        self.assertEqual(self.response.content, "Test response content")
        self.assertEqual(self.response.webhook_message, self.response_webhook)
        self.assertIsNotNone(self.response.timestamp)

    def test_whatsapp_response_string_representation(self):
        """Test WhatsAppResponse string representation."""
        expected = f"Response at {self.response.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        self.assertEqual(str(self.response), expected)

    def test_get_message_method(self):
        """Test get_message method."""
        self.assertEqual(self.response.get_message(), self.message)


class WhatsAppCredentialModelTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            email="test@example.com"
        )
        self.credential = WhatsAppCredential.objects.create(
            organization=self.organization,
            client_id="test_client_id",
            client_secret="test_client_secret",
            business_id="test_business_id",
            phone_number_id="test_phone_number_id",
            access_token="test_access_token",
            token_expiry=timezone.now() + timedelta(days=30)
        )

    def test_whatsapp_credential_creation(self):
        """Test WhatsAppCredential model can be created."""
        self.assertEqual(self.credential.organization, self.organization)
        self.assertEqual(self.credential.client_id, "test_client_id")
        self.assertEqual(self.credential.client_secret, "test_client_secret")
        self.assertEqual(self.credential.business_id, "test_business_id")
        self.assertEqual(self.credential.phone_number_id, "test_phone_number_id")
        self.assertEqual(self.credential.access_token, "test_access_token")
        self.assertIsNotNone(self.credential.token_expiry)

    def test_whatsapp_credential_string_representation(self):
        """Test WhatsAppCredential string representation."""
        expected = f"WhatsApp Credentials for Test Organization"
        self.assertEqual(str(self.credential), expected)