from typing import List, Dict, Any, Optional
from django.http import HttpRequest, HttpResponse, JsonResponse
import json
import uuid
import time
import logging
import requests
import base64
from datetime import datetime, timezone, timedelta
from django.core.files.base import ContentFile

from platform_adapters.base_adapter import BaseAdapter
from shared.models.standard_message import StandardMessage
from webhook_handler.models import (
    Contact, WhatsAppMedia, WhatsAppMessage, WhatsAppResponse,
    Organization, WhatsAppCredential, Conversation, WebhookMessage
)
from django.conf import settings
from platform_adapters.whatsApp.token_manager import TokenManager
from platform_adapters.whatsApp.chatbot_adapter import MaternalHealthChatbot

logger = logging.getLogger(__name__)

class WhatsAppAdapter(BaseAdapter):
    """
    Adapter for handling WhatsApp messages as a platform in the gateway.
    
    This adapter processes WhatsApp webhook data and converts it to
    the standardized message format used by the gateway. It also integrates
    maternal health chatbot functionality for messages containing "HEALTH".
    """
    
    def __init__(self):
        """Initialize the WhatsApp Adapter."""
        self.config = self._get_config()
        self.chatbot = MaternalHealthChatbot()  # Initialize chatbot
    
    def _get_config(self):
        """Get configuration from settings."""
        platform_configs = getattr(settings, 'PLATFORM_CONFIGS', {})
        return platform_configs.get('whatsapp', {})
    
    def get_media_url_from_whatsapp(self, media_id):
        """
        Fetches the media URL from WhatsApp API using the provided media ID.
        
        Args:
            media_id: ID of the media to fetch
            
        Returns:
            Media URL or None if the request fails
        """
        # Get access token using TokenManager
        access_token = TokenManager.get_access_token()
        
        if not access_token:
            logger.error("Missing WhatsApp API token")
            return None
        
        # WhatsApp Graph API endpoint for media
        url = f"https://graph.facebook.com/v18.0/{media_id}"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Extract media URL from response
            media_url = response.json().get("url")
            
            if not media_url:
                logger.error("Failed to get media URL from WhatsApp API")
                return None
                
            return media_url
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching media URL: {e}")
            return None
    
    def download_media(self, media_url, media_type, media_id):
        """
        Downloads media from a given URL and returns a Django ContentFile object.
        
        Args:
            media_url: URL of the media to download
            media_type: Type of media (image, video, audio, document)
            media_id: ID of the media (for naming)
            
        Returns:
            Django ContentFile object containing the media
        """
        # Get access token using TokenManager
        access_token = TokenManager.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}

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
    
    def handle_verification(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Handle WhatsApp webhook verification challenge.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            HttpResponse with challenge if verification, None otherwise
        """
        hub_mode = request.GET.get("hub.mode")
        hub_challenge = request.GET.get("hub.challenge")
        hub_verify_token = request.GET.get("hub.verify_token")
        
        verify_token = self.config.get('verify_token')
        
        if hub_mode == "subscribe" and hub_verify_token == verify_token:
            logger.info("WhatsApp webhook verification successful")
            return HttpResponse(int(hub_challenge), status=200)
        
        return None
    
    def validate_request(self, request: Any) -> bool:
        """
        Validate the authenticity of incoming WhatsApp webhook request.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            True if request is valid, False otherwise
        """
        # For WhatsApp, we could validate X-Hub-Signature header
        # But for simplicity, we'll just check basic structure
        if isinstance(request, HttpRequest):
            try:
                data = json.loads(request.body)
                
                # Check for basic WhatsApp webhook structure
                if 'entry' in data and len(data['entry']) > 0:
                    for entry in data['entry']:
                        if 'changes' in entry and len(entry['changes']) > 0:
                            return True
                
                logger.warning("WhatsApp webhook validation failed: invalid structure")
                return False
            except json.JSONDecodeError:
                logger.warning("WhatsApp webhook validation failed: invalid JSON")
                return False
        
        return False
    
    def parse_messages(self, request: Any) -> List[Dict[str, Any]]:
        """
        Extract messages from WhatsApp webhook data.
        
        Args:
            request: The incoming HttpRequest or data
            
        Returns:
            List of parsed messages in StandardMessage format
        """
        standard_messages = []
        
        # Parse the request body
        if isinstance(request, HttpRequest):
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from WhatsApp webhook")
                return []
        else:
            data = request

        # Process each entry and change
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                
                # Process messages
                messages = value.get('messages', [])
                contacts = value.get('contacts', [])
                
                # Extract contact information
                contact_info = {}
                if contacts and len(contacts) > 0:
                    contact = contacts[0]
                    profile = contact.get('profile', {})
                    contact_info = {
                        'name': profile.get('name'),
                        'wa_id': contact.get('wa_id')
                    }
                
                # Process each message
                for message in messages:
                    # Check if this is a chatbot message
                    is_chatbot = False
                    sender_id = message.get('from')
                    
                    # Check if this is a "HEALTH" message or from active session
                    if message.get('type') == 'text':
                        text_content = message.get('text', {}).get('body', '')
                        if text_content.strip().upper() == "HEALTH" or self.chatbot.is_active_session(sender_id):
                            is_chatbot = True
                            # Handle via chatbot (will be processed in process_incoming_message)
                            # Just mark the message so we know to handle it
                            if 'metadata' not in message:
                                message['metadata'] = {}
                            message['metadata']['is_chatbot_message'] = True
                    
                    # Handle media if present
                    media_instance = None
                    if message.get('type') in ['image', 'video', 'audio', 'document']:
                        # Media handling code would be here 
                        # For simplicity, we're skipping the detailed implementation
                        pass
                    
                    # Create or get contact
                    contact_name = contact_info.get('name')
                    
                    if sender_id:
                        # First, create or get the contact
                        contact, created = Contact.objects.get_or_create(
                            wa_id=sender_id,
                            defaults={'name': contact_name or 'Unknown'}
                        )
                        
                        # Ensure contact is saved, even if it was just created
                        if created:
                            contact.save()

                        # Create the WhatsAppMessage
                        whatsapp_message = WhatsAppMessage.objects.create(
                            sender=contact,
                            recipient=None,  # No recipient for incoming message
                            message_type=message.get('type', 'text'),
                            content=message.get('text', {}).get('body', '') if message.get('type') == 'text' else '',
                            caption=message.get('caption', ''),
                            media=media_instance,
                            status="received"
                        )

                        # Add the newly created message ID to the metadata
                        if 'metadata' not in message:
                            message['metadata'] = {}
                        message['metadata']['whatsapp_message_id'] = whatsapp_message.id
                    
                    # Convert to standard message
                    standard_message = self._convert_to_standard_message(message, contact_info)
                    if standard_message:
                        standard_messages.append(standard_message.to_dict())
        
        return standard_messages
    
    def _convert_to_standard_message(self, message: Dict[str, Any], contact_info: Dict[str, Any]) -> Optional[StandardMessage]:
        """
        Convert a WhatsApp message to StandardMessage format.
        
        Args:
            message: WhatsApp message data
            contact_info: Contact information
            
        Returns:
            StandardMessage object or None if conversion fails
        """
        try:
            message_id = message.get('id', str(uuid.uuid4()))
            sender_id = message.get('from')
            timestamp_str = message.get('timestamp')
            
            if not sender_id or not timestamp_str:
                logger.error(f"Missing required fields in WhatsApp message: {message}")
                return None
            
            # Convert timestamp to float
            timestamp = int(timestamp_str) / 1000.0  # Convert milliseconds to seconds
            
            # Extract message content based on type
            message_type = message.get('type', 'text')
            content = ""
            media_url = None
            
            if message_type == 'text':
                content = message.get('text', {}).get('body', '')
            elif message_type in ['image', 'video', 'audio', 'document']:
                # For media messages, extract media information
                media_data = message.get(message_type, {})
                
                # Prefer URL from message if already fetched, otherwise use ID
                media_url = media_data.get('url')
                if not media_url:
                    media_id = media_data.get('id')
                    if media_id:
                        # Try to get the URL on-demand if not already fetched
                        media_url = self.get_media_url_from_whatsapp(media_id)
                
                caption = message.get('caption', '')
                content = caption or f"{message_type} message"
            
            # Create metadata
            metadata = {
                'contact_name': contact_info.get('name'),
                'message_type': message_type,
                'whatsapp_message_id': message_id,
            }
            
            # For media messages, add media details
            if message_type in ['image', 'video', 'audio', 'document']:
                media_data = message.get(message_type, {})
                metadata['media'] = {
                    'mime_type': media_data.get('mime_type'),
                    'sha256': media_data.get('sha256'),
                    'id': media_data.get('id')
                }
                
                # Add any additional media metadata from previous processing
                if 'metadata' in message and 'media_file_id' in message['metadata']:
                    metadata['media']['file_id'] = message['metadata']['media_file_id']
            
            # Check if this is a chatbot message
            if 'metadata' in message and message['metadata'].get('is_chatbot_message'):
                metadata['is_chatbot_message'] = True
            
            # Create StandardMessage
            return StandardMessage(
                source='whatsapp',
                source_uid=sender_id,
                source_address=sender_id,
                message_id=message_id,
                source_timestamp=timestamp,
                content=content,
                platform='whatsapp',
                content_type=self._get_content_type(message_type),
                media_url=media_url,
                metadata=metadata
            )
        
        except Exception as e:
            logger.error(f"Error converting WhatsApp message to StandardMessage: {str(e)}")
            return None
    
    def _get_content_type(self, message_type: str) -> str:
        """
        Map WhatsApp message type to MIME content type.
        
        Args:
            message_type: WhatsApp message type
            
        Returns:
            MIME content type
        """
        content_type_map = {
            'text': 'text/plain',
            'image': 'image/jpeg',
            'video': 'video/mp4',
            'audio': 'audio/ogg',
            'document': 'application/pdf',
        }
        
        return content_type_map.get(message_type, 'text/plain')
    
    def should_handle_with_chatbot(self, message: Dict[str, Any]) -> bool:
        """
        Determine if a message should be handled by the chatbot.
        
        Args:
            message: The message to check
            
        Returns:
            True if chatbot should handle, False otherwise
        """
        # Get the sender ID and message content
        sender_id = message.get('from')
        
        # Get message content based on message type
        content = ""
        if message.get('type') == 'text':
            content = message.get('text', {}).get('body', '')
        
        # Check if message content is exactly "HEALTH"
        if content.strip().upper() == "HEALTH":
            self.chatbot.activate_session(sender_id)
            return True
        
        # Check if user is in an active chatbot session
        if self.chatbot.is_active_session(sender_id):
            return True
        
        return False
    
    def process_webhook_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single WhatsApp message and determine routing.
        
        Args:
            message: The message to process
            
        Returns:
            Processing result
        """
        try:
            # Extract message information
            sender_id = message.get('from')
            message_id = message.get('id')
            message_type = message.get('type', 'text')
            text_content = ""
            
            if message_type == 'text':
                text_content = message.get('text', {}).get('body', '')
            elif message_type in ['image', 'video', 'audio', 'document']:
                text_content = message.get('caption', '')
            
            # Get or create conversation
            conversation, created = Conversation.objects.get_or_create(
                sender_id=sender_id,
                platform='whatsapp',
                defaults={
                    'conversation_id': f"whatsapp-{sender_id}",
                    'is_active': True
                }
            )
            
            # Check if this message should be handled by the chatbot
            if self.should_handle_with_chatbot(message):
                return self._process_chatbot_message(sender_id, text_content, message_id, conversation)
            else:
                # Process with standard flow - convert to StandardMessage and route to endpoints
                return self._process_standard_message(message, conversation)
        
        except Exception as e:
            logger.exception(f"Error processing webhook message: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _process_chatbot_message(self, sender_id: str, message_text: str, message_id: str, conversation) -> Dict[str, Any]:
        """
        Process a message with the maternal health chatbot.
        
        Args:
            sender_id: WhatsApp ID of the sender
            message_text: Message text
            message_id: Message ID
            conversation: Conversation object
            
        Returns:
            Processing result
        """
        try:
            # Get response from chatbot
            response_text = self.chatbot.process_message(sender_id, message_text)
            
            # If message is "EXIT", deactivate the session
            if message_text.strip().upper() == "EXIT":
                self.chatbot.deactivate_session(sender_id)
            
            # Send response to user
            response_data = self.send_message(sender_id, {
                'message_type': 'text',
                'content': response_text
            })
            
            # Record outgoing message
            if response_data.get('status') == 'success':
                # Create webhook message record
                outgoing_message = WebhookMessage.objects.create(
                    message_id=response_data.get('message_id', f"response-{message_id}"),
                    conversation=conversation,
                    sender_id='system',
                    platform='whatsapp',
                    content=response_text,
                    message_type='text'
                )
            
            return {
                'status': 'success',
                'message_id': message_id,
                'sender_id': sender_id,
                'response_text': response_text,
                'chatbot_handled': True
            }
        
        except Exception as e:
            logger.exception(f"Error processing chatbot message: {str(e)}")
            return {
                'status': 'error',
                'sender_id': sender_id,
                'error': str(e)
            }
    
    def _process_standard_message(self, message: Dict[str, Any], conversation) -> Dict[str, Any]:
        """
        Process a standard (non-chatbot) message.
        
        Args:
            message: Message data
            conversation: Conversation object
            
        Returns:
            Processing result
        """
        # Standard message processing - your existing implementation
        return {
            'status': 'success',
            'message_id': message.get('id'),
            'sender_id': message.get('from'),
            'chatbot_handled': False
        }
    
    def send_message(self, recipient_id: str, message_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to a recipient on WhatsApp.
        
        Args:
            recipient_id: WhatsApp ID of the recipient
            message_content: Content to send
            
        Returns:
            Response data from WhatsApp API
        """
        try:
            # Get configuration
            phone_number_id = self.config.get('phone_number_id')
            
            # Get access token using TokenManager
            api_token = TokenManager.get_access_token()
            
            if not phone_number_id or not api_token:
                logger.error("Missing WhatsApp API configuration")
                return {
                    'status': 'error',
                    'error': 'Missing WhatsApp API configuration'
                }
            
            # Prepare API URL
            url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
            
            # Prepare headers
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            # Extract content details
            message_type = message_content.get('message_type', 'text')
            content = message_content.get('content', '')
            caption = message_content.get('caption')
            media_url = message_content.get('media_url')
            
            # Prepare request body
            request_body = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient_id,
                "type": message_type
            }
            
            # Add content based on message type
            if message_type == 'text':
                request_body['text'] = {
                    "body": content
                }
            elif message_type in ['image', 'video', 'audio', 'document']:
                if not media_url:
                    return {
                        'status': 'error',
                        'error': f'Media URL is required for {message_type} messages'
                    }
                
                request_body[message_type] = {
                    "link": media_url
                }
                
                if caption:
                    request_body[message_type]['caption'] = caption
            
            # Make API request
            logger.info(f"Sending WhatsApp message to {recipient_id}")
            response = requests.post(url, json=request_body, headers=headers)
            
            # Check response
            if response.status_code == 200:
                response_data = response.json()
                
                # Create a Contact (recipient) if doesn't exist
                contact, _ = Contact.objects.get_or_create(
                    wa_id=recipient_id,
                    defaults={'name': 'Unknown'}
                )
                
                # Create WhatsAppMedia if this is a media message
                media = None
                if message_type in ['image', 'video', 'audio', 'document'] and media_url:
                    media = WhatsAppMedia.objects.create(
                        media_type=message_type,
                        media_url=media_url,
                        media_mime_type=self._get_content_type(message_type)
                    )
                
                # Create WhatsAppMessage record
                whatsapp_message = WhatsAppMessage.objects.create(
                    sender=None,  # Outgoing message (from us)
                    recipient=contact,
                    message_type=message_type,
                    content=content,
                    caption=caption,
                    media=media,
                    status="sent"
                )
                
                return {
                    'status': 'success',
                    'message_id': response_data.get('messages', [{}])[0].get('id'),
                    'whatsapp_message_id': whatsapp_message.id
                }
            else:
                logger.error(f"WhatsApp API error: {response.status_code} - {response.text}")
                return {
                    'status': 'error',
                    'error': f"WhatsApp API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def format_webhook_response(self, responses: List[Dict[str, Any]]) -> HttpResponse:
        """
        Format response to return to WhatsApp webhook.
        
        Args:
            responses: List of processed message responses
            
        Returns:
            HTTP 200 OK response (WhatsApp expects a 200 response)
        """
        # WhatsApp expects a 200 OK response for webhooks
        return HttpResponse(status=200)
    
    def generate_token(self, short_lived_token: str, org_id: str) -> Dict[str, Any]:
        """
        Generate a long-lived token from a short-lived token.
        
        Args:
            short_lived_token: The short-lived access token
            org_id: Organization ID
            
        Returns:
            Dictionary with token information
        """
        return TokenManager.refresh_access_token(org_id, short_lived_token)
        
    def process_incoming_message(self, request: Any) -> List[Dict[str, Any]]:
        """
        Process incoming WhatsApp messages and route appropriately.
        
        This method:
        1. Parses incoming webhook data
        2. Identifies if messages should be handled by chatbot
        3. Routes each message to chatbot or standard flow
        4. Returns processing results
        
        Args:
            request: The incoming webhook request
            
        Returns:
            List of processing results for each message
        """
        # Parse the request
        if isinstance(request, HttpRequest):
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from WhatsApp webhook")
                return []
        else:
            data = request
            
        results = []
        
        # Extract messages from webhook data
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                
                # Process messages
                messages = value.get('messages', [])
                contacts = value.get('contacts', [])
                
                # Extract contact information
                contact_info = {}
                if contacts and len(contacts) > 0:
                    contact = contacts[0]
                    profile = contact.get('profile', {})
                    contact_info = {
                        'name': profile.get('name'),
                        'wa_id': contact.get('wa_id')
                    }
                
                # Process each message
                for message in messages:
                    sender_id = message.get('from')
                    
                    # Get or create conversation
                    conversation, created = Conversation.objects.get_or_create(
                        sender_id=sender_id,
                        platform='whatsapp',
                        defaults={
                            'conversation_id': f"whatsapp-{sender_id}",
                            'is_active': True
                        }
                    )
                    
                    # Record incoming message
                    message_type = message.get('type', 'text')
                    text_content = ""
                    
                    if message_type == 'text':
                        text_content = message.get('text', {}).get('body', '')
                    
                    # Create webhook message record for incoming message
                    webhook_message = WebhookMessage.objects.create(
                        message_id=message.get('id', str(uuid.uuid4())),
                        conversation=conversation,
                        sender_id=sender_id,
                        platform='whatsapp',
                        content=text_content,
                        message_type=message_type
                    )
                    
                    # Check if this message should be handled by the chatbot
                    if message_type == 'text' and (text_content.strip().upper() == "HEALTH" or self.chatbot.is_active_session(sender_id)):
                        # Process with chatbot
                        result = self._process_chatbot_message(sender_id, text_content, message.get('id'), conversation)
                    else:
                        # Process with standard flow
                        standard_message = self._convert_to_standard_message(message, contact_info)
                        if standard_message:
                            result = {
                                'status': 'success',
                                'message': standard_message.to_dict(),
                                'chatbot_handled': False
                            }
                        else:
                            result = {
                                'status': 'error',
                                'error': 'Failed to convert to standard message',
                                'chatbot_handled': False
                            }
                    
                    results.append(result)
        
        return results

    def to_standard_message(self, message_data: Dict[str, Any]) -> StandardMessage:
            """
            Convert WhatsApp message data to StandardMessage format.
            This method handles both raw WhatsApp message data and data that's already in StandardMessage format.
            
            Args:
                message_data: WhatsApp message data or StandardMessage dict
                
            Returns:
                StandardMessage instance (never returns None)
            """
            try:
                # Check if this looks like a StandardMessage already
                if all(key in message_data for key in ['source', 'source_uid', 'message_id', 'content', 'platform']):
                    logger.info("Message appears to be in StandardMessage format already")
                    
                    # If it's already a StandardMessage object, return it
                    if isinstance(message_data, StandardMessage):
                        return message_data
                        
                    # If it's a dict representation of StandardMessage, create a new StandardMessage from it
                    return StandardMessage(
                        source=message_data.get('source', 'whatsapp'),
                        source_uid=message_data.get('source_uid', ''),
                        source_address=message_data.get('source_address', ''),
                        message_id=message_data.get('message_id', ''),
                        source_timestamp=float(message_data.get('source_timestamp', 0)),
                        content=message_data.get('content', ''),
                        platform=message_data.get('platform', 'whatsapp'),
                        content_type=message_data.get('content_type', 'text/plain'),
                        media_url=message_data.get('media_url'),
                        metadata=message_data.get('metadata', {})
                    )
                    
                # This appears to be a raw WhatsApp message
                # Extract information for contact_info
                contact_info = {}
                if 'contact_name' in message_data:
                    contact_info['name'] = message_data['contact_name']
                    
                # Try to use the existing conversion method
                standard_message = self._convert_to_standard_message(message_data, contact_info)
                if standard_message:
                    return standard_message
                    
                # If conversion failed, create a basic StandardMessage as fallback
                logger.warning(f"Conversion to StandardMessage failed, creating fallback for message: {message_data}")
                
                # Extract basic information, handling common WhatsApp formats
                message_id = message_data.get('id', str(uuid.uuid4()))
                
                # Get sender ID (could be in 'from' for WhatsApp or elsewhere)
                sender_id = message_data.get('from', message_data.get('sender_id', ''))
                
                # Get timestamp, handle different formats
                timestamp = time.time()  # Default to current time if not found
                if 'timestamp' in message_data:
                    try:
                        timestamp = float(message_data['timestamp'])
                    except (ValueError, TypeError):
                        pass
                    
                # Get content, handling different message formats
                content = ''
                if 'text' in message_data and isinstance(message_data['text'], dict):
                    content = message_data['text'].get('body', '')
                elif 'content' in message_data:
                    content = message_data['content']
                elif 'body' in message_data:
                    content = message_data['body']
                    
                # Create a minimal but valid StandardMessage
                return StandardMessage(
                    source='whatsapp',
                    source_uid=sender_id,
                    source_address=sender_id,
                    message_id=message_id,
                    source_timestamp=timestamp,
                    content=content,
                    platform='whatsapp',
                    content_type='text/plain',
                    media_url=None,
                    metadata={'raw_message': str(message_data)[:500]}  # Store truncated raw message for debugging
                )
                
            except Exception as e:
                logger.exception(f"Error in to_standard_message: {str(e)}")
                # Always return a valid StandardMessage, never None
                return StandardMessage(
                    source='whatsapp',
                    source_uid='error',
                    source_address='error',
                    message_id=str(uuid.uuid4()),
                    source_timestamp=time.time(),
                    content='Error processing message',
                    platform='whatsapp',
                    metadata={'error': str(e)}
                )

        # Additional method to integrate with UnifiedWebhookView
    def handle_incoming_webhook(self, request: HttpRequest) -> HttpResponse:
            """
            Central handler for all incoming WhatsApp webhook requests,
            integrated with the chatbot functionality.
            
            Args:
                request: HTTP request object
            
            Returns:
                HTTP response to return to WhatsApp
            """
            try:
                # First, validate the request
                if not self.validate_request(request):
                    logger.error("Invalid WhatsApp webhook request")
                    return HttpResponse("Invalid request", status=400)
                
                # Process incoming messages
                results = self.process_incoming_message(request)
                
                # Return a 200 OK response (WhatsApp expects this)
                return HttpResponse(status=200)
                
            except Exception as e:
                logger.exception(f"Error handling WhatsApp webhook: {str(e)}")
                return HttpResponse("Error processing webhook", status=500)