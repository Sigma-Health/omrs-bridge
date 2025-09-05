#!/usr/bin/env python3
"""
Test script for creating observations
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any


def test_create_observation(base_url: str, api_key: str) -> bool:
    """Test creating a new observation"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Sample observation data
        observation_data = {
            "person_id": 1,
            "concept_id": 5089,  # Weight concept
            "encounter_id": 1,
            "creator": 1,
            "value_numeric": 70.5,
            "obs_datetime": datetime.utcnow().isoformat(),
            "location_id": 1,
            "comments": "Test observation created via API"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/observations/",
            headers=headers,
            json=observation_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully created observation with ID: {data.get('obs_id')}")
            print(f"   UUID: {data.get('uuid')}")
            print(f"   Person ID: {data.get('person_id')}")
            print(f"   Concept ID: {data.get('concept_id')}")
            print(f"   Value: {data.get('value_numeric')}")
            return True
        else:
            print(f"❌ Failed to create observation: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating observation: {e}")
        return False


def test_create_text_observation(base_url: str, api_key: str) -> bool:
    """Test creating a text observation"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Sample text observation data
        observation_data = {
            "person_id": 1,
            "concept_id": 160632,  # Chief complaint concept
            "encounter_id": 1,
            "creator": 1,
            "value_text": "Patient reports headache and fever",
            "obs_datetime": datetime.utcnow().isoformat(),
            "location_id": 1,
            "comments": "Text observation created via API"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/observations/",
            headers=headers,
            json=observation_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully created text observation with ID: {data.get('obs_id')}")
            print(f"   UUID: {data.get('uuid')}")
            print(f"   Value: {data.get('value_text')}")
            return True
        else:
            print(f"❌ Failed to create text observation: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating text observation: {e}")
        return False


def test_create_coded_observation(base_url: str, api_key: str) -> bool:
    """Test creating a coded observation"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Sample coded observation data
        observation_data = {
            "person_id": 1,
            "concept_id": 5090,  # Height concept
            "encounter_id": 1,
            "creator": 1,
            "value_coded": 5090,  # Same as concept_id for this example
            "obs_datetime": datetime.utcnow().isoformat(),
            "location_id": 1,
            "comments": "Coded observation created via API"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/observations/",
            headers=headers,
            json=observation_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully created coded observation with ID: {data.get('obs_id')}")
            print(f"   UUID: {data.get('uuid')}")
            print(f"   Value Coded: {data.get('value_coded')}")
            return True
        else:
            print(f"❌ Failed to create coded observation: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating coded observation: {e}")
        return False


def main():
    """Main test function"""
    base_url = "http://localhost:1221"
    api_key = "omrs_abc123def456ghi789"  # Default API key from env.example
    
    print("🧪 Testing Observation Creation")
    print("=" * 50)
    
    # Test creating numeric observation
    print("\n1. Testing numeric observation creation:")
    if not test_create_observation(base_url, api_key):
        sys.exit(1)
    
    # Test creating text observation
    print("\n2. Testing text observation creation:")
    if not test_create_text_observation(base_url, api_key):
        sys.exit(1)
    
    # Test creating coded observation
    print("\n3. Testing coded observation creation:")
    if not test_create_coded_observation(base_url, api_key):
        sys.exit(1)
    
    print("\n🎉 All observation creation tests passed!")
    print("\n📋 Available Observation Creation Fields:")
    print("  • Required: person_id, concept_id, encounter_id, creator")
    print("  • Optional value types: value_numeric, value_text, value_coded, value_datetime, value_drug, value_complex")
    print("  • Other optional fields: order_id, obs_datetime, location_id, obs_group_id, comments, etc.")
    
    print("\n💡 Example Usage:")
    print("""
curl -X POST "http://localhost:1221/api/v1/observations/" \\
  -H "Authorization: Bearer your_api_key" \\
  -H "Content-Type: application/json" \\
  -d '{
    "person_id": 1,
    "concept_id": 5089,
    "encounter_id": 1,
    "creator": 1,
    "value_numeric": 70.5,
    "comments": "Weight measurement"
  }'
    """)


if __name__ == "__main__":
    main() 