# platform_adapters/mamacare/mamacare_adapter.py

import json
import requests
import logging
import uuid
import base64
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone

from platform_adapters.base_adapter import BaseAdapter
from platform_adapters.whatsApp.chatbot_adapter import MaternalHealthChatbot
from shared.models.standard_message import StandardMessage
from webhook_handler.models import (
    Conversation, WebhookMessage, Contact
)

logger = logging.getLogger(__name__)

class MamaCareAdapter(BaseAdapter):
    """
    Dedicated adapter for the MamaCare maternal health chatbot.
    
    This adapter handles WhatsApp messages for maternal health services,
    providing pregnancy information, health guidance, and support through
    a dedicated WhatsApp Business account.
    """
    
    def __init__(self):
        """Initialize the MamaCare adapter."""
        self.config = self._get_config()
        self.chatbot = MaternalHealthChatbot()
    
    def _get_config(self):
        """Get configuration from settings."""
        mamacare_config = getattr(settings, 'MAMACARE_CONFIG', {})
        if not mamacare_config:
            # Default configuration if not specified
            mamacare_config = {
                'phone_number_id': getattr(settings, 'MAMACARE_PHONE_NUMBER_ID', ''),
                'verify_token': getattr(settings, 'MAMACARE_VERIFY_TOKEN', ''),
                'access_token': getattr(settings, 'MAMACARE_ACCESS_TOKEN', '')
            }
        return mamacare_config
    
    def handle_verification(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Handle WhatsApp webhook verification challenge.
        
        Args:
            request: The HTTP request object
            
        Returns:
            HttpResponse with challenge if verification, None otherwise
        """
        hub_mode = request.GET.get("hub.mode")
        hub_challenge = request.GET.get("hub.challenge")
        hub_verify_token = request.GET.get("hub.verify_token")
        
        verify_token = self.config.get('verify_token')
        
        if hub_mode == "subscribe" and hub_verify_token == verify_token:
            logger.info("MamaCare webhook verification successful")
            return HttpResponse(hub_challenge, status=200)
        
        return None
    
    def validate_request(self, request: Any) -> bool:
        """
        Validate the authenticity of incoming WhatsApp webhook request.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            True if request is valid, False otherwise
        """
        if isinstance(request, HttpRequest):
            try:
                data = json.loads(request.body)
                
                # Check for basic WhatsApp webhook structure
                if 'object' in data and data['object'] == 'whatsapp_business_account':
                    if 'entry' in data and len(data['entry']) > 0:
                        return True
                
                logger.warning("MamaCare webhook validation failed: invalid structure")
                return False
            except json.JSONDecodeError:
                logger.warning("MamaCare webhook validation failed: invalid JSON")
                return False
        
        return False
    
    def parse_messages(self, payload: Any) -> List[Dict[str, Any]]:
        """
        Extract messages from WhatsApp webhook data.
        
        Args:
            payload: The webhook payload data
            
        Returns:
            List of parsed message dictionaries
        """
        messages_list = []
        logger.debug(f"Parsing MamaCare webhook payload: {payload}")
        
        try:
            # Extract messages from WhatsApp format
            if 'entry' in payload and len(payload['entry']) > 0:
                for entry in payload['entry']:
                    if 'changes' in entry and len(entry['changes']) > 0:
                        for change in entry['changes']:
                            if 'value' in change and 'messages' in change['value']:
                                messages = change['value']['messages']
                                contacts = change['value'].get('contacts', [])
                                
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
                                    # Extract message data
                                    message_id = message.get('id')
                                    sender_id = message.get('from')
                                    timestamp = message.get('timestamp')
                                    message_type = message.get('type')
                                    
                                    # Extract message content based on type
                                    content = ""
                                    media_url = None
                                    
                                    if message_type == 'text' and 'text' in message:
                                        content = message['text'].get('body', '')
                                    elif message_type in ['image', 'video', 'audio', 'document']:
                                        # For media messages
                                        media_data = message.get(message_type, {})
                                        media_id = media_data.get('id')
                                        if media_id:
                                            media_url = self._get_media_url(media_id)
                                        
                                        # Get caption if available
                                        content = message.get('caption', f"{message_type} message")
                                    
                                    # Create standard format dictionary
                                    message_dict = {
                                        'id': message_id,
                                        'from': sender_id,
                                        'timestamp': timestamp,
                                        'type': message_type,
                                        'text': {'body': content},
                                        'media_url': media_url,
                                        'contact_name': contact_info.get('name')
                                    }
                                    
                                    # Create or update contact record
                                    if sender_id and contact_info.get('name'):
                                        self._store_contact(sender_id, contact_info.get('name'))
                                    
                                    messages_list.append(message_dict)
            
            return messages_list
            
        except Exception as e:
            logger.exception(f"Error parsing MamaCare messages: {str(e)}")
            return []
    
    def _store_contact(self, wa_id: str, name: str) -> None:
        """
        Store or update contact information.
        
        Args:
            wa_id: WhatsApp ID
            name: Contact name
        """
        try:
            contact, created = Contact.objects.get_or_create(
                wa_id=wa_id,
                defaults={'name': name or 'Unknown'}
            )
            
            if not created and name and contact.name != name:
                contact.name = name
                contact.save(update_fields=['name'])
                
        except Exception as e:
            logger.error(f"Error storing contact: {str(e)}")
    
    def _get_media_url(self, media_id: str) -> Optional[str]:
        """
        Get media URL from WhatsApp.
        
        Args:
            media_id: Media ID from WhatsApp
            
        Returns:
            Media URL or None if failed
        """
        try:
            phone_number_id = self.config.get('phone_number_id')
            access_token = self.config.get('access_token')
            
            if not phone_number_id or not access_token:
                logger.error("Missing WhatsApp configuration for media")
                return None
            
            # Make API request to get media URL
            url = f"https://graph.facebook.com/v17.0/{media_id}"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                media_url = response.json().get('url')
                return media_url
            else:
                logger.error(f"Failed to get media URL: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting media URL: {str(e)}")
            return None
    
    def to_standard_message(self, message_data: Dict[str, Any]) -> StandardMessage:
        """
        Convert message data to StandardMessage format.
        
        Args:
            message_data: Message data dictionary
            
        Returns:
            StandardMessage instance
        """
        try:
            # Extract necessary fields
            message_id = message_data.get('id', str(uuid.uuid4()))
            sender_id = message_data.get('from', '')
            content = ''
            
            if 'text' in message_data and isinstance(message_data['text'], dict):
                content = message_data['text'].get('body', '')
            
            # Get timestamp or default to current time
            timestamp = int(message_data.get('timestamp', time.time()))
            
            # Create metadata
            metadata = {
                'contact_name': message_data.get('contact_name'),
                'message_type': message_data.get('type', 'text'),
                'platform': 'mamacare'
            }
            
            # Create StandardMessage
            return StandardMessage(
                source='mamacare',
                source_uid=sender_id,
                source_address=sender_id,
                message_id=message_id,
                source_timestamp=float(timestamp),
                content=content,
                platform='mamacare',
                content_type='text/plain',
                media_url=message_data.get('media_url'),
                metadata=metadata
            )
            
        except Exception as e:
            logger.exception(f"Error converting to StandardMessage: {str(e)}")
            # Return a minimal valid StandardMessage
            return StandardMessage(
                source='mamacare',
                source_uid='error',
                source_address='error',
                message_id=str(uuid.uuid4()),
                source_timestamp=time.time(),
                content='Error processing message',
                platform='mamacare',
                metadata={'error': str(e)}
            )
    
    def send_message(self, recipient_id: str, message_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to a recipient on WhatsApp.
        
        Args:
            recipient_id: WhatsApp ID of the recipient
            message_content: Content to send
            
        Returns:
            Response data
        """
        try:
            # Get configuration
            phone_number_id = self.config.get('phone_number_id')
            access_token = self.config.get('access_token')
            
            if not phone_number_id or not access_token:
                logger.error("Missing MamaCare WhatsApp API configuration")
                return {
                    'status': 'error',
                    'error': 'Missing WhatsApp API configuration'
                }
            
            # Prepare API URL
            url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
            
            # Prepare headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Extract content details
            if isinstance(message_content, dict):
                message_type = message_content.get('message_type', 'text')
                content = message_content.get('content', '')
                caption = message_content.get('caption')
                media_url = message_content.get('media_url')
            else:
                # If message_content is a string or other type, treat it as text content
                message_type = 'text'
                content = str(message_content)
                caption = None
                media_url = None
            
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
            logger.info(f"Sending MamaCare message to {recipient_id}")
            
            response = requests.post(url, json=request_body, headers=headers)
            
            # Check response
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"MamaCare message sent successfully: {response_data}")
                
                # Create message record
                try:
                    # Create a conversation if it doesn't exist
                    conversation, created = Conversation.objects.get_or_create(
                        sender_id=recipient_id,
                        platform='mamacare',
                        defaults={
                            'conversation_id': f"mamacare-{recipient_id}",
                            'is_active': True
                        }
                    )
                    
                    # Record outgoing message
                    message_id = response_data.get('messages', [{}])[0].get('id', f"msg-{uuid.uuid4()}")
                    
                    webhook_message = WebhookMessage.objects.create(
                        message_id=message_id,
                        conversation=conversation,
                        sender_id='system',
                        platform='mamacare',
                        content=content,
                        message_type=message_type,
                        timestamp=timezone.now(),
                        metadata={'direction': 'outgoing'}
                    )
                    
                except Exception as e:
                    logger.error(f"Error recording sent message: {str(e)}")
                
                return {
                    'status': 'success',
                    'message_id': response_data.get('messages', [{}])[0].get('id'),
                    'wam_id': response_data.get('messages', [{}])[0].get('id')
                }
            else:
                logger.error(f"Failed to send MamaCare message: {response.status_code} - {response.text}")
                return {
                    'status': 'error',
                    'error': f"API error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error sending MamaCare message: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def format_webhook_response(self, responses: List[Dict[str, Any]]) -> HttpResponse:
        """
        Format response to return to webhook.
        
        Args:
            responses: List of processed message responses
            
        Returns:
            HTTP response
        """
        # WhatsApp expects a 200 OK response for webhooks
        return HttpResponse(status=200)
    
    def process_webhook(self, request: HttpRequest) -> HttpResponse:
        """
        Process incoming webhook request and handle chatbot interaction.
        
        Args:
            request: HTTP request object
            
        Returns:
            HTTP response
        """
        try:
            # Validate the request
            if not self.validate_request(request):
                logger.error("Invalid MamaCare webhook request")
                return HttpResponse("Invalid request", status=400)
            
            # Parse the request body
            try:
                payload = json.loads(request.body)
                logger.info(f"MamaCare webhook payload: {payload}")
            except json.JSONDecodeError:
                logger.error("Invalid JSON in webhook request")
                return HttpResponse("Invalid JSON", status=400)
            
            # Parse messages from the payload
            messages = self.parse_messages(payload)
            
            if not messages:
                logger.info("No messages found in webhook payload")
                return HttpResponse(status=200)
            
            # Process each message with the chatbot
            for message in messages:
                # Extract message details
                sender_id = message.get('from')
                message_id = message.get('id')
                message_text = message.get('text', {}).get('body', '')
                
                # Get or create conversation
                conversation, created = Conversation.objects.get_or_create(
                    sender_id=sender_id,
                    platform='mamacare',
                    defaults={
                        'conversation_id': f"mamacare-{sender_id}",
                        'is_active': True
                    }
                )
                
                # Record incoming message
                webhook_message = WebhookMessage.objects.create(
                    message_id=message_id,
                    conversation=conversation,
                    sender_id=sender_id,
                    platform='mamacare',
                    content=message_text,
                    message_type='text',
                    timestamp=timezone.now(),
                    metadata={'direction': 'incoming'}
                )
                
                # Activate chatbot session with first message or for active users
                if message_text.strip().upper() == 'HEALTH':
                    self.chatbot.activate_session(sender_id)
                
                # Process with MamaCare chatbot
                if self.chatbot.is_active_session(sender_id) or message_text.strip().upper() == 'HEALTH':
                    response_text = self.chatbot.process_message(sender_id, message_text)
                    
                    # Send response back to user
                    self.send_message(sender_id, {
                        'message_type': 'text',
                        'content': response_text
                    })
                    
                # If message wasn't handled by chatbot, you could add alternate handling here
            
            # Return success response
            return HttpResponse(status=200)
            
        except Exception as e:
            logger.exception(f"Error processing MamaCare webhook: {str(e)}")
            return HttpResponse("Error processing webhook", status=500)