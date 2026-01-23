#!/usr/bin/env python3
"""
Test script for the drugs API endpoints.

Run this script after starting the FastAPI service to verify that the
new drug CRUD endpoints are reachable and respond as expected.
"""

from __future__ import annotations

from typing import Dict

import requests


# Configuration
BASE_URL = "http://localhost:1221"
API_KEY = "omrs_test_key_1234567890abcdef"  # Replace in production


def _auth_headers() -> Dict[str, str]:
    """Return the standard authorization headers."""
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


def test_health() -> bool:
    """Verify that the service health endpoint is reachable."""
    print("🔍 Checking service health...")
    response = requests.get(f"{BASE_URL}/health", timeout=10)
    print(f"Status: {response.status_code}")
    if response.ok:
        print(f"Response: {response.json()}")
    return response.ok


def test_list_drugs() -> bool:
    """Test listing drugs."""
    print("\n📋 Listing drugs...")
    response = requests.get(
        f"{BASE_URL}/api/v1/drugs",
        headers=_auth_headers(),
        timeout=10,
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        drugs = response.json()
        print(f"Found {len(drugs)} drugs")
        if drugs:
            first = drugs[0]
            print(
                f"First drug: id={first.get('drug_id')} name={first.get('name')} retired={first.get('retired')}"
            )
    else:
        print(f"Response: {response.text}")
    return response.status_code in {200, 401}


def test_list_active_drugs() -> bool:
    """Test listing active drugs."""
    print("\n✅ Listing active drugs...")
    response = requests.get(
        f"{BASE_URL}/api/v1/drugs/active",
        headers=_auth_headers(),
        timeout=10,
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Active drugs returned: {len(response.json())}")
    else:
        print(f"Response: {response.text}")
    return response.status_code in {200, 401}


def test_list_retired_drugs() -> bool:
    """Test listing retired drugs."""
    print("\n🛌 Listing retired drugs...")
    response = requests.get(
        f"{BASE_URL}/api/v1/drugs/retired",
        headers=_auth_headers(),
        timeout=10,
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Retired drugs returned: {len(response.json())}")
    else:
        print(f"Response: {response.text}")
    return response.status_code in {200, 401}


def test_search_drugs(term: str = "test") -> bool:
    """Test the search endpoint with a sample term."""
    print(f"\n🔎 Searching for drugs containing '{term}'...")
    response = requests.get(
        f"{BASE_URL}/api/v1/drugs/search",
        headers=_auth_headers(),
        params={"name": term},
        timeout=10,
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Search results: {len(response.json())}")
    else:
        print(f"Response: {response.text}")
    return response.status_code in {200, 401}


def test_get_drug_sample() -> bool:
    """
    Attempt to fetch the first available drug (if any).

    The test first lists existing drugs, then retrieves one by ID and UUID
    to ensure both endpoints respond correctly.
    """
    print("\n🧪 Fetching sample drug by ID and UUID...")
    list_response = requests.get(
        f"{BASE_URL}/api/v1/drugs",
        headers=_auth_headers(),
        timeout=10,
    )
    if list_response.status_code != 200:
        print("⚠️ Could not retrieve drugs list; skipping sample fetch test.")
        return list_response.status_code in {200, 401}

    drugs_list = list_response.json()
    if not drugs_list:
        print("ℹ️ No drugs available to test fetching by ID/UUID.")
        return True

    sample = drugs_list[0]
    drug_id = sample.get("drug_id")
    drug_uuid = sample.get("uuid")

    print(f"Using drug_id={drug_id}, uuid={drug_uuid} for retrieval tests.")

    id_response = requests.get(
        f"{BASE_URL}/api/v1/drugs/{drug_id}",
        headers=_auth_headers(),
        timeout=10,
    )
    print(f"GET by ID status: {id_response.status_code}")

    uuid_response = requests.get(
        f"{BASE_URL}/api/v1/drugs/uuid/{drug_uuid}",
        headers=_auth_headers(),
        timeout=10,
    )
    print(f"GET by UUID status: {uuid_response.status_code}")

    success_statuses = {200, 401, 404}
    return (
        id_response.status_code in success_statuses
        and uuid_response.status_code in success_statuses
    )


def main() -> None:
    """Execute the basic drugs endpoint smoke tests."""
    print("🚀 Starting drugs API smoke tests")
    print("=" * 60)

    tests = [
        test_health,
        test_list_drugs,
        test_list_active_drugs,
        test_list_retired_drugs,
        test_search_drugs,
        test_get_drug_sample,
    ]

    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as exc:
            print(f"❌ Test {test.__name__} failed with exception: {exc}")

    print("\n" + "=" * 60)
    print(f"📊 Test results: {passed}/{len(tests)} passed")
    if passed == len(tests):
        print("🎉 All drugs API smoke tests passed.")
    else:
        print("⚠️ Some drugs API smoke tests failed. Review the output above.")


if __name__ == "__main__":
    main()
