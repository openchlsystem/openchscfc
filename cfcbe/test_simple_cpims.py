#!/usr/bin/env python3
"""
Simple Test Script for CPIMS Adapter with New JSON Object
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
    print("Make sure you're running this from the Django project root.")
    sys.exit(1)

# Now we can import Django modules
from platform_adapters.cpims.helpline_cpims_abuse_adapter import HelplineCPIMSAbuseAdapter

def load_test_payload():
    """Load the test payload from the JSON file."""
    try:
        with open('test_new_payload.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ test_new_payload.json not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return None

def main():
    """Main test execution."""
    print("🔧 Testing CPIMS Adapter with New JSON Object")
    print("="*60)
    
    # Load test payload
    payload = load_test_payload()
    if not payload:
        print("❌ Cannot proceed without payload")
        return
    
    print(f"📄 Loaded payload with case ID: {payload.get('id')}")
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
    
    # Test validation (this payload structure is different from expected format)
    print("\n=== Testing Payload Processing ===")
    try:
        # First, let's see what this adapter expects vs what we have
        print(f"Payload type: {type(payload)}")
        print(f"Payload keys: {list(payload.keys())[:10]}...")
        
        # Try to process as if it was in the expected format
        # The adapter might expect a different structure
        test_payload = {"cases": [payload], "reporters": []}
        
        messages = adapter.parse_messages(test_payload)
        print(f"✅ Parsed {len(messages)} message(s)")
        
        if messages:
            msg = messages[0]
            print(f"   Message ID: {msg.get('message_id')}")
            print(f"   Content preview: {msg.get('content', '')[:100]}...")
            
            # Test CPIMS mapping
            if hasattr(adapter, '_map_to_cpims_format'):
                try:
                    cpims_payload = adapter._map_to_cpims_format(test_payload)
                    print(f"✅ CPIMS mapping successful with {len(cpims_payload)} fields")
                    
                    # Show some key fields
                    key_fields = ['case_narration', 'reporter_first_name', 'county', 'child_sex']
                    for field in key_fields:
                        if field in cpims_payload:
                            print(f"   {field}: {cpims_payload[field]}")
                    
                except Exception as e:
                    print(f"❌ CPIMS mapping failed: {e}")
        else:
            print("❌ No messages were parsed")
            
    except Exception as e:
        print(f"❌ Payload processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()