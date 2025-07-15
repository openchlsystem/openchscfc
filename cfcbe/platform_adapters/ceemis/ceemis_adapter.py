# platform_adapters/ceemis/ceemis_adapter.py

import json
import logging
import requests
from typing import Any, Dict, List, Optional
from django.http import HttpRequest, HttpResponse, JsonResponse

from platform_adapters.base_adapter import BaseAdapter


logger = logging.getLogger(__name__)

class CEEMISAdapter(BaseAdapter):
    """
    Adapter for the CEEMIS platform integration.
    
    This adapter:
    1. Handles case creation from Helpline
    2. Handles case updates from Helpline
    3. Formats data for CEEMIS API
    4. Sends data to the CEEMIS endpoints
    """
    
    def __init__(self):
        self.ceemis_create_endpoint = "http://ceemis.mglsd.go.ug:8080/api.ceemis/service/create/sauti_case"
        self.ceemis_update_endpoint = "http://ceemis.mglsd.go.ug:8080/api.ceemis/service/update/sauti_case_update"
    
    def handle_verification(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        CEEMIS doesn't require verification challenges.
        """
        return None
    
    def validate_request(self, request: Any) -> bool:
        """
        Validate authenticity of incoming Helpline request.
        Check for required fields based on whether it's an update or create operation.
        
        Args:
            request: The request data to validate
            
        Returns:
            True if the request is valid, False otherwise
        """
        try:
            if isinstance(request, dict):
                payload = request
            else:
                payload = json.loads(request.body)
            
            # Check if this is an update request (has ref) or create request
            if "ref" in payload:
                # Update operation
                required_fields = ["ref"]
                operation = "update"
            else:
                # Create operation
                required_fields = ["src", "src_uid", "src_callid", "narrative", "case_category"]
                operation = "create"
            
            # Validate required fields
            for field in required_fields:
                if field not in payload:
                    logger.error(f"Missing required field for {operation}: {field}")
                    return False
                    
            return True
            
        except (json.JSONDecodeError, AttributeError) as e:
            logger.error(f"Invalid request format: {str(e)}")
            return False
    
    def parse_messages(self, request: Any) -> List[Dict[str, Any]]:
        """
        Convert Helpline data to StandardMessage format.
        Determine operation type based on presence of ref.
        
        Args:
            request: The request data to parse
            
        Returns:
            List of StandardMessage dictionaries
        """
        try:
            if isinstance(request, dict):
                payload = request
            else:
                payload = json.loads(request.body)
            
            # Determine if this is an update or create operation
            content_type = "case/ceemis/update" if "ref" in payload else "case/ceemis/create"
            
            # Create a StandardMessage from the payload
            message = {
                "source": "helpline",
                "source_uid": payload.get("src_uid", ""),
                "source_address": payload.get("src_address", ""),
                "message_id": payload.get("src_callid", ""),
                "source_timestamp": float(payload.get("src_ts", 0)),
                "content": payload.get("narrative", ""),
                "platform": "ceemis",
                "content_type": content_type,
                "media_url": None,
                "metadata": payload  # Store the full payload as metadata for further processing
            }
            
            return [message]
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error parsing message: {str(e)}")
            return []
    
    def send_message(self, recipient_id: str, message_content: Any) -> Dict[str, Any]:
        """
        Send a message to CEEMIS.
        Determine whether to create or update based on the presence of ref.
        
        Args:
            recipient_id: Target platform identifier (always "ceemis")
            message_content: The message content (can be dict or StandardMessage)
            
        Returns:
            Response from CEEMIS
        """
        # Extract metadata based on message_content type
        if hasattr(message_content, 'metadata'):
            # It's a StandardMessage object
            metadata = message_content.metadata
        else:
            # It's a dictionary with a metadata field
            metadata = message_content.get("metadata", {})
            if not metadata:  # If metadata is empty, the dict itself might be the metadata
                metadata = message_content
        
        # Print the narrative for debugging
        narrative = metadata.get("narrative", "")
        print(f"Metadata: {narrative}")
        
        # Determine operation type based on presence of ref in metadata
        if "ref" in metadata:
            logger.info("Case update operation detected based on ref field")
            return self._update_case(metadata)
        else:
            logger.info("Case creation operation detected (no ref field)")
            return self._create_case(metadata)  # Pass metadata instead of message_content
    
    def _create_case(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new case in CEEMIS.
        
        Args:
            metadata: The metadata containing the case information
            
        Returns:
            Response from CEEMIS
        """
        try:
            # Map Helpline fields to CEEMIS fields
            ceemis_payload = self._map_to_ceemis_format(metadata)
        
            # Debug logging
            logger.debug(f"Creating case in CEEMIS: {self.ceemis_create_endpoint}")
            logger.debug(f"Payload: {ceemis_payload}")
            
            # Create a multipart form request
            files = {}
            for key, value in ceemis_payload.items():
                # Convert each field to a "file" with content type text/plain
                # This ensures proper multipart/form-data encoding
                files[key] = (None, str(value), 'text/plain')
            
            # Send to CEEMIS endpoint - explicitly as multipart/form-data
            response = requests.post(
                self.ceemis_create_endpoint,
                files=files  # This ensures multipart/form-data format
            )
            
            logger.debug(f"CEEMIS response status: {response.status_code}")
            logger.debug(f"CEEMIS response text: {response.text}")
            
            if response.status_code in (200, 201):
                try:
                    result = response.json()
                    return {
                        "status": "success",
                        "message": "Case successfully created in CEEMIS",
                        "ceemis_response": result
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "success",
                        "message": "Case created in CEEMIS",
                        "ceemis_response": response.text
                    }
            else:
                logger.error(f"CEEMIS API error: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "message": f"CEEMIS API error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.exception(f"Error creating case in CEEMIS: {str(e)}")
            return {
                "status": "error",
                "message": f"Error creating case in CEEMIS: {str(e)}"
            }
    
    def _update_case(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing case in CEEMIS.
        
        Args:
            metadata: The metadata containing the case information
            
        Returns:
            Response from CEEMIS
        """
        try:
            # Extract the CEEMIS case ID from the ref field
            ref = metadata.get("ref", "")
            ceemis_case_id = self._extract_ceemis_case_id(ref)
            
            # Add the extracted case ID to the metadata
            metadata_with_caseid = metadata.copy()
            metadata_with_caseid["caseid"] = ceemis_case_id
            
            # Map Helpline fields to CEEMIS update fields
            ceemis_payload = self._map_to_ceemis_update_format(metadata_with_caseid)
            
            # Debug logging
            logger.debug(f"Updating case in CEEMIS: {self.ceemis_update_endpoint}")
            logger.debug(f"CEEMIS Case ID: {ceemis_case_id}")
            logger.debug(f"Payload: {ceemis_payload}")
            
            # Create a multipart form request
            files = {}
            for key, value in ceemis_payload.items():
                # Convert each field to a "file" with content type text/plain
                # This ensures proper multipart/form-data encoding
                files[key] = (None, str(value), 'text/plain')
            
            # Send to CEEMIS endpoint - explicitly as multipart/form-data
            response = requests.post(
                self.ceemis_update_endpoint,
                files=files  # This ensures multipart/form-data format
            )
            
            logger.debug(f"CEEMIS response status: {response.status_code}")
            logger.debug(f"CEEMIS response text: {response.text}")
            
            if response.status_code in (200, 201):
                try:
                    result = response.json()
                    return {
                        "status": "success",
                        "message": "Case successfully updated in CEEMIS",
                        "ceemis_response": result
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "success",
                        "message": "Case updated in CEEMIS",
                        "ceemis_response": response.text
                    }
            else:
                logger.error(f"CEEMIS API error: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "message": f"CEEMIS API error: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.exception(f"Error updating case in CEEMIS: {str(e)}")
            return {
                "status": "error",
                "message": f"Error updating case in CEEMIS: {str(e)}"
            }
    
    def format_webhook_response(self, responses: List[Dict[str, Any]]) -> HttpResponse:
        """
        Format response to return to the Helpline webhook.
        """
        # Return the first response or a default response
        if responses:
            return JsonResponse(responses[0])
        else:
            return JsonResponse({"status": "error", "message": "No response from CEEMIS"})
    
    def _extract_ceemis_case_id(self, ref: str) -> str:
        """
        Extract the CEEMIS case ID from the reference string.
        
        Args:
            ref: Reference string that should contain the CEEMIS case ID
            
        Returns:
            CEEMIS case ID or empty string if not found
        """
        try:
            # If the ref is already in MGLSD format, just return it
            if ref.startswith("MGLSD"):
                return ref
                
            # Try to extract MGLSD case ID format (e.g., MGLSD7093227)
            import re
            match = re.search(r'MGLSD\d+', ref)
            if match:
                return match.group(0)
            
            # If the extraction didn't work, log and return the ref as is
            logger.warning(f"Could not extract CEEMIS case ID in MGLSD format from ref: {ref}")
            return ref
        except Exception as e:
            logger.error(f"Error extracting CEEMIS case ID: {str(e)}")
            return ref
    
    def _map_to_ceemis_create_format(self, helpline_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map Helpline data format to CEEMIS create format.
        This uses the original mapping function for case creation.
        """
        return self._map_to_ceemis_format(helpline_data)
    
    def _map_to_ceemis_format(self, helpline_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map Helpline data format to CEEMIS expected format.
        This is the original mapping function kept for backward compatibility.
        """
        # Extract client information (victim)
        client = {}
        if helpline_data.get("clients_case") and len(helpline_data["clients_case"]) > 0:
            client = helpline_data["clients_case"][0]
        
        # Extract perpetrator information
        perpetrator = {}
        if helpline_data.get("perpetrators_case") and len(helpline_data["perpetrators_case"]) > 0:
            perpetrator = helpline_data["perpetrators_case"][0]
    
        # Map fields from Helpline to CEEMIS format
        ceemis_data = {
            # Migrant worker information
            "mw_name": client.get("fname", ""),
            "mw_phone": client.get("phone", helpline_data.get("src_address", "")),
            "mw_email": client.get("email", ""),
            "mw_passport": client.get("national_id", ""),
            "mw_sys_id": helpline_data.get("session_id", ""),
            "mw_country": "Uganda",  # Default to Uganda
            "mw_city": "",
            
            # Employer information
            "emp_sector": "Unknown",  # Default value
            "emp_name": perpetrator.get("fname", "NA"),
            "emp_number": perpetrator.get("phone", "NA"),
            
            # Location information
            "location": "Uganda",  # Default to Uganda
            "mw_loca": "Unknown",  # Default value
            
            # Case information
            "comp_category": helpline_data.get("case_category", "COMPLAINT"),
            "mw_narative": helpline_data.get("narrative", "Case details"),
        }
        
        return ceemis_data
    
    def _map_to_ceemis_update_format(self, helpline_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map Helpline data format to CEEMIS sauti_case_update expected format.
        Uses caseid for the CEEMIS case identifier.
        """
        # Extract client information (victim) if available
        client = {}
        if helpline_data.get("clients_case") and len(helpline_data["clients_case"]) > 0:
            client = helpline_data["clients_case"][0]
        
        # Extract perpetrator information if available
        perpetrator = {}
        if helpline_data.get("perpetrators_case") and len(helpline_data["perpetrators_case"]) > 0:
            perpetrator = helpline_data["perpetrators_case"][0]
        
        # Map fields from Helpline to CEEMIS sauti_case_update format
        ceemis_data = {
            # Required fields for update - use caseid from helpline_data
            "caseid": helpline_data.get("caseid", ""),
            "status": helpline_data.get("status", "2"),  # Default to status 2
            
            # Migrant worker information
            "mw_name": client.get("fname", ""),
            "mw_phone": client.get("phone", helpline_data.get("src_address", "")),
            "mw_email": client.get("email", ""),
            "mw_passport": client.get("national_id", ""),
            "mw_sys_id": helpline_data.get("session_id", "NA"),
            "mw_country": "Uganda",
            "mw_city": "Kampala",
            
            # Employer information
            "emp_sector": "Housemaid",  # Default value
            "emp_name": perpetrator.get("fname", "NA"),
            "emp_number": perpetrator.get("phone", "NA"),
            
            # Location information
            "location": "Kampala",
            "mw_loca": "Kampala",
            
            # Case information
            "comp_category": helpline_data.get("case_category", "COMPLAINT"),
            "mw_narative": helpline_data.get("narrative", "Case update"),
        }
        
        # Log the update payload
        logger.info(f"Update payload for CEEMIS with caseid: {ceemis_data['caseid']}")
        
        return ceemis_data
    
    def validate_ceemis_request(self, payload: Dict[str, Any]) -> bool:
        """
        Validate incoming CEEMIS form data.
        
        Args:
            payload: The CEEMIS form data to validate
            
        Returns:
            True if the request is valid, False otherwise
        """
        try:
            # Required fields for CEEMIS case creation
            required_fields = ["mw_name", "mw_phone", "comp_category", "mw_narative"]
            
            # Validate required fields
            for field in required_fields:
                if field not in payload or not payload[field].strip():
                    logger.error(f"Missing or empty required field from CEEMIS: {field}")
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Error validating CEEMIS request: {str(e)}")
            return False
    
    def send_to_helpline(self, ceemis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send CEEMIS case data to Helpline API.
        Converts CEEMIS form data to Helpline JSON format.
        
        Args:
            ceemis_data: Form data received from CEEMIS
            
        Returns:
            Response from Helpline API
        """
        try:
            # Convert CEEMIS data to Helpline format
            helpline_payload = self._map_ceemis_to_helpline_format(ceemis_data)
            
            # Get auth token from config
            auth_token = getattr(settings, 'HELPLINE_AUTH_TOKEN', '')
            if not auth_token:
                logger.error("Helpline auth token not configured")
                return {
                    "status": "error",
                    "message": "Helpline authentication not configured"
                }
            
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {auth_token}',
                'Content-Type': 'application/json'
            }
            
            # Helpline API endpoint
            helpline_endpoint = "https://demo-openchs.bitz-itc.com/helpline/api/cases/"
            
            logger.debug(f"Sending to Helpline: {helpline_endpoint}")
            logger.debug(f"Payload: {json.dumps(helpline_payload, indent=2)}")
            
            # Send to Helpline API
            response = requests.post(
                helpline_endpoint,
                json=helpline_payload,
                headers=headers,
                timeout=30
            )
            
            logger.debug(f"Helpline response status: {response.status_code}")
            logger.debug(f"Helpline response text: {response.text}")
            
            if response.status_code in (200, 201):
                try:
                    result = response.json()
                    return {
                        "status": "success",
                        "message": "Case successfully sent to Helpline",
                        "helpline_response": result
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "success",
                        "message": "Case sent to Helpline",
                        "helpline_response": response.text
                    }
            else:
                logger.error(f"Helpline API error: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "message": f"Helpline API error: {response.status_code}",
                    "details": response.text
                }
                
        except requests.RequestException as e:
            logger.exception(f"Network error sending to Helpline: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }
        except Exception as e:
            logger.exception(f"Error sending to Helpline: {str(e)}")
            return {
                "status": "error",
                "message": f"Error sending to Helpline: {str(e)}"
            }
    
    def _map_ceemis_to_helpline_format(self, ceemis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert CEEMIS form data to Helpline JSON format.
        
        Args:
            ceemis_data: CEEMIS form data
            
        Returns:
            Helpline formatted data
        """
        # Generate UUIDs and timestamps
        src_uid = f"ceemis-{uuid.uuid4().hex[:8]}-{int(datetime.now().timestamp())}"
        src_callid = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        current_timestamp = datetime.now().timestamp()
        
        # Build the reporters_uuid (victim/client information)
        reporters_uuid = {
            "fname": ceemis_data.get("mw_name", ""),
            "age_t": "0",
            "age": "",
            "dob": "",
            "age_group_id": "",
            "location_id": self._lookup_location(ceemis_data.get("mw_loca", "")),
            "sex_id": "",
            "landmark": "",
            "nationality_id": "",
            "national_id_type_id": self._lookup_id_type("Passport"),
            "national_id": ceemis_data.get("mw_passport", ""),
            "lang_id": "",
            "tribe_id": "",
            "phone": ceemis_data.get("mw_phone", ""),
            "phone2": "",
            "email": ceemis_data.get("mw_email", ""),
            ".id": ""
        }
        
        # Build clients_case (same as reporters_uuid)
        clients_case = [reporters_uuid.copy()]
        
        # Build perpetrators_case (employer information)
        perpetrators_case = []
        if ceemis_data.get("emp_name") and ceemis_data.get("emp_name") != "NA":
            perpetrator = {
                "fname": ceemis_data.get("emp_name", ""),
                "age_t": "0",
                "age": "",
                "dob": "",
                "age_group_id": "",
                "age_group": "",
                "location_id": self._lookup_location(ceemis_data.get("location", "")),
                "sex_id": "",
                "sex": "",
                "landmark": "",
                "nationality_id": "",
                "national_id_type_id": self._lookup_id_type("EMP_NUMBER"),
                "national_id": ceemis_data.get("emp_number", ""),
                "lang_id": "",
                "tribe_id": "",
                "phone": "",
                "phone2": "",
                "email": "",
                "relationship_id": "",
                "relationship": "Employer",
                "shareshome_id": "",
                "health_id": "",
                "employment_id": self._lookup_employment(ceemis_data.get("emp_sector", "")),
                "marital_id": "",
                "guardian_fullname": "",
                "notes": f"Employer in {ceemis_data.get('emp_sector', 'Unknown')} sector",
                ".id": ""
            }
            perpetrators_case.append(perpetrator)
        
        # Build the complete Helpline payload
        helpline_payload = {
            "src": "ceemis",
            "src_uid": src_uid,
            "src_address": ceemis_data.get("mw_phone", ""),
            "src_uid2": f"{src_uid}-2",
            "src_usr": "ceemis",
            "src_vector": "2",
            "src_callid": src_callid,
            "src_ts": str(current_timestamp),
            "reporter_nickname": "ceemis_user",
            "case_category": ceemis_data.get("comp_category", ""),
            "case_category_id": self._lookup_case_category(ceemis_data.get("comp_category", "")),
            "narrative": ceemis_data.get("mw_narative", ""),
            "complaint_text": None,
            "complaint_image": None,
            "complaint_audio": None,
            "complaint_video": None,
            "message_id_ref": "",
            "session_id": session_id,
            "plan": "---",
            "priority": "1",
            "status": "1",
            "escalated_to_id": "0",
            "gbv_related": "0",
            "reporters_uuid": reporters_uuid,
            "clients_case": clients_case,
            "perpetrators_case": perpetrators_case,
            "attachments_case": [],
            "services": []
        }
        
        return helpline_payload
    
    def _lookup_id_type(self, id_type: str) -> str:
        """
        Lookup ID type mapping.
        
        Args:
            id_type: The ID type to lookup
            
        Returns:
            Mapped ID type value
        """
        lookup_map = {
            "Passport": "1",
            "EMP_NUMBER": "2",
            "National_ID": "3"
        }
        return lookup_map.get(id_type, "1")  # Default to Passport
    
    def _lookup_location(self, location: str) -> str:
        """
        Lookup location mapping.
        
        Args:
            location: The location to lookup
            
        Returns:
            Mapped location ID
        """
        lookup_map = {
            "Kampala": "258783",
            "Uganda": "258783",
            "Entebbe": "258784",
            "Jinja": "258785"
        }
        return lookup_map.get(location, "258783")  # Default to Kampala
    
    def _lookup_employment(self, sector: str) -> str:
        """
        Lookup employment sector mapping.
        
        Args:
            sector: The employment sector to lookup
            
        Returns:
            Mapped employment ID
        """
        lookup_map = {
            "Housemaid": "1",
            "Construction": "2",
            "Agriculture": "3",
            "Manufacturing": "4",
            "Services": "5"
        }
        return lookup_map.get(sector, "1")  # Default to Housemaid
    
    def _lookup_case_category(self, category: str) -> str:
        """
        Lookup case category mapping.
        
        Args:
            category: The case category to lookup
            
        Returns:
            Mapped case category ID
        """
        lookup_map = {
            "COMPLAINT": "362484",
            "COMPLIMENT": "362485",
            "Child Exploitation": "362486",
            "Labor Abuse": "362487",
            "Wage Theft": "362488"
        }
        return lookup_map.get(category, "362484")  # Default to COMPLAINT