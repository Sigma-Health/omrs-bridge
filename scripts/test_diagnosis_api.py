#!/usr/bin/env python3
"""
Test script to verify diagnosis API endpoints.
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = "http://localhost:8001"
API_KEY = "omrs_abc123def456ghi789"  # Use one of the keys from your env.example

def test_diagnosis_endpoints():
    """Test all diagnosis API endpoints."""
    
    headers = {"X-API-Key": API_KEY}
    
    print("=== Testing Diagnosis API Endpoints ===\n")
    
    # Test 1: Get all diagnoses
    print("1. Testing GET /api/v1/diagnoses/")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/diagnoses/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total diagnoses: {data.get('total_count', 0)}")
            print(f"   Returned: {len(data.get('diagnoses', []))} diagnoses")
            if data.get('diagnoses'):
                print(f"   First diagnosis: {data['diagnoses'][0].get('concept', {}).get('name', 'Unknown')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 2: Get diagnoses with reference codes filter
    print("2. Testing GET /api/v1/diagnoses/?has_reference_codes=true")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/diagnoses/?has_reference_codes=true", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Diagnoses with reference codes: {data.get('total_count', 0)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 2b: Get diagnoses with specific source filter
    print("2b. Testing GET /api/v1/diagnoses/?source_name=ICD-10")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/diagnoses/?source_name=ICD-10", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Diagnoses with ICD-10 codes: {data.get('total_count', 0)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 3: Get diagnoses for a specific visit by ID
    print("3. Testing GET /api/v1/diagnoses/visit/1")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/diagnoses/visit/1", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Visit diagnoses: {data.get('total_count', 0)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 3b: Get diagnoses for a specific visit by UUID
    print("3b. Testing GET /api/v1/diagnoses/visit/uuid/sample-uuid")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/diagnoses/visit/uuid/sample-uuid", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Visit diagnoses by UUID: {data.get('total_count', 0)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 4: Get diagnoses for a specific patient
    print("4. Testing GET /api/v1/diagnoses/patient/1")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/diagnoses/patient/1", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Patient diagnoses: {data.get('total_count', 0)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 5: Health check
    print("5. Testing health check")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Health: {data.get('status', 'Unknown')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_diagnosis_endpoints()
