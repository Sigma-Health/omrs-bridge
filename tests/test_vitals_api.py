"""
Test script for vitals API endpoints.
"""

import requests
import json
from typing import Dict, Any


def test_vitals_endpoints(
    base_url: str = "http://localhost:1221", api_key: str = "omrs_abc123def456ghi789"
) -> bool:
    """
    Test vitals API endpoints.
    """
    headers = {"X-API-Key": api_key}

    print("=== Testing Vitals API Endpoints ===")

    # Test 1: Get vitals by visit ID
    print("\n1. Testing GET /api/v1/vitals/visit/1")
    try:
        response = requests.get(f"{base_url}/api/v1/vitals/visit/1", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Visit ID: {data.get('visit_id', 'N/A')}")
            print(f"   Total Vitals: {data.get('total_count', 0)}")
            print(f"   Vitals Count: {len(data.get('vitals', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 2: Get vitals grouped by type
    print("\n2. Testing GET /api/v1/vitals/visit/1/grouped")
    try:
        response = requests.get(
            f"{base_url}/api/v1/vitals/visit/1/grouped", headers=headers
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Visit ID: {data.get('visit_id', 'N/A')}")
            print(f"   Total Vitals: {data.get('total_count', 0)}")
            print(f"   Vitals by Type Count: {len(data.get('vitals_by_type', []))}")

            # Show vitals by type
            for vital_type in data.get("vitals_by_type", [])[:3]:  # Show first 3 types
                print(
                    f"     - {vital_type.get('vital_type', 'Unknown')}: {len(vital_type.get('vitals', []))} measurements"
                )
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test 3: Test with different visit ID
    print("\n3. Testing GET /api/v1/vitals/visit/2")
    try:
        response = requests.get(f"{base_url}/api/v1/vitals/visit/2", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Visit ID: {data.get('visit_id', 'N/A')}")
            print(f"   Total Vitals: {data.get('total_count', 0)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n=== Vitals API Test Complete ===")
    return True


if __name__ == "__main__":
    test_vitals_endpoints()
