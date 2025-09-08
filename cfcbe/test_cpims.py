#!/usr/bin/env python3
"""
CPIMS Adapter Test Script

Usage:
    python test_cpims.py
    python test_cpims.py --url http://localhost:8000
    python test_cpims.py --verbose
"""

import requests
import json
import argparse
import sys
from datetime import datetime

# Sample test payload
SAMPLE_PAYLOAD = {
    "cases": [
        [
            "TEST001",  # [0] Case ID
            "1703678400",  # [1] Created timestamp
            "test_user",  # [2] User
            "", "", "", "", "", "", "", "", "", "", "", "",  # [3-14] Empty fields
            "Sexual Exploitation and abuse",  # [15] Category (cat_0)
            "Online harassment",  # [16] Sub-category (cat_1)  
            "Chronic/On-going event",  # [17] Nature (cat_2)
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",  # [18-34] Empty fields
            "High",  # [35] Priority/Risk level
            "", "", "",  # [36-38] Empty fields
            "Child reported being harassed online by unknown person",  # [39] Narrative
            "Provide counseling and report to authorities",  # [40] Plan
            "OB/001/2024",  # [41] Police OB number
            "Central Police Station",  # [42] Police station
            "", "", "", "", "", "", "", "", "",  # [43-51] Empty fields
            "Online platform",  # [52] Incident location
            "1703678400"  # [53] Incident date
        ]
    ],
    "reporters": [
        [
            "REP001",  # [0] Reporter ID
            "1703678400",  # [1] Timestamp
            "test_user",  # [2] User
            "", "", "",  # [3-5] Empty fields
            "Jane Doe",  # [6] Full name
            "", "",  # [7-8] Empty fields
            "0700123456",  # [9] Phone
            "jane.doe@email.com",  # [10] Email
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",  # [11-47] Empty fields
            "Self"  # [48] Relationship
        ]
    ],
    "clients": [
        [
            "CLIENT001",  # [0] Client ID
            "1703678400",  # [1] Timestamp  
            "test_user",  # [2] User
            "", "", "", "",  # [3-6] Empty fields
            "Mary Smith",  # [7] Full name
            "", "", "", "", "",  # [8-12] Empty fields
            "946684800",  # [13] Date of birth (timestamp)
            "", "", "", "",  # [14-17] Empty fields
            "Female",  # [18] Gender
            "", "", "", "", "", "", "", "",  # [19-26] Empty fields
            "Kikuyu",  # [27] Tribe
            "Christian",  # [28] Religion
            "", "", "", "",  # [29-32] Empty fields
            "Nairobi Central",  # [33] Location/Landmark (contact_location_0 - County)
            "Nairobi",  # [34] County name (contact_location_0)
            "Starehe",  # [35] Constituency (contact_location_1)
            "Nairobi Central Ward",  # [36] Ward (contact_location_2)
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",  # [37-56] Empty fields
            "Appears Normal",  # [57] Physical condition
            "",  # [58] Empty field
            "Appears Normal",  # [59] Other condition
            "", "",  # [60-61] Empty fields
            "None reported",  # [62] Special services/remarks
            "Yes",  # [63] In school
            "", "", "",  # [64-66] Empty fields
            "Grade 8",  # [67] School level/class
            "",  # [68] Empty field
            "Nairobi Primary School",  # [69] School name
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",  # [70-85] Empty fields
            "Middle Income (apparent)"  # [86] Economic status
        ]
    ],
    "perpetrators": [
        [
            "PERP001",  # [0] Perpetrator ID
            "1703678400",  # [1] Timestamp
            "test_user",  # [2] User
            "", "", "", "",  # [3-6] Empty fields
            "Unknown Person",  # [7] Full name
            "", "", "", "", "", "", "", "", "",  # [8-17] Empty fields
            "Male",  # [18] Gender
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",  # [19-48] Empty fields
            "Strangers"  # [49] Relationship to victim
        ]
    ]
}

def test_cpims_adapter(base_url="http://localhost:8000", verbose=False):
    """Test the CPIMS adapter endpoint"""
    
    endpoint = f"{base_url}/api/webhook/helpline/cpims/abuse/"
    
    print("🧪 Testing CPIMS Adapter")
    print(f"📡 Endpoint: {endpoint}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Test 1: Check if server is running
    try:
        print("1️⃣ Testing server availability...")
        health_response = requests.get(f"{base_url}/admin/", timeout=5)
        if health_response.status_code in [200, 302]:
            print("   ✅ Server is running")
        else:
            print(f"   ❌ Server returned {health_response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Server not reachable: {e}")
        return False
    
    # Test 2: Send sample payload
    try:
        print("2️⃣ Sending test payload...")
        if verbose:
            print(f"   📦 Payload: {json.dumps(SAMPLE_PAYLOAD, indent=2)}")
        
        response = requests.post(
            endpoint,
            json=SAMPLE_PAYLOAD,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"   📊 Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            status = response_data.get('status', 'unknown')
            message = response_data.get('message', 'No message')
            
            if status == 'success':
                print(f"   ✅ SUCCESS: {message}")
                
                # Show CPIMS response details
                cpims_response = response_data.get('cpims_response', {})
                if 'case_id' in cpims_response:
                    print(f"   🎯 CPIMS Case ID: {cpims_response['case_id']}")
                if 'case_serial' in cpims_response:
                    print(f"   🎯 CPIMS Case Serial: {cpims_response['case_serial']}")
                if 'county' in cpims_response:
                    print(f"   🌍 County Code: {cpims_response['county']}")
                if 'constituency' in cpims_response:
                    print(f"   🌍 Constituency Code: {cpims_response['constituency']}")
                    
                if verbose and 'payload_sent' in response_data:
                    print(f"   📤 Payload sent to CPIMS:")
                    print(json.dumps(response_data['payload_sent'], indent=4))
                    
                return True
                
            elif status == 'error':
                print(f"   ❌ ERROR: {message}")
                details = response_data.get('details', '')
                if details:
                    print(f"   📋 Details: {details}")
                    
                if verbose and 'payload_sent' in response_data:
                    print(f"   📤 Payload that was sent:")
                    print(json.dumps(response_data['payload_sent'], indent=4))
                    
                return False
            else:
                print(f"   ⚠️ UNKNOWN STATUS: {status}")
                if verbose:
                    print(f"   📋 Full response: {json.dumps(response_data, indent=4)}")
                return False
                
        except json.JSONDecodeError:
            print(f"   ❌ Invalid JSON response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test CPIMS Adapter')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='Base URL of the Django server (default: http://localhost:8000)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed output including payloads')
    
    args = parser.parse_args()
    
    success = test_cpims_adapter(args.url, args.verbose)
    
    print("-" * 50)
    if success:
        print("🎉 All tests passed! CPIMS adapter is working correctly.")
        sys.exit(0)
    else:
        print("❌ Tests failed. Check the error messages above.")
        sys.exit(1)

if __name__ == '__main__':
    main()