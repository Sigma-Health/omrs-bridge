"""
Quick test to verify the vitals endpoint fix.
"""

import requests
import json


def test_vitals_fix():
    """Test the vitals endpoint with the UUID that was failing."""
    base_url = "http://localhost:1221"
    api_key = "omrs_abc123def456ghi789"
    headers = {"X-API-Key": api_key}

    # Test the UUID that was failing
    visit_uuid = "c8f5e759-e140-4c20-a93f-2912902bde3a"

    print(f"Testing vitals endpoint with UUID: {visit_uuid}")

    try:
        response = requests.get(
            f"{base_url}/api/v1/vitals/visit/uuid/{visit_uuid}", headers=headers
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response structure:")
            print(f"  - Visit ID: {data.get('visit_id', 'N/A')}")
            print(f"  - Visit UUID: {data.get('visit_uuid', 'N/A')}")
            print(f"  - Total Vitals: {data.get('total_count', 0)}")
            print(f"  - Vitals Count: {len(data.get('vitals', []))}")

            if data.get("patient"):
                print(f"  - Patient: {data['patient'].get('name', 'Unknown')}")
            if data.get("encounter"):
                print(
                    f"  - Encounter ID: {data['encounter'].get('encounter_id', 'N/A')}"
                )
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {e}")


if __name__ == "__main__":
    test_vitals_fix()
