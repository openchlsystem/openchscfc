#!/usr/bin/env python3
"""
Comprehensive Test Script for CPIMS Adapter

This script tests the HelplineCPIMSAbuseAdapter with the provided sample payload
to verify that all components are working correctly.
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
from shared.models.standard_message import StandardMessage

def load_sample_payload():
    """Load the sample payload from the JSON file."""
    try:
        with open('test_sample_payload.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ test_sample_payload.json not found. Creating it first...")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return None

def test_adapter_initialization():
    """Test that the adapter initializes correctly."""
    print("\n=== Testing Adapter Initialization ===")
    try:
        adapter = HelplineCPIMSAbuseAdapter()
        print("✅ Adapter initialized successfully")
        print(f"   CPIMS endpoint: {adapter.cpims_endpoint}")
        print(f"   CPIMS geo endpoint: {adapter.cpims_geo_endpoint}")
        print(f"   Auth token configured: {'Yes' if adapter.cpims_auth_token else 'No'}")
        print(f"   Case categories loaded: {len(adapter.case_categories)} categories")
        return adapter
    except Exception as e:
        print(f"❌ Adapter initialization failed: {e}")
        return None

def test_payload_validation(adapter, payload):
    """Test payload validation."""
    print("\n=== Testing Payload Validation ===")
    try:
        is_valid = adapter.validate_request(payload)
        print(f"✅ Payload validation result: {is_valid}")
        
        if is_valid:
            print("   ✓ Required fields present")
            print(f"   ✓ Cases array has {len(payload.get('cases', []))} entries")
            print(f"   ✓ Reporters array has {len(payload.get('reporters', []))} entries")
        else:
            print("   ❌ Validation failed - check required fields")
        
        return is_valid
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

def test_message_parsing(adapter, payload):
    """Test message parsing functionality."""
    print("\n=== Testing Message Parsing ===")
    try:
        messages = adapter.parse_messages(payload)
        print(f"✅ Parsed {len(messages)} message(s)")
        
        if messages:
            msg = messages[0]
            print(f"   Message ID: {msg.get('message_id')}")
            print(f"   Source: {msg.get('source')}")
            print(f"   Platform: {msg.get('platform')}")
            print(f"   Content Type: {msg.get('content_type')}")
            print(f"   Content Preview: {msg.get('content', '')[:100]}...")
            print(f"   Metadata keys: {list(msg.get('metadata', {}).keys())}")
        
        return messages
    except Exception as e:
        print(f"❌ Message parsing failed: {e}")
        return []

def test_cpims_mapping(adapter, payload):
    """Test the CPIMS payload mapping without sending."""
    print("\n=== Testing CPIMS Mapping ===")
    try:
        cpims_payload = adapter._map_to_cpims_format(payload)
        
        print("✅ CPIMS mapping successful")
        print(f"   Mapped payload has {len(cpims_payload)} top-level fields")
        
        # Show key mapped fields
        key_fields = [
            'physical_condition', 'county', 'sub_county_code', 'child_sex',
            'reporter_first_name', 'case_date', 'child_first_name', 
            'case_narration', 'risk_level', 'area_code'
        ]
        
        print("\n   Key mapped fields:")
        for field in key_fields:
            value = cpims_payload.get(field, 'NOT_FOUND')
            print(f"     {field}: {value}")
        
        # Show array lengths
        arrays = ['case_details', 'categories', 'perpetrators', 'siblings']
        print(f"\n   Array fields:")
        for array_name in arrays:
            array_val = cpims_payload.get(array_name, [])
            print(f"     {array_name}: {len(array_val)} items")
        
        return cpims_payload
        
    except Exception as e:
        print(f"❌ CPIMS mapping failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_standard_message_creation(adapter, messages):
    """Test StandardMessage object creation."""
    print("\n=== Testing StandardMessage Creation ===")
    try:
        if not messages:
            print("❌ No messages to convert")
            return None
            
        msg_dict = messages[0]
        standard_msg = adapter.to_standard_message(msg_dict)
        
        print("✅ StandardMessage created successfully")
        print(f"   Message ID: {standard_msg.message_id}")
        print(f"   Source: {standard_msg.source}")
        print(f"   Platform: {standard_msg.platform}")
        print(f"   Content Type: {standard_msg.content_type}")
        print(f"   Has metadata: {'Yes' if standard_msg.metadata else 'No'}")
        
        return standard_msg
        
    except Exception as e:
        print(f"❌ StandardMessage creation failed: {e}")
        return None

def test_data_extraction(payload):
    """Test extraction of specific data points from the payload."""
    print("\n=== Testing Data Extraction ===")
    try:
        case_data = payload.get("cases", [[]])[0]
        reporter_data = payload.get("reporters", [[]])[0] if payload.get("reporters") else []
        
        # Test key data extractions
        print("✅ Key data points extracted:")
        print(f"   Case ID: {case_data[0] if case_data else 'N/A'}")
        print(f"   Case Narrative: {case_data[39] if len(case_data) > 39 else 'N/A'}")
        print(f"   Reporter Name: {reporter_data[6] if len(reporter_data) > 6 else 'N/A'}")
        print(f"   Reporter Phone: {reporter_data[9] if len(reporter_data) > 9 else 'N/A'}")
        print(f"   County: {reporter_data[41] if len(reporter_data) > 41 else 'N/A'}")
        print(f"   Sub County: {reporter_data[42] if len(reporter_data) > 42 else 'N/A'}")
        print(f"   Category: {case_data[15] if len(case_data) > 15 else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data extraction test failed: {e}")
        return False

def test_send_message_preparation(adapter, standard_msg):
    """Test message sending preparation (without actually sending)."""
    print("\n=== Testing Send Message Preparation ===")
    try:
        # We'll test the preparation part without actually sending
        metadata = standard_msg.metadata if hasattr(standard_msg, 'metadata') else {}
        
        if not metadata:
            print("❌ No metadata available for sending")
            return False
        
        # Test CPIMS format mapping (this would be called in send_message)
        cpims_payload = adapter._map_to_cpims_format(metadata)
        
        print("✅ Send message preparation successful")
        print(f"   CPIMS payload ready with {len(cpims_payload)} fields")
        print(f"   Would send to: {adapter.cpims_endpoint}")
        
        return True
        
    except Exception as e:
        print(f"❌ Send message preparation failed: {e}")
        return False

def print_test_summary(results):
    """Print a summary of all test results."""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<40} {status}")
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed! The CPIMS adapter is working correctly.")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Please check the errors above.")

def main():
    """Main test execution."""
    print("🔧 CPIMS Adapter Comprehensive Test Suite")
    print("="*60)
    
    # Load sample payload
    payload = load_sample_payload()
    if not payload:
        print("❌ Cannot proceed without sample payload")
        return
    
    print(f"📄 Loaded sample payload with {len(payload)} top-level keys")
    
    # Track test results
    results = {}
    
    # Test 1: Adapter Initialization
    adapter = test_adapter_initialization()
    results["Adapter Initialization"] = adapter is not None
    
    if not adapter:
        print("❌ Cannot proceed without adapter")
        print_test_summary(results)
        return
    
    # Test 2: Payload Validation
    is_valid = test_payload_validation(adapter, payload)
    results["Payload Validation"] = is_valid
    
    # Test 3: Data Extraction
    extraction_ok = test_data_extraction(payload)
    results["Data Extraction"] = extraction_ok
    
    # Test 4: Message Parsing
    messages = test_message_parsing(adapter, payload)
    results["Message Parsing"] = len(messages) > 0
    
    # Test 5: CPIMS Mapping
    cpims_payload = test_cpims_mapping(adapter, payload)
    results["CPIMS Mapping"] = cpims_payload is not None
    
    # Test 6: StandardMessage Creation
    standard_msg = None
    if messages:
        standard_msg = test_standard_message_creation(adapter, messages)
        results["StandardMessage Creation"] = standard_msg is not None
    else:
        results["StandardMessage Creation"] = False
    
    # Test 7: Send Message Preparation
    if standard_msg:
        send_prep_ok = test_send_message_preparation(adapter, standard_msg)
        results["Send Message Preparation"] = send_prep_ok
    else:
        results["Send Message Preparation"] = False
    
    # Print final summary
    print_test_summary(results)
    
    # Show final CPIMS payload if mapping was successful
    if cpims_payload:
        print("\n" + "="*60)
        print("FINAL CPIMS PAYLOAD (Preview)")
        print("="*60)
        print(json.dumps(cpims_payload, indent=2)[:2000])
        if len(json.dumps(cpims_payload, indent=2)) > 2000:
            print("... (truncated for readability)")

if __name__ == "__main__":
    main()