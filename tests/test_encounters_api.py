#!/usr/bin/env python3
"""
Test script for encounters API endpoints
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any


def test_health(base_url: str) -> bool:
    """Test health endpoint"""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_create_encounter(base_url: str, api_key: str) -> bool:
    """Test creating a new encounter"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Sample encounter data
        encounter_data = {
            "creator": 1,
            "encounter_type": 2,
            "patient_id": 9,
            "location_id": 5,
            "form_id": None,
            "encounter_datetime": datetime.utcnow().isoformat(),
            "visit_id": 1
        }
        
        response = requests.post(
            f"{base_url}/api/v1/encounters/",
            headers=headers,
            json=encounter_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully created encounter with ID: {data.get('encounter_id')}")
            print(f"   UUID: {data.get('uuid')}")
            print(f"   Patient ID: {data.get('patient_id')}")
            print(f"   Encounter Type: {data.get('encounter_type')}")
            return True
        else:
            print(f"❌ Failed to create encounter: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating encounter: {e}")
        return False


def test_list_encounters(base_url: str, api_key: str) -> bool:
    """Test listing encounters"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{base_url}/api/v1/encounters/", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully listed {len(data)} encounters")
            return True
        else:
            print(f"❌ Failed to list encounters: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error listing encounters: {e}")
        return False


def test_list_active_encounters(base_url: str, api_key: str) -> bool:
    """Test listing active encounters"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{base_url}/api/v1/encounters/active", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully listed {len(data)} active encounters")
            return True
        else:
            print(f"❌ Failed to list active encounters: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error listing active encounters: {e}")
        return False


def test_get_encounters_by_patient(base_url: str, api_key: str) -> bool:
    """Test getting encounters by patient"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            f"{base_url}/api/v1/encounters/patient/9",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully got {len(data)} encounters for patient 9")
            return True
        else:
            print(f"❌ Failed to get encounters by patient: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting encounters by patient: {e}")
        return False


def test_get_encounters_by_type(base_url: str, api_key: str) -> bool:
    """Test getting encounters by type"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            f"{base_url}/api/v1/encounters/type/2",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully got {len(data)} encounters for type 2")
            return True
        else:
            print(f"❌ Failed to get encounters by type: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting encounters by type: {e}")
        return False


def test_get_encounters_by_location(base_url: str, api_key: str) -> bool:
    """Test getting encounters by location"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            f"{base_url}/api/v1/encounters/location/5",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully got {len(data)} encounters for location 5")
            return True
        else:
            print(f"❌ Failed to get encounters by location: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting encounters by location: {e}")
        return False


def test_get_encounters_by_visit(base_url: str, api_key: str) -> bool:
    """Test getting encounters by visit"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            f"{base_url}/api/v1/encounters/visit/1",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully got {len(data)} encounters for visit 1")
            return True
        else:
            print(f"❌ Failed to get encounters by visit: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting encounters by visit: {e}")
        return False


def test_get_encounters_by_creator(base_url: str, api_key: str) -> bool:
    """Test getting encounters by creator"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            f"{base_url}/api/v1/encounters/creator/5",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully got {len(data)} encounters for creator 5")
            return True
        else:
            print(f"❌ Failed to get encounters by creator: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting encounters by creator: {e}")
        return False


def test_get_encounters_by_date_range(base_url: str, api_key: str) -> bool:
    """Test getting encounters by date range"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Create date range (last 30 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        response = requests.get(
            f"{base_url}/api/v1/encounters/date-range",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully got {len(data)} encounters in date range")
            return True
        else:
            print(f"❌ Failed to get encounters by date range: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting encounters by date range: {e}")
        return False


def test_get_encounter_by_uuid(base_url: str, api_key: str) -> bool:
    """Test getting an encounter by UUID"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # First, get a list of encounters to find a UUID
        list_response = requests.get(f"{base_url}/api/v1/encounters/", headers=headers, timeout=10)
        if list_response.status_code != 200:
            print("❌ Could not get encounters list for UUID test")
            return False
        
        encounters = list_response.json()
        if not encounters:
            print("❌ No encounters found for UUID test")
            return False
        
        # Use the first encounter's UUID
        encounter_uuid = encounters[0]['uuid']
        
        response = requests.get(
            f"{base_url}/api/v1/encounters/{encounter_uuid}",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully got encounter by UUID: Patient {data.get('patient_id', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to get encounter by UUID: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting encounter by UUID: {e}")
        return False


def check_openapi_schema(base_url: str) -> bool:
    """Check if encounters endpoints are in OpenAPI schema"""
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get("paths", {})
            
            # Check for encounters endpoints
            encounters_endpoints = []
            for path, methods in paths.items():
                if path.startswith("/api/v1/encounters"):
                    encounters_endpoints.append(path)
            
            if encounters_endpoints:
                print(f"✅ Found {len(encounters_endpoints)} encounters endpoints in OpenAPI schema:")
                for endpoint in encounters_endpoints:
                    print(f"   • {endpoint}")
                return True
            else:
                print("❌ No encounters endpoints found in OpenAPI schema")
                return False
        else:
            print(f"❌ Failed to get OpenAPI schema: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OpenAPI schema error: {e}")
        return False


def main():
    """Main test function"""
    base_url = "http://localhost:1221"
    api_key = "omrs_abc123def456ghi789"
    
    print("🧪 Testing Encounters API")
    print("=" * 50)
    
    # Test health
    if not test_health(base_url):
        print("❌ Service is not running or not accessible")
        sys.exit(1)
    
    # Check OpenAPI schema
    if not check_openapi_schema(base_url):
        print("❌ Encounters endpoints not found in API schema")
        sys.exit(1)
    
    # Test encounters endpoints
    print("\n🧪 Testing Encounters Endpoints:")
    print("-" * 30)
    
    if not test_list_encounters(base_url, api_key):
        print("❌ List encounters endpoint failed")
        sys.exit(1)
    
    if not test_list_active_encounters(base_url, api_key):
        print("❌ List active encounters endpoint failed")
        sys.exit(1)
    
    if not test_get_encounters_by_patient(base_url, api_key):
        print("❌ Get encounters by patient endpoint failed")
        sys.exit(1)
    
    if not test_get_encounters_by_type(base_url, api_key):
        print("❌ Get encounters by type endpoint failed")
        sys.exit(1)
    
    if not test_get_encounters_by_location(base_url, api_key):
        print("❌ Get encounters by location endpoint failed")
        sys.exit(1)
    
    if not test_get_encounters_by_visit(base_url, api_key):
        print("❌ Get encounters by visit endpoint failed")
        sys.exit(1)
    
    if not test_get_encounters_by_creator(base_url, api_key):
        print("❌ Get encounters by creator endpoint failed")
        sys.exit(1)
    
    if not test_get_encounters_by_date_range(base_url, api_key):
        print("❌ Get encounters by date range endpoint failed")
        sys.exit(1)
    
    if not test_get_encounter_by_uuid(base_url, api_key):
        print("❌ Get encounter by UUID endpoint failed")
        sys.exit(1)
    
    if not test_create_encounter(base_url, api_key):
        print("❌ Create encounter endpoint failed")
        sys.exit(1)
    
    print("\n🎉 All encounters API tests passed!")
    print("\n📋 Available Encounters Endpoints:")
    print("  • POST /api/v1/encounters/ - Create new encounter")
    print("  • GET /api/v1/encounters/ - List all encounters")
    print("  • GET /api/v1/encounters/active - List active encounters")
    print("  • GET /api/v1/encounters/voided - List voided encounters")
    print("  • GET /api/v1/encounters/patient/{id} - Get encounters by patient")
    print("  • GET /api/v1/encounters/type/{id} - Get encounters by type")
    print("  • GET /api/v1/encounters/location/{id} - Get encounters by location")
    print("  • GET /api/v1/encounters/visit/{id} - Get encounters by visit")
    print("  • GET /api/v1/encounters/creator/{id} - Get encounters by creator")
    print("  • GET /api/v1/encounters/date-range - Get encounters by date range")
    print("  • GET /api/v1/encounters/{uuid} - Get encounter by UUID")
    print("  • PATCH /api/v1/encounters/{uuid} - Update encounter partially")
    print("  • PUT /api/v1/encounters/{uuid} - Replace encounter completely")


if __name__ == "__main__":
    main() 