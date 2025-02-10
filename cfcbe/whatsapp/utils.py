import json
import requests
import base64
import logging
from django.utils.timezone import now
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.core.files.base import ContentFile
from whatsapp.models import WhatsAppCredential

from cfcbe.settings import WHATSAPP_API_URL, WHATSAPP_PHONE_NUMBER_ID

from .models import Contact, Organization, WhatsAppMessage, WhatsAppMedia

logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set the token refresh threshold in minutes
TOKEN_REFRESH_THRESHOLD = getattr(
    settings, "TOKEN_REFRESH_THRESHOLD", 30
)  # Default to 30 minutes if not set



TOKEN_REFRESH_THRESHOLD = 5  # Refresh if less than 5 minutes left

from django.core.exceptions import ObjectDoesNotExist
def get_access_token(org_id):
    """
    Retrieve or create a WhatsApp access token.
    """
    from whatsapp.models import WhatsAppCredential, Organization
    from datetime import datetime, timezone, timedelta

    try:
        org = Organization.objects.get(id=org_id)

        # Ensure WhatsApp credentials exist
        creds, created = WhatsAppCredential.objects.get_or_create(
            organization=org,
            defaults={
                "access_token": "your_default_access_token",
                "client_id": "your_default_client_id",
                "client_secret": "your_default_client_secret",
                "phone_number_id": "your_default_phone_number_id",
                "business_id": "your_default_business_id",
                "token_expiry": datetime.now(timezone.utc) + timedelta(days=60),
            }
        )

        if created:
            logging.info(f"✅ Created WhatsAppCredential for organization {org_id}.")

        # Refresh token if expired
        if not creds.token_expiry or creds.token_expiry <= datetime.now(timezone.utc) + timedelta(minutes=5):
            logging.info(f"🔄 Token expired for org_id {org_id}. Refreshing...")
            return refresh_access_token(org_id)

        logging.info("✔️ Using stored access token.")
        return creds.access_token

    except Organization.DoesNotExist:
        logging.error(f"❌ Organization with ID {org_id} does not exist.")
        return None

def refresh_access_token(org_id):
    """
    Refresh the WhatsApp API access token using Facebook's OAuth API.
    If credentials exist, update them. Otherwise, create a new entry.
    """
    try:
        creds, created = WhatsAppCredential.objects.get_or_create(organization_id=org_id)

        refresh_url = "https://graph.facebook.com/v19.0/oauth/access_token"
        payload = {
            "grant_type": "fb_exchange_token",
            "client_id": creds.client_id or settings.WHATSAPP_CLIENT_ID,
            "client_secret": creds.client_secret or settings.WHATSAPP_CLIENT_SECRET,
            "fb_exchange_token": creds.access_token or settings.WHATSAPP_ACCESS_TOKEN,
        }

        response = requests.get(refresh_url, params=payload)

        if response.status_code == 200:
            data = response.json()
            new_token = data["access_token"]
            expires_in = data.get("expires_in", 5184000)  # Default 60 days if missing
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            # print("Token expires at:" + {expires_at})
            print(f"Token expires at: {expires_at}")  # ✅ Correct formatting


            # Update database with new token
            creds.access_token = new_token  # Encrypt before saving
            creds.token_expiry = expires_at
            creds.client_id = creds.client_id or settings.WHATSAPP_CLIENT_ID
            creds.client_secret = creds.client_secret or settings.WHATSAPP_CLIENT_SECRET
            creds.phone_number_id = creds.phone_number_id or settings.WHATSAPP_PHONE_NUMBER_ID
            creds.business_id = creds.business_id or settings.WHATSAPP_BUSINESS_ID
            creds.save()

            logging.info("Successfully refreshed and stored new access token in DB.")
            return new_token

        else:
            logging.error(f"Failed to refresh token: {response.status_code} {response.text}")
            response.raise_for_status()

    except Exception as e:
        logging.error(f"Error refreshing token: {e}")
        return None


def setup(org_id):
    """
    Initial setup for storing the access token in database if not already present.
    If missing, it will fetch from settings and store it.
    """
    if not get_access_token(org_id):
        logging.info("No valid access token found; attempting to refresh.")
        refresh_access_token(org_id)


def send_whatsapp_message(
    phone_number, message_type, content=None, caption=None, media_url=None
):
    """
    Sends a message to WhatsApp via API.
    """
    # url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    url = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {get_access_token(1)}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": message_type,
    }
    if message_type == "text":
        payload["text"] = {"body": content}
    elif message_type in ["image", "video", "audio", "document"]:
        payload[message_type] = {"link": media_url}
        if caption:
            payload[message_type]["caption"] = caption

    logging.info(f"Sending WhatsApp message: {payload}")

    response = requests.post(url, json=payload, headers=headers)

    logging.info(f"WhatsApp API Response: {response.status_code} {response.text}")

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


def download_media(media_url, media_type, media_id):
    """
    Downloads media from a given URL and returns a Django ContentFile object.
    """
    headers = {"Authorization": f"Bearer {get_access_token(1)}"}

    try:
        response = requests.get(media_url, headers=headers)
        response.raise_for_status()

        # Determine the file extension based on media type
        extension_map = {
            "image": "jpg",
            "video": "mp4",
            "audio": "mp3",
            "document": "pdf",
        }
        file_extension = extension_map.get(media_type, "bin")

        # Save as Django ContentFile
        file_content = ContentFile(
            response.content, name=f"{media_id}.{file_extension}"
        )
        return file_content

    except Exception as e:
        logger.error(f"Error downloading media: {e}")
        return None


def get_media_url_from_whatsapp(media_id):
    """
    Fetches the media URL from WhatsApp API using the provided media ID.
    """
    print("Getting media url")
    access_token = get_access_token(1)  # Function that fetches your access token

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

PHONE_NUMBER_MAPPING = {
    "123456789012345": "15551234567",  # phone_number_id -> actual phone number
}
# def sanitize_text(text):
#     return text.encode("utf-8", errors="replace").decode("utf-8") if text else text


# payload = {
#     "sender": sanitize_text(message.sender.wa_id if message.sender else None),
#     "recipient": sanitize_text(message.recipient.wa_id if message.recipient else None),
#     "message_type": sanitize_text(message.message_type),
#     "content": sanitize_text(message.content),
#     "caption": sanitize_text(message.caption),
#     "media_url": sanitize_text(message.media.media_url if message.media else None),
#     "media_mime_type": sanitize_text(message.media.media_mime_type if message.media else None),
#     "timestamp": message.timestamp.isoformat(),
# }

API_URL = "https://demo-openchs.bitz-itc.com/helpline/api/msg/"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sci9de994iddqlmj8fv7r1js74",
}

def forward_whatsapp_message_to_main_system(message):
    """
    Sends WhatsApp messages to the main system.
    - If the message is text, it sends normally.
    - If the message contains media, it converts it to Base64 and sends it.
    - If the message has a caption, it sends the caption separately.
    """
    try:
        # Default values
        encoded_message = None
        mime_type = "text/plain"

        if message.message_type == "text":
            # Encode the text message
            encoded_message = base64.b64encode(message.content.encode("utf-8")).decode("utf-8")

            # Send text message
            send_to_main_system(message, encoded_message, "text/plain")

        elif message.media:
            # Handle media messages
            media_instance = message.media
            if not media_instance.media_file:
                logging.error(f"Media file missing for message {message.id}")
                return
            
            # Read media file and convert to Base64
            with media_instance.media_file.open("rb") as file:
                encoded_message = base64.b64encode(file.read()).decode("utf-8")
            
            # Use the correct MIME type from the media instance
            mime_type = media_instance.media_mime_type or "application/octet-stream"

            # Send media message
            send_to_main_system(message, encoded_message, mime_type)

            # If there's a caption, send it separately
            if message.caption:
                encoded_caption = base64.b64encode(message.caption.encode("utf-8")).decode("utf-8")
                send_to_main_system(message, encoded_caption, "text/plain")

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to forward message {message.id}. Error: {e}")

def send_to_main_system(message, encoded_message, mime_type):
    """
    Sends the formatted message to the main system.
    """
    payload = {
        "channel": "whatsup",
        "timestamp": message.timestamp.isoformat(),
        "session_id": message.sender.wa_id if message.sender else None,
        "message_id": str(message.id),
        "from": message.sender.wa_id if message.sender else None,
        "message": encoded_message,
        "mime": mime_type,
    }

    response = requests.post(API_URL, json=payload, headers=HEADERS)
    logging.info(f"API Response: {response.status_code}, {response.text}")
    response.raise_for_status()
    
    
    from whatsapp.models import Organization

def create_dummy_organization():
    """
    Creates a dummy organization with hardcoded values if none exists.
    """
    if not Organization.objects.exists():
        org = Organization.objects.create(
            name="Demo Organization",
            email="demo@organization.com",
            phone="+1234567890"
        )
        logging.info(f"Dummy organization created with ID {org.id}.")
        return org
    else:
        org = Organization.objects.first()
        logging.info(f"Using existing organization with ID {org.id}.")
        return org
