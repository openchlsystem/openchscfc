import json
import logging
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from django_filters import rest_framework as filters
from django.db.models.signals import post_save
from django.dispatch import receiver

from cfcbe.settings import WHATSAPP_API_URL, WHATSAPP_PHONE_NUMBER_ID

from .models import Contact, WhatsAppMessage, WhatsAppMedia
from .serializers import (
    WhatsAppMessageSerializer,
    WhatsAppMediaSerializer,
    ContactSerializer,
)
from .utils import (
    download_media,
    get_access_token,
    get_media_url_from_whatsapp,
    setup,
)  # Assume this function is well implemented


# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "GET":
        return handle_verification_request(request)
    elif request.method == "POST":
        return handle_incoming_messages(request)
    else:
        logging.warning(f"Received invalid HTTP method: {request.method}")
        return HttpResponseBadRequest(
            "Invalid HTTP method. This endpoint expects a GET or POST request."
        )


def handle_verification_request(request):
    """Handles WhatsApp webhook verification."""
    hub_mode = request.GET.get("hub.mode")
    hub_challenge = request.GET.get("hub.challenge")
    hub_verify_token = request.GET.get("hub.verify_token")

    logging.debug(
        f"Received verification request: mode={hub_mode}, challenge={hub_challenge}, token={hub_verify_token}"
    )

    if hub_mode == "subscribe" and hub_verify_token == settings.VERIFICATION_TOKEN:
        logging.info("Webhook verified successfully.")
        return JsonResponse(int(hub_challenge), safe=False, status=200)

    return HttpResponseBadRequest("Verification failed. Check your verification token.")


logger = logging.getLogger(__name__)


def handle_incoming_messages(request):
    try:
        # Parse the JSON payload
        data = json.loads(request.body.decode("utf-8"))
        logger.info(f"Received payload: {json.dumps(data, indent=4)}")

        # Extract messages from the payload
        entries = data.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                contacts = value.get("contacts", [])
                messages = value.get("messages", [])

                for message in messages:
                    # Extract sender and message type
                    sender_wa_id = message.get("from")  # Sender's WhatsApp ID
                    message_type = message.get("type")

                    # Extract contact name if available
                    contact_name = None
                    if contacts:
                        contact_name = contacts[0].get("profile", {}).get("name")

                    # Extract message content
                    content = (
                        message.get("text", {}).get("body")
                        if message_type == "text"
                        else None
                    )
                    caption = message.get("caption", None)

                    # Ensure the message data is valid
                    if not sender_wa_id:
                        logger.error(
                            "Message does not contain a sender (from). Skipping."
                        )
                        continue

                    # Get or create the contact
                    contact, _ = Contact.objects.get_or_create(
                        wa_id=sender_wa_id, defaults={"name": contact_name}
                    )
                    logger.info(f"Contact retrieved/created: {contact}")

                    # Handle media messages
                    media_instance = None
                    if message_type in ["image", "video", "audio", "document"]:
                        media_id = message.get(message_type, {}).get("id")
                        mime_type = message.get(message_type, {}).get("mime_type")

                        if media_id:
                            media_url = get_media_url_from_whatsapp(media_id)
                            media_file = (
                                download_media(media_url, message_type)
                                if media_url
                                else None
                            )
                            if media_url:
                                media_instance = WhatsAppMedia.objects.create(
                                    media_type=message_type,
                                    media_url=media_url,
                                    media_mime_type=mime_type,
                                )
                            # Save file if downloaded successfully
                            if media_file:
                                media_instance.media_file.save(
                                     media_file
                                )
                                logger.info(f"Saved media file: {media_file}")

                            media_instance.save()
                            logger.info(f"Saved media: {media_instance}")

                    # Save the message
                    whatsapp_message = WhatsAppMessage.objects.create(
                        sender=contact,
                        recipient=None,  # Incoming messages have no recipient
                        message_type=message_type,
                        content=content,
                        caption=caption,
                        media=media_instance,
                        status="received",
                    )
                    logger.info(f"Message saved: {whatsapp_message}")

        return JsonResponse(
            {"status": "Success", "message": "Messages received and saved successfully"}
        )

    except Exception as e:
        logger.error(f"Error handling incoming message: {str(e)}")
        return HttpResponseBadRequest(f"Error handling incoming message: {str(e)}")



@csrf_exempt
def send_message(request):
    setup() 
    """Handles sending and replying to WhatsApp messages."""
    
    # Ensure the request is a POST request
    if request.method != "POST":
        return HttpResponseBadRequest("This endpoint only supports POST requests.")

    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        recipient_wa_id = data.get("recipient")  # WhatsApp recipient ID
        message_type = data.get("message_type", "text")  # Message type (default: text)
        content = data.get("content", "")  # Message content (for text messages)
        caption = data.get("caption", None)  # Caption for media messages (optional)
        media_url = data.get("media_url", None)  # Media URL (for image, video, etc.)
        mime_type = data.get("mime_type", None)  # MIME type of media (optional)

        # Fixed sender (WhatsApp Business ID) from settings
        fixed_sender_wa_id = settings.WHATSAPP_BUSINESS_ID  

        # Validate recipient ID
        if not recipient_wa_id:
            return JsonResponse({"status": "Error", "message": "Recipient ID is required"}, status=400)

        # Validate message content based on message type
        if message_type == "text" and not content:
            return JsonResponse({"status": "Error", "message": "Text message requires content"}, status=400)
        if message_type in ["image", "video", "audio", "document"] and not media_url:
            return JsonResponse({"status": "Error", "message": "Media message requires media_url"}, status=400)

        # Ensure the recipient exists in the database, or create a new entry
        recipient, _ = Contact.objects.get_or_create(wa_id=recipient_wa_id)
        if not recipient or not recipient.wa_id:
            logging.error(f"Failed to create or retrieve recipient: {recipient_wa_id}")
            return JsonResponse({"status": "Error", "message": "Recipient could not be created"}, status=400)

        # Ensure the sender exists in the database, or create a new entry
        sender, _ = Contact.objects.get_or_create(wa_id=fixed_sender_wa_id)
        if not sender or not sender.wa_id:
            logging.error(f"Failed to create or retrieve sender: {fixed_sender_wa_id}")
            return JsonResponse({"status": "Error", "message": "Sender could not be created"}, status=400)

        # Log message details before sending
        logging.info(f"Sending {message_type} message to {recipient_wa_id}")

        # Retrieve the access token for WhatsApp API
        access_token = get_access_token()
        if not access_token:
            logging.error("Failed to retrieve WhatsApp API access token.")
            return JsonResponse({"status": "Error", "message": "Access token retrieval failed"}, status=500)

        # Send the message using WhatsApp API
        response = send_whatsapp_message(
            access_token, recipient_wa_id, message_type, content, caption, media_url
        )

        # Log response from the WhatsApp API
        logging.info(f"WhatsApp API Response: {response}")

        # Handle media message storage (if media is sent)
        media_instance = None
        if media_url:
            media_instance = WhatsAppMedia.objects.create(
                media_type=message_type,
                media_url=media_url,
                media_mime_type=mime_type,
            )

        # Save message details in the database
        WhatsAppMessage.objects.create(
            sender=sender,  # Sender is the fixed WhatsApp Business ID
            recipient=recipient,  # Recipient who receives the message
            message_type=message_type,  # Type of message (text, image, etc.)
            content=content,  # Message content for text messages
            caption=caption,  # Caption for media messages
            media=media_instance,  # Media instance if applicable
            status="sent" if response.get("success") else "failed",  # Track message status
        )

        # Return success response
        return JsonResponse({"status": "Success", "response": "Message sent and logged"})

    except json.JSONDecodeError:
        # Handle invalid JSON format errors
        return JsonResponse({"status": "Error", "message": "Invalid JSON format"}, status=400)
    
    except Exception as e:
        # Log unexpected errors and return a server error response
        logging.error(f"Error processing request: {str(e)}", exc_info=True)
        return JsonResponse({"status": "Error", "message": "Internal Server Error"}, status=500)


@receiver(post_save, sender=WhatsAppMessage)
def send_whatsapp_message_on_create(sender, instance, created, **kwargs):
    """Automatically sends a message when a new outgoing message is created."""
    if created and instance.recipient:
        access_token = get_access_token()
        send_whatsapp_message(
            access_token,
            instance.recipient.wa_id,
            instance.message_type,
            instance.content,
            instance.caption,
            instance.media.media_url if instance.media else None,
        )


def send_whatsapp_message(
    access_token, recipient, message_type, content=None, caption=None, media_url=None
):
    """Sends a message via the WhatsApp API."""
    endpoint_url = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    request_body = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": message_type,
    }

    if message_type == "text":
        request_body["text"] = {"preview_url": False, "body": content}
    elif message_type in ["image", "video", "audio", "document"]:
        request_body[message_type] = (
            {"link": media_url, "caption": caption} if caption else {"link": media_url}
        )

    try:
        response = requests.post(endpoint_url, json=request_body, headers=headers)
        response.raise_for_status()
        logging.info("Message sent successfully.")
        return {"success": True}
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending message: {e}")
        return {"success": False}


# Lists only incoming messages (where recipient is NULL)
class IncomingMessageList(generics.ListAPIView):
    queryset = WhatsAppMessage.objects.filter(recipient=None)
    serializer_class = WhatsAppMessageSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["sender", "message_type", "status"]


# Lists only outgoing messages (where sender is NULL)
class OutgoingMessageList(generics.ListAPIView):
    queryset = WhatsAppMessage.objects.filter(sender=None)
    serializer_class = WhatsAppMessageSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["recipient", "message_type", "status"]


# API Views using Django REST Framework
class WhatsAppMessageList(generics.ListCreateAPIView):
    queryset = WhatsAppMessage.objects.all()
    serializer_class = WhatsAppMessageSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["sender", "recipient", "message_type", "status"]


class WhatsAppMediaList(generics.ListCreateAPIView):
    queryset = WhatsAppMedia.objects.all()
    serializer_class = WhatsAppMediaSerializer


class ContactList(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ["wa_id"]
