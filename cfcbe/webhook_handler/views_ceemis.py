# webhook_handler/views_ceemis.py

import json
import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from platform_adapters.adapter_factory import AdapterFactory
from webhook_handler.models import Conversation, WebhookMessage
from dataclasses import dataclass
from typing import Dict, Any, Optional
import uuid
import time

logger = logging.getLogger(__name__)

@dataclass
class StandardMessage:
    """
    Standardized message format for CEEMIS communication.
    """
    source: str
    source_uid: str
    source_address: str
    message_id: str
    source_timestamp: float
    content: str
    platform: str
    content_type: str = "application/json"
    media_url: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the StandardMessage to a dictionary."""
        return {
            'source': self.source,
            'source_uid': self.source_uid,
            'source_address': self.source_address,
            'message_id': self.message_id,
            'source_timestamp': self.source_timestamp,
            'content': self.content,
            'content_type': self.content_type,
            'platform': self.platform,
            'media_url': self.media_url,
            'metadata': self.metadata
        }


@method_decorator(csrf_exempt, name='dispatch')
class CEEMISWebhookView(View):
    """
    View to handle CEEMIS webhook requests.
    
    This view:
    1. Receives requests from helpline with national_id
    2. Uses the CEEMISAdapter to fetch data from the external API
    3. Returns the response to the helpline
    """
    
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests from helpline.
        
        Args:
            request: The HTTP request object
            
        Returns:
            HTTP response containing operation result
        """
        try:
            # Get the CEEMIS adapter
            adapter = AdapterFactory.get_adapter('ceemis')
            
            # Validate the request
            if not adapter.validate_request(request):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid request format'
                }, status=400)
            
            # Parse the request body
            try:
                if request.body:
                    payload = json.loads(request.body)
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Request body is empty'
                    }, status=400)
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid JSON in request body'
                }, status=400)
                
            # Check if national_id is present
            if not payload.get('national_id'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'national_id is required'
                }, status=400)
            
            # Create a standard message
            src = payload.get('src', 'unknown')
            src_uid = payload.get('src_uid', str(uuid.uuid4()))
            
            message = StandardMessage(
                source=src,
                source_uid=src_uid,
                source_address=payload.get('src_address', ''),
                message_id=payload.get('src_callid', str(uuid.uuid4())),
                source_timestamp=float(payload.get('src_ts', time.time())),
                content=json.dumps(payload),
                platform='ceemis',
                metadata=payload
            )
            
            # Store conversation and message for audit
            try:
                # Get or create conversation
                conversation, created = Conversation.objects.get_or_create(
                    conversation_id=f"ceemis-{src_uid}",
                    defaults={
                        'sender_id': src_uid,
                        'platform': 'ceemis'
                    }
                )
                
                # Create webhook message record
                WebhookMessage.objects.create(
                    message_id=message.message_id,
                    conversation=conversation,
                    sender_id=src_uid,
                    platform='ceemis',
                    content=message.content,
                    message_type='json',
                    metadata=payload
                )
            except Exception as e:
                logger.exception(f"Error storing message: {str(e)}")
                # Continue processing even if storage fails
            
            # Send to CEEMIS API
            response = adapter.send_message('', payload)
            
            # Format and return the response
            return adapter.format_webhook_response([response])
            
        except Exception as e:
            logger.exception(f"Error processing CEEMIS webhook: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'An unexpected error occurred: {str(e)}'
            }, status=500)