#!/usr/bin/env python
"""
Test script to verify CPIMS connection and category mapping.
"""
import json
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfcbe.settings')
django.setup()

from platform_adapters.cpims.helpline_cpims_abuse_adapter import HelplineCPIMSAbuseAdapter


def test_cpims_connection():
    """Test CPIMS adapter with sample payload."""

    # Load test payload
    with open('test_cpims_connection.json', 'r') as f:
        test_payload = json.load(f)

    print("=" * 80)
    print("CPIMS Connection Test")
    print("=" * 80)
    print("\nTest Payload:")
    print(json.dumps(test_payload, indent=2))

    # Initialize adapter
    adapter = HelplineCPIMSAbuseAdapter()

    # Validate request
    print("\n" + "=" * 80)
    print("Validating Request...")
    print("=" * 80)
    is_valid = adapter.validate_request(test_payload)
    print(f"Validation Result: {'VALID' if is_valid else 'INVALID'}")

    if not is_valid:
        print("\nValidation failed. Stopping test.")
        return

    # Parse messages
    print("\n" + "=" * 80)
    print("Parsing Messages...")
    print("=" * 80)
    messages = adapter.parse_messages(test_payload)
    print(f"Parsed {len(messages)} message(s)")

    if messages:
        print("\nStandard Message:")
        print(json.dumps(messages[0], indent=2, default=str))

    # Send to CPIMS
    print("\n" + "=" * 80)
    print("Sending to CPIMS...")
    print("=" * 80)

    if messages:
        result = adapter.send_message("cpims", messages[0])

        print("\n" + "=" * 80)
        print("CPIMS Response")
        print("=" * 80)
        print(json.dumps(result, indent=2, default=str))

        # Check categories in payload
        if result.get("payload_sent"):
            payload_sent = result["payload_sent"]
            print("\n" + "=" * 80)
            print("Categories Verification")
            print("=" * 80)

            categories = payload_sent.get("categories", [])
            if categories:
                print("Categories array present")
                for i, cat in enumerate(categories):
                    print(f"\nCategory {i+1}:")
                    print(f"  - case_category: {cat.get('case_category')}")
                    print(f"  - case_sub_category: {cat.get('case_sub_category')}")
                    print(f"  - case_nature: {cat.get('case_nature')}")
                    print(f"  - case_date_event: {cat.get('case_date_event')}")
            else:
                print("Categories array is empty or missing!")

        # Final status
        print("\n" + "=" * 80)
        print("Test Result")
        print("=" * 80)
        status = result.get("status", "unknown")
        if status == "success":
            print("Test PASSED - Case successfully sent to CPIMS")
        elif status == "partial_success":
            print("Test PARTIAL - Case sent but CPIMS returned non-standard response")
        else:
            print(f"Test FAILED - Status: {status}")
            print(f"  Message: {result.get('message', 'No message')}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        test_cpims_connection()
    except Exception as e:
        print(f"\nError during test: {str(e)}")
        import traceback
        traceback.print_exc()
