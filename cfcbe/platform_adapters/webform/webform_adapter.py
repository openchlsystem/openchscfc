from typing import List, Dict, Any, Optional
from django.http import HttpRequest, HttpResponse, JsonResponse
import json
import uuid
import time
import logging

from platform_adapters.base_adapter import BaseAdapter
from shared.models.standard_message import StandardMessage


logger = logging.getLogger(__name__)

class WebformAdapter(BaseAdapter):
    """
    Adapter for handling webform submissions as a platform in the gateway.
    
    This adapter processes web form submissions and converts them to
    the standardized message format used by the gateway.
    """
    
    def handle_verification(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Handle platform verification challenges.
        
        Webforms don't typically need verification challenges,
        so this method returns None.
        
        Args:
            request: The incoming HTTP request
            
        Returns:
            None as webforms don't use verification challenges
        """
        return None
    
    def validate_request(self, request: Any) -> bool:
        """
        Validate the authenticity of the incoming request.
        
        For webforms, we trust the request as it comes through our server.
        Basic validation can be done to ensure required fields are present.
        
        Args:
            request: The request data
            
        Returns:
            True if request is valid, False otherwise
        """
        # For webforms, ensure required fields are present
        if isinstance(request, dict):
            # Check for complaint_text as a required field
            if 'complaint_text' not in request:
                logger.warning("Webform submission missing required field: complaint_text")
                return False
            return True
        return False
    
    def parse_messages(self, request: Any) -> List[Dict[str, Any]]:
        """
        Convert form data to a list of standardized messages.
        
        Args:
            request: Form submission data or HTTP request
            
        Returns:
            List containing one standardized message dict
        """
        # If request is a dictionary, it's already parsed form data
        if isinstance(request, dict):
            data = request
        # If request is an HttpRequest, try to parse the body
        elif isinstance(request, HttpRequest):
            try:
                if request.body:
                    data = json.loads(request.body)
                else:
                    data = request.POST.dict()
            except json.JSONDecodeError:
                data = request.POST.dict()
        else:
            # Fallback - try to convert to dict
            data = dict(request)
        
        # Create a StandardMessage from the form data
        standard_message = self._form_data_to_standard_message(data)
        
        # Return as a list of one message dict
        return [standard_message.to_dict()]
    
    def send_message(self, recipient_id: str, message_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to a webform user.
        
        For webforms, this might create a notification that
        the user can access when checking their submission status.
        
        Args:
            recipient_id: Typically the session_id
            message_content: Content to send
            
        Returns:
            Status of the notification creation
        """
        try:
            # For webforms, we create a notification
            # Note: This logic can be updated to fit how you want to notify users
            from webhook_handler.models import Notification, Complaint
            
            # Try to find the complaint associated with the session_id
            try:
                complaint = Complaint.objects.get(session_id=recipient_id)
                
                # Create a notification for the complaint
                notification = Notification.objects.create(
                    complaint=complaint,
                    message=message_content.get('content', 'Update on your complaint'),
                    is_read=False
                )
                
                return {
                    'status': 'success',
                    'notification_id': str(notification.notification_id),
                    'message': 'Notification created successfully'
                }
            except Complaint.DoesNotExist:
                return {
                    'status': 'error',
                    'error': f'No complaint found with session_id: {recipient_id}'
                }
            
        except Exception as e:
            logger.error(f"Error sending webform notification: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def format_webhook_response(self, responses: List[Dict[str, Any]]) -> HttpResponse:
        """
        Format response for a webform submission.
        
        Args:
            responses: List of processed message responses
            
        Returns:
            JSON response with status information
        """
        return JsonResponse({
            'status': 'success',
            'message': 'Form processed successfully',
            'responses': responses
        })
    
    def _form_data_to_standard_message(self, data: Dict[str, Any]) -> StandardMessage:
        """
        Convert form submission data to a StandardMessage.
        
        Args:
            data: Form submission data
            
        Returns:
            StandardMessage: The form data in standardized format
        """
        # Generate unique IDs if not provided
        message_id = data.get('submission_id', str(uuid.uuid4()))
        sender_id = data.get('session_id', str(uuid.uuid4()))
        
        # Extract content
        content = data.get('complaint_text', '')
        
        # Extract victim and perpetrator data
        victim_data = data.get('victim', {})
        perpetrator_data = data.get('perpetrator', {})
        
        # Build metadata
        metadata = {
            'reporter_nickname': data.get('reporter_nickname'),
            'case_category': data.get('case_category'),
            'case_category_id': data.get('case_category_id', '362484'),  # Default ID if not provided
            'victim': victim_data,
            'perpetrator': perpetrator_data,
            'has_image': bool(data.get('complaint_image')),
            'has_audio': bool(data.get('complaint_audio')),
            'has_video': bool(data.get('complaint_video')),
        }
        
        # Determine message type based on content
        message_type = 'complaint'
        if data.get('complaint_image'):
            message_type = 'complaint_with_image'
        elif data.get('complaint_audio'):
            message_type = 'complaint_with_audio'
        elif data.get('complaint_video'):
            message_type = 'complaint_with_video'
        
        # Get media URL if available
        media_url = None
        if data.get('complaint_image'):
            media_url = data.get('complaint_image')
        elif data.get('complaint_audio'):
            media_url = data.get('complaint_audio')
        elif data.get('complaint_video'):
            media_url = data.get('complaint_video')
        
        # Create StandardMessage
        return StandardMessage(
            message_id=message_id,
            sender_id=sender_id,
            platform='webform',
            content=content,
            timestamp=time.time(),
            message_type=message_type,
            media_url=media_url,
            metadata=metadata
        )
        
    def create_from_complaint(self, complaint) -> StandardMessage:
        from webhook_handler.models import Complaint
        """
        Create a StandardMessage from a Complaint model instance.
        
        Args:
            complaint: A Complaint model instance
            
        Returns:
            StandardMessage in the gateway's standard format
        """
        # Convert victim to dict if exists
        victim_data = {}
        if complaint.victim:
            victim_data = {
                'name': complaint.victim.name,
                'age': complaint.victim.age,
                'gender': complaint.victim.gender,
                'additional_info': complaint.victim.additional_info
            }
        
        # Convert perpetrator to dict if exists
        perpetrator_data = {}
        if complaint.perpetrator:
            perpetrator_data = {
                'name': complaint.perpetrator.name,
                'age': complaint.perpetrator.age,
                'gender': complaint.perpetrator.gender,
                'additional_info': complaint.perpetrator.additional_info if hasattr(complaint.perpetrator, 'additional_info') else None
            }
        
        # Build metadata with complaint-specific information
        metadata = {
            'complaint_id': str(complaint.complaint_id),
            'reporter_nickname': complaint.reporter_nickname,
            'case_category': complaint.case_category,
            'case_category_id': "362484",  # Default ID or map from category
            'victim': victim_data,
            'perpetrator': perpetrator_data,
            'has_image': bool(complaint.complaint_image),
            'has_audio': bool(complaint.complaint_audio),
            'has_video': bool(complaint.complaint_video),
        }
        
        # Determine MIME type based on content
        content_type = 'application/json'
        
        # Get media URL if available
        media_url = None
        if complaint.complaint_image:
            try:
                media_url = complaint.complaint_image.url
                content_type = 'image/jpeg'  # Adjust as needed based on image type
            except:
                pass
        elif complaint.complaint_audio:
            try:
                media_url = complaint.complaint_audio.url
                content_type = 'audio/mpeg'  # Adjust as needed based on audio type
            except:
                pass
        elif complaint.complaint_video:
            try:
                media_url = complaint.complaint_video.url
                content_type = 'video/mp4'  # Adjust as needed based on video type
            except:
                pass
        
        # Generate a unique session ID if not available
        session_id = str(complaint.session_id or uuid.uuid4())
        
        # Create StandardMessage aligned with endpoint formats
        return StandardMessage(
            source="walkin",                            # Will map to 'src' in cases endpoint
            source_uid=f"walkin-100-{int(time.time())}",  # Will map to 'src_uid'
            source_address=complaint.reporter_nickname or "",  # Will map to 'src_address'
            message_id=str(complaint.complaint_id),     # Will map to 'src_callid'
            source_timestamp=complaint.created_at.timestamp(),  # Will map to 'src_ts'
            content=complaint.complaint_text or "",     # Will map to 'narrative'
            content_type=content_type,                 # MIME type for the content
            platform="webform",                        # Internal platform identifier
            media_url=media_url,                       # URL to any media content
            metadata=metadata                          # Platform-specific data
        )