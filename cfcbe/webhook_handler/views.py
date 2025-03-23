import json
import logging
import uuid
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from platform_adapters.adapter_factory import AdapterFactory
from endpoint_integration.message_router import MessageRouter
from shared.models.standard_message import StandardMessage
from webhook_handler.services.conversation_service import ConversationService
from webhook_handler.models import (
    Contact, Person, Complaint, WhatsAppMessage, 
    WhatsAppMedia, Conversation, WebhookMessage,
    Organization, WhatsAppCredential, Notification
)

logger = logging.getLogger(__name__)
router = MessageRouter()

@method_decorator(csrf_exempt, name='dispatch')
class UnifiedWebhookView(View):
    """
    Unified view for handling webhooks from all platforms.
    
    This view processes all communication for all platforms:
    - Incoming messages (from platforms to the system)
    - Outgoing messages (from the system to platforms)
    - Verification challenges
    - Token management
    """
    
    def get(self, request, platform, *args, **kwargs):
        """
        Handle GET requests (typically verification challenges).
        
        Args:
            request: The HTTP request
            platform: Platform identifier from URL
            
        Returns:
            HTTP response
        """
        try:
            # Get the appropriate adapter for this platform
            adapter = AdapterFactory.get_adapter(platform)
            
            # Let the adapter handle verification
            response = adapter.handle_verification(request)
            if response:
                return response
                
            # If adapter didn't handle it, return a default response
            return HttpResponse("Verification not required or failed.")
            
        except ValueError as e:
            # Unsupported platform
            logger.error(f"Unsupported platform: {platform}")
            return HttpResponse(f"Unsupported platform: {platform}", status=404)
            
        except Exception as e:
            logger.exception(f"Error handling verification: {str(e)}")
            return HttpResponse("Verification failed", status=500)
    
    def post(self, request, platform, *args, **kwargs):
        """
        Handle POST requests (incoming and outgoing messages).
        
        This method now handles:
        1. Incoming messages from platforms
        2. Outgoing messages to platforms
        3. Token management operations
        
        Args:
            request: The HTTP request
            platform: Platform identifier from URL
            
        Returns:
            HTTP response
        """
        try:
            # Get the appropriate adapter for this platform
            adapter = AdapterFactory.get_adapter(platform)
            
            # Parse the request body
            try:
                payload = json.loads(request.body)
            except json.JSONDecodeError:
                # If the body isn't JSON, treat it as form data
                payload = request.POST.dict()
                
            # Determine the direction of the message flow
            direction = payload.get('direction', 'incoming')
            
            # Handle outgoing messages (system to platform)
            if direction == 'outgoing':
                return self._handle_outgoing_message(adapter, platform, payload, request)
                
            # Handle token operations
            elif direction == 'token':
                return self._handle_token_operation(adapter, platform, payload, request)
                
            # Handle incoming messages (platform to system)
            else:
                return self._handle_incoming_message(adapter, platform, payload, request)
                
        except ValueError as e:
            # Unsupported platform
            logger.error(f"Unsupported platform: {platform}")
            return HttpResponse(f"Unsupported platform: {platform}", status=404)
            
        except Exception as e:
            logger.exception(f"Error processing webhook: {str(e)}")
            return HttpResponse("Processing failed", status=500)
    
    def _handle_incoming_message(self, adapter, platform, payload, request):
        """
        Process incoming messages from a platform.
        
        Args:
            adapter: Platform adapter instance
            platform: Platform identifier
            payload: Request payload
            request: HTTP request
            
        Returns:
            HTTP response
        """
        # For webform, use the payload data directly
        if platform == 'webform':
            return self._handle_webform_submission(adapter, payload)
            
        # For other platforms, validate the request
        if not adapter.validate_request(request):
            return HttpResponse("Invalid request", status=400)
        
        # Parse messages from the request
        messages = adapter.parse_messages(request)
        
        # Process each message
        responses = []
        for message_dict in messages:
            # Convert to StandardMessage object
            std_message = StandardMessage.from_dict(message_dict)
            
            # Route to endpoint
            response = router.route_to_endpoint(std_message)
            responses.append(response)
        
        # Format the response according to platform requirements
        return adapter.format_webhook_response(responses)
    
    def _handle_outgoing_message(self, adapter, platform, payload, request):
        """
        Process outgoing messages to a platform.
        
        Args:
            adapter: Platform adapter instance
            platform: Platform identifier
            payload: Request payload
            request: HTTP request
            
        Returns:
            HTTP response
        """
        data = payload.get('data', {})
        
        if platform == 'whatsapp':
            # Required fields
            recipient = data.get('recipient')
            message_type = data.get('message_type', 'text')
            content = data.get('content', '')
            
            if not recipient:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Recipient is required'
                }, status=400)
            
            # Prepare message content
            message_content = {
                'message_type': message_type,
                'content': content,
                'caption': data.get('caption'),
                'media_url': data.get('media_url')
            }
            
            # Send the message
            response = adapter.send_message(recipient, message_content)
            
            # Return response
            if response.get('status') == 'success':
                return JsonResponse({
                    'status': 'success',
                    'message_id': response.get('message_id'),
                    'message': 'Message sent successfully'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': response.get('error', 'Failed to send message')
                }, status=400)
        
        # Return error for unsupported platforms
        return JsonResponse({
            'status': 'error',
            'message': f'Sending messages not supported for platform: {platform}'
        }, status=400)
    
    def _handle_token_operation(self, adapter, platform, payload, request):
        """
        Process token operations for a platform.
        
        Args:
            adapter: Platform adapter instance
            platform: Platform identifier
            payload: Request payload
            request: HTTP request
            
        Returns:
            HTTP response
        """
        data = payload.get('data', {})
        
        if platform == 'whatsapp':
            # Required fields
            short_lived_token = data.get('short_lived_token')
            org_id = data.get('org_id')
            
            if not short_lived_token:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Short-lived token is required'
                }, status=400)
            
            # Generate token
            if hasattr(adapter, 'generate_token'):
                response = adapter.generate_token(short_lived_token, org_id)
                
                # Return response
                if response.get('status') == 'success':
                    return JsonResponse({
                        'status': 'success',
                        'token': response.get('token'),
                        'expiry': response.get('expiry'),
                        'organization_id': response.get('organization_id')
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': response.get('error', 'Failed to generate token')
                    }, status=400)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Token operations not supported for platform: {platform}'
                }, status=400)
        
        # Return error for unsupported platforms
        return JsonResponse({
            'status': 'error',
            'message': f'Token operations not supported for platform: {platform}'
        }, status=400)
    
    def _handle_webform_submission(self, adapter, payload):
        try:
            # Extract data from payload
            data = payload.get('data', payload)
            
            # Import the ComplaintSerializer 
            from platform_adapters.webform.serializers import ComplaintSerializer
            
            # Generate a session ID if not provided or use complaint_id
            # session_id = data.get('complaint_id') or data.get('session_id') or str(uuid.uuid4())
            
            # # Get or create a conversation
            # conversation_service = ConversationService()
            # conversation = conversation_service.get_or_create_conversation(session_id, 'webform')
            
            # # Include the conversation in the data
            # data['conversation'] = conversation.id if conversation else None
            # data['session_id'] = session_id
            
            # Validate and create using the nested serializer
            complaint_serializer = ComplaintSerializer(data=data)
            if complaint_serializer.is_valid():
                complaint = complaint_serializer.save()
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid complaint data',
                    'errors': complaint_serializer.errors
                }, status=400)
            
            # Create a status for the complaint if needed
            # ComplaintStatus.objects.create(
            #     complaint=complaint, 
            #     status="New",
            #     updated_by="System"
            # )
            
            # Convert complaint to StandardMessage
            standard_message = adapter.create_from_complaint(complaint)
            
            # Route to endpoint
            response = router.route_to_endpoint(standard_message)
            
            # Update complaint with message_id_ref if available
            if response.get('status') == 'success' and response.get('message_id'):
                complaint.message_id_ref = response['message_id']
                complaint.save(update_fields=["message_id_ref"])
            
            # Create a notification
            notification = Notification.objects.create(
                complaint=complaint,
                message=f"Your complaint has been submitted successfully. Reference ID: {complaint.complaint_id}"
            )
            
            return JsonResponse({
                'status': 'success',
                'complaint_id': str(complaint.complaint_id),
                'message': 'Complaint submitted successfully',
                'notification_id': str(notification.notification_id)
            })
                
        except Exception as e:
            logger.exception(f"Error processing webform: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Processing failed',
                'error': str(e)
            }, status=500)