#!/usr/bin/env python3
"""
Test script for real helpline payload
"""
import requests
import json

# Real payload from helpline
REAL_PAYLOAD = {
  "cases": [
    [
      "CASE001",
      "1703678400",
      "helpline_user",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "Sexual Exploitation and abuse",
      "Online harassment",
      "Chronic/On-going event",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "High",
      "",
      "",
      "",
      "Child reported being harassed online by unknown person",
      "Provide counseling and report to authorities",
      "OB/001/2024",
      "Central Police Station",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "Online platform",
      "1703678400"
    ]
  ],
  "reporters": [
    [
      "REP001",
      "1703678400",
      "helpline_user",
      "",
      "",
      "",
      "Jane Doe",
      "",
      "",
      "0700123456",
      "jane.doe@email.com",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "Self"
    ]
  ],
  "clients": [
    [
      "CLIENT001",
      "1703678400",
      "helpline_user",
      "",
      "",
      "",
      "",
      "Mary Smith",
      "",
      "",
      "",
      "",
      "",
      "946684800",
      "",
      "",
      "",
      "",
      "Female",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "Kikuyu",
      "Christian",
      "",
      "",
      "",
      "Nairobi Central",
      "Nairobi",
      "Starehe",
      "Nairobi Central Ward",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "Appears Normal",
      "",
      "Appears Normal",
      "",
      "",
      "None reported",
      "Yes",
      "",
      "",
      "",
      "Grade 8",
      "",
      "Nairobi Primary School",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "Middle Income (apparent)"
    ]
  ],
  "perpetrators": [
    [
      "PERP001",
      "1703678400",
      "helpline_user",
      "",
      "",
      "",
      "",
      "Unknown Person",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "Male",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "",
      "Strangers"
    ]
  ]
}
def test_real_payload():
    """Test with real helpline payload"""
    endpoint = "http://localhost:8000/api/webhook/helpline/cpims/abuse/"
    
    print("🧪 Testing with REAL helpline payload")
    print(f"📡 Endpoint: {endpoint}")
    print("-" * 60)
    
    try:
        response = requests.post(
            endpoint,
            json=REAL_PAYLOAD,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        result = response.json()
        status = result.get('status', 'unknown')
        message = result.get('message', 'No message')
        
        if status == 'success':
            print(f"✅ SUCCESS: {message}")
            cpims_response = result.get('cpims_response', {})
            if 'case_id' in cpims_response:
                print(f"🎯 CPIMS Case ID: {cpims_response['case_id']}")
            if 'county' in cpims_response:
                print(f"🌍 County Code: {cpims_response['county']}")
            if 'constituency' in cpims_response:
                print(f"🌍 Constituency Code: {cpims_response['constituency']}")
        else:
            print(f"❌ ERROR: {message}")
            details = result.get('details', '')
            if details:
                print(f"📋 Details: {details}")
        
        print("\n📤 Full Response:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == '__main__':
    test_real_payload()