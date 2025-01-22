import json
import requests
import base64
import logging
from django.utils.timezone import now
from .models import WhatsAppMessage

logger = logging.getLogger(__name__)

def send_whatsapp_message(phone_number, message):
    url = f"{settings.WHATSAPP_API_URL}/v1/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": phone_number,
        "type": "text",
        "text": {"body": message},
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def download_media(media_id, access_token):
    """
    Downloads media using WhatsApp API and converts it to Base64.
    """
    api_url = f"https://graph.facebook.com/v17.0/{media_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    try:
        # Fetch media metadata
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        media_url = response.json().get("url")

        # Download media file
        media_response = requests.get(media_url, headers=headers)
        media_response.raise_for_status()

        # Convert media content to Base64
        media_base64 = base64.b64encode(media_response.content).decode("utf-8")
        return media_base64
    except Exception as e:
        logging.error(f"Error downloading media: {e}")
        return None

# Mapping of phone_number_id to actual WhatsApp numbers
PHONE_NUMBER_MAPPING = {
    "123456789012345": "15551234567",  # phone_number_id -> actual phone number
}

def decode_and_save_message(message_data, phone_number_id, access_token):
    """
    Decodes incoming WhatsApp message data, converts it to a string or Base64 if applicable,
    and saves it in the database.

    :param message_data: Dictionary containing WhatsApp message details
    :param phone_number_id: The phone_number_id from metadata (used to derive recipient)
    :param access_token: WhatsApp API access token for downloading media
    :return: WhatsAppMessage instance or None if failed
    """
    try:
        # Derive the recipient from phone_number_id
        recipient = PHONE_NUMBER_MAPPING.get(phone_number_id, "UNKNOWN_RECIPIENT")
        sender = message_data.get('from')  # WhatsApp number of the sender
        message_type = message_data.get('type')
        timestamp = message_data.get('timestamp')

        # Convert Unix timestamp to timezone-aware datetime
        if timestamp:
            timestamp = now()

        # Initialize fields for saving
        content = None
        media_url = None
        media_base64 = None
        media_mime_type = None
        caption = None

        # Handle different message types
        if message_type == 'text':
            content = message_data['text']['body']
        elif message_type in ['image', 'video', 'audio', 'document']:
            media_id = message_data[message_type]['id']
            media_mime_type = message_data[message_type].get('mime_type')
            caption = message_data[message_type].get('caption')
            # Download and convert the media to Base64
            media_base64 = download_media(media_id, access_token)
        else:
            content = f"Unsupported message type: {message_type}"

        # Save the message to the database
        message = WhatsAppMessage.objects.create(
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            content=content,
            caption=caption,
            media_url=media_url,
            media_base64=media_base64,
            media_mime_type=media_mime_type,
            timestamp=timestamp,
        )
        logger.info(f"Message from {sender} saved successfully.")
        return message

    except Exception as e:
        logger.error(f"Failed to decode and save message: {e}")
        return None

def forward_whatsapp_message_to_main_system(message):
    """
    Sends the WhatsApp message details to the main system via a POST request.
    
    :param message: WhatsAppMessage object to be forwarded
    """
    # API configuration
    api_url = "https://demo-openchs.bitz-itc.com/helpline/api/msg/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sccjqsonvfvro3v2pn80iat2me",
    }

        # Sanitize and construct payload
    def sanitize_text(text):
        if text:
            return text.encode("utf-8", errors="replace").decode("utf-8")
        return text

    payload = {
        "sender": sanitize_text(message.sender),
        "recipient": sanitize_text(message.recipient),
        "message_type": sanitize_text(message.message_type),
        "content": sanitize_text(message.content),
        "caption": sanitize_text(message.caption),
        "media_url": sanitize_text(message.media_url),
        "media_base64": sanitize_text(message.media_base64),
        "media_mime_type": sanitize_text(message.media_mime_type),
        "timestamp": message.timestamp.isoformat(),
    }
    
    logging.info(f"Payload JSON: {payload}")

    try:
        # Base64 encoding
        payload_json = json.dumps(payload)
        encoded_data = base64.b64encode(payload_json.encode("utf-8")).decode("utf-8")
        logging.info(f"Base64 Encoded Data: {encoded_data}")

        # Construct complaint
        complaint = {
            "channel": "chat",
            "timestamp": message.timestamp.isoformat(),
            "session_id": "str(instance.session_id)",  # Replace or derive session_id
            "message_id": str(message.id),
            "from": "str(instance.session_id)",  # Replace or derive session_id
            "message": encoded_data,
            "mime": "application/json",
        }

        # Send POST request
        response = requests.post(api_url, json=complaint, headers=headers)
        logging.info(f"API Response: {response.status_code}, {response.text}")
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e} - Response: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to forward email: {message.sender}. Error: {e}")
