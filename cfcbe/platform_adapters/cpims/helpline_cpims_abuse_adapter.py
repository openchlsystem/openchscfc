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
        self.cpims_auth_token = getattr(settings, 'CPIMS_AUTH_TOKEN', '')
        
        # Cache for geo data to avoid repeated API calls
        self._geo_data_cache = None
        
        # CPIMS case categories mapping
        self.case_categories = [
            {"item_id": "CSCU", "item_description": "Harmful cultural practice", "item_sub_category": "cultural_practice_id", "the_order": 22},
            {"item_id": "CSRG", "item_description": "Sexual Exploitation and abuse", "item_sub_category": "sexual_exploit_id", "the_order": 34},
            {"item_id": "CLCM", "item_description": "Child Mother", "item_sub_category": "", "the_order": 41},
            {"item_id": "CIDC", "item_description": "Orphaned Child", "item_sub_category": "orphaned_child_id", "the_order": 28},
            {"item_id": "CSIC", "item_description": "Neglect", "item_sub_category": "neglect_denial_id", "the_order": 27},
            {"item_id": "CCMO", "item_description": "Mother Offer", "item_sub_category": "mother_offer_id", "the_order": 40},
            {"item_id": "CCDF", "item_description": "Defilement", "item_sub_category": "defilement_id", "the_order": 17},
            {"item_id": "CSTC", "item_description": "Trafficked child / Person", "item_sub_category": "trafficking_id", "the_order": 37},
            {"item_id": "CSSM", "item_description": "Smuggling", "item_sub_category": "", "the_order": 43},
            {"item_id": "CCIP", "item_description": "Children / Persons on the streets", "item_sub_category": "on_streets_id", "the_order": 15},
            {"item_id": "CDIS", "item_description": "Abandoned", "item_sub_category": None, "the_order": 1},
            {"item_id": "CDSA", "item_description": "Abduction", "item_sub_category": None, "the_order": 2},
            {"item_id": "CLAB", "item_description": "Child Affected by HIV/AIDS", "item_sub_category": None, "the_order": 3},
            {"item_id": "CORP", "item_description": "Child Delinquency", "item_sub_category": None, "the_order": 4},
            {"item_id": "COSR", "item_description": "Child headed household", "item_sub_category": None, "the_order": 5},
            {"item_id": "CTRF", "item_description": "Child Labour", "item_sub_category": "child_labour_id", "the_order": 6},
            {"item_id": "CCCM", "item_description": "Child Marriage", "item_sub_category": None, "the_order": 7},
            {"item_id": "SCCI", "item_description": "Child of imprisoned parent (s)", "item_sub_category": None, "the_order": 8},
            {"item_id": "CSAB", "item_description": "Child offender", "item_sub_category": "offender_id", "the_order": 9},
            {"item_id": "CSAD", "item_description": "Child out of school", "item_sub_category": None, "the_order": 10},
            {"item_id": "CSHV", "item_description": "Child pregnancy", "item_sub_category": None, "the_order": 11},
            {"item_id": "CSDQ", "item_description": "Child radicalization", "item_sub_category": None, "the_order": 12},
            {"item_id": "CCCT", "item_description": "Child truancy", "item_sub_category": "out_of_school_id", "the_order": 13},
            {"item_id": "CSCL", "item_description": "Child with disability", "item_sub_category": None, "the_order": 14},
            {"item_id": "CCCP", "item_description": "Custody", "item_sub_category": "custody_id", "the_order": 16},
            {"item_id": "CSCT", "item_description": "Disputed paternity", "item_sub_category": None, "the_order": 18},
            {"item_id": "CSDS", "item_description": "Drug and Substance Abuse", "item_sub_category": "drug_abuse_id", "the_order": 19},
            {"item_id": "CCEA", "item_description": "Emotional Abuse", "item_sub_category": "emotional_abuse_id", "the_order": 20},
            {"item_id": "CSCS", "item_description": "FGM", "item_sub_category": None, "the_order": 21},
            {"item_id": "CSDF", "item_description": "Incest", "item_sub_category": None, "the_order": 23},
            {"item_id": "CSDP", "item_description": "Inheritance/Succession", "item_sub_category": None, "the_order": 24},
            {"item_id": "CSRC", "item_description": "Sexual assault", "item_sub_category": None, "the_order": 33},
            {"item_id": "CFGM", "item_description": "Internally displaced child", "item_sub_category": None, "the_order": 25},
            {"item_id": "CLFC", "item_description": "Parental child abduction", "item_sub_category": None, "the_order": 29},
            {"item_id": "CSSA", "item_description": "Sick Child (Chronic Illness)", "item_sub_category": None, "the_order": 35},
            {"item_id": "CSSO", "item_description": "Sodomy", "item_sub_category": None, "the_order": 36},
            {"item_id": "CSNG", "item_description": "Physical abuse/violence", "item_sub_category": None, "the_order": 30},
            {"item_id": "CPCA", "item_description": "Refugee Children", "item_sub_category": None, "the_order": 31},
            {"item_id": "CPAV", "item_description": "Registration", "item_sub_category": None, "the_order": 32},
            {"item_id": "CSUC", "item_description": "Unlawful confinement", "item_sub_category": None, "the_order": 38},
            {"item_id": "CHCP", "item_description": "Missing Child (Lost & Found)", "item_sub_category": None, "the_order": 26},
            {"item_id": "CCDT", "item_description": "Destitution", "item_sub_category": None, "the_order": 42},
            {"item_id": "CCOA", "item_description": "Online Child Exploitation and Abuse", "item_sub_category": "online_abuse_id", "the_order": 39}
        ]
        
        # Debug logging for token pickup
        logger.info(f"🔑 CPIMS Token Debug:")
        logger.info(f"   Raw token from settings: '{self.cpims_auth_token}'")
        logger.info(f"   Token length: {len(self.cpims_auth_token) if self.cpims_auth_token else 0}")
        logger.info(f"   Token exists: {bool(self.cpims_auth_token)}")
    
    def handle_verification(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        CPIMS doesn't require verification challenges.
        """
        return None
    
    def validate_request(self, request: Any) -> bool:
        """
        Validate authenticity of incoming Helpline request.
        
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
            
            # Check for required fields for CPIMS case creation
            required_fields = ["cases", "reporters"]
            
            # Validate required fields exist
            for field in required_fields:
                if field not in payload:
                    logger.error(f"Missing required field for CPIMS: {field}")
                    return False
            
            # Validate that cases array has at least one item
            if not payload["cases"] or len(payload["cases"]) == 0:
                logger.error("Cases array cannot be empty")
                return False
                
            # Validate that reporters array has at least one item  
            if not payload["reporters"] or len(payload["reporters"]) == 0:
                logger.error("Reporters array cannot be empty")
                return False
                
            # Note: clients array can be empty in some cases, so we don't validate it as required
                    
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

            # Debug logging - only show what's being sent to CPIMS
            logger.info(f"📤 Sending case to CPIMS: {self.cpims_endpoint}")
            logger.info("=== CPIMS OUTGOING PAYLOAD ===")
            logger.info(json.dumps(outgoing_payload, indent=2))
            logger.info("=== END CPIMS PAYLOAD ===")

            # Prepare headers
            headers = {
                'Content-Type': 'application/json'
            }

            # Add authorization if token is configured (optional for test environment)
            logger.info(f"🔐 Header Preparation Debug:")
            logger.info(f"   Token value: '{self.cpims_auth_token}'")
            logger.info(f"   Token bool check: {bool(self.cpims_auth_token)}")

            if self.cpims_auth_token:
                # CPIMS expects the token directly in Authorization header (as per Postman)
                headers['Authorization'] = f"Token {self.cpims_auth_token}"

                logger.info(f"✅ Using CPIMS authentication token in Authorization header")
                logger.info(f"   Token: {self.cpims_auth_token[:8]}...{self.cpims_auth_token[-8:]}")
            else:
                logger.info("❌ No CPIMS auth token - proceeding without authentication")

            logger.info(f"📋 Final headers: {dict(headers)}")

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
        
        # Extract location from reporter data (since clients array is empty in real payload)
        # Region: reporters[0][39] = "CENTRAL" (contact_location_0)  
        # District: reporters[0][40] = "WAKISO" (contact_location_1)
        # County: reporters[0][41] = "ENTEBBE MUNICIPALITY" (contact_location_2)
        # Sub County: reporters[0][42] = "DIVISION A" (contact_location_3)
        # Parish: reporters[0][43] = "CENTRAL" (contact_location_4)  
        # Village: reporters[0][44] = "LUNYO CENTRAL" (contact_location_5)
        
        # Use reporter location data since clients array is empty
        # Corrected mapping based on actual data structure:
        county_name = get_safe(reporter_data, 39, "")  # contact_location_0 - County (was Region)
        constituency_name = get_safe(reporter_data, 40, "")  # contact_location_1 - Constituency (was District)  
        ward_name = get_safe(reporter_data, 41, "")  # contact_location_2 - Ward (was County)
        subcounty_name = get_safe(reporter_data, 42, "")  # contact_location_3 - Sub County
        
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
            
        # Log the extracted location values for debugging
        logger.info(f"🌍 Location Extraction Debug:")
        logger.info(f"   County (reporter contact_location_0, index 39): '{county_name}'")
        logger.info(f"   Constituency (reporter contact_location_1, index 40): '{constituency_name}'")
        logger.info(f"   Ward (reporter contact_location_2, index 41): '{ward_name}'")
        logger.info(f"   Sub County (reporter contact_location_3, index 42): '{subcounty_name}'")
        logger.info(f"🌍 Location Extraction Debug (API Format):")
        logger.info(f"   County: '{county_name}'")
        logger.info(f"   Constituency: '{constituency_name}'")
        logger.info(f"   Ward: '{ward_name}'")
        logger.info(f"   Full reporter_location: '{reporter_location}'")
        
        # Look up area_code values from CPIMS geo API using type-specific lookups for better accuracy
        parish_name = get_safe(reporter_data, 43, "")  # contact_location_4 - Parish
        
        # Use type-specific lookups for better disambiguation
        county_code = self._lookup_area_code_by_type(county_name, "GPRV") if county_name else None
        constituency_code = self._lookup_area_code_by_type(constituency_name, "GDIS") if constituency_name else None
        ward_code = self._lookup_area_code_by_type(ward_name, "GWRD") if ward_name else None
        # Look up area_code values from CPIMS geo API
        county_code = self._lookup_area_code_by_type(county_name, "GPRV") if county_name else None
        constituency_code = self._lookup_area_code_by_type(constituency_name, "GDIS") if constituency_name else None
        ward_code = self._lookup_area_code_by_type(ward_name, "GWRD") if ward_name else None
        
        # Fallback to generic lookup for broader compatibility if type-specific lookup fails
        if not county_code and county_name:
            county_code = self._lookup_area_code(county_name)
        if not constituency_code and constituency_name:
            constituency_code = self._lookup_area_code(constituency_name)
        
        # Fallback to generic lookup if type-specific lookup fails
        if not county_code and county_name:
            county_code = self._lookup_area_code(county_name)
        if not constituency_code and constituency_name:
            constituency_code = self._lookup_area_code(constituency_name)
        if not ward_code and ward_name:
            ward_code = self._lookup_area_code(ward_name)
            
        # Log the lookup results
        logger.info(f"🔍 Location Lookup Results:")
        logger.info(f"   County '{county_name}' -> area_code: '{county_code}' (GPRV)")
        logger.info(f"   Constituency '{constituency_name}' -> area_code: '{constituency_code}' (GDIS)")
        logger.info(f"   Ward '{ward_name}' -> area_code: '{ward_code}' (GWRD)")
        logger.info(f"🔍 Location Lookup Results (API Format):")
        logger.info(f"   County '{county_name}' -> area_code: '{county_code}'")
        logger.info(f"   Constituency '{constituency_name}' -> area_code: '{constituency_code}'")
        logger.info(f"   Ward '{ward_name}' -> area_code: '{ward_code}'")
        
        # Extract case category 
        category_description = get_safe(case_data, "cat_0", "")
        
        # Log the extracted category value for debugging
        logger.info(f"📂 Category Extraction Debug (API Format):")
        logger.info(f"   Category (cat_0): '{category_description}'")
        
        # Look up item_id for the category description
        category_item_id = self._lookup_category_item_id(category_description) if category_description else None
        
        # Log the category lookup result
        logger.info(f"🔍 Category Lookup Results (API Format):")
        logger.info(f"   Category '{category_description}' -> item_id: '{category_item_id}'")
        
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
            # Basic case information - using the mapping you provided with required field fallbacks
            "physical_condition": "PNRM",  # Default to "Appears Normal" - not available in this payload structure
            "county": county_code or "UNK",  # Use the actual county area_code found
            "sub_county_code": constituency_code or "UNK",  # Use constituency code as sub_county_code
            "hh_economic_status": "UINC",  # Default to Unknown - not available in this payload structure
            "other_condition": "CHNM",  # Default to "Appears Normal" - not available in this payload structure  
            "child_sex": self._map_code(get_person_data(18, 16, ""), "sex") or "SMAL",  # Use person data with fallback
            "reporter_first_name": self._extract_name(get_safe(reporter_data, 6, ""), "first") or "Unknown",  # reporter contact_fullname
            "ob_number": get_safe(case_data, 41, ""),  # case police_ob_no
            "longitude": None,
            "recommendation_bic": get_safe(case_data, 40, ""),  # case plan
            "family_status": "FSLA",  # Default to "Living alone" - not available in this payload structure
            "reporter_other_names": self._extract_name(get_safe(reporter_data, 6, ""), "other"),  # reporter contact_fullname
            "case_date": self._format_timestamp(get_safe(case_data, 1, "")),  # case created_on
            "child_other_names": self._extract_name(get_person_data(7, 6, ""), "other"),  # Use person data
            # Basic case information
            "physical_condition": "PNRM",  # Default - not available in API payload
            "county": county_code or "UNK",
            "sub_county_code": constituency_code or "UNK",
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
            "sublocation": ward_name or "Unknown",
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
            "case_landmark": ward_name or county_name or "Helpline Report",  # Use ward or county as landmark
            "case_landmark": get_safe(case_data, "reporter_landmark", "") or ward_name or county_name or "Helpline Report",
            "religion_type": None,
            "long_term_needs": None,
            "immediate_needs": None,
            "mental_condition": "MNRM",  # Default
            "police_station": "",
            "risk_level": self._map_code(get_safe(case_data, 35, ""), "risk_level") or "RLMD",  # case priority with default
            "constituency": (constituency_code or "UNK")[:3],  # Use the actual constituency area_code found, max 3 chars
            "risk_level": self._map_code(get_safe(case_data, "priority", ""), "risk_level") or "RLMD",
            "constituency": (constituency_code or "UNK")[:3],  # Max 3 chars
            "hobbies": None,
            "reporter_email": get_safe(reporter_data, 10, ""),  # reporter contact_email
            "location": get_safe(reporter_data, 44, "") or "Unknown",  # reporter village
            "reporter_county": county_code or "UNK",  # County area_code from lookup
            "reporter_sub_county": constituency_code or "UNK",  # Constituency area_code as sub_county
            "reporter_ward": ward_code or get_safe(reporter_data, 43, "UNKNOWN_WARD"),  # Ward area_code from GWRD lookup with fallback
            "reporter_village": get_safe(reporter_data, 44, "UNKNOWN_VILLAGE"),  # reporter village
            "reporter_email": get_safe(case_data, "reporter_email", ""),
            "location": get_safe(case_data, "reporter_location_5", "") or ward_name or "Unknown",
            "reporter_county": county_code or "UNK",
            "reporter_sub_county": constituency_code or "UNK", 
            "reporter_ward": ward_code or "UNKNOWN_WARD",
            "reporter_village": get_safe(case_data, "reporter_location_5", "") or "UNKNOWN_VILLAGE",
            "has_birth_cert": None,
            "user": get_safe(case_data, 2, "helpline_user"),  # case created_by
            "area_code": county_code or "UNK",  # Always include the actual county area_code in payload
            
            "user": get_safe(case_data, "created_by", "helpline_user"),
            "area_code": county_code or "UNK",

            # Case details array
            "case_details": [{
                "place_of_event": get_safe(case_data, "incidence_location", ""),
                "category": category_item_id or category_description,
                "nature_of_event": self._map_code(get_safe(case_data, "cat_2", ""), "case_nature"),
                "date_of_event": format_api_timestamp(get_safe(case_data, "incidence_when", ""))
            }],
            
            # Categories array
            "categories": [{
                "case_category": category_item_id or category_description,
                "case_sub_category": get_safe(case_data, "cat_1", ""),
                "case_date_event": format_api_timestamp(get_safe(case_data, "incidence_when", "")),
                "case_nature": self._map_code(get_safe(case_data, "cat_2", ""), "case_nature"),
                "case_place_of_event": get_safe(case_data, "incidence_location", ""),
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

        # Debug log for final payload structure
        logger.info(f"[CPIMS PAYLOAD] Final payload structure created from API data")
        logger.info(f"   Case ID: '{cpims_payload.get('case_details', [{}])[0].get('case_id', 'N/A')}'")
        logger.info(f"   Reporter County: '{cpims_payload['reporter_county']}'")
        logger.info(f"   Child Name: '{cpims_payload['child_first_name']} {cpims_payload['child_surname']}'")
        
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
            logger.info(f"📍 Fetching geo data from CPIMS: {self.cpims_geo_endpoint}")
            
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
                logger.info(f"Found area_code '{area_code}' for area '{area_name}' with type '{area_type_id}'")
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
                logger.info(f"Found area_type_id '{area_type_id}' for area '{area_name}'")
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
                logger.info(f"Found area_code '{area_code}' for area '{area_name}'")
                return area_code
                
        logger.warning(f"Area '{area_name}' not found in CPIMS geo data")
        return None
    
    
    def _lookup_category_item_id(self, category_description: str) -> Optional[str]:
        """
        Look up item_id for a given category description from CPIMS case categories.
        
        Args:
            category_description: The description of the category to look up
            
        Returns:
            The item_id if found, None otherwise
        """
        if not category_description:
            return None
        
        # Search for the category by description (case-insensitive)
        category_description_lower = category_description.lower().strip()
        
        for category in self.case_categories:
            if category.get('item_description', '').lower().strip() == category_description_lower:
                item_id = category.get('item_id')
                logger.info(f"Found item_id '{item_id}' for category '{category_description}'")
                return item_id
        
        logger.warning(f"Category '{category_description}' not found in CPIMS categories")
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
        
        # Risk level codes - handle both description and order number
        risk_level_codes = {
            "Low": "RLLW",
            "Medium": "RLMD", 
            "High": "RLHG",
            "1": "RLLW",
            "2": "RLMD", 
            "3": "RLHG"
        }
        
        # Case reporter codes
        case_reporter_codes = {
            "Self": "CRSF",
            "Helpline 116": "CRHE",
            "Police": "CRPO",
            "Father": "CRFA",
            "Mother": "CRMO",
            "Court": "CRCO",
            "Other relative(s)": "CROR",
            "Other non-relative(s)": "CRON",
            "Probation": "CRPR",
            "Chief": "CRCH",
            "Immigration": "CRIM",
            "Helpline 1195": "CRHL",
            "Service Providers": "CRSP",
            "Labour Officers": "CRLO",
            "Ministry of Tourism": "CRMT",
            "Trade Union": "CRTU",
            "Diplomatic missions": "CRDM",
            "Other Government agency": "CROG"
        }
        
        # Family status codes
        family_status_codes = {
            "Caregiver is more than 60 years old": "FSOL",
            "Living with biological parents": "CCBP",
            "Living with adoptive parents": "CCAP",
            "Living in child-headed household (no adult caregiver)": "FSHD",
            "Living alone": "FSLA",
            "Living with a friend": "FSLF",
            "Caregiver is chronically ill": "FSCI",
            "Caregiver is disabled": "FSCD",
            "Living in children home": "FSCH",
            "Living with father only": "CCFO",
            "In institution with mother (has child mother)": "RSMI",
            "Informal Guardian": "CCIG",
            "Living in poor household (destitute)": "FSPH",
            "Living on the Street": "CCLS",
            "Living with mother only": "CCMO",
            "Orphaned - father dead": "FSOF",
            "Orphaned - mother dead": "FSOM",
            "Other Family": "CCOF"
        }
        
        # Tribe codes
        tribe_codes = {
            "Kisii": "TRII",
            "Kikuyu": "TRKI",
            "Luhya": "TRLU",
            "Luo": "TRLO",
            "American": "TRAM",
            "European": "TREU",
            "Kalenjin": "TRKE",
            "Kamba": "TRKA",
            "Kenyan Somali": "TRKS",
            "Kuria": "TRKU",
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
        
        # Case category codes
        case_category_codes = {
            "Neglect": "CSIC",
            "Defilement": "CCDF",
            "Trafficked child / Person": "CSTC",
            "Harmful cultural practice": "CSCU",
            "Sexual Exploitation and abuse": "CSRG",    
            "Child Mother": "CLCM",
            "Online Abuse": "CCOA",
            "Orphaned Child": "CIDC",
            "Mother Offer": "CCMO",
            "Smuggling": "CSSM",
            "Children / Persons on the streets": "CCIP",
            "Abandoned": "CDIS",
            "Abduction": "CDSA",
            "Child Affected by HIV/AIDS": "CLAB",
            "Child Delinquency": "CORP",
            "Child headed household": "COSR",
            "Child Labour": "CTRF",
            "Child Marriage": "CCCM"
        }
        
        # Case nature codes
        case_nature_codes = {
            "Chronic/On-going event": "OCGE",
            "One-off event": "OOEV",
            "Emergency": "OOEM"
        }
        
        # Relationship codes (for perpetrators)
        relationship_codes = {
            "Commercial Drivers": "RCCD",
            "Employer": "RCEP",
            "Friend": "RCFD",
            "Health care worker": "RCHW",
            "Local Influentials": "RCLI",
            "Neighbour": "RCNB",
            "Other non-family": "RCOT",
            "Other family member": "ROFM",
            "Other Humanitarian Worker": "ROHW",
            "Other Primary Care Giver/Guardian": "ROCG",
            "Other person in positions of authority": "ROPA",
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

        # For risk_level, enforce strict mapping to ensure CPIMS codes are emitted
        if mapping_type == "risk_level":
            # Return empty string if not found so caller can apply a safe default
            return mapping_dict.get(normalized_value, "")

        # Return the mapped value or the original value if not found (non-strict)
        return mapping_dict.get(normalized_value, value)

