from typing import List, Dict, Any, Optional
from django.http import HttpRequest, HttpResponse, JsonResponse
import json
import uuid
import time
import logging
import requests
import base64
from datetime import datetime, timezone, timedelta

from platform_adapters.base_adapter import BaseAdapter
from shared.models.standard_message import StandardMessage
from webhook_handler.models import (
    Contact, WhatsAppMedia, WhatsAppMessage, WhatsAppResponse,
     Organization, WhatsAppCredential
)
from django.conf import settings

logger = logging.getLogger(__name__)

class WhatsAppAdapter(BaseAdapter):
    """
    Adapter for handling WhatsApp messages as a platform in the gateway.
    
    This adapter processes WhatsApp webhook data and converts it to
    the standardized message format used by the gateway.
    """
    
    def __init__(self):
        """Initialize the WhatsApp Adapter."""
        self.config = self._get_config()
    
    def _get_config(self):
        """Get configuration from settings."""
        platform_configs = getattr(settings, 'PLATFORM_CONFIGS', {})
        return platform_configs.get('whatsapp', {})
    
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
                media_url = media_data.get('url') or media_data.get('id')
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
            api_token = self.config.get('api_token')
            
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
        try:
            # Get configuration
            client_id = self.config.get('client_id')
            client_secret = self.config.get('client_secret')
            
            if not client_id or not client_secret:
                logger.error("Missing WhatsApp API client configuration")
                return {
                    'status': 'error',
                    'error': 'Missing client configuration'
                }
            
            # Get or create the organization
            organization = None
            try:
                organization = Organization.objects.get(id=org_id)
            except Organization.DoesNotExist:
                # Create a dummy organization
                organization = Organization.objects.create(
                    id=org_id,
                    name=f"Organization {org_id}",
                    email=f"org{org_id}@example.com"
                )
            
            # Exchange token URL
            url = f"https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                "grant_type": "fb_exchange_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "fb_exchange_token": short_lived_token
            }
            
            # Make request
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                response_data = response.json()
                new_token = response_data.get('access_token')
                
                if new_token:
                    # Calculate expiry (60 days from now)
                    expiry = datetime.now(timezone.utc) + timedelta(days=60)
                    
                    # Save or update credentials
                    credentials, created = WhatsAppCredential.objects.update_or_create(
                        organization=organization,
                        defaults={
                            'access_token': new_token,
                            'token_expiry': expiry,
                            'client_id': client_id,
                            'client_secret': client_secret,
                            # These could be added to the payload if needed
                            'business_id': self.config.get('business_id', ''),
                            'phone_number_id': self.config.get('phone_number_id', '')
                        }
                    )
                    
                    return {
                        'status': 'success',
                        'token': new_token,
                        'expiry': expiry.isoformat(),
                        'organization_id': organization.id
                    }
                else:
                    return {
                        'status': 'error',
                        'error': 'No token in response'
                    }
            else:
                logger.error(f"Token exchange error: {response.status_code} - {response.text}")
                return {
                    'status': 'error',
                    'error': f"Token exchange error: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error generating token: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }