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
    """Handles sending and replying to WhatsApp messages."""
    if request.method != "POST":
        return HttpResponseBadRequest("This endpoint only supports POST requests.")

    try:
        data = json.loads(request.body)
        recipient_wa_id = data.get("recipient")
        message_type = data.get("message_type", "text")
        content = data.get("content", "")
        caption = data.get("caption", None)
        media_url = data.get("media_url", None)
        mime_type = data.get("mime_type", None)
        sender_id = data.get("sender_id")

        if not recipient_wa_id:
            return JsonResponse({"status": "Error", "message": "Recipient ID is missing"}, status=400)

        # Ensure sender exists
        sender = None
        if sender_id:
            sender =" 254101541655" # Use `first()` to avoid NoneType errors
            if not sender:
                return JsonResponse({"status": "Error", "message": "Invalid sender ID"}, status=400)

        # Ensure recipient exists or create it if not
        recipient, created = Contact.objects.get_or_create(wa_id=recipient_wa_id)
        
        if not recipient:
            return JsonResponse({"status": "Error", "message": "Recipient not found or could not be created"}, status=400)

        access_token = get_access_token()
        response = send_whatsapp_message(
            access_token, recipient_wa_id, message_type, content, caption, media_url
        )

        media_instance = None
        if media_url:
            media_instance = WhatsAppMedia.objects.create(
                media_type=message_type,
                media_url=media_url,
                media_mime_type=mime_type,
            )

        # Save the message
        WhatsAppMessage.objects.create(
            sender=sender,  # Sender is now validated
            recipient=recipient,
            message_type=message_type,
            content=content,
            caption=caption,
            media=media_instance,
            status="sent" if response["success"] else "failed",
        )

        return JsonResponse({"status": "Success", "response": "Message sent and logged"})

    except json.JSONDecodeError:
        return JsonResponse({"status": "Error", "message": "Invalid JSON format"}, status=400)
    except Exception as e:
        logging.error(f"Failed to send message: {str(e)}")
        return JsonResponse({"status": "Error", "message": str(e)}, status=400)



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
    endpoint_url = "https://graph.facebook.com/v18.0/101592599705197/messages"
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
