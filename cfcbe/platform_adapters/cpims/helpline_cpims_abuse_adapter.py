# platform_adapters/cpims/helpline_cpims_abuse_adapter.py

import json
import logging
import requests
from typing import Any, Dict, List, Optional
from django.http import HttpRequest, HttpResponse, JsonResponse
import uuid
from datetime import datetime
from django.conf import settings

from platform_adapters.base_adapter import BaseAdapter

logger = logging.getLogger(__name__)

class HelplineCPIMSAbuseAdapter(BaseAdapter):
    """
    Adapter for the CPIMS (Child Protection Information Management System) platform integration ,.
    
    This adapter:
    1. Receives case data from Helpline.
    2. Transforms the data to CPIMS format
    3. Sends the case to CPIMS CRS endpoint
    4. Returns appropriate responses to the Helpline
    """
    
    def __init__(self):
        self.cpims_endpoint = getattr(settings, 'CPIMS_ENDPOINT_URL', 'https://test.cpims.net/api/v1/crs/')
        self.cpims_geo_endpoint = getattr(settings, 'CPIMS_GEO_ENDPOINT_URL', 'https://test.cpims.net/api/v1/geo/')
        self.cpims_settings_endpoint = getattr(settings, 'CPIMS_SETTINGS_ENDPOINT_URL', 'https://test.cpims.net/api/v1/settings/')
        self.cpims_auth_token = getattr(settings, 'CPIMS_AUTH_TOKEN', '')

        # Cache for data to avoid repeated API calls
        self._geo_data_cache = None
        self._category_data_cache = None
        self._sub_category_caches = {}  # Dict to cache sub-category data by field_name
        self._case_nature_cache = None
        self._place_of_event_cache = None

        # Log token configuration status once at initialization
        logger.info(f"CPIMS adapter initialized - Auth configured: {bool(self.cpims_auth_token)}")

    def handle_verification(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        CPIMS doesn't require verification challenges.
        """
        return None
    
    def validate_request(self, request: Any) -> bool:
        """
        Validate authenticity of incoming Helpline request (new object-based format).

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

            # Check for required fields in new object-based format
            required_fields = ["id", "narrative"]

            # Validate required fields exist
            for field in required_fields:
                if field not in payload:
                    logger.error(f"Missing required field for CPIMS: {field}")
                    return False

            # Validate narrative is not empty
            if not payload.get("narrative", "").strip():
                logger.error("Narrative cannot be empty")
                return False

            return True

        except (json.JSONDecodeError, AttributeError) as e:
            logger.error(f"Invalid request format: {str(e)}")
            return False
    
    def parse_messages(self, request: Any) -> List[Dict[str, Any]]:
        """
        Convert Helpline API JSON data to StandardMessage format.
        
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
            
            # Extract data from the JSON structure
            case_id = payload.get("id", "")
            narrative = payload.get("narrative", "")
            reporter_phone = payload.get("reporter_phone", "")
            
            # Extract timestamp and convert to float
            created_on_timestamp = payload.get("created_on", "0")
            try:
                timestamp = float(created_on_timestamp) if created_on_timestamp else 0
            except (ValueError, TypeError):
                timestamp = 0
                
            # Create a StandardMessage from the payload
            message = {
                "source": "helpline",
                "source_uid": str(case_id),
                "source_address": reporter_phone,
                "message_id": str(case_id),
                "source_timestamp": timestamp,
                "content": narrative,
                "platform": "cpims",
                "content_type": "case/cpims/abuse",
                "media_url": None,
                "metadata": payload  # Store the full payload as metadata for further processing
            }
            
            return [message]
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error parsing API message: {str(e)}")
            return []
    
    def to_standard_message(self, message_dict: Dict[str, Any]):
        """
        Convert message dictionary to StandardMessage object.
        
        Args:
            message_dict: Message dictionary from parse_messages
            
        Returns:
            StandardMessage object
        """
        from shared.models.standard_message import StandardMessage
        return StandardMessage(**message_dict)
    
    def send_message(self, recipient_id: str, message_content: Any) -> Dict[str, Any]:
        """
        Send case data to CPIMS CRS endpoint.
        
        Args:
            recipient_id: Target platform identifier (always "cpims")
            message_content: The message content (can be dict or StandardMessage)
            
        Returns:
            Response from CPIMS
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
        
        logger.info("Sending case to CPIMS CRS endpoint")
        return self._send_to_cpims(metadata)
    
    def _send_to_cpims(self, helpline_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send case data to CPIMS CRS endpoint.
        
        Args:
            helpline_data: The helpline case data
            
        Returns:
            Response from CPIMS
        """
        try:
            # Map Helpline fields to CPIMS fields
            cpims_payload = self._map_to_cpims_format(helpline_data)

            # Flatten the payload: all fields in cpims_payload go to the top level
            outgoing_payload = dict(cpims_payload)

            # Log what's being sent to CPIMS
            logger.info(f"Sending case to CPIMS: {self.cpims_endpoint}")
            logger.info(f"Payload: {json.dumps(outgoing_payload, indent=2)}")

            # Prepare headers
            headers = {
                'Content-Type': 'application/json'
            }

            # Add authorization if token is configured (optional for test environment)
            if self.cpims_auth_token:
                headers['Authorization'] = f"Token {self.cpims_auth_token}"
                logger.info("Using CPIMS authentication token")
            else:
                logger.warning("No CPIMS auth token - proceeding without authentication")

            # Handle SSL verification based on configuration
            disable_ssl = getattr(settings, 'DISABLE_SSL_VERIFICATION', False)
            verify_ssl = not disable_ssl

            if disable_ssl:
                logger.warning(f"SSL verification disabled by configuration for CPIMS: {self.cpims_endpoint}")

            # Send to CPIMS endpoint
            response = requests.post(
                self.cpims_endpoint,
                json=outgoing_payload,
                headers=headers,
                timeout=30,
                verify=verify_ssl
            )

            logger.info(f"CPIMS response status: {response.status_code}")
            logger.info(f"CPIMS response text: {response.text}")

            if response.status_code in (200, 201, 202):
                try:
                    result = response.json()
                    return {
                        "status": "success",
                        "message": "Case successfully sent to CPIMS",
                        "cpims_response": result,
                        "payload_sent": outgoing_payload
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "success",
                        "message": "Case sent to CPIMS",
                        "cpims_response": response.text,
                        "payload_sent": outgoing_payload
                    }
            elif response.status_code == 401 and self.cpims_auth_token:
                # Only treat 401 as auth error if we actually tried to use a token
                logger.warning(f"CPIMS authentication failed: {response.text}")
                return {
                    "status": "error",
                    "message": "CPIMS authentication failed - check your auth token",
                    "details": response.text
                }
            elif response.status_code == 401:
                # 401 without token might mean endpoint requires no auth but returned 401 for other reasons
                logger.warning(f"CPIMS returned 401 without authentication attempt: {response.text}")
                return {
                    "status": "partial_success", 
                    "message": "Payload processed and sent to CPIMS but received 401 response",
                    "cpims_response": response.text,
                    "payload_sent": outgoing_payload,
                    "note": "Check if CPIMS endpoint configuration is correct"
                }
            else:
                logger.error(f"CPIMS API error: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "message": f"CPIMS API error: {response.status_code}",
                    "details": response.text,
                    "payload_sent": outgoing_payload
                }

        except ValueError as e:
            # Handle category validation errors
            logger.warning(f"Case rejected due to invalid category: {str(e)}")
            return {
                "status": "rejected",
                "message": f"Case rejected: {str(e)}",
                "reason": "invalid_category"
            }
        except requests.RequestException as e:
            logger.exception(f"Network error sending to CPIMS: {str(e)}")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }
        except Exception as e:
            logger.exception(f"Error sending to CPIMS: {str(e)}")
            return {
                "status": "error",
                "message": f"Error sending to CPIMS: {str(e)}"
            }
    
    def format_webhook_response(self, responses: List[Dict[str, Any]]) -> HttpResponse:
        """
        Format response to return to the Helpline webhook.
        """
        # Return the first response or a default response
        if responses:
            return JsonResponse(responses[0])
        else:
            return JsonResponse({"status": "error", "message": "No response from CPIMS"})
    
    def _map_to_cpims_format(self, helpline_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map Helpline JSON API data format to CPIMS expected format.
        
        Args:
            helpline_data: The helpline case data from API
            
        Returns:
            CPIMS formatted payload
        """
        # Helper function to safely get nested values
        def get_safe(data, key, default=""):
            try:
                return data.get(key, default) if data else default
            except (AttributeError, TypeError):
                return default

        # Extract main case data
        case_data = helpline_data
        
        # Extract client data (first client if exists)
        clients = helpline_data.get("clients", [])
        client_data = clients[0] if clients else {}
        
        # Extract perpetrator data (first perpetrator if exists)  
        perpetrators = helpline_data.get("perpetrators", [])
        perpetrator_data = perpetrators[0] if perpetrators else {}
        
        # Use reporter data as primary source for location and contact info
        reporter_location = get_safe(case_data, "reporter_location", "")  # "^Murang'a^Kandara^Kagundu-Ini"
        reporter_location_parts = reporter_location.split("^") if reporter_location else []
        
        # Extract location components from reporter_location string
        # Format: "^County^Constituency^Ward"
        county_name = reporter_location_parts[1] if len(reporter_location_parts) > 1 else get_safe(case_data, "reporter_location_0", "")
        constituency_name = reporter_location_parts[2] if len(reporter_location_parts) > 2 else get_safe(case_data, "reporter_location_1", "")
        ward_name = reporter_location_parts[3] if len(reporter_location_parts) > 3 else get_safe(case_data, "reporter_location_2", "")

        # Fallback to individual location fields if split didn't work
        if not county_name:
            county_name = get_safe(case_data, "reporter_location_0", "")
        if not constituency_name:
            constituency_name = get_safe(case_data, "reporter_location_1", "")
        if not ward_name:
            ward_name = get_safe(case_data, "reporter_location_2", "")

        # Look up area_code values from CPIMS geo API using type-specific lookups
        county_code = self._lookup_area_code_by_type(county_name, "GPRV") if county_name else None
        constituency_code = self._lookup_area_code_by_type(constituency_name, "GDIS") if constituency_name else None
        ward_code = self._lookup_area_code_by_type(ward_name, "GWRD") if ward_name else None
        
        # Fallback to generic lookup if type-specific lookup fails
        if not county_code and county_name:
            county_code = self._lookup_area_code(county_name)
        if not constituency_code and constituency_name:
            constituency_code = self._lookup_area_code(constituency_name)
        if not ward_code and ward_name:
            ward_code = self._lookup_area_code(ward_name)

        # Extract case category from Helpline
        helpline_category = get_safe(case_data, "cat_1", "")

        # Look up full category info (item_id, cpims_description, has_sub_category)
        category_info = self._lookup_category_info(helpline_category) if helpline_category else None

        # Strict validation: If category is not found in CPIMS categories, reject the case
        if not category_info:
            logger.warning(f"❌ CASE REJECTED: Helpline category '{helpline_category}' not found in CPIMS category mapping")
        if not category_info:
            logger.warning(f"❌ CASE REJECTED: Helpline category '{helpline_category}' not found in CPIMS category mapping")
            logger.warning(f"   Available Helpline categories: (Fetch from API failed or returned no matches)")
            raise ValueError(f"Invalid Helpline category '{helpline_category}' - not found in CPIMS category mapping")
            raise ValueError(f"Invalid Helpline category '{helpline_category}' - not found in CPIMS category mapping")

        # Extract CPIMS values from category info

        category_item_id = category_info.get('item_id')
        cpims_category_description = category_info.get('cpims_description')
        has_sub_category = category_info.get('has_sub_category', False)
        item_sub_category_field = category_info.get('item_sub_category')

        # Resolve sub-category ID
        # Default to category_item_id as CPIMS requires a value even if no sub-category
        sub_category_id = category_item_id
        
        if has_sub_category and item_sub_category_field:
            # Try to resolve sub-category from input
            # First check explicit 'sub_category' field, then fallback to 'cat_2' (often used for sub-type)
            sub_category_name = get_safe(case_data, "sub_category", "") or get_safe(case_data, "cat_2", "")
            
            if sub_category_name:
                found_sub_id = self._lookup_sub_category_id(sub_category_name, item_sub_category_field)
                if found_sub_id:
                    sub_category_id = found_sub_id
                    logger.info(f"Resolved sub-category '{sub_category_name}' to ID '{sub_category_id}'")
            else:
                logger.warning(f"Category '{helpline_category}' expects sub-category ('{item_sub_category_field}') but no 'sub_category' field found in input")
        
        # Determine data source priority: client data if available, otherwise reporter data
        has_client_data = bool(client_data)
        
        # Helper function to get person data with fallback
        def get_person_data(client_field, reporter_field, default=""):
            if has_client_data and client_field in client_data:
                return get_safe(client_data, client_field, default)
            else:
                return get_safe(case_data, reporter_field, default)
        
        # Extract sex from client or reporter data
        person_sex = get_person_data("contact_sex", "reporter_sex", "")
        # Remove the "^" prefix if present (e.g., "^Female" -> "Female")
        person_sex = person_sex.lstrip("^") if person_sex else ""
        
        # Extract full name from client or reporter data
        person_fullname = get_person_data("contact_fullname", "reporter_fullname", "")
        
        # Extract phone from client or reporter
        person_phone = get_person_data("contact_phone", "reporter_phone", "")
        
        # Extract email from client or reporter  
        person_email = get_person_data("contact_email", "reporter_email", "")
        
        # Format timestamp helper
        def format_api_timestamp(timestamp_str):
            if not timestamp_str or timestamp_str == "0":
                return self._get_current_date()
            try:
                # API timestamps appear to be Unix timestamps as strings
                if timestamp_str.isdigit():
                    from datetime import datetime
                    dt = datetime.fromtimestamp(int(timestamp_str))
                    return dt.strftime("%Y-%m-%d")
                else:
                    return str(timestamp_str)
            except (ValueError, TypeError):
                return self._get_current_date()
        
        # Map according to CPIMS format using API payload fields
        cpims_payload = {
            # Basic case information
            "physical_condition": "PNRM",  # Default - not available in API payload
            "county": county_code or "UNK",  # Use county code instead of name
            "sub_county_code": constituency_code or "UNK",  # Use constituency code instead of name
            "hh_economic_status": "UINC",  # Default - not available in API payload
            "other_condition": "CHNM",  # Default - not available in API payload
            "child_sex": self._map_code(person_sex, "sex") or "SMAL",
            "reporter_first_name": self._extract_name(get_safe(case_data, "reporter_fullname", ""), "first") or "Unknown",
            "ob_number": get_safe(case_data, "police_ob_no", ""),
            "longitude": None,  # Not available in this API payload structure
            "recommendation_bic": get_safe(case_data, "plan", ""),
            "family_status": "FSLA",  # Default - not available in API payload
            "reporter_other_names": self._extract_name(get_safe(case_data, "reporter_fullname", ""), "other"),
            "case_date": format_api_timestamp(get_safe(case_data, "created_on", "")),
            "child_other_names": self._extract_name(person_fullname, "other"),
            "friends": None,
            "organization_unit": "Helpline 116",
            "case_reporter": self._map_code("Helpline 116", "case_reporter") or "CRHE",
            "child_in_school": get_safe(client_data, "in_school", None) if has_client_data else None,
            "tribe": get_safe(client_data, "contact_tribe", None) if has_client_data else get_safe(case_data, "reporter_tribe", None),
            "sublocation": ward_code or "Unk",
            "child_surname": self._extract_name(person_fullname, "surname") or "Unknown",
            "case_village": get_safe(case_data, "reporter_location_5", "") or "Unknown Village",  # Lowest level location
            "latitude": None,  # Not available in this API payload structure
            "child_first_name": self._extract_name(person_fullname, "first") or "Unknown",
            "reporter_telephone": get_safe(case_data, "reporter_phone", "0700000000"),
            "court_number": "",
            "verification_status": "001",  # Unverified status as default
            "child_dob": format_api_timestamp(get_safe(client_data, "contact_dob", "")) if has_client_data else "2010-01-01",
            "perpetrator_status": "PUNK" if not perpetrator_data else "PKNW",  # Unknown if no perpetrator data
            "reporter_surname": self._extract_name(get_safe(case_data, "reporter_fullname", ""), "surname") or "Unknown",
            "case_narration": get_safe(case_data, "narrative", "") or "Case reported through helpline",
            "court_name": "",
            "case_landmark": get_safe(case_data, "reporter_landmark", "") or ward_name or county_name or "Helpline Report",
            "religion_type": None,
            "long_term_needs": None ,
            "immediate_needs": None,
            "mental_condition": "MNRM",  # Default
            "police_station": "",
            "risk_level": self._map_code(get_safe(case_data, "priority", ""), "risk_level") or "RLMD",
            "constituency": (constituency_code or "UNK")[:3],  # Max 3 chars  
            "hobbies": None,
            "reporter_email": get_safe(case_data, "reporter_email", ""),
            "location": get_safe(case_data, "reporter_location_5", "") or ward_code or "Unk",
            "reporter_county": county_code or "UNK",
            "reporter_sub_county": constituency_code or "UNK", 
            "reporter_ward": ward_code or "UNK",
            "reporter_village": get_safe(case_data, "reporter_location_5", "") or "UNK",
            "has_birth_cert": None,
            "user": get_safe(case_data, "created_by", "helpline_user"),
            "area_code": county_code or "UNK",
            "case_category_id": category_item_id,
            "case_category": category_info.get('cpims_description', ''),
            "case_details": [{
                "place_of_event": self._lookup_place_of_event(get_safe(case_data, "incidence_location", "")) or "",
                "category": category_item_id,
                "sub_category": sub_category_id,
                "nature_of_event": self._lookup_case_nature(get_safe(case_data, "cat_2", "")) or "OOEV",
                "date_of_event": format_api_timestamp(get_safe(case_data, "incidence_when", ""))
            }],

            # Categories array
            "categories": [{
                "case_category": category_item_id,  # CPIMS code (e.g., "CCDF" for Defilement) - from case_category_id endpoint
                "case_sub_category": sub_category_id,
                "case_date_event": format_api_timestamp(get_safe(case_data, "incidence_when", "")),  # Date format YYYY-MM-DD
                "case_nature": self._lookup_case_nature(get_safe(case_data, "cat_2", "")) or "OOEV",
                "case_place_of_event": self._lookup_place_of_event(get_safe(case_data, "incidence_location", "")) or "",  # From event_place_id endpoint
                "case_id": get_safe(case_data, "id", "")
            }],
            
            # Perpetrators array
            "perpetrators": [{
                "first_name": self._extract_name(get_safe(perpetrator_data, "contact_fullname", ""), "first"),
                "surname": self._extract_name(get_safe(perpetrator_data, "contact_fullname", ""), "surname"),
                "relationship": self._map_code(get_safe(perpetrator_data, "relationship", ""), "relationship"),
                "sex": self._map_code(get_safe(perpetrator_data, "contact_sex", "").lstrip("^"), "sex")
            }] if perpetrator_data else [],
            
            # Siblings array (using client data if available)
            "siblings": [{
                "surname": self._extract_name(get_safe(client_data, "contact_fullname", ""), "surname"),
                "dob": format_api_timestamp(get_safe(client_data, "contact_dob", "")),
                "sex": self._map_code(get_safe(client_data, "contact_sex", "").lstrip("^"), "sex"),
                "school_name": get_safe(client_data, "school_name", ""),
                "other_names": self._extract_name(get_safe(client_data, "contact_fullname", ""), "other"),
                "first_name": self._extract_name(get_safe(client_data, "contact_fullname", ""), "first"),
                "class": get_safe(client_data, "school_level", ""),
                "remarks": get_safe(client_data, "special_services", "")
            }] if has_client_data else [],
            
            # Empty arrays for now
            "parents": [{}, {}],
            "caregivers": []
        }

        return cpims_payload
    
    def _format_timestamp(self, timestamp_str: str) -> str:
        """
        Format timestamp from helpline format to CPIMS format.
        
        Args:
            timestamp_str: Timestamp string (could be unix timestamp or date string)
            
        Returns:
            Formatted date string
        """
        if not timestamp_str:
            return ""
        
        try:
            # If it's a unix timestamp (numeric string)
            if timestamp_str.isdigit():
                from datetime import datetime
                dt = datetime.fromtimestamp(int(timestamp_str))
                return dt.strftime("%Y-%m-%d")
            else:
                # Return as is if it's already a string
                return str(timestamp_str)
        except (ValueError, TypeError):
            return str(timestamp_str)
    
    def _get_current_date(self) -> str:
        """
        Get current date in CPIMS format.
        
        Returns:
            Current date as YYYY-MM-DD string
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    def _get_geo_data(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch geographic data from CPIMS geo endpoint.
        Uses caching to avoid repeated API calls.
        
        Returns:
            List of geographic areas or None if request fails
        """
        # Return cached data if available
        if self._geo_data_cache is not None:
            return self._geo_data_cache

        try:
            logger.info(f"Fetching geo data from CPIMS: {self.cpims_geo_endpoint}")

            headers = {'Content-Type': 'application/json'}
            
            # Add authorization if token is available
            if self.cpims_auth_token:
                headers['Authorization'] = f"Token {self.cpims_auth_token}"
            
            # Handle SSL verification
            disable_ssl = getattr(settings, 'DISABLE_SSL_VERIFICATION', False)
            verify_ssl = not disable_ssl
            
            response = requests.get(
                self.cpims_geo_endpoint,
                headers=headers,
                timeout=30,
                verify=verify_ssl
            )
            
            logger.info(f"Geo API response status: {response.status_code}")
            
            if response.status_code == 200:
                geo_data = response.json()
                # Cache the successful response
                self._geo_data_cache = geo_data
                logger.info(f"Successfully fetched {len(geo_data)} geographic areas")
                return geo_data
            else:
                logger.error(f"Failed to fetch geo data: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Network error fetching geo data: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching geo data: {str(e)}")
            return None

    def _get_category_data(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch category data from CPIMS settings endpoint.
        Uses caching to avoid repeated API calls.

        Returns:
            List of case categories or None if request fails
        """
        # Return cached data if available
        if self._category_data_cache is not None:
            return self._category_data_cache

        try:
            # Fetch case_category_id from CPIMS settings API
            url = f"{self.cpims_settings_endpoint}?field_name=case_category_id"
            logger.info(f"Fetching category data from CPIMS: {url}")

            headers = {'Content-Type': 'application/json'}

            # Add authorization if token is available
            if self.cpims_auth_token:
                headers['Authorization'] = f"Token {self.cpims_auth_token}"

            # Handle SSL verification
            disable_ssl = getattr(settings, 'DISABLE_SSL_VERIFICATION', False)
            verify_ssl = not disable_ssl

            response = requests.get(
                url,
                headers=headers,
                timeout=30,
                verify=verify_ssl
            )

            logger.info(f"Category API response status: {response.status_code}")

            if response.status_code == 200:
                category_data = response.json()
                # Cache the successful response
                self._category_data_cache = category_data
                logger.info(f"Successfully fetched {len(category_data)} case categories")
                return category_data
            else:
                logger.error(f"Failed to fetch category data: {response.status_code} - {response.text}")
                return None

        except requests.RequestException as e:
            logger.error(f"Network error fetching category data: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching category data: {str(e)}")
            return None

    def _get_sub_category_data(self, field_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch sub-category data from CPIMS settings endpoint for a specific field.
        Uses caching to avoid repeated API calls.

        Args:
            field_name: The sub-category field name (e.g., 'child_labour_id', 'offender_id')

        Returns:
            List of sub-category items if successful, None otherwise
        """
        if not field_name:
            return None

        # Check if already cached
        if field_name in self._sub_category_caches:
            return self._sub_category_caches[field_name]

        try:
            url = f"{self.cpims_settings_endpoint}?field_name={field_name}"
            logger.info(f"Fetching sub-category data from CPIMS: {url}")

            headers = {'Content-Type': 'application/json'}
            if self.cpims_auth_token:
                headers['Authorization'] = f"Token {self.cpims_auth_token}"

            disable_ssl = getattr(settings, 'DISABLE_SSL_VERIFICATION', False)
            verify_ssl = not disable_ssl

            response = requests.get(url, headers=headers, timeout=30, verify=verify_ssl)

            if response.status_code == 200:
                sub_category_data = response.json()
                self._sub_category_caches[field_name] = sub_category_data
                logger.info(f"Successfully fetched {len(sub_category_data)} sub-categories for {field_name}")
                return sub_category_data
            else:
                logger.error(f"Failed to fetch sub-category data for {field_name}: {response.status_code}")
                return None

        except requests.RequestException as e:
            logger.error(f"Network error fetching sub-category data for {field_name}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching sub-category data for {field_name}: {str(e)}")
            return None

    def _lookup_area_code_by_type(self, area_name: str, area_type_id: str) -> Optional[str]:
        """
        Look up area_code for a given area name and area_type_id from CPIMS geo data.
        
        Args:
            area_name: The name of the area to look up
            area_type_id: The area type ID to filter by (GPRV, GDIS, GWRD)
            
        Returns:
            The area_code if found, None otherwise
        """
        if not area_name:
            return None
        
        geo_data = self._get_geo_data()
        if not geo_data:
            logger.warning(f"No geo data available for lookup of: {area_name}")
            return None
        
        # Search for the area by name and area_type_id (case-insensitive)
        area_name_lower = area_name.lower().strip()
        
        for area in geo_data:
            if (area.get('area_name', '').lower().strip() == area_name_lower and
                area.get('area_type_id') == area_type_id):
                area_code = area.get('area_code')
                return area_code

        logger.warning(f"Area '{area_name}' with type '{area_type_id}' not found in CPIMS geo data")
        return None
    
    def _lookup_area_type_id(self, area_name: str) -> Optional[str]:
        """
        Look up area_type_id for a given area name from CPIMS geo data.
        
        Args:
            area_name: The name of the area to look up
            
        Returns:
            The area_type_id if found, None otherwise
        """
        if not area_name:
            return None
        
        geo_data = self._get_geo_data()
        if not geo_data:
            logger.warning(f"No geo data available for lookup of: {area_name}")
            return None
        
        # Search for the area by name (case-insensitive)
        area_name_lower = area_name.lower().strip()
        
        for area in geo_data:
            if area.get('area_name', '').lower().strip() == area_name_lower:
                area_type_id = area.get('area_type_id')
                return area_type_id

        logger.warning(f"Area '{area_name}' not found in CPIMS geo data")
        return None
    
    def _lookup_area_code(self, area_name: str) -> Optional[str]:
        """
        Look up area_code for a given area name from CPIMS geo data.
        
        Args:
            area_name: The name of the area to look up
            
        Returns:
            The area_code if found, None otherwise
        """
        if not area_name:
            return None
            
        geo_data = self._get_geo_data()
        if not geo_data:
            logger.warning(f"No geo data available for lookup of: {area_name}")
            return None
            
        # Search for the area by name (case-insensitive)
        area_name_lower = area_name.lower().strip()
        
        for area in geo_data:
            if area.get('area_name', '').lower().strip() == area_name_lower:
                area_code = area.get('area_code')
                return area_code

        logger.warning(f"Area '{area_name}' not found in CPIMS geo data")
        return None
    
    
    def _lookup_category_info(self, helpline_category: str) -> Optional[Dict[str, Any]]:
        """
        Look up category information from CPIMS API with intelligent fuzzy matching.
        
        Args:
            helpline_category: The Helpline category description to look up
            
        Returns:
            Category dict with item_id, cpims_description, has_sub_category, item_sub_category if found
        """
        if not helpline_category:
            return None

        # Get category data from CPIMS API
        category_data = self._get_category_data()
        if not category_data:
            logger.warning(f"No category data available for lookup of: {helpline_category}")
            return None

        # Common category aliases mapping
        category_aliases = {
            "child labor": "Child Labour",
            "child labour": "Child Labour", 
            "abuse": "Physical abuse/violence",
            "physical abuse": "Physical abuse/violence",
            "violence": "Physical abuse/violence",
            "emotional abuse": "Emotional Abuse",
            "sexual abuse": "Sexual Exploitation and abuse",
            "sexual assault": "Sexual assault",
            "sexual exploitation": "Sexual Exploitation and abuse",
            "rape": "Defilement",
            "defilement": "Defilement",
            "neglect": "Neglect",
            "drug abuse": "Drug and Substance Abuse",
            "substance abuse": "Drug and Substance Abuse",
            "drugs": "Drug and Substance Abuse",
            "trafficking": "Trafficked child",
            "child trafficking": "Trafficked child",
            "fgm": "FGM",
            "female genital mutilation": "FGM",
            "child marriage": "Child Marriage",
            "early marriage": "Child Marriage",
            "abandoned": "Abandoned",
            "abandonment": "Abandoned",
            "street children": "Children on the streets",
            "street child": "Children on the streets",
            "orphan": "Orphaned Child",
            "teenage pregnancy": "Child pregnancy",
            "child pregnancy": "Child pregnancy",
            "pregnancy": "Child pregnancy",
            "birth registration": "Registration",
            "registration": "Registration",
            "missing child": "Missing Child (Lost & Found)",
            "lost child": "Missing Child (Lost & Found)",
            "custody": "Custody",
            "truancy": "Child truancy",
            "disability": "Child with disability",
            "hiv": "Child Affected by HIV/AIDS",
            "aids": "Child Affected by HIV/AIDS",
            "incest": "Incest",
            "sodomy": "Sodomy",
            "child offender": "Child offender",
            "out of school": "Child out of school",
            "radicalization": "Child radicalization",
            "child radicalization": "Child radicalization",
            "abduction": "Abduction",
            "online abuse": "Online Child Exploitation and Abuse",
            "cyber abuse": "Online Child Exploitation and Abuse",
            "delinquency": "Child Delinquency",
        }

        helpline_category_lower = helpline_category.lower().strip()

        # Try exact match first
        for category in category_data:
            if category.get('item_description', '').lower().strip() == helpline_category_lower:
                return {
                    'item_id': category.get('item_id'),
                    'cpims_description': category.get('item_description'),
                    'has_sub_category': bool(category.get('item_sub_category')),
                    'item_sub_category': category.get('item_sub_category')
                }

        # Try alias mapping
        mapped_category = category_aliases.get(helpline_category_lower)
        if mapped_category:
            for category in category_data:
                if category.get('item_description', '').lower().strip() == mapped_category.lower().strip():
                    logger.info(f"Matched category '{helpline_category}' via alias to '{mapped_category}'")
                    return {
                        'item_id': category.get('item_id'),
                        'cpims_description': category.get('item_description'),
                        'has_sub_category': bool(category.get('item_sub_category')),
                        'item_sub_category': category.get('item_sub_category')
                    }

        # Try partial matching (e.g., "Labour" in "Child Labour")
        for category in category_data:
            item_desc = category.get('item_description', '').lower()
            if helpline_category_lower in item_desc or item_desc in helpline_category_lower:
                logger.info(f"Matched category '{helpline_category}' via partial match to '{category.get('item_description')}'")
                return {
                    'item_id': category.get('item_id'),
                    'cpims_description': category.get('item_description'),
                    'has_sub_category': bool(category.get('item_sub_category')),
                    'item_sub_category': category.get('item_sub_category')
                }

        logger.warning(f"Helpline category '{helpline_category}' not found in CPIMS API data")
        return None



    def _lookup_category_item_id(self, category_description: str) -> Optional[str]:
        """
        Look up item_id for a given Helpline category description.

        Args:
            category_description: The Helpline category description to look up

        Returns:
            The CPIMS item_id if found, None otherwise
        """
        category_info = self._lookup_category_info(category_description)
        return category_info.get('item_id') if category_info else None

    def _lookup_sub_category_id(self, sub_category_name: str, field_name: str) -> Optional[str]:
        """
        Look up item_id for a given sub-category name and field_name with fuzzy matching.
        
        Args:
            sub_category_name: The sub-category name to look up
            field_name: The settings field name for this sub-category type
            
        Returns:
            The CPIMS item_id if found, None otherwise
        """
        if not sub_category_name or not field_name:
            return None
            
        # Context-aware aliases based on field type
        sub_category_aliases = {
            # Child labour aliases
            "domestic work": "Domestic work / Exploitative household chores",
            "agriculture": "Agriculture / Farming work (Milking, tilling, harvesting, weeding, scarring animals)",
            "farming": "Agriculture / Farming work (Milking, tilling, harvesting, weeding, scarring animals)",
            "jua kali": "Informal Sector (Jua kali)",
            "informal": "Informal Sector (Jua kali)",
            "transport": "Transport industry work (bodaboda, motor cycle taxis, bicycles, carts, matatus, boat rowing, touting)",
            "bodaboda": "Transport industry work (bodaboda, motor cycle taxis, bicycles, carts, matatus, boat rowing, touting)",
            "mining": "Mining and quarrying (Sand harvesting, ballast making)",
            "quarrying": "Mining and quarrying (Sand harvesting, ballast making)",
            "hotel": "Hotels, restaurants and bars work",
            "restaurant": "Hotels, restaurants and bars work",
            
            # Offender type aliases
            "theft": "Theft",
            "stealing": "Theft",
            "robbery": "Robbery with Violence",
            "burglary": "House breaking/Burglary",
            "housebreaking": "House breaking/Burglary",
            "assault": "Assault",
            "murder": "Murder",
            "rape": "Attempted Defilement/Rape",
            "defilement": "Defilement",
            "drugs": "Possession of narcotics",
            "narcotics": "Possession of narcotics",
            "peddling": "Peddling of drugs",
            
            # Out of school reasons
            "poverty": "Family Poverty",
            "family poverty": "Family Poverty",
            "disability": "Disability/Chronic Illness",
            "illness": "Disability/Chronic Illness",
            "work": "Engaged in child labour",
            "labour": "Engaged in child labour",
            "preference": "Childs Preference",
            "caregiver": "Care Givers Decision",
            
            # Custody
            "guardianship": "Guardianship",
            "disputed": "Disputed Custody",
            "access": "Access denied",
        }
        
        # Fetch data for this sub-category type
        sub_category_data = self._get_sub_category_data(field_name)
        if not sub_category_data:
            logger.warning(f"No data available for sub-category field: {field_name}")
            return None
            
        # Search for the sub-category by name (case-insensitive)
        name_lower = sub_category_name.lower().strip()
        
        # Try exact match first
        for item in sub_category_data:
            # Check if name matches description (case-insensitive)
            if item.get('item_description', '').lower().strip() == name_lower:
                return item.get('item_id')
            # Also check if the input IS the ID itself
            if item.get('item_id', '') == sub_category_name:
                 return item.get('item_id')
        
        # Try alias mapping
        mapped_sub_category = sub_category_aliases.get(name_lower)
        if mapped_sub_category:
            for item in sub_category_data:
                if item.get('item_description', '').lower().strip() == mapped_sub_category.lower().strip():
                    logger.info(f"Matched sub-category '{sub_category_name}' via alias to '{mapped_sub_category}'")
                    return item.get('item_id')
        
        # Try partial matching
        for item in sub_category_data:
            item_desc = item.get('item_description', '').lower()
            if name_lower in item_desc or item_desc in name_lower:
                logger.info(f"Matched sub-category '{sub_category_name}' via partial match to '{item.get('item_description')}'")
                return item.get('item_id')
                
        logger.warning(f"Sub-category '{sub_category_name}' not found in {field_name}")
        return None

    def _get_case_nature_data(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch case nature data from CPIMS settings endpoint.
        """
        if self._case_nature_cache is not None:
            return self._case_nature_cache

        return self._fetch_settings_data("case_nature_id", "_case_nature_cache")

    def _get_place_of_event_data(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch place of event data from CPIMS settings endpoint.
        """
        if self._place_of_event_cache is not None:
            return self._place_of_event_cache

        return self._fetch_settings_data("event_place_id", "_place_of_event_cache")

    def _fetch_settings_data(self, field_name: str, cache_attr: str) -> Optional[List[Dict[str, Any]]]:
        """
        Generic method to fetch settings data.
        """
        try:
            url = f"{self.cpims_settings_endpoint}?field_name={field_name}"
            headers = {'Content-Type': 'application/json'}
            if self.cpims_auth_token:
                headers['Authorization'] = f"Token {self.cpims_auth_token}"

            disable_ssl = getattr(settings, 'DISABLE_SSL_VERIFICATION', False)
            response = requests.get(url, headers=headers, timeout=30, verify=not disable_ssl)

            if response.status_code == 200:
                data = response.json()
                setattr(self, cache_attr, data)
                return data
            else:
                logger.error(f"Failed to fetch {field_name}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching {field_name}: {str(e)}")
            return None

    def _lookup_case_nature(self, nature_description: str) -> Optional[str]:
        """Look up item_id for case nature."""
        if not nature_description: return None
        data = self._get_case_nature_data()
        return self._lookup_item_id(data, nature_description)

    def _lookup_place_of_event(self, place_description: str) -> Optional[str]:
        """Look up item_id for place of event with smart matching."""
        if not place_description: return None
        
        # Common aliases mapping
        place_aliases = {
            "home": "Home & Family",
            "school": "School and Educational Settings",
            "street": "On the Street",
            "church": "Place of worship/Religious Centre",
            "mosque": "Place of worship/Religious Centre",
            "temple": "Place of worship/Religious Centre",
            "work": "Places of Work",
            "hospital": "Health Facility",
            "clinic": "Health Facility",
        }
        
        data = self._get_place_of_event_data()
        if not data: return None
        
        place_lower = place_description.lower().strip()
        
        # Try exact match first
        result = self._lookup_item_id(data, place_description)
        if result: return result
        
        # Try alias mapping
        mapped_place = place_aliases.get(place_lower)
        if mapped_place:
            result = self._lookup_item_id(data, mapped_place)
            if result: return result
        
        # Try partial matching (e.g., "Home" in "Home & Family")
        for item in data:
            item_desc = item.get('item_description', '').lower()
            if place_lower in item_desc or item_desc in place_lower:
                return item.get('item_id')
        
        logger.warning(f"Place of event '{place_description}' not found in API data")
        return None

    def _lookup_item_id(self, data_list: Optional[List[Dict[str, Any]]], description: str) -> Optional[str]:
        """Generic lookup helper."""
        if not data_list or not description: return None
        desc_lower = description.lower().strip()
        for item in data_list:
            if item.get('item_description', '').lower().strip() == desc_lower:
                return item.get('item_id')
        return None
        return None
    
    def _extract_name(self, full_name: str, part: str) -> str:
        """
        Extract parts of a full name.
        
        Args:
            full_name: The full name string
            part: Which part to extract ("first", "surname", "other")
            
        Returns:
            The requested part of the name
        """
        if not full_name:
            return ""
        
        name_parts = full_name.strip().split()
        
        if part == "first":
            return name_parts[0] if name_parts else ""
        elif part == "surname":
            return name_parts[-1] if len(name_parts) > 1 else ""
        elif part == "other":
            return " ".join(name_parts[1:-1]) if len(name_parts) > 2 else ""
        
        return ""
    
    def _map_code(self, value: str, mapping_type: str) -> str:
        """
        Map helpline values to CPIMS codes.
        
        Args:
            value: The value to map
            mapping_type: The type of mapping to use
            
        Returns:
            The mapped CPIMS code
        """
        # Sex codes
        sex_codes = {
            "Male": "SMAL",
            "Female": "SFEM", 
            "Intersex": "SINT"
        }
        
        # Yes/No codes
        yes_no_codes = {
            "No": "ANNO",
            "Yes": "AYES"  # Assuming this exists
        }
        
        # Economic status codes
        economic_status_codes = {
            "High Income (apparent)": "HINC",
            "Middle Income (apparent)": "MINC", 
            "Low Income (apparent)": "LINC",
            "Unknown": "UINC"
        }
        
        # Physical condition codes
        physical_condition_codes = {
            "Appears Normal": "PNRM",
            "Challenged (unverified)": "PHAU",
            "Challenged (verified)": "PHAV"
        }
        
        # Mental condition codes
        mental_condition_codes = {
            "Appears Normal": "MNRM",
            "Challenged (verified)": "MCAV",
            "Challenged (unverified)": "MCAU"
        }
        
        # Other condition codes
        other_condition_codes = {
            "Appears Normal": "CHNM",
            "Chronic": "CHRO"
        }
        
        # Risk level codes
        risk_level_codes = {
            "Low": "RLLW",
            "Medium": "RLMD", 
            "High": "RLHG",
            "1": "RLLW",
            "2": "RLMD", 
            "3": "RLHG"
        }
        
        # Case reporter codes - sorted A-Z
        case_reporter_codes = {
            "Chief": "CRCH",
            "Court": "CRCO",
            "Diplomatic missions": "CRDM",
            "Father": "CRFA",
            "Helpline 116": "CRHE",
            "Helpline 1195": "CRHL",
            "Immigration": "CRIM",
            "Labour Officers": "CRLO",
            "Ministry of Tourism": "CRMT",
            "Mother": "CRMO",
            "Other Government agency": "CROG",
            "Other non-relative(s)": "CRON",
            "Other relative(s)": "CROR",
            "Police": "CRPO",
            "Probation": "CRPR",
            "Self": "CRSF",
            "Service Providers": "CRSP",
            "Trade Union": "CRTU"
        }
        
        # Family status codes - sorted A-Z
        family_status_codes = {
            "Caregiver is chronically ill": "FSCI",
            "Caregiver is disabled": "FSCD",
            "Caregiver is more than 60 years old": "FSOL",
            "In institution with mother (has child mother)": "RSMI",
            "Informal Guardian": "CCIG",
            "Living alone": "FSLA",
            "Living in child-headed household (no adult caregiver)": "FSHD",
            "Living in children home": "FSCH",
            "Living in poor household (destitute)": "FSPH",
            "Living on the Street": "CCLS",
            "Living with a friend": "FSLF",
            "Living with adoptive parents": "CCAP",
            "Living with biological parents": "CCBP",
            "Living with father only": "CCFO",
            "Living with mother only": "CCMO",
            "Orphaned - father dead": "FSOF",
            "Orphaned - mother dead": "FSOM",
            "Other Family": "CCOF"
        }
        
        # Tribe codes - sorted A-Z
        tribe_codes = {
            "American": "TRAM",
            "European": "TREU",
            "Kalenjin": "TRKE",
            "Kamba": "TRKA",
            "Kenyan Somali": "TRKS",
            "Kikuyu": "TRKI",
            "Kisii": "TRII",
            "Kuria": "TRKU",
            "Luhya": "TRLU",
            "Luo": "TRLO",
            "Maasai": "TRAA",
            "Mbeere": "TRMB",
            "Meru": "TRME",
            "Mijikenda": "TRMJ",
            "Nubi": "TRNU",
            "Orma": "TROR",
            "Pokomo": "TRPO",
            "Rendile": "TRRE",
            "Swahili": "TRSW",
            "Taita": "TRTT"
        }
        
        # Religion codes
        religion_codes = {
            "Christian": "RECH",
            "Muslim": "REMU",
            "Buddhist": "REBU",
            "Atheist": "REAT",
            "Other": "REOT"
        }
        
        # Perpetrator status codes
        perpetrator_status_codes = {
            "Known": "PKNW",
            "Unknown": "PUNK", 
            "Self": "PSSL",
            "Not Applicable": "PSNA"
        }
        
        # Case category codes - updated with latest CPIMS mapping (sorted A-Z)
        case_category_codes = {
            "Birth Registration": "CPAV",
            "Child Abandonment": "CDIS",
            "Child Abduction": "CDSA",
            "Child affected by HIV/AIDS": "CLAB",
            "Child headed household": "COSR",
            "Child Labor": "CTRF",
            "Child Marriage": "CCCM",
            "Child Mother": "CLCM",
            "Child Neglect": "CSIC",
            "Child offender": "CSAB",
            "Child of imprisoned parent (S)": "SCCI",
            "Child out of school": "CSAD",
            "Child Prostitution, Sexual Abuse": "CSRG",
            "Child radicalization": "CSDQ",
            "Child Trafficking": "CSTC",
            "Child Truancy": "CCCT",
            "Children on the streets": "CCIP",
            "Custody": "CCCP",
            "Defilement": "CCDF",
            "Disputed Paternity": "CSCT",
            "Drug Abuse": "CSDS",
            "Emotional Abuse": "CCEA",
            "Female Genital Mutilation": "CSCS",
            "Harmful cultural practice": "CSCU",
            "Inheritance/succession": "CSDP",
            "Internally displaced child": "CFGM",
            "Juvenile Deliquency": "CORP",
            "Lost and Found, Lost Child": "CHCP",
            "Mental & physical disability": "CSCL",
            "Mother offer": "CCMO",
            "Online Abuse": "CCOA",
            "Orphan & Vulnerable children": "CIDC",
            "Parental child abduction": "CLFC",
            "Physical Abuse": "CSNG",
            "Refugee Children": "CPCA",
            "Sexual Abuse (Incest)": "CSDF",
            "Sexual Abuse (Sodomy)": "CSSO",
            "Sexual assault": "CSRC",
            "Sickness or illness": "CSSA",
            "Teenage Pregnancy": "CSHV",
            "Unlawful Confinement": "CSUC"
        }
        
        # Case nature codes
        case_nature_codes = {
            "Chronic/On-going event": "OCGE",
            "One-off event": "OOEV",
            "Emergency": "OOEM"
        }
        
        # Relationship codes (for perpetrators) - sorted A-Z
        relationship_codes = {
            "Commercial Drivers": "RCCD",
            "Employer": "RCEP",
            "Friend": "RCFD",
            "Health care worker": "RCHW",
            "Local Influentials": "RCLI",
            "Neighbour": "RCNB",
            "Other family member": "ROFM",
            "Other Humanitarian Worker": "ROHW",
            "Other non-family": "RCOT",
            "Other person in positions of authority": "ROPA",
            "Other Primary Care Giver/Guardian": "ROCG",
            "Parent": "RCPT",
            "Religious Leader": "RCRL",
            "Security Guards": "RCSG",
            "Security Personnel/Disciplined force member": "RCSP",
            "Strangers": "RCST",
            "Teacher": "RCTC",
            "Tourist": "RCTR",
            "Unknown/Not Recorded": "RCUN"
        }
        
        # Select the appropriate mapping
        mapping_dict = {}
        if mapping_type == "sex":
            mapping_dict = sex_codes
        elif mapping_type == "yes_no":
            mapping_dict = yes_no_codes
        elif mapping_type == "economic_status":
            mapping_dict = economic_status_codes
        elif mapping_type == "physical_condition":
            mapping_dict = physical_condition_codes
        elif mapping_type == "mental_condition":
            mapping_dict = mental_condition_codes
        elif mapping_type == "other_condition":
            mapping_dict = other_condition_codes
        elif mapping_type == "risk_level":
            mapping_dict = risk_level_codes
        elif mapping_type == "case_reporter":
            mapping_dict = case_reporter_codes
        elif mapping_type == "family_status":
            mapping_dict = family_status_codes
        elif mapping_type == "tribe":
            mapping_dict = tribe_codes
        elif mapping_type == "religion":
            mapping_dict = religion_codes
        elif mapping_type == "perpetrator_status":
            mapping_dict = perpetrator_status_codes
        elif mapping_type == "case_category":
            mapping_dict = case_category_codes
        elif mapping_type == "case_nature":
            mapping_dict = case_nature_codes
        elif mapping_type == "relationship":
            mapping_dict = relationship_codes
        
        # Normalize incoming value (remove caret prefixes and trim whitespace)
        normalized_value = (value or "").lstrip("^").strip()

        # For risk_level and case_nature, enforce strict mapping to ensure CPIMS codes are emitted
        if mapping_type in ["risk_level", "case_nature"]:
            # Return empty string if not found so caller can apply a safe default
            return mapping_dict.get(normalized_value, "")

        # Return the mapped value or the original value if not found (non-strict)
        return mapping_dict.get(normalized_value, value)