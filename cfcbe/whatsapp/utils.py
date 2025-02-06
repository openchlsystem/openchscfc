import json
import requests
import base64
import logging
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile

from .models import Contact, WhatsAppMessage, WhatsAppMedia

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set the token refresh threshold in minutes
TOKEN_REFRESH_THRESHOLD = getattr(settings, 'TOKEN_REFRESH_THRESHOLD', 30)  # Default to 30 minutes if not set


def get_access_token():
    """
    Retrieve the current access token from cache or refresh it if needed.
    """
    token_info = cache.get('whatsapp_access_token')
    if token_info and token_info['expires_at'] > datetime.utcnow() + timedelta(minutes=TOKEN_REFRESH_THRESHOLD):
        logging.info("Using cached access token.")
        return token_info['access_token']
    else:
        logging.info("Access token from cache is expired or missing; refreshing token.")
        return refresh_access_token()


def refresh_access_token():
    """
    Refresh the WhatsApp API access token using Facebook's OAuth API.
    """
    refresh_url = "https://graph.facebook.com/v19.0/oauth/access_token"
    payload = {
        'grant_type': 'fb_exchange_token',
        'client_id': settings.WHATSAPP_CLIENT_ID,
        'client_secret': settings.WHATSAPP_CLIENT_SECRET,
        'fb_exchange_token': settings.WHATSAPP_INITIAL_ACCESS_TOKEN,
    }
    response = requests.get(refresh_url, params=payload)
    if response.status_code == 200:
        data = response.json()
        new_token = data['access_token']
        expires_in = data.get('expires_in', 5184000)  # Default to 60 days if not provided

        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        cache.set('whatsapp_access_token', {'access_token': new_token, 'expires_at': expires_at}, timeout=expires_in)

        logging.info("Successfully refreshed access token.")
        return new_token
    else:
        logging.error(f"Failed to refresh token: {response.status_code} {response.text}")
        response.raise_for_status()


def setup():
    """
    Initial setup for storing the access token in cache if not already present.
    """
    if not cache.get('whatsapp_access_token'):
        logging.info("No access token in cache; attempting to refresh.")
        refresh_access_token()


def send_whatsapp_message(phone_number, message_type, content=None, caption=None, media_url=None):
    """
    Sends a message to WhatsApp via API.
    """
    url = f"{settings.WHATSAPP_API_URL}/v1/messages"
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone_number,
        "type": message_type,
    }

    if message_type == "text":
        payload["text"] = {"body": content}
    elif message_type in ["image", "video", "audio", "document"]:
        payload[message_type] = {"link": media_url, "caption": caption} if caption else {"link": media_url}

    response = requests.post(url, json=payload, headers=headers)
    return response.json()


# def download_media(media_id, access_token):
#     """
#     Downloads media using WhatsApp API and returns the Base64 representation.
#     """
#     api_url = f"https://graph.facebook.com/v17.0/{media_id}"
#     headers = {"Authorization": f"Bearer {access_token}"}

#     try:
#         # Fetch media metadata
#         response = requests.get(api_url, headers=headers)
#         response.raise_for_status()
#         media_url = response.json().get("url")

#         # Download media file
#         media_response = requests.get(media_url, headers=headers)
#         media_response.raise_for_status()

#         # Convert media content to Base64
#         media_base64 = base64.b64encode(media_response.content).decode("utf-8")
#         return media_base64
#     except Exception as e:
#         logging.error(f"Error downloading media: {e}")
#         return None

def download_media(media_url, media_type):
    """
    Downloads media from a given URL and returns a Django ContentFile object.
    """
    headers = {"Authorization": f"Bearer {get_access_token()}"}

    try:
        response = requests.get(media_url, headers=headers)
        response.raise_for_status()

        # Determine the file extension based on media type
        extension_map = {
            "image": "jpg",
            "video": "mp4",
            "audio": "mp3",
            "document": "pdf"
        }
        file_extension = extension_map.get(media_type, "bin")

        # Save as Django ContentFile
        file_content = ContentFile(response.content, name=f"downloaded_media.{file_extension}")
        return file_content

    except Exception as e:
        logger.error(f"Error downloading media: {e}")
        return None


PHONE_NUMBER_MAPPING = {
    "123456789012345": "15551234567",  # phone_number_id -> actual phone number
}

def forward_whatsapp_message_to_main_system(message):
    """
    Sends the WhatsApp message details to the main system via a POST request.
    """
    api_url = "https://demo-openchs.bitz-itc.com/helpline/api/msg/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sccjqsonvfvro3v2pn80iat2me",
    }

    def sanitize_text(text):
        return text.encode("utf-8", errors="replace").decode("utf-8") if text else text

    payload = {
        "sender": sanitize_text(message.sender.wa_id if message.sender else None),
        "recipient": sanitize_text(message.recipient.wa_id if message.recipient else None),
        "message_type": sanitize_text(message.message_type),
        "content": sanitize_text(message.content),
        "caption": sanitize_text(message.caption),
        "media_url": sanitize_text(message.media.media_url if message.media else None),
        "media_mime_type": sanitize_text(message.media.media_mime_type if message.media else None),
        "timestamp": message.timestamp.isoformat(),
    }

    logging.info(f"Payload JSON: {payload}")

    try:
        # Base64 encode the payload
        payload_json = json.dumps(payload)
        encoded_data = base64.b64encode(payload_json.encode("utf-8")).decode("utf-8")
        logging.info(f"Base64 Encoded Data: {encoded_data}")

        complaint = {
            "channel": "chat",
            "timestamp": message.timestamp.isoformat(),
            "session_id": "session_id_placeholder",
            "message_id": str(message.id),
            "from": message.sender.wa_id if message.sender else None,
            "message": encoded_data,
            "mime": "application/json",
        }

        response = requests.post(api_url, json=complaint, headers=headers)
        logging.info(f"API Response: {response.status_code}, {response.text}")
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to forward message: {message.id}. Error: {e}")

def get_media_url_from_whatsapp(media_id):
    """
    Fetches the media URL from WhatsApp API using the provided media ID.
    """
    access_token = get_access_token()  # Function that fetches your access token

    url = f"https://graph.facebook.com/v18.0/{media_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        media_url = response.json().get("url")

        if not media_url:
            logger.error("Failed to get media URL from WhatsApp API.")
            return None

        return media_url

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching media URL: {e}")
        return None
