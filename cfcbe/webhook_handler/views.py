import json
import logging
import time
import uuid
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime
import logging
import requests
import csv
from django.http import JsonResponse, HttpResponse
from webhook_handler.token_manager import TokenManager
from platform_adapters.adapter_factory import AdapterFactory
from endpoint_integration.message_router import MessageRouter
from shared.models.standard_message import StandardMessage
from webhook_handler.services.conversation_service import ConversationService
from webhook_handler.models import (
    Contact, Person, Complaint, WhatsAppMessage, 
    WhatsAppMedia, Conversation, WebhookMessage,
    Organization, WhatsAppCredential, Notification
)
# from platform_adapters.whatsApp.chatbot_adapter import WhatsAppChatbotIntegration
# from platform_adapters.whatsApp.chatbot_adapter import WhatsAppChatbotIntegration
# With this:
from platform_adapters.whatsApp.chatbot_adapter import MaternalHealthChatbot

logger = logging.getLogger(__name__)
router = MessageRouter()
@method_decorator(csrf_exempt, name='dispatch')
class UnifiedWebhookView(View):
    """
    Central webhook handler for all communication platforms.
    
    This class processes incoming webhook requests from various platforms,
    routes them to appropriate handlers, and returns responses.
    
    Updated to integrate with the WhatsApp MaternalHealth chatbot based on "HEALTH" keyword.
    """
    
    def get(self, request, platform, *args, **kwargs):
        """
        Handles GET requests typically used for platform verification.
        Args:
            request: The HTTP request object
            platform: The platform identifier from the URL
        Returns:
            HTTP response, typically for verification challenges
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
        except Exception as e:
            logger.exception(f"Error handling verification: {str(e)}")
            return HttpResponse("Verification failed", status=500)
    
# Update your UnifiedWebhookView post method

    def post(self, request, platform, *args, **kwargs):
        """
        Handles POST requests for message exchange and token operations.
        """
        try:
            if platform == 'helpline' and 'case/ceemis' in request.path:
                return self._handle_helpline_ceemis_case(request)
            # Get the appropriate adapter for this platform
            adapter = AdapterFactory.get_adapter(platform)
            
            # Parse the request body
            try:
                payload = json.loads(request.body)
                # Log full raw payload for debugging
                logger.info(f"THIS IS THE PAYLOAD{payload}")
            except json.JSONDecodeError:
                # If the body isn't JSON, treat it as form data
                payload = request.POST.dict()
                
            # Special handling for WhatsApp platform
            # if platform == 'whatsapp':
            #     sender_id = None
            #     message_content = None
            #     message_id = None
                
            #     # Extract information from WhatsApp business format
            #     if 'entry' in payload and len(payload['entry']) > 0:
            #         for entry in payload['entry']:
            #             if 'changes' in entry and len(entry['changes']) > 0:
            #                 for change in entry['changes']:
            #                     if 'value' in change and 'messages' in change['value']:
            #                         messages = change['value']['messages']
            #                         if messages and len(messages) > 0:
            #                             message = messages[0]
                                        
            #                             # Extract sender ID and message ID
            #                             sender_id = message.get('from')
            #                             message_id = message.get('id')
                                        
            #                             # Check for text message
            #                             if message.get('type') == 'text' and 'text' in message:
            #                                 message_content = message['text'].get('body', '')
                
            #     # Or extract from simpler format
            #     if not sender_id and 'from' in payload:
            #         sender_id = payload.get('from')
                    
            #     if not message_id and 'message_id' in payload:
            #         message_id = payload.get('message_id')
                    
            #     if not message_content and 'message' in payload:
            #         message_content = payload.get('message')
                    
            #         # Try to decode base64 encoded message
            #         try:
            #             import base64
            #             # Add padding if needed
            #             padded = message_content + '=' * (4 - len(message_content) % 4) % 4
            #             decoded_bytes = base64.b64decode(padded)
            #             decoded_content = decoded_bytes.decode('utf-8')
            #             logger.info(f"Decoded base64 message: {message_content} -> {decoded_content}")
            #             message_content = decoded_content
            #         except Exception as e:
            #             # Not base64 encoded or other error
            #             logger.debug(f"Message not base64 encoded or error: {str(e)}")
                
            #     # Check if this is HEALTH message or user has active session
            #     is_health_message = message_content and message_content.strip().upper() == 'HEALTH'
                
            #     # Import the chatbot to check active sessions
            #     from platform_adapters.whatsApp.chatbot_adapter import MaternalHealthChatbot
            #     chatbot = MaternalHealthChatbot()
                
            #     has_active_session = sender_id and chatbot.is_active_session(sender_id)
                
            #     # Process with chatbot if HEALTH or active session
            #     if is_health_message or has_active_session:
            #         # Activate session if HEALTH message
            #         if is_health_message:
            #             chatbot.activate_session(sender_id)
                    
            #         logger.info(f"Processing message '{message_content}' from {sender_id} with chatbot")
                    
            #         # Get or create conversation
            #         conversation = ConversationService().get_or_create_conversation(
            #             sender_id, 'whatsapp'
            #         )
                    
            #         # Process with chatbot
            #         response_text = chatbot.process_message(sender_id, message_content)
                    
            #         # Send response back to user
            #         adapter.send_message(sender_id, {
            #             'message_type': 'text',
            #             'content': response_text
            #         })
                    
            #         # Return success
            #         return HttpResponse(status=200)
            
            # Regular webhook flow continues if not handled by chatbot
            direction = payload.get('direction', 'incoming')
            
            if direction == 'outgoing':
                return self._handle_outgoing_message(adapter, platform, payload, request)
            elif direction == 'token':
                return self._handle_token_operation(adapter, platform, payload, request)
            else:
                return self._handle_incoming_message(adapter, platform, payload, request)
                
        except Exception as e:
            logger.exception(f"Error processing webhook: {str(e)}")
            return HttpResponse("Processing failed", status=500)
    # webhook_handler/views.py (add PUT support to UnifiedWebhookView)

    
    def _handle_helpline_ceemis_case(self, request):
        """
        Handle a case creation from Helpline to be forwarded to CEEMIS.
        Args:
            request: The HTTP request object
        Returns:
            HTTP response containing operation result
        """
        try:
            # Get the CEEMIS adapter
            adapter = AdapterFactory.get_adapter('ceemis')
            
            # Parse the request body
            try:
                payload = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    "status": "error", 
                    "message": "Invalid JSON payload"
                }, status=400)
            
            # Validate the request
            if not adapter.validate_request(payload):
                return JsonResponse({
                    "status": "error", 
                    "message": "Invalid case data"
                }, status=400)
            
            # Parse the message
            messages = adapter.parse_messages(payload)
            if not messages:
                return JsonResponse({
                    "status": "error", 
                    "message": "Failed to parse case data"
                }, status=400)
            
            # Process each message (likely just one for a case)
            responses = []
            for msg_dict in messages:
                # Create StandardMessage object
                message = StandardMessage(**msg_dict)
                
                # Save to database if needed
                # self._save_message(message, request)
                
                # Send to CEEMIS
                response = adapter.send_message("ceemis", message.metadata)
                responses.append(response)
            
            # Format response
            return adapter.format_webhook_response(responses)
            
        except Exception as e:
            logger.exception(f"Error processing Helpline to CEEMIS case: {str(e)}")
            return JsonResponse({
                "status": "error",
                "message": f"Failed to process case: {str(e)}"
            }, status=500)
   
    def _check_for_chatbot_keywords(self, payload):
        """
        Examine the raw payload for chatbot trigger keywords or check if user is in active session.
        """
        try:
            sender_id = None
            message_content = None
            
            # Check for WhatsApp business format
            if 'entry' in payload and len(payload['entry']) > 0:
                for entry in payload['entry']:
                    if 'changes' in entry and len(entry['changes']) > 0:
                        for change in entry['changes']:
                            if 'value' in change and 'messages' in change['value']:
                                messages = change['value']['messages']
                                if messages and len(messages) > 0:
                                    message = messages[0]
                                    
                                    # Extract sender ID and message content
                                    sender_id = message.get('from')
                                    
                                    # Check for text message
                                    if message.get('type') == 'text' and 'text' in message:
                                        message_content = message['text'].get('body', '')
                                        
                                        # Check for HEALTH keyword directly
                                        if message_content.strip().upper() == 'HEALTH':
                                            logger.info(f"Found HEALTH keyword in raw payload from {sender_id}")
                                            return True, sender_id, message_content
                                            
                                        # Also check if SEVBTFRI is the encoded form of HEALTH
                                        if message_content.strip().upper() == 'SEVBTFRI':
                                            logger.info(f"Found SEVBTFRI (encoded HEALTH) in raw payload from {sender_id}")
                                            return True, sender_id, 'HEALTH'
            
            # Also check simpler format (might be after transformation)
            if not sender_id and 'from' in payload:
                sender_id = payload.get('from', '')
                
            if not message_content and 'message' in payload:
                message_content = payload.get('message', '')
                
                if message_content.strip().upper() == 'HEALTH':
                    return True, sender_id, message_content
                elif message_content.strip().upper() == 'SEVBTFRI':
                    return True, sender_id, 'HEALTH'
            
            # If we have a sender ID but no keyword match yet, check if user is in active session
            if sender_id:
                # Import chatbot here to avoid circular imports
                from platform_adapters.whatsApp.chatbot_adapter import MaternalHealthChatbot
                chatbot = MaternalHealthChatbot()
                
                # Check if user has an active chatbot session
                if chatbot.is_active_session(sender_id):
                    logger.info(f"User {sender_id} has active chatbot session")
                    return True, sender_id, message_content
            
            # No match found
            return False, None, None
        except Exception as e:
            logger.exception(f"Error checking for chatbot keywords: {str(e)}")
            return False, None, None
        
    def decode_message_if_needed(self, message: str) -> str:
        """
        Attempt to decode a message that might be encoded.
        
        Args:
            message: The message to decode
            
        Returns:
            The decoded message or the original if decoding fails
        """
        if not message:
            return message
            
        # Try to decode, handle common encoding methods
        try:
            # Check if it's base64 encoded
            import base64
            # Some implementations might pad or adjust base64, try a few variations
            padded_message = message + "=" * ((4 - len(message) % 4) % 4)
            decoded_bytes = base64.b64decode(padded_message)
            decoded = decoded_bytes.decode('utf-8')
            logger.info(f"Successfully decoded message: {message} -> {decoded}")
            return decoded
        except Exception:
            pass
            
        # Handle specific known encodings (like the one in your logs)
        # "SEVBTFRI" should decode to "HEALTH"
        if message == "SEVBTFRI":
            logger.info("Detected known encoded message 'SEVBTFRI', treating as 'HEALTH'")
            return "HEALTH"
            
        # Return original if decoding fails
        return message
# Then update the _handle_maternal_health_message method:
    def _handle_maternal_health_message(self, adapter, message_data, payload, request):
        """
        Handle message for the maternal health chatbot.
        
        Args:
            adapter: The platform adapter
            message_data: The parsed message data
            payload: The full request payload
            request: The HTTP request
            
        Returns:
            HTTP response
        """
        try:
            # Extract message information
            sender_id = message_data.get('from')
            message_id = message_data.get('id') 
            
            # Get message content based on message type
            text_content = ""
            if message_data.get('type') == 'text':
                text_content = message_data.get('text', {}).get('body', '')
            else:
                # For non-text messages, use caption if available
                text_content = message_data.get('caption', '')
            
            # Get or create conversation
            conversation = ConversationService().get_or_create_conversation(
                sender_id, 'whatsapp'
            )
            
            # Create webhook message record
            webhook_message = WebhookMessage.objects.create(
                message_id=message_id or str(uuid.uuid4()),
                conversation=conversation,
                sender_id=sender_id,
                platform='whatsapp',
                content=text_content,
                message_type='text',
                timestamp=timezone.now(),
                metadata={'chatbot_message': True}
            )

            # Process with MaternalHealthChatbot
            chatbot = MaternalHealthChatbot()
            
            # If this is a HEALTH message, activate a new session
            if text_content.strip().upper() == "HEALTH":
                chatbot.activate_session(sender_id)
                
            # Process the message and get response
            response_text = chatbot.process_message(sender_id, text_content)
            
            # Send response back to user
            response_data = adapter.send_message(sender_id, {
                'message_type': 'text',
                'content': response_text
            })
            
            # Record outgoing message
            if response_data.get('status') == 'success':
                outgoing_message = WebhookMessage.objects.create(
                    message_id=response_data.get('message_id', f"response-{message_id}"),
                    conversation=conversation,
                    sender_id='system',
                    platform='whatsapp',
                    content=response_text,
                    message_type='text',
                    timestamp=timezone.now(),
                    metadata={'chatbot_response': True}
                )
            
            # Format the webhook response
            return adapter.format_webhook_response([{
                'status': 'success',
                'message_id': message_id,
                'response': response_text
            }])
            
        except Exception as e:
            logger.exception(f"Error processing maternal health message: {str(e)}")
            return HttpResponse("Processing failed", status=500)

    
    def _handle_incoming_message(self, adapter, platform, payload, request):
        """
        Process incoming messages from platforms.
        
        Args:
            adapter: The platform adapter
            platform: The platform identifier
            payload: The request payload
            request: The HTTP request
            
        Returns:
            HTTP response
        """
        # For webform, use the payload data directly
        if platform == 'webform':
            return self._handle_webform_submission(adapter, payload)
            
        try:
            # Validate the request
            is_valid = adapter.validate_request(request)
            if not is_valid:
                return HttpResponse("Validation failed", status=403)
                
            # Parse messages from the platform-specific format
            messages = adapter.parse_messages(payload)
            
            responses = []
            for message_data in messages:
                # Convert to standard message format
                standard_message = adapter.to_standard_message(message_data)
                
                # Create a webhook message record
                conversation = ConversationService().get_or_create_conversation(
                    standard_message.source_uid, standard_message.platform
                )
                
                webhook_message = WebhookMessage.objects.create(
                    message_id=standard_message.message_id,
                    conversation=conversation,
                    sender_id=standard_message.source_uid,
                    platform=standard_message.platform,
                    content=standard_message.content,
                    media_url=standard_message.media_url,
                    message_type=standard_message.content_type,
                    timestamp=timezone.now(),
                    metadata=standard_message.metadata
                )
                
                # Route to endpoint
                endpoint_response = router.route_to_endpoint(standard_message)
                
                responses.append({
                    'webhook_message_id': str(webhook_message.id),
                    'response': endpoint_response
                })
            
            # Format the webhook response
            return adapter.format_webhook_response(responses)
            
        except Exception as e:
            logger.exception(f"Error processing incoming message: {str(e)}")
            return HttpResponse("Processing failed", status=500)
    
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
        Handle token operations for platform authentication.
        
        Args:
            adapter: The platform adapter
            platform: The platform identifier
            payload: The request payload
            request: The HTTP request
            
        Returns:
            HTTP response
        """
        try:
            # Extract operation and parameters
            operation = payload.get('operation')
            
            if operation == 'refresh':
                # Extract token info
                client_id = payload.get('client_id')
                client_secret = payload.get('client_secret')
                
                if not client_id or not client_secret:
                    return JsonResponse({
                        'status': 'error',
                        'error': 'Missing required fields: client_id or client_secret'
                    }, status=400)
                
                # Get platform adapter with token refresh support
                if hasattr(adapter, 'refresh_token'):
                    response = adapter.refresh_token(client_id, client_secret)
                    return JsonResponse(response)
                else:
                    return JsonResponse({
                        'status': 'error',
                        'error': f'Token operations not supported for {platform}'
                    }, status=400)
            else:
                return JsonResponse({
                    'status': 'error',
                    'error': f'Unsupported token operation: {operation}'
                }, status=400)
                
        except Exception as e:
            logger.exception(f"Error processing token operation: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'error': str(e)
            }, status=500)
    def _handle_webform_submission(self, adapter, payload, request=None):
        """
        Handle webform submissions.
        
        Args:
            adapter: The platform adapter
            platform: The platform identifier
            payload: The request payload
            request: The HTTP request
            
        Returns:
            HTTP response
        """
        try:
            # Extract data from payload
            data = payload.get('data', payload)  # Allow both nested and flat data
            
            # Add organization ID if available from token authentication
            if request and hasattr(request, 'organization_id'):
                data['organization_id'] = request.organization_id
                data['organization_name'] = request.organization_name
            
            # Import the ComplaintSerializer 
            from platform_adapters.webform.serializers import ComplaintSerializer
            
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
                'notification_id': str(notification.notification_id),
                'response_from_kim': response
            })
                
        except Exception as e:
            logger.exception(f"Error processing webform: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Processing failed',
                'error': str(e)
            }, status=500)
    
    def _get_categories_from_payload(self, adapter):
        """
        Extract categories from the payload.
        
        Args:
            payload: The request payload
        
        Returns:
            List of categories
        """
        # Assuming the payload contains a 'categories' field
        return payload.get('categories', [])

from django.http import JsonResponse
from django.views import View
import logging

logger = logging.getLogger(__name__)

class WebformCategoriesView(View):
    """
    View for retrieving categories and subcategories for the webform.
    """
    
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests for categories and subcategories.
        
        Args:
            request: The HTTP request, which may contain a category ID as a query parameter.

        Returns:
            JSON response with categories or subcategories.
        """
        try:
            # Get the webform adapter
            adapter = AdapterFactory.get_adapter('webform')

            # Get category ID from request parameters (if provided)
            category_id = request.GET.get('category_id')

            if category_id:
                try:
                    category_id = int(category_id)  # Ensure it's an integer
                except ValueError:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid category_id. It must be an integer.'
                    }, status=400)

                # Fetch subcategories for the given category_id
                response = adapter.get_subcategories(category_id)

                if response.get('status') == 'success':
                    return JsonResponse({
                        'status': 'success',
                        'category_id': category_id,
                        'subcategories': response.get('subcategories', [])
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': response.get('error', 'Failed to fetch subcategories')
                    }, status=400)
            
            # If no category_id is provided, return main categories
            response = adapter.get_categories()

            if response.get('status') == 'success':
                return JsonResponse({
                    'status': 'success',
                    'categories': response.get('categories', [])
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': response.get('error', 'Failed to fetch categories')
                }, status=400)

        except Exception as e:
            logger.error(f"Unexpected error in WebformCategoriesView: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Internal Server Error: {str(e)}'
            }, status=500)
from django.http import JsonResponse
from django.views import View
import logging


class TokenGenerationView(View):
    """
    View for generating authentication tokens for organizations.
    """
    
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for token generation.
        
        Args:
            request: The HTTP request
            
        Returns:
            JSON response with token
        """
        try:
            # Parse request body
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid JSON in request body.'
                }, status=400)
                
            # Extract organization name
            organization_name = data.get('organization_name')
            organization_email = data.get('organization_email')
            
            if not organization_name:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Organization name is required.'
                }, status=400)
                
            # Generate token
            token_data = TokenManager.generate_token(organization_name, organization_email)
            
            # Return token
            return JsonResponse({
                'status': 'success',
                'message': 'Authentication token generated successfully.',
                'token': token_data['token'],
                'organization_id': token_data['organization_id'],
                'expires': token_data['expires']
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error generating token: {str(e)}'
            }, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class HelplineCEEMISView(View):
    """
    Dedicated view for handling Helpline to CEEMIS case forwarding.
    """
    
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for Helpline case creation to be forwarded to CEEMIS.
        """
        try:
            # Get the CEEMIS adapter
            adapter = AdapterFactory.get_adapter('ceemis')
            
            # Parse the request body
            try:
                payload = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    "status": "error", 
                    "message": "Invalid JSON payload"
                }, status=400)
            
            # Validate the request
            if not adapter.validate_request(payload):
                return JsonResponse({
                    "status": "error", 
                    "message": "Invalid case data"
                }, status=400)

            # Parse the message
            messages = adapter.parse_messages(payload)
            print(f"THIS IS THE MESSAGE {messages}")
            
            if not messages:
                return JsonResponse({
                    "status": "error", 
                    "message": "Failed to parse case data"
                }, status=400)
            
            # Process each message (likely just one for a case)
            responses = []

            for msg_dict in messages:
                # Create StandardMessage object
                message = StandardMessage(**msg_dict)
                print(f"THIS IS THE MESSAGE in the for loop {message.metadata}")
                # Send to CEEMIS
                response = adapter.send_message("ceemis", message.metadata)
                print(f"THIS IS THE RESPONSE {response}")
                responses.append(response)
            
            # Format response
            return adapter.format_webhook_response(responses)
            
        except Exception as e:
            logger.exception(f"Error processing Helpline to CEEMIS case: {str(e)}")
            return JsonResponse({
                "status": "error",
                "message": f"Failed to process case: {str(e)}"
            }, status=500)
        # webhook_handler/views.py

class CEEMISHelplineView(View):
    """
    Dedicated view for handling CEEMIS case creation to be forwarded to Helpline.
    Receives form data from CEEMIS and converts it to Helpline format.
    """
    
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests from CEEMIS for case creation to be forwarded to Helpline.
        Expects multipart/form-data from CEEMIS.
        """
        try:
            # Get the CEEMIS adapter
            adapter = AdapterFactory.get_adapter('ceemis')
            
            # Parse the form data from CEEMIS
            ceemis_payload = {}
            
            # Extract form data
            for key, value in request.POST.items():
                ceemis_payload[key] = value
            
            logger.info(f"Received CEEMIS payload: {ceemis_payload}")
            
            # Validate the CEEMIS request
            if not adapter.validate_ceemis_request(ceemis_payload):
                return JsonResponse({
                    "status": "error", 
                    "message": "Invalid CEEMIS case data"
                }, status=400)

            # Convert CEEMIS data to Helpline format and send
            response = adapter.send_to_helpline(ceemis_payload)
            
            logger.info(f"Helpline response: {response}")
            
            # Return response to CEEMIS
            if response.get("status") == "success":
                return JsonResponse({
                    "status": "success",
                    "message": "Case successfully forwarded to Helpline",
                    "helpline_response": response
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "Failed to forward case to Helpline",
                    "details": response
                }, status=500)
            
        except Exception as e:
            logger.exception(f"Error processing CEEMIS to Helpline case: {str(e)}")
            return JsonResponse({
                "status": "error",
                "message": f"Failed to process case: {str(e)}"
            }, status=500)
@method_decorator(csrf_exempt, name='dispatch')
class HelplineCEEMISUpdateView(View):
    """
    Dedicated view for handling Helpline to CEEMIS case updates.
    Uses the sauti_case_update endpoint.
    """
# webhook_handler/views.py (add this PUT method to HelplineCEEMISUpdateView)

    # webhook_handler/views.py

    def put(self, request, *args, **kwargs):
        """
        Handle PUT requests for Helpline case updates to be forwarded to CEEMIS.
        """
        try:
            # Get the CEEMIS adapter
            adapter = AdapterFactory.get_adapter('ceemis')
            
            # Parse the request body
            try:
                payload = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    "status": "error", 
                    "message": "Invalid JSON payload"
                }, status=400)
            
            # Ensure the payload has a ref field for CEEMIS case ID
            if "ref" not in payload:
                return JsonResponse({
                    "status": "error", 
                    "message": "Missing ref field required for case update"
                }, status=400)
            
            # Validate the request
            if not adapter.validate_request(payload):
                return JsonResponse({
                    "status": "error", 
                    "message": "Invalid case update data"
                }, status=400)
            
            # Parse the message
            message_dicts = adapter.parse_messages(payload)
            if not message_dicts or len(message_dicts) == 0:
                return JsonResponse({
                    "status": "error", 
                    "message": "Failed to parse case update data"
                }, status=400)
            
            # Get the message dictionary (first one)
            message_dict = message_dicts[0]
            
            # Process the update - pass the dictionary directly
            response = adapter.send_message("ceemis", message_dict)
            
            # Log the response for debugging
            print(f"THIS IS THE RESPONSE {response}")
            
            # Format response
            return adapter.format_webhook_response([response])
                
        except Exception as e:
            logger.exception(f"Error processing Helpline to CEEMIS case update: {str(e)}")
            return JsonResponse({
                "status": "error",
                "message": f"Failed to process case update: {str(e)}"
            }, status=500)

        
# Assuming you have a logger set up
# logger = logging.getLogger(__name__)

# class LocationExportView(View):
#     """
#     View to export all locations in a hierarchical structure.
#     This endpoint provides a complete export of all locations in the system,
#     organized in their hierarchical structure.
    
#     Options:
#     - ?format=json (default) - Returns hierarchical JSON data
#     - ?format=csv - Returns flattened CSV data
#     - ?log_level=INFO (default) - Sets logging verbosity (DEBUG, INFO, WARNING, ERROR)
#     """

#     def get(self, request, *args, **kwargs):
#         try:
#             # Set logging level based on request parameter
#             log_level = request.GET.get('log_level', 'INFO').upper()
#             valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
            
#             if log_level in valid_levels:
#                 numeric_level = getattr(logging, log_level)
#                 logger.setLevel(numeric_level)
#                 logger.info(f"Log level set to {log_level}")
#             else:
#                 logger.setLevel(logging.INFO)
#                 logger.warning(f"Invalid log level: {log_level}. Using INFO.")
            
#             # Get the adapter from the factory
#             adapter = AdapterFactory.get_adapter('webform')
            
#             # Get the format parameter (default to 'json')
#             export_format = request.GET.get('format', 'json').lower()
            
#             # Log request details
#             logger.info(f"Location export requested with format: {export_format}")
            
#             # Export all locations
#             response_data = adapter.export_all_locations()
            
#             # Check if export was successful
#             if response_data.get('status') != 'success':
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': response_data.get('error', 'Failed to export locations')
#                 }, status=400)
            
#             # Handle different output formats
#             if export_format == 'csv':
#                 # Convert hierarchical data to flat structure for CSV
#                 flat_locations = self._flatten_location_hierarchy(response_data['location_hierarchy'])
                
#                 # Create CSV response
#                 response = HttpResponse(content_type='text/csv')
#                 response['Content-Disposition'] = 'attachment; filename="locations_export.csv"'
                
#                 writer = csv.writer(response)
#                 writer.writerow(['id', 'name', 'level', 'parent_id', 'full_path'])
                
#                 for location in flat_locations:
#                     writer.writerow([
#                         location['id'],
#                         location['name'],
#                         location['level'],
#                         location['parent_id'],
#                         location['full_path']
#                     ])
                
#                 return response
#             else:
#                 # Default to JSON response
#                 return JsonResponse(response_data)
                
#         except Exception as e:
#             logger.error(f"Error in LocationExportView: {str(e)}")
#             return JsonResponse({
#                 'status': 'error',
#                 'message': f"Internal server error: {str(e)}"
#             }, status=500)
    
#     def _flatten_location_hierarchy(self, locations, flat_list=None):
#         """
#         Convert the hierarchical location structure to a flat list.
        
#         Args:
#             locations: List of location dictionaries with nested children
#             flat_list: List to accumulate flattened locations
            
#         Returns:
#             list: Flat list of all locations
#         """
#         if flat_list is None:
#             flat_list = []
        
#         for location in locations:
#             # Create a copy without the children field
#             flat_location = {
#                 'id': location['id'],
#                 'name': location['name'],
#                 'level': location['level'],
#                 'parent_id': location['parent_id'],
#                 'full_path': location['full_path']
#             }
            
#             flat_list.append(flat_location)
            
#             # Process children recursively
#             if 'children' in location and location['children']:
#                 self._flatten_location_hierarchy(location['children'], flat_list)
        
#         return flat_list
    


# POST {{base_url}}/api/webhook/webform/auth/token/
# Content-Type: application/json

# {
#   "organization_name": "CPMIS System",
#   "organization_email": "admin@cpmis.org"
# }

# {
#   "status": "success",
#   "message": "Authentication token generated successfully.",
#   "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#   "organization_id": "12345",
#   "expires": "2026-04-03T11:09:50.554Z"
# }

# POST {{base_url}}/api/webhook/webform/
# Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
# Content-Type: application/json

# {
#   "reporter_nickname": "Anonymous",
#   "case_category": "HARASSMENT",
#   "complaint_text": "I would like to report a case of harassment...",
#   ...
# }

# class CaseCategoryExportView(View):
#     """
#     View to export all case categories in a hierarchical structure.
#     This endpoint provides a complete export of all case categories in the system,
#     organized in their hierarchical structure.
    
#     Options:
#     - ?format=json (default) - Returns hierarchical JSON data
#     - ?format=csv - Returns flattened CSV data
#     - ?log_level=INFO (default) - Sets logging verbosity (DEBUG, INFO, WARNING, ERROR)
#     """

#     def get(self, request, *args, **kwargs):
#         try:
#             # Set logging level based on request parameter
#             log_level = request.GET.get('log_level', 'INFO').upper()
#             valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
            
#             if log_level in valid_levels:
#                 numeric_level = getattr(logging, log_level)
#                 logger.setLevel(numeric_level)
#                 logger.info(f"Log level set to {log_level}")
#             else:
#                 logger.setLevel(logging.INFO)
#                 logger.warning(f"Invalid log level: {log_level}. Using INFO.")
            
#             # Get the adapter from the factory
#             adapter = AdapterFactory.get_adapter('webform')
            
#             # Get the format parameter (default to 'json')
#             export_format = request.GET.get('format', 'json').lower()
            
#             # Log request details
#             logger.info(f"Case category export requested with format: {export_format}")
            
#             # Export all case categories
#             response_data = adapter.export_case_categories()
            
#             # Check if export was successful
#             if response_data.get('status') != 'success':
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': response_data.get('error', 'Failed to export case categories')
#                 }, status=400)
            
#             # Handle different output formats
#             if export_format == 'csv':
#                 # Convert hierarchical data to flat structure for CSV
#                 flat_categories = self._flatten_category_hierarchy(response_data['category_hierarchy'])
                
#                 # Create CSV response
#                 response = HttpResponse(content_type='text/csv')
#                 response['Content-Disposition'] = 'attachment; filename="case_categories_export.csv"'
                
#                 writer = csv.writer(response)
#                 writer.writerow(['id', 'name', 'level', 'parent_id', 'full_path'])
                
#                 for category in flat_categories:
#                     writer.writerow([
#                         category['id'],
#                         category['name'],
#                         category['level'],
#                         category['parent_id'],
#                         category['full_path']
#                     ])
                
#                 return response
#             else:
#                 # Default to JSON response
#                 return JsonResponse(response_data)
                
#         except Exception as e:
#             logger.error(f"Error in CaseCategoryExportView: {str(e)}")
#             return JsonResponse({
#                 'status': 'error',
#                 'message': f"Internal server error: {str(e)}"
#             }, status=500)
    
#     def _flatten_category_hierarchy(self, categories, flat_list=None):
#         """
#         Convert the hierarchical category structure to a flat list.
        
#         Args:
#             categories: List of category dictionaries with nested children
#             flat_list: List to accumulate flattened categories
            
#         Returns:
#             list: Flat list of all categories
#         """
#         if flat_list is None:
#             flat_list = []
        
#         for category in categories:
#             # Create a copy without the children field
#             flat_category = {
#                 'id': category['id'],
#                 'name': category['name'],
#                 'level': category['level'],
#                 'parent_id': category['parent_id'],
#                 'full_path': category['full_path']
#             }
            
#             flat_list.append(flat_category)
            
#             # Process children recursively
#             if 'children' in category and category['children']:
#                 self._flatten_category_hierarchy(category['children'], flat_list)
        
#         return flat_list

# Add this to your urls.py


