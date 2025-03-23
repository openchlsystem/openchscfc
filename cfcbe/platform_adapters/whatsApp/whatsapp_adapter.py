from typing import List, Dict, Any, Optional
import hmac
import hashlib
import json
import base64
import logging
import time
import requests
from datetime import datetime, timedelta
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile

from platform_adapters.base_adapter import BaseAdapter
from shared.models.standard_message import StandardMessage
from webhook_handler.models import (
    Contact, WhatsAppMessage, WhatsAppMedia, Conversation, WebhookMessage,
    Organization, WhatsAppCredential
)
from webhook_handler.services.conversation_service import ConversationService

logger = logging.getLogger(__name__)

class WhatsAppAdapter(BaseAdapter):
    """
    Adapter for handling WhatsApp messages through the Meta Business API.
    
    This adapter handles webhook verification, signature validation,
    and message parsing for WhatsApp.
    """
    
    def __init__(self):
        """Initialize WhatsApp adapter."""
        self.conversation_service = ConversationService()
    
    def handle_verification(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Handle WhatsApp webhook verification.
        
        WhatsApp (Meta) sends a GET request with a verification token
        that must be echoed back to confirm the webhook.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            HTTP response with the challenge if verification successful
        """
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        # Get config for this platform
        from platform_adapters.adapter_factory import AdapterFactory
        config = AdapterFactory.get_adapter_config('whatsapp')
        verify_token = config.get('verify_token')
        
        # Verify the token
        if mode == 'subscribe' and token == verify_token:
            if challenge:
                return HttpResponse(challenge)
        
        return None
    
    def validate_request(self, request: HttpRequest) -> bool:
        """
        Validate the authenticity of incoming WhatsApp webhook.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            True if request has valid signature, False otherwise
        """
        # Get config for this platform
        from platform_adapters.adapter_factory import AdapterFactory
        config = AdapterFactory.get_adapter_config('whatsapp')
        app_secret = config.get('app_secret')
        
        if not app_secret:
            logger.warning("WhatsApp app_secret not configured, skipping signature validation")
            return True
        
        # Get the signature from header
        signature = request.headers.get('X-Hub-Signature-256')
        if not signature:
            logger.warning("Missing X-Hub-Signature-256 header in WhatsApp webhook")
            return False
        
        # Get request body as bytes
        if request.body:
            # Compute HMAC signature
            expected_signature = 'sha256=' + hmac.new(
                app_secret.encode('utf-8'),
                request.body,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            if not hmac.compare_digest(signature, expected_signature):
                logger.warning("Invalid WhatsApp webhook signature")
                return False
                
            return True
        
        logger.warning("Empty request body in WhatsApp webhook")
        return False
    
    def parse_messages(self, request: HttpRequest) -> List[Dict[str, Any]]:
        """
        Extract messages from WhatsApp webhook.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            List of messages in standardized format
        """
        try:
            # Parse the request body
            if not request.body:
                return []
                
            # Check if this is an outgoing message request
            try:
                data = json.loads(request.body)
                if 'direction' in data and data['direction'] == 'outgoing':
                    # For outgoing messages, we don't parse but return an empty list
                    # The actual sending is handled elsewhere
                    return []
                elif 'direction' in data and data['direction'] == 'token':
                    # For token operations, we don't parse but return an empty list
                    # The actual token operation is handled elsewhere
                    return []
            except (json.JSONDecodeError, AttributeError):
                # Not JSON or doesn't have the expected structure, continue with normal parsing
                pass
                
            body = json.loads(request.body)
            
            # Check for entry and changes
            entries = body.get('entry', [])
            if not entries:
                return []
                
            messages = []
            
            for entry in entries:
                changes = entry.get('changes', [])
                for change in changes:
                    value = change.get('value', {})
                    
                    # Process contact information
                    contacts = value.get('contacts', [])
                    contact_info = contacts[0] if contacts else {}
                    
                    # Process messages
                    message_values = value.get('messages', [])
                    for message_value in message_values:
                        # Extract message details
                        message_id = message_value.get('id')
                        from_user = message_value.get('from')
                        timestamp = message_value.get('timestamp', int(time.time()))
                        
                        # Get or create contact
                        contact_name = contact_info.get('profile', {}).get('name', from_user)
                        contact, created = Contact.objects.get_or_create(
                            wa_id=from_user,
                            defaults={'name': contact_name}
                        )
                        
                        # Get or create conversation
                        conversation = self.conversation_service.get_or_create_conversation(
                            from_user, 'whatsapp'
                        )
                        
                        # Link contact to conversation if needed
                        if not created and contact.conversation != conversation:
                            contact.conversation = conversation
                            contact.save(update_fields=['conversation'])
                        
                        # Process different message types
                        if 'text' in message_value:
                            text = message_value['text'].get('body', '')
                            
                            # Create WhatsApp-specific message record
                            wa_message = self._create_whatsapp_message(
                                contact, None, 'text', text, 
                                None, None, conversation
                            )
                            
                            # Create standard message
                            message = self._create_standard_message(
                                message_id=message_id,
                                sender_id=from_user,
                                content=text,
                                timestamp=timestamp,
                                message_type='text',
                                wa_message=wa_message
                            )
                            messages.append(message.to_dict())
                            
                        elif 'image' in message_value:
                            image = message_value['image']
                            caption = message_value.get('caption', '')
                            media_id = image.get('id')
                            mime_type = image.get('mime_type', 'image/jpeg')
                            
                            # Process the media
                            media_instance = self._process_media(media_id, 'image', mime_type)
                            
                            # Create WhatsApp-specific message record
                            wa_message = self._create_whatsapp_message(
                                contact, None, 'image', caption,
                                caption, media_instance, conversation
                            )
                            
                            # Create standard message
                            message = self._create_standard_message(
                                message_id=message_id,
                                sender_id=from_user,
                                content=caption,
                                timestamp=timestamp,
                                message_type='image',
                                media_url=media_instance.media_url if media_instance else None,
                                wa_message=wa_message
                            )
                            messages.append(message.to_dict())
                            
                        elif 'audio' in message_value:
                            audio = message_value['audio']
                            media_id = audio.get('id')
                            mime_type = audio.get('mime_type', 'audio/ogg')
                            
                            # Process the media
                            media_instance = self._process_media(media_id, 'audio', mime_type)
                            
                            # Create WhatsApp-specific message record
                            wa_message = self._create_whatsapp_message(
                                contact, None, 'audio', '',
                                None, media_instance, conversation
                            )
                            
                            # Create standard message
                            message = self._create_standard_message(
                                message_id=message_id,
                                sender_id=from_user,
                                content='',
                                timestamp=timestamp,
                                message_type='audio',
                                media_url=media_instance.media_url if media_instance else None,
                                wa_message=wa_message
                            )
                            messages.append(message.to_dict())
                            
                        elif 'video' in message_value:
                            video = message_value['video']
                            caption = message_value.get('caption', '')
                            media_id = video.get('id')
                            mime_type = video.get('mime_type', 'video/mp4')
                            
                            # Process the media
                            media_instance = self._process_media(media_id, 'video', mime_type)
                            
                            # Create WhatsApp-specific message record
                            wa_message = self._create_whatsapp_message(
                                contact, None, 'video', caption,
                                caption, media_instance, conversation
                            )
                            
                            # Create standard message
                            message = self._create_standard_message(
                                message_id=message_id,
                                sender_id=from_user,
                                content=caption,
                                timestamp=timestamp,
                                message_type='video',
                                media_url=media_instance.media_url if media_instance else None,
                                wa_message=wa_message
                            )
                            messages.append(message.to_dict())
                            
                        elif 'document' in message_value:
                            document = message_value['document']
                            caption = message_value.get('caption', '')
                            media_id = document.get('id')
                            mime_type = document.get('mime_type', 'application/pdf')
                            
                            # Process the media
                            media_instance = self._process_media(media_id, 'document', mime_type)
                            
                            # Create WhatsApp-specific message record
                            wa_message = self._create_whatsapp_message(
                                contact, None, 'document', caption,
                                caption, media_instance, conversation
                            )
                            
                            # Create standard message
                            message = self._create_standard_message(
                                message_id=message_id,
                                sender_id=from_user,
                                content=caption,
                                timestamp=timestamp,
                                message_type='document',
                                media_url=media_instance.media_url if media_instance else None,
                                wa_message=wa_message
                            )
                            messages.append(message.to_dict())
            
            return messages
                
        except json.JSONDecodeError:
            logger.exception("Error decoding WhatsApp webhook JSON")
            return []
        except Exception as e:
            logger.exception(f"Error parsing WhatsApp messages: {str(e)}")
            return []  
        
    def send_message(self, recipient_id: str, message_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to a WhatsApp user.
        
        Args:
            recipient_id: WhatsApp ID of the recipient
            message_content: Content to send
            
        Returns:
            Response data from WhatsApp API
        """
        try:
            # Get config for this platform
            from platform_adapters.adapter_factory import AdapterFactory
            config = AdapterFactory.get_adapter_config('whatsapp')
            api_token = self._get_access_token()
            phone_number_id = config.get('phone_number_id')
            
            if not api_token or not phone_number_id:
                return {
                    'status': 'error',
                    'error': 'WhatsApp API not configured'
                }
            
            # Determine message type and format payload
            message_type = message_content.get('message_type', 'text')
            content = message_content.get('content', '')
            caption = message_content.get('caption', '')
            media_url = message_content.get('media_url', '')
            
            # Construct the WhatsApp API payload
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient_id,
                "type": message_type,
            }
            
            if message_type == 'text':
                payload["text"] = {"body": content}
            elif message_type == 'image':
                payload["image"] = {"link": media_url}
                if caption:
                    payload["image"]["caption"] = caption
            elif message_type == 'audio':
                payload["audio"] = {"link": media_url}
            elif message_type == 'video':
                payload["video"] = {"link": media_url}
                if caption:
                    payload["video"]["caption"] = caption
            elif message_type == 'document':
                payload["document"] = {"link": media_url}
                if caption:
                    payload["document"]["caption"] = caption
            
            # Get or create conversation and contact
            conversation = self.conversation_service.get_or_create_conversation(
                recipient_id, 'whatsapp'
            )
            
            contact, _ = Contact.objects.get_or_create(
                wa_id=recipient_id,
                defaults={'name': recipient_id}
            )
            
            # Link contact to conversation if needed
            if contact.conversation != conversation:
                contact.conversation = conversation
                contact.save(update_fields=['conversation'])
            
            # Send to WhatsApp API
            url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            }
            
            logger.info(f"Sending to WhatsApp API: {json.dumps(payload)}")
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code in (200, 201):
                response_data = response.json()
                
                # Create a webhook message record
                webhook_message = WebhookMessage.objects.create(
                    message_id=response_data.get('messages', [{}])[0].get('id', str(time.time())),
                    conversation=conversation,
                    sender_id='system',
                    platform='whatsapp',
                    content=content,
                    media_url=media_url,
                    message_type=message_type,
                    timestamp=timezone.now()
                )
                
                # Create WhatsApp-specific message record
                media_instance = None
                if media_url:
                    media_instance = WhatsAppMedia.objects.create(
                        media_type=message_type,
                        media_url=media_url,
                        media_mime_type=self._get_mime_type(message_type)
                    )
                
                wa_message = self._create_whatsapp_message(
                    None, contact, message_type, content,
                    caption, media_instance, conversation
                )
                
                # Link the WhatsApp message to the webhook message
                wa_message.webhook_message = webhook_message
                wa_message.save(update_fields=['webhook_message'])
                
                return {
                    'status': 'success',
                    'message_id': response_data.get('messages', [{}])[0].get('id'),
                    'response': response_data
                }
            else:
                logger.error(f"WhatsApp API error: {response.status_code} {response.text}")
                return {
                    'status': 'error',
                    'http_status': response.status_code,
                    'error': response.text
                }
                
        except Exception as e:
            logger.exception(f"Error sending WhatsApp message: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def format_webhook_response(self, responses: List[Dict[str, Any]]) -> HttpResponse:
        """
        Format response to return to WhatsApp webhook.
        
        WhatsApp expects a 200 OK response for successful webhook processing.
        
        Args:
            responses: List of processed message responses
            
        Returns:
            HTTP 200 OK response
        """
        # WhatsApp just needs a 200 OK response
        return HttpResponse(status=200)
    
    def _create_whatsapp_message(
        self, sender: Optional[Contact], recipient: Optional[Contact], 
        message_type: str, content: str, caption: Optional[str],
        media: Optional[WhatsAppMedia], conversation: Conversation
    ) -> WhatsAppMessage:
        """
        Create a WhatsApp message record.
        
        Args:
            sender: Sender contact
            recipient: Recipient contact
            message_type: Type of message
            content: Message content
            caption: Media caption
            media: Media instance
            conversation: Conversation
            
        Returns:
            WhatsAppMessage instance
        """
        wa_message = WhatsAppMessage.objects.create(
            sender=sender.wa_id if sender else None,
            recipient=recipient,
            conversation=conversation,
            message_type=message_type,
            content=content,
            caption=caption,
            media=media,
            status='received' if sender else 'sent'
        )
        
        return wa_message
    
    def _create_standard_message(
        self, message_id: str, sender_id: str, content: str, 
        timestamp: int, message_type: str = 'text', 
        media_url: str = None, wa_message: WhatsAppMessage = None
    ) -> StandardMessage:
        """
        Create a StandardMessage from WhatsApp message data.
        
        Args:
            message_id: WhatsApp message ID
            sender_id: WhatsApp user ID
            content: Message text content
            timestamp: Message timestamp (Unix time)
            message_type: Type of message (text, image, etc.)
            media_url: URL to media content if applicable
            wa_message: WhatsAppMessage instance
            
        Returns:
            StandardMessage instance
        """
        # Convert timestamp to float if it's an integer
        timestamp_float = float(timestamp)
        
        # Create metadata
        metadata = {
            'whatsapp_message_id': message_id,
            'whatsapp_message_db_id': wa_message.id if wa_message else None,
            'platform_specific': {
                'wa_message_type': message_type
            }
        }
        
        return StandardMessage(
            message_id=message_id,
            sender_id=sender_id,
            platform='whatsapp',
            content=content,
            timestamp=timestamp_float,
            message_type=message_type,
            media_url=media_url,
            metadata=metadata
        )
    
    def _get_access_token(self) -> str:
        """
        Get the WhatsApp access token.
        
        Tries to get token from WhatsAppCredential model, then falls back to settings.
        
        Returns:
            Access token
        """
        try:
            # Try to get credentials from the database
            org = Organization.objects.first()
            if org:
                creds = WhatsAppCredential.objects.filter(organization=org).first()
                if creds and creds.access_token:
                    # Check if token is expired
                    if creds.token_expiry and creds.token_expiry > timezone.now():
                        return creds.access_token
                    else:
                        # Token is expired, try to refresh
                        new_token = self._refresh_access_token(creds)
                        if new_token:
                            return new_token
            
            # Fall back to token in settings
            from django.conf import settings
            return getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')
            
        except Exception as e:
            logger.exception(f"Error getting access token: {str(e)}")
            # Fall back to token in settings
            from django.conf import settings
            return getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')
    
    def _refresh_access_token(self, creds: WhatsAppCredential) -> Optional[str]:
        """
        Refresh the WhatsApp access token.
        
        Args:
            creds: WhatsAppCredential instance
            
        Returns:
            New access token or None if refresh failed
        """
        try:
            from django.conf import settings
            client_id = getattr(settings, 'WHATSAPP_CLIENT_ID', '')
            client_secret = getattr(settings, 'WHATSAPP_CLIENT_SECRET', '')
            
            if not client_id or not client_secret:
                logger.error("WhatsApp client ID or secret not configured")
                return None
            
            # Exchange token
            url = f"https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': client_id,
                'client_secret': client_secret,
                'fb_exchange_token': creds.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                new_token = data.get('access_token')
                if new_token:
                    # Update the credential
                    creds.access_token = new_token
                    creds.token_expiry = timezone.now() + timedelta(days=60)
                    creds.save()
                    return new_token
            
            logger.error(f"Failed to refresh token: {response.status_code} {response.text}")
            return None
            
        except Exception as e:
            logger.exception(f"Error refreshing access token: {str(e)}")
            return None
    
    def _get_mime_type(self, message_type: str) -> str:
        """
        Get MIME type based on message type.
        
        Args:
            message_type: Type of message
            
        Returns:
            MIME type
        """
        mime_types = {
            'text': 'text/plain',
            'image': 'image/jpeg',
            'audio': 'audio/ogg',
            'video': 'video/mp4',
            'document': 'application/pdf'
        }
        
        return mime_types.get(message_type, 'application/octet-stream')
    
    def _process_media(self, media_id: str, media_type: str, mime_type: str) -> Optional[WhatsAppMedia]:
        """
        Process media from WhatsApp.
        
        Args:
            media_id: WhatsApp media ID
            media_type: Type of media
            mime_type: MIME type
            
        Returns:
            WhatsAppMedia instance or None if processing failed
        """
        try:
            # Get media URL
            media_url = self._get_media_url(media_id)
            
            if not media_url:
                logger.error(f"Failed to get media URL for {media_id}")
                return None
            
            # Download media
            media_file = self._download_media(media_url, media_type, media_id)
            
            if not media_file:
                logger.error(f"Failed to download media for {media_id}")
                # Create media record with URL only
                return WhatsAppMedia.objects.create(
                    media_type=media_type,
                    media_url=media_url,
                    media_mime_type=mime_type
                )
            
            # Create media record with file
            media = WhatsAppMedia.objects.create(
                media_type=media_type,
                media_url=media_url,
                media_mime_type=mime_type
            )
            
            # Save the file
            file_name = f"{media_id}.{self._get_file_extension(media_type)}"
            media.media_file.save(file_name, media_file, save=True)
            
            return media
            
        except Exception as e:
            logger.exception(f"Error processing media: {str(e)}")
            return None
    
    def _get_media_url(self, media_id: str) -> Optional[str]:
        """
        Get media URL from WhatsApp.
        
        Args:
            media_id: WhatsApp media ID
            
        Returns:
            Media URL or None if fetch failed
        """
        try:
            url = f"https://graph.facebook.com/v18.0/{media_id}"
            headers = {'Authorization': f'Bearer {self._get_access_token()}'}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('url')
            
            logger.error(f"Failed to get media URL: {response.status_code} {response.text}")
            return None
            
        except Exception as e:
            logger.exception(f"Error getting media URL: {str(e)}")
            return None
    
    def _download_media(self, media_url: str, media_type: str, media_id: str) -> Optional[ContentFile]:
        """
        Download media from URL.
        
        Args:
            media_url: Media URL
            media_type: Type of media
            media_id: Media ID
            
        Returns:
            ContentFile or None if download failed
        """
        try:
            headers = {'Authorization': f'Bearer {self._get_access_token()}'}
            
            response = requests.get(media_url, headers=headers)
            
            if response.status_code == 200:
                file_extension = self._get_file_extension(media_type)
                return ContentFile(response.content, name=f"{media_id}.{file_extension}")
            
            logger.error(f"Failed to download media: {response.status_code}")
            return None
            
        except Exception as e:
            logger.exception(f"Error downloading media: {str(e)}")
            return None
    
    def _get_file_extension(self, media_type: str) -> str:
        """
        Get file extension based on media type.
        
        Args:
            media_type: Type of media
            
        Returns:
            File extension
        """
        extensions = {
            'image': 'jpg',
            'audio': 'ogg',
            'video': 'mp4',
            'document': 'pdf'
        }
        
        return extensions.get(media_type, 'bin')
        
    def generate_token(self, short_lived_token: str, org_id: int = None) -> Dict[str, Any]:
        """
        Exchange a short-lived token for a long-lived token.
        
        Args:
            short_lived_token: Short-lived access token
            org_id: Optional organization ID
            
        Returns:
            Dictionary with token information
        """
        try:
            from django.conf import settings
            client_id = getattr(settings, 'WHATSAPP_CLIENT_ID', '')
            client_secret = getattr(settings, 'WHATSAPP_CLIENT_SECRET', '')
            
            if not client_id or not client_secret:
                return {
                    'status': 'error',
                    'error': 'WhatsApp client ID or secret not configured'
                }
            
            # Exchange token
            url = f"https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': client_id,
                'client_secret': client_secret,
                'fb_exchange_token': short_lived_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                new_token = data.get('access_token')
                if new_token:
                    # Get or create organization
                    if org_id:
                        org, created = Organization.objects.get_or_create(
                            id=org_id,
                            defaults={
                                'name': f'Organization {org_id}',
                                'email': f'org{org_id}@example.com'
                            }
                        )
                    else:
                        org, created = Organization.objects.get_or_create(
                            name='Default Organization',
                            defaults={
                                'email': 'default@example.com'
                            }
                        )
                    
                    # Update or create credentials
                    creds, _ = WhatsAppCredential.objects.update_or_create(
                        organization=org,
                        defaults={
                            'access_token': new_token,
                            'token_expiry': timezone.now() + timedelta(days=60),
                            'client_id': client_id,
                            'client_secret': client_secret,
                            'phone_number_id': getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', ''),
                            'business_id': getattr(settings, 'WHATSAPP_BUSINESS_ID', '')
                        }
                    )
                    
                    return {
                        'status': 'success',
                        'token': new_token,
                        'expiry': creds.token_expiry.isoformat(),
                        'organization_id': org.id
                    }
                    
                else:
                    return {
                        'status': 'error',
                        'error': 'No access token in response'
                    }
            else:
                return {
                    'status': 'error',
                    'http_status': response.status_code,
                    'error': response.text
                }
                
        except Exception as e:
            logger.exception(f"Error generating token: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }