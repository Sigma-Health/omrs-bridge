#!/usr/bin/env python3
"""
Test script for concepts API endpoints
"""

import requests
import json
import sys
from datetime import datetime
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


def test_create_concept(base_url: str, api_key: str) -> bool:
    """Test creating a new concept"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Sample concept data
        concept_data = {
            "creator": 1,
            "short_name": "Test Concept",
            "description": "A test concept created via API",
            "datatype_id": 4,
            "class_id": 11,
            "is_set": False,
            "version": "1.0"
        }
        
        response = requests.post(
            f"{base_url}/api/v1/concepts/",
            headers=headers,
            json=concept_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully created concept with ID: {data.get('concept_id')}")
            print(f"   UUID: {data.get('uuid')}")
            print(f"   Short Name: {data.get('short_name')}")
            print(f"   Description: {data.get('description')}")
            return True
        else:
            print(f"❌ Failed to create concept: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating concept: {e}")
        return False


def test_list_concepts(base_url: str, api_key: str) -> bool:
    """Test listing concepts"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{base_url}/api/v1/concepts/", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully listed {len(data)} concepts")
            return True
        else:
            print(f"❌ Failed to list concepts: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error listing concepts: {e}")
        return False


def test_list_active_concepts(base_url: str, api_key: str) -> bool:
    """Test listing active concepts"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{base_url}/api/v1/concepts/active", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully listed {len(data)} active concepts")
            return True
        else:
            print(f"❌ Failed to list active concepts: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error listing active concepts: {e}")
        return False


def test_search_concepts(base_url: str, api_key: str) -> bool:
    """Test searching concepts"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            f"{base_url}/api/v1/concepts/search?name=test",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully searched concepts, found {len(data)} results")
            return True
        else:
            print(f"❌ Failed to search concepts: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error searching concepts: {e}")
        return False


def test_get_concepts_by_datatype(base_url: str, api_key: str) -> bool:
    """Test getting concepts by datatype"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            f"{base_url}/api/v1/concepts/datatype/4",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully got {len(data)} concepts for datatype 4")
            return True
        else:
            print(f"❌ Failed to get concepts by datatype: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting concepts by datatype: {e}")
        return False


def test_get_concepts_by_class(base_url: str, api_key: str) -> bool:
    """Test getting concepts by class"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(
            f"{base_url}/api/v1/concepts/class/11",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully got {len(data)} concepts for class 11")
            return True
        else:
            print(f"❌ Failed to get concepts by class: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting concepts by class: {e}")
        return False


def test_get_concept_by_uuid(base_url: str, api_key: str) -> bool:
    """Test getting a concept by UUID"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # First, get a list of concepts to find a UUID
        list_response = requests.get(f"{base_url}/api/v1/concepts/", headers=headers, timeout=10)
        if list_response.status_code != 200:
            print("❌ Could not get concepts list for UUID test")
            return False
        
        concepts = list_response.json()
        if not concepts:
            print("❌ No concepts found for UUID test")
            return False
        
        # Use the first concept's UUID
        concept_uuid = concepts[0]['uuid']
        
        response = requests.get(
            f"{base_url}/api/v1/concepts/{concept_uuid}",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully got concept by UUID: {data.get('short_name', 'N/A')}")
            return True
        else:
            print(f"❌ Failed to get concept by UUID: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting concept by UUID: {e}")
        return False


def check_openapi_schema(base_url: str) -> bool:
    """Check if concepts endpoints are in OpenAPI schema"""
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get("paths", {})
            
            # Check for concepts endpoints
            concepts_endpoints = []
            for path, methods in paths.items():
                if path.startswith("/api/v1/concepts"):
                    concepts_endpoints.append(path)
            
            if concepts_endpoints:
                print(f"✅ Found {len(concepts_endpoints)} concepts endpoints in OpenAPI schema:")
                for endpoint in concepts_endpoints:
                    print(f"   • {endpoint}")
                return True
            else:
                print("❌ No concepts endpoints found in OpenAPI schema")
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
    
    print("🧪 Testing Concepts API")
    print("=" * 50)
    
    # Test health
    if not test_health(base_url):
        print("❌ Service is not running or not accessible")
        sys.exit(1)
    
    # Check OpenAPI schema
    if not check_openapi_schema(base_url):
        print("❌ Concepts endpoints not found in API schema")
        sys.exit(1)
    
    # Test concepts endpoints
    print("\n🧪 Testing Concepts Endpoints:")
    print("-" * 30)
    
    if not test_list_concepts(base_url, api_key):
        print("❌ List concepts endpoint failed")
        sys.exit(1)
    
    if not test_list_active_concepts(base_url, api_key):
        print("❌ List active concepts endpoint failed")
        sys.exit(1)
    
    if not test_search_concepts(base_url, api_key):
        print("❌ Search concepts endpoint failed")
        sys.exit(1)
    
    if not test_get_concepts_by_datatype(base_url, api_key):
        print("❌ Get concepts by datatype endpoint failed")
        sys.exit(1)
    
    if not test_get_concepts_by_class(base_url, api_key):
        print("❌ Get concepts by class endpoint failed")
        sys.exit(1)
    
    if not test_get_concept_by_uuid(base_url, api_key):
        print("❌ Get concept by UUID endpoint failed")
        sys.exit(1)
    
    if not test_create_concept(base_url, api_key):
        print("❌ Create concept endpoint failed")
        sys.exit(1)
    
    print("\n🎉 All concepts API tests passed!")
    print("\n📋 Available Concepts Endpoints:")
    print("  • POST /api/v1/concepts/ - Create new concept")
    print("  • GET /api/v1/concepts/ - List all concepts")
    print("  • GET /api/v1/concepts/active - List active concepts")
    print("  • GET /api/v1/concepts/retired - List retired concepts")
    print("  • GET /api/v1/concepts/search - Search concepts by name")
    print("  • GET /api/v1/concepts/datatype/{id} - Get concepts by datatype")
    print("  • GET /api/v1/concepts/class/{id} - Get concepts by class")
    print("  • GET /api/v1/concepts/creator/{id} - Get concepts by creator")
    print("  • GET /api/v1/concepts/{uuid} - Get concept by UUID")
    print("  • PATCH /api/v1/concepts/{uuid} - Update concept partially")
    print("  • PUT /api/v1/concepts/{uuid} - Replace concept completely")


if __name__ == "__main__":
    main() 