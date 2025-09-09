import logging
import json
import requests
import base64
import time
from typing import Dict, Any, Optional
from django.conf import settings
from shared.models.standard_message import StandardMessage
from webhook_handler.services.conversation_service import ConversationService

logger = logging.getLogger(__name__)

class MessageRouter:
    """
    Routes standardized messages to appropriate endpoints.
    
    This class is responsible for determining which endpoint to use
    and formatting messages according to endpoint requirements.
    """
    
    def __init__(self):
        """Initialize the MessageRouter."""
        self.conversation_service = ConversationService()
        self.endpoint_config = getattr(settings, 'ENDPOINT_CONFIG', {})
        
    def route_to_endpoint(self, message: StandardMessage) -> Dict[str, Any]:
        """
        Route a standardized message to an endpoint.
        
        Args:
            message: A StandardMessage instance
            
        Returns:
            Response data from the endpoint
        """
        # Choose endpoint based on platform
        endpoint = self._determine_endpoint(message)
        
        # Get or create a conversation for this message
        conversation = self.conversation_service.get_or_create_conversation(
            message.source_uid, message.platform
        )
        
        # Get endpoint configuration
        if endpoint not in self.endpoint_config:
            error_msg = f"Endpoint not configured: {endpoint}"
            logger.error(error_msg)
            return {'status': 'error', 'error': error_msg}
        
        config = self.endpoint_config[endpoint]
        
        # Format the message for the endpoint
        formatted_message = self._format_for_endpoint(message, conversation, config, endpoint)
        print(f"THIS IS THE PAYLOAD{formatted_message} THIS IS THE CONFIG{config}")
        # Send the formatted message to the endpoint
        response = self._send_to_endpoint(formatted_message, config)
        print(f"Response from endpoint: {response}")
        
        
        return response
    
    def _determine_endpoint(self, message: StandardMessage) -> str:
        """
        Determine which endpoint to use based on the platform.
        
        Args:
            message: A StandardMessage instance
            
        Returns:
            Endpoint identifier
        """
        # For webform, use the cases endpoint
        if message.platform == 'webform':
            return 'cases_endpoint'
            # Add specific routing for CEEMIS cases
        if message.platform == 'ceemis' and message.content_type == 'case/ceemis':
            return 'ceemis'
        # For all other platforms (WhatsApp, Messenger, etc.), use messaging endpoint
        return 'messaging_endpoint'
    
    def _format_for_endpoint(self, message: StandardMessage, conversation: Any, 
                            config: Dict[str, Any], endpoint: str) -> Dict[str, Any]:
        """
        Format the message according to endpoint requirements.
        
        Args:
            message: A StandardMessage instance
            conversation: The conversation object
            config: Endpoint configuration
            endpoint: The endpoint identifier
            
        Returns:
            Formatted message ready to send to the endpoint
        """
        if endpoint == 'cases_endpoint':
            return self._format_cases_endpoint(message, conversation, config)
        elif endpoint == 'messaging_endpoint':
            return self._format_messaging_endpoint(message, conversation, config)
        else:
            # Default formatter just passes through the message as a dict
            return message.to_dict()
    
    def _format_cases_endpoint(self, message: StandardMessage, conversation: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format message for the cases endpoint (used by webform).
        
        Args:
            message: A StandardMessage instance
            conversation: The conversation object
            config: Endpoint configuration
            
        Returns:
            Formatted message for the cases endpoint
        """
        # Extract metadata from the message
        metadata = message.metadata
        
        # Generate or use provided timestamp in Unix format with milliseconds
        source_timestamp = message.source_timestamp
        unix_timestamp = f"{source_timestamp:.3f}"
        
        # Use the source_uid from the message or generate one
        source_uid = message.source_uid
        if not source_uid.startswith('walkin-'):
            source_uid = f"walkin-100-{int(source_timestamp)}"
        
        # Create a deterministic uid2 based on source_uid
        source_uid2 = f"{source_uid}-2"
        
        # Extract victim and perpetrator data
        victim_data = metadata.get('victim', {})
        perpetrator_data = metadata.get('perpetrator', {})
        
        # Prepare client (victim) data
        # Ensure name is never empty - use "Anonymous" as fallback
        victim_name = victim_data.get('name', '')
        if not victim_name or victim_name.strip() == '':
            victim_name = "Anonymous Victim"
            
        client_data = {
            "fname": victim_name,
            "age_t": "0",
            "age": str(victim_data.get('age', '0')),  # Default to "0" if age is empty
            "dob": "",
            "age_group_id": "361953",
            "location_id": "258783",
            "sex_id": "",
            "landmark": "",
            "nationality_id": "",
            "national_id_type_id": "",
            "national_id": "",
            "lang_id": "",
            "tribe_id": "",
            "phone": "",
            "phone2": "",
            "email": "",
            ".id": "86164"
        }
        
        # Create gender mapping
        gender_mapping = {
            "male": "121",
            "female": "122",
        }
        
        # Prepare perpetrator data
        # Ensure perpetrator name is never empty - use "Unknown" as fallback
        perp_name = perpetrator_data.get('name', '')
        if not perp_name or perp_name.strip() == '':
            perp_name = "Unknown Perpetrator"
            
        perp_data = {
            "fname": perp_name,
            "age_t": "0",
            "age": str(perpetrator_data.get('age', '0')),  # Default to "0" if age is empty
            "dob": "",
            "age_group_id": "361955",
            "age_group": "31-45",
            "location_id": "",
            "sex_id": gender_mapping.get(perpetrator_data.get('gender', '').lower(), ""),
            "sex": f"^{perpetrator_data.get('gender', '').capitalize()}" if perpetrator_data.get('gender') else "",
            "landmark": "",
            "nationality_id": "",
            "national_id_type_id": "",
            "national_id": "",
            "lang_id": "",
            "tribe_id": "",
            "phone": "",
            "phone2": "",
            "email": "",
            "relationship_id": "",
            "shareshome_id": "",
            "health_id": "",
            "employment_id": "",
            "marital_id": "",
            "guardian_fullname": "",
            "notes": "",
            ".id": ""
        }

        # Ensure narrative is never empty
        narrative = message.content
        if not narrative or narrative.strip() == '':
            narrative = "No details provided"

        # Construct the cases endpoint payload matching the required format
        cases_payload = {
            "src": "webform",                     # Fixed source
            "src_uid": source_uid,               # Maps from message.source_uid (with prefix)
            "src_address": source_uid2 or "0101010101", # Maps from message.source_address
            "src_uid2": source_uid2,             # Derived from src_uid
            "src_usr": "100",                    # Default value
            "src_vector": "2",                   # Default value
            "src_callid": message.message_id,    # Maps from message.message_id
            "src_ts": unix_timestamp,            # Maps from message.source_timestamp
            
            "reporters_uuid": client_data,          # Using 'reporters_a' instead of 'reporter'
            
            "clients_case": [
                client_data
            ],
            
            "perpetrators_case": [
                perp_data
            ],
            
            "attachments_case": [],
            
            "services": [],
            
            "knowabout116_id": "",
            
            "case_category_id": metadata.get('case_category_id', "362484"),
            
            "narrative": narrative,              # Maps from message.content with fallback
            
            "plan": "---",
            
            "justice_id": "",
            
            "assessment_id": "",
            
            "priority": "1",
            
            "status": "1",
            
            "escalated_to_id": "0",
            
            "gbv_related": "0"                  # Added this field
        }
        
        return cases_payload
    
    def _format_messaging_endpoint(self, message: StandardMessage, conversation: Any, 
                                  config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format for the messaging endpoint (WhatsApp, Messenger, etc.).
        
        Args:
            message: A StandardMessage instance
            conversation: The conversation object
            config: Endpoint configuration
            
        Returns:
            Formatted message for the messaging endpoint
        """
        # Determine the channel from the source
        channel_mapping = {
            'whatsapp': 'whatsApp',  # Note the capitalization difference
            'messenger': 'messenger',
            'telegram': 'telegram',
            'sms': 'sms',
        }
        
        channel = channel_mapping.get(message.source.lower(), message.source.lower())
        
        # Encode the message content in Base64
        content_bytes = message.content.encode('utf-8')
        encoded_content = base64.b64encode(content_bytes).decode('utf-8')
        
        # Get ISO format timestamp
        iso_timestamp = message.get_iso_timestamp()
        
        # Construct the messaging endpoint payload directly mapping StandardMessage fields
        messaging_payload: Dict[str, Any] = {
            "channel": channel,                 # Maps from message.source
            "timestamp": iso_timestamp,         # Maps from message.source_timestamp
            "session_id": message.source_uid or "",   # Maps from message.source_uid (ensure not None)
            "message_id": message.message_id or "",   # Maps from message.message_id (ensure not None)
            "from": message.source_address or "",     # Maps from message.source_address (ensure not None)
            "message": encoded_content,         # Maps from message.content (encoded)
            "mime": message.content_type or ""  # Maps from message.content_type (ensure not None)
        }
        
        # Include media URL if available (for fallback)
        if message.media_url:
            messaging_payload["media_url"] = message.media_url
        
        # Include base64 encoded media content if available
        if message.media_content:
            messaging_payload["media_content"] = message.media_content
            messaging_payload["media_mime"] = message.media_mime or ""
            messaging_payload["media_filename"] = message.media_filename or ""
            messaging_payload["media_size"] = message.media_size or 0
            logger.info(f"📦 ENHANCED PAYLOAD - Added media content: {message.media_filename}, size: {message.media_size} bytes")
            logger.info(f"📊 Final payload keys: {list(messaging_payload.keys())}")
            
            # Log payload structure (without full base64 content)
            payload_preview = {k: v if k != 'media_content' else f"<base64_content_{len(v)}_chars>" 
                             for k, v in messaging_payload.items()}
            logger.info(f"📋 FINAL PAYLOAD PREVIEW: {json.dumps(payload_preview, indent=2)}")
        else:
            logger.info(f"📦 STANDARD PAYLOAD - No media content to add")
        
        return messaging_payload
    
    def _send_to_endpoint(self, formatted_message: Dict[str, Any], 
                     config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send the formatted message to the endpoint.
        
        Args:
            formatted_message: The message formatted for the endpoint
            config: Endpoint configuration
            
        Returns:
            Response data from the endpoint
        """
        url = config.get('url')
        auth_token = config.get('auth_token')
        
        if not url:
            error_msg = f"Endpoint URL not configured"
            logger.error(error_msg)
            return {'status': 'error', 'error': error_msg}
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        if auth_token:
            headers['Authorization'] = f"Bearer {auth_token}"
        
        try:
            logger.info(f"Sending to endpoint {url}: {json.dumps(formatted_message)}")
            
            # Handle SSL verification based on configuration
            disable_ssl = getattr(settings, 'DISABLE_SSL_VERIFICATION', False)
            verify_ssl = not disable_ssl
            
            if disable_ssl:
                logger.warning(f"SSL verification disabled by configuration for: {url}")
            
            response = requests.post(
                url, 
                headers=headers, 
                json=formatted_message,
                verify=verify_ssl
            )
            
            # Log the response for debugging
            logger.info(f"Endpoint response: {response.status_code}, {response.text}")
            logger.info(f"This is the header: {headers}")
            
            if response.status_code in (200, 201):
                # Parse response JSON
                try:
                    response_data = response.json()
                    
                    # Check if this is a case creation response (has cases array)
                    if 'cases' in response_data and len(response_data['cases']) > 0:
                        # Extract case ID from first case
                        case_id = response_data['cases'][0][0]  # Get "31661"
                        case_reference = f"lwf{case_id}"  # Create "lwf31661"
                        
                        logger.info(f"Case created successfully with ID: {case_id}, Reference: {case_reference}")
                        
                        return {
                            'status': 'success',
                            'case_id': case_id,
                            'case_reference': case_reference,
                            'message': 'Case submitted successfully',
                            'tracking_info': f'Use reference "{case_reference}" to track your case status',
                            'response': response_data
                        }
                    else:
                        # Regular response without cases
                        return {
                            'status': 'success',
                            'message_id': response_data.get('id'),  # Adjust based on API
                            'response': response_data
                        }
                except json.JSONDecodeError:
                    return {
                        'status': 'success',
                        'response_text': response.text
                    }
            else:
                return {
                    'status': 'error',
                    'http_status': response.status_code,
                    'error': response.text
                }
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Request to endpoint failed: {str(e)}"
            logger.error(error_msg)
            return {'status': 'error', 'error': error_msg}