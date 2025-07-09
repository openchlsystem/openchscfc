# platform_adapters/eemis/eemis_adapter.py

import json
import requests
import logging
from django.http import HttpResponse, JsonResponse
from platform_adapters.base_adapter import BaseAdapter
from typing import Dict, Any, List, Optional
from django.conf import settings

logger = logging.getLogger(__name__)
    
class EEMISAdapter(BaseAdapter):
    """
    Adapter for handling EEMIS (External Migrant Worker API) integration.
    
    This adapter:
    1. Receives helpline data with nationality_id
    2. Makes requests to the external EEMIS API
    3. Returns the EEMIS data as response
    """
    
    EEMIS_API_URL = "https://api.eemis.mglsd.go.ug/api/migrant-wokers/passports/"
    
    def handle_verification(self, request):
        """
        Handle verification challenges if any.
        For EEMIS, no verification is needed.
        """
        return None
    
    def validate_request(self, request) -> bool:
        """
        Validate the incoming request.
        
        Args:
            request: The Django request object
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Check if the body is parseable as JSON
            if request.method == 'POST':
                if hasattr(request, 'body') and request.body:
                    json.loads(request.body)
                return True
            return False
        except json.JSONDecodeError:
            logger.error("Invalid JSON in EEMIS request")
            return False
    
    def parse_messages(self, request) -> List[Dict[str, Any]]:
        """
        Extract message data from the request.
        
        Args:
            request: The Django request object
            
        Returns:
            List of parsed messages as dictionaries
        """
        try:
            # If request is already a dict, just return it as a list
            if isinstance(request, dict):
                return [request]
            
            # Otherwise, assume it's a Django request object
            if hasattr(request, 'method') and request.method == 'POST':
                # Parse the JSON body
                body = json.loads(request.body)
                return [body]  # Return as a list with single item
            
            return []
        except Exception as e:
            logger.error(f"Error parsing EEMIS request: {str(e)}")
            return []
        
    def send_message(self, recipient_id: str, message_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send message to EEMIS API.
        
        In this case, it makes a request to the EEMIS API with the nationality_id.
        
        Args:
            recipient_id: Not used in this context
            message_content: The message content containing nationality_id
            
        Returns:
            The response from the EEMIS API
        """
        try:
            # Extract national_id from the message content
            national_id = message_content.get('national_id', '')
            
            if not national_id:
                return {
                    'status': 'error',
                    'message': 'National ID is required',
                    'code': 400
                }
            
            # Make request to EEMIS API
            response = requests.get(
                f"{self.EEMIS_API_URL}{national_id}",
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                return {
                    'status': 'success',
                    'data': response.json(),
                    'code': 200
                }
            else:
                return {
                    'status': 'error',
                    'message': f'EEMIS API returned status code {response.status_code}',
                    'code': response.status_code
                }
                
        except Exception as e:
            logger.exception(f"Error sending request to EEMIS API: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error: {str(e)}',
                'code': 500
            }
    
    def _transform_response_data(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform the EEMIS API response to the required format.
        
        Args:
            response_data: The raw response from EEMIS API
            
        Returns:
            Transformed response data
        """
        try:
            # Extract the nested data
            if response_data.get('status') == 'success' and 'data' in response_data:
                nested_data = response_data['data'].get('data', {})
                
                # Map gender to sex_id (assuming M=121, F=120)
                gender = nested_data.get('gender', '')
                sex_id = "121" if gender == "M" else "120" if gender == "F" else ""
                
                # Transform to required format
                transformed_data = {
                    "fname": nested_data.get('first_name', ''),
                    "lname": nested_data.get('surname', ''),
                    "age_group_id": "",
                    "location_id": "",
                    "sex_id": sex_id,
                    "landmark": "",
                    "nationality_id": nested_data.get('nationality', ''),
                    "national_id_type_id": "",
                    "national_id": nested_data.get('passport_no', ''),
                    "lang_id": "",
                    "tribe_id": "",
                    "phone": nested_data.get('phone', ''),
                    "phone2": nested_data.get('home_phone', ''),
                    "email": nested_data.get('email', ''),
                }
                
                return transformed_data
            else:
                # Return error response as is
                return response_data
                
        except Exception as e:
            logger.exception(f"Error transforming EEMIS response: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error transforming response: {str(e)}',
                'code': 500
            }
    
    def format_webhook_response(self, responses: List[Dict[str, Any]]) -> HttpResponse:
        """
        Format response to return to the caller.
        
        Args:
            responses: List of processed message responses
            
        Returns:
            HttpResponse in the format expected by the helpline
        """
        if not responses:
            return JsonResponse(
                {'status': 'error', 'message': 'No valid response from EEMIS API'},
                status=500
            )
        
        response = responses[0]  # Get the first response
        
        # Transform the response data if successful
        if response.get('status') == 'success':
            transformed_data = self._transform_response_data(response)
            status_code = 200
        else:
            transformed_data = response
            status_code = response.get('code', 500)
        
        # Return the response data
        return JsonResponse(transformed_data, status=status_code)