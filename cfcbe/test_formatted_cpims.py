#!/usr/bin/env python3
"""
Test CPIMS Adapter with Properly Formatted Payload
"""

import os
import sys
import json
import django
from pathlib import Path

# Add the Django project path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfcbe.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from platform_adapters.cpims.helpline_cpims_abuse_adapter import HelplineCPIMSAbuseAdapter

def main():
    """Main test execution."""
    print("🔧 Testing CPIMS Adapter with Direct JSON Object")
    print("="*60)
    
    # Use the provided JSON object directly in the format the adapter expects
    payload = {
        "id": "31687",
        "created_on": "1757487391",
        "created_by": "test",
        "created_by_id": "273",
        "created_by_role": "99",
        "gbv_related": "1",
        "case_category_id": "387389",
        "case_category": "^Abuse & Violence",
        "case_category_root_id": "362559",
        "case_category_fullname_id": "387389:Abuse & Violence^",
        "cat_id_0": "387389",
        "cat_id_1": "0",
        "cat_id_2": "0",
        "cat_id_3": "0",
        "cat_id_4": "0",
        "cat_0": "Abuse & Violence",
        "cat_1": "",
        "cat_2": "",
        "cat_3": "",
        "cat_4": "",
        "narrative": "Agnes from Murang'a is severely beaten by her father when he's drunk for no reason.",
        "plan": "Agnes needs to be sheltered from her abusive father.",
        "src": "walkin",
        "src_uid": "walkin-100-1757484659785",
        "src_vector": "2",
        "reporter_id": "86732",
        "reporter_contact_id": "133243",
        "reporter_fullname": "Agnes Wacera",
        "reporter_phone": "254728769034",
        "reporter_national_id": "24567895",
        "reporter_landmark": "ACC church",
        "reporter_dob": "1252530000",
        "reporter_age": "16",
        "reporter_age_group": "^15-17",
        "reporter_sex": "^Female",
        "reporter_nationality": "^Kenyan",
        "reporter_location": "^Murang'a^Kandara^Kagundu-Ini",
        "reporter_location_0": "Murang'a",
        "reporter_location_1": "Kandara", 
        "reporter_location_2": "Kagundu-Ini",
        "reporter_location_3": "",
        "reporter_location_4": "",
        "reporter_location_5": "",
        "priority": "3",
        "status": "1",
        "disposition": "Complete",
        "final_status": "1",
        "perpetrators": [],
        "clients": [{
            "id": "44266",
            "contact_fullname": "Agnes Wacera",
            "contact_phone": "254728769034",
            "contact_age": "16",
            "contact_sex": "^Female",
            "contact_nationality": "^Kenyan",
            "contact_location_0": "Murang'a",
            "contact_location_1": "Kandara",
            "contact_location_2": "Kagundu-Ini"
        }],
        "services": [],
        "referals": []
    }
    
    print(f"📄 Testing with case ID: {payload.get('id')}")
    print(f"   Reporter: {payload.get('reporter_fullname')}")
    print(f"   Location: {payload.get('reporter_location_0')}")
    print(f"   Category: {payload.get('cat_0')}")
    print(f"   Narrative: {payload.get('narrative')[:50]}...")
    
    # Initialize adapter
    try:
        adapter = HelplineCPIMSAbuseAdapter()
        print("✅ Adapter initialized successfully")
    except Exception as e:
        print(f"❌ Adapter initialization failed: {e}")
        return
    
    # Test processing
    print("\n=== Testing Direct Payload Processing ===")
    try:
        # Try to process the payload using the adapter's format expectations
        result = adapter.process_message(payload)
        print(f"✅ Process message result: {result}")
        
    except Exception as e:
        print(f"❌ Direct processing failed: {e}")
        
        # Try alternative approach - wrapping in expected structure
        print("\n=== Testing Alternative Structure ===")
        try:
            # Based on the comprehensive test, it expects this structure
            wrapped_payload = payload  # Direct use
            
            # Test validation
            is_valid = adapter.validate_request(wrapped_payload)
            print(f"Validation result: {is_valid}")
            
            # Test message parsing
            messages = adapter.parse_messages(wrapped_payload)
            print(f"✅ Parsed {len(messages)} message(s)")
            
            if messages:
                msg = messages[0]
                print(f"   Message content preview: {msg.get('content', '')[:100]}...")
                
                # Test CPIMS mapping
                cpims_payload = adapter._map_to_cpims_format(wrapped_payload)
                print(f"✅ CPIMS mapping successful with {len(cpims_payload)} fields")
                
                # Show key mapped fields with actual data
                key_fields = ['case_narration', 'reporter_first_name', 'county', 'child_sex', 'area_code']
                print("\n   Mapped fields:")
                for field in key_fields:
                    if field in cpims_payload:
                        print(f"     {field}: {cpims_payload[field]}")
                
                print("\n   Sample CPIMS payload structure:")
                sample_keys = list(cpims_payload.keys())[:10]
                for key in sample_keys:
                    print(f"     {key}: {cpims_payload[key]}")
                
                # Test StandardMessage creation
                standard_msg = adapter.to_standard_message(msg)
                print(f"\n✅ StandardMessage created: {standard_msg.message_id}")
                
        except Exception as e:
            print(f"❌ Alternative processing failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()