#!/usr/bin/env python3
"""
Test script for Observations API endpoints
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:1221"
API_KEY = "omrs_abc123def456ghi789"  # Replace with actual API key

# Headers for authentication
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_list_observations():
    """Test listing observations"""
    print("\n🔍 Testing list observations...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/observations/", headers=headers)
        if response.status_code == 200:
            observations = response.json()
            print(f"✅ List observations passed - Found {len(observations)} observations")
            if observations:
                print(f"   First observation ID: {observations[0].get('obs_id', 'N/A')}")
        else:
            print(f"❌ List observations failed: {response.status_code}")
            print(f"   Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ List observations error: {e}")
        return False


def test_get_observation_by_uuid():
    """Test getting observation by UUID"""
    print("\n🔍 Testing get observation by UUID...")
    
    # First, get a list of observations to find a UUID
    try:
        response = requests.get(f"{BASE_URL}/api/v1/observations/", headers=headers)
        if response.status_code == 200:
            observations = response.json()
            if observations:
                uuid = observations[0].get('uuid')
                if uuid:
                    # Test getting by UUID
                    response = requests.get(f"{BASE_URL}/api/v1/observations/{uuid}", headers=headers)
                    if response.status_code == 200:
                        obs = response.json()
                        print(f"✅ Get observation by UUID passed")
                        print(f"   Observation ID: {obs.get('obs_id')}")
                        print(f"   Person ID: {obs.get('person_id')}")
                        print(f"   Concept ID: {obs.get('concept_id')}")
                    else:
                        print(f"❌ Get observation by UUID failed: {response.status_code}")
                        print(f"   Response: {response.text}")
                    return response.status_code == 200
                else:
                    print("⚠️  No UUID found in observations")
                    return False
            else:
                print("⚠️  No observations found to test with")
                return False
        else:
            print(f"❌ Failed to get observations list: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get observation by UUID error: {e}")
        return False


def test_get_observations_by_person():
    """Test getting observations by person ID"""
    print("\n🔍 Testing get observations by person...")
    
    # First, get a list of observations to find a person ID
    try:
        response = requests.get(f"{BASE_URL}/api/v1/observations/", headers=headers)
        if response.status_code == 200:
            observations = response.json()
            if observations:
                person_id = observations[0].get('person_id')
                if person_id:
                    # Test getting by person ID
                    response = requests.get(f"{BASE_URL}/api/v1/observations/person/{person_id}", headers=headers)
                    if response.status_code == 200:
                        obs_list = response.json()
                        print(f"✅ Get observations by person passed")
                        print(f"   Person ID: {person_id}")
                        print(f"   Found {len(obs_list)} observations")
                    else:
                        print(f"❌ Get observations by person failed: {response.status_code}")
                        print(f"   Response: {response.text}")
                    return response.status_code == 200
                else:
                    print("⚠️  No person_id found in observations")
                    return False
            else:
                print("⚠️  No observations found to test with")
                return False
        else:
            print(f"❌ Failed to get observations list: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get observations by person error: {e}")
        return False


def test_get_observations_by_encounter():
    """Test getting observations by encounter ID"""
    print("\n🔍 Testing get observations by encounter...")
    
    # First, get a list of observations to find an encounter ID
    try:
        response = requests.get(f"{BASE_URL}/api/v1/observations/", headers=headers)
        if response.status_code == 200:
            observations = response.json()
            if observations:
                encounter_id = observations[0].get('encounter_id')
                if encounter_id:
                    # Test getting by encounter ID
                    response = requests.get(f"{BASE_URL}/api/v1/observations/encounter/{encounter_id}", headers=headers)
                    if response.status_code == 200:
                        obs_list = response.json()
                        print(f"✅ Get observations by encounter passed")
                        print(f"   Encounter ID: {encounter_id}")
                        print(f"   Found {len(obs_list)} observations")
                    else:
                        print(f"❌ Get observations by encounter failed: {response.status_code}")
                        print(f"   Response: {response.text}")
                    return response.status_code == 200
                else:
                    print("⚠️  No encounter_id found in observations")
                    return False
            else:
                print("⚠️  No observations found to test with")
                return False
        else:
            print(f"❌ Failed to get observations list: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get observations by encounter error: {e}")
        return False


def test_get_observations_by_concept():
    """Test getting observations by concept ID"""
    print("\n🔍 Testing get observations by concept...")
    
    # First, get a list of observations to find a concept ID
    try:
        response = requests.get(f"{BASE_URL}/api/v1/observations/", headers=headers)
        if response.status_code == 200:
            observations = response.json()
            if observations:
                concept_id = observations[0].get('concept_id')
                if concept_id:
                    # Test getting by concept ID
                    response = requests.get(f"{BASE_URL}/api/v1/observations/concept/{concept_id}", headers=headers)
                    if response.status_code == 200:
                        obs_list = response.json()
                        print(f"✅ Get observations by concept passed")
                        print(f"   Concept ID: {concept_id}")
                        print(f"   Found {len(obs_list)} observations")
                    else:
                        print(f"❌ Get observations by concept failed: {response.status_code}")
                        print(f"   Response: {response.text}")
                    return response.status_code == 200
                else:
                    print("⚠️  No concept_id found in observations")
                    return False
            else:
                print("⚠️  No observations found to test with")
                return False
        else:
            print(f"❌ Failed to get observations list: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get observations by concept error: {e}")
        return False


def test_update_observation_partial():
    """Test updating observation partially (PATCH)"""
    print("\n🔍 Testing update observation partial...")
    
    # First, get a list of observations to find a UUID
    try:
        response = requests.get(f"{BASE_URL}/api/v1/observations/", headers=headers)
        if response.status_code == 200:
            observations = response.json()
            if observations:
                uuid = observations[0].get('uuid')
                if uuid:
                    # Test partial update
                    update_data = {
                        "comments": f"Updated via API test at {datetime.now().isoformat()}",
                        "status": "FINAL"
                    }
                    
                    response = requests.patch(
                        f"{BASE_URL}/api/v1/observations/{uuid}",
                        headers=headers,
                        json=update_data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ Update observation partial passed")
                        print(f"   Updated fields: {result.get('updated_fields', [])}")
                        print(f"   Message: {result.get('message', '')}")
                    else:
                        print(f"❌ Update observation partial failed: {response.status_code}")
                        print(f"   Response: {response.text}")
                    return response.status_code == 200
                else:
                    print("⚠️  No UUID found in observations")
                    return False
            else:
                print("⚠️  No observations found to test with")
                return False
        else:
            print(f"❌ Failed to get observations list: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Update observation partial error: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Testing Observations API")
    print("=" * 50)
    
    # Test results
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("List Observations", test_list_observations()))
    results.append(("Get Observation by UUID", test_get_observation_by_uuid()))
    results.append(("Get Observations by Person", test_get_observations_by_person()))
    results.append(("Get Observations by Encounter", test_get_observations_by_encounter()))
    results.append(("Get Observations by Concept", test_get_observations_by_concept()))
    results.append(("Update Observation Partial", test_update_observation_partial()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Observations API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 