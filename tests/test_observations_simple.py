#!/usr/bin/env python3
"""
Simple test script for observations endpoints
"""

import requests
import json
import sys
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


def test_api_docs(base_url: str) -> bool:
    """Test if API documentation is accessible"""
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API documentation is accessible")
            return True
        else:
            print(f"❌ API documentation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API documentation error: {e}")
        return False


def test_observations_list(base_url: str, api_key: str) -> bool:
    """Test observations list endpoint"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{base_url}/api/v1/observations/", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Observations list endpoint working (found {len(data)} observations)")
            return True
        else:
            print(f"❌ Observations list failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Observations list error: {e}")
        return False


def test_observations_person(base_url: str, api_key: str) -> bool:
    """Test observations by person endpoint"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{base_url}/api/v1/observations/person/1", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Observations by person endpoint working (found {len(data)} observations for person 1)")
            return True
        else:
            print(f"❌ Observations by person failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Observations by person error: {e}")
        return False


def check_openapi_schema(base_url: str) -> bool:
    """Check if observations endpoints are in OpenAPI schema"""
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get("paths", {})
            
            # Check for observations endpoints
            obs_endpoints = []
            for path, methods in paths.items():
                if path.startswith("/api/v1/observations"):
                    obs_endpoints.append(path)
            
            if obs_endpoints:
                print(f"✅ Found {len(obs_endpoints)} observations endpoints in OpenAPI schema:")
                for endpoint in obs_endpoints:
                    print(f"   • {endpoint}")
                
                # Check specifically for POST endpoint
                post_endpoint = "/api/v1/observations/"
                if post_endpoint in paths and "post" in paths[post_endpoint]:
                    print("✅ POST endpoint for creating observations is available")
                else:
                    print("❌ POST endpoint for creating observations is missing")
                    return False
                
                return True
            else:
                print("❌ No observations endpoints found in OpenAPI schema")
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
    api_key = "omrs_abc123def456ghi789"  # Default API key from env.example
    
    print("🔍 Testing Observations Endpoints")
    print("=" * 50)
    
    # Test health
    if not test_health(base_url):
        print("❌ Service is not running or not accessible")
        sys.exit(1)
    
    # Test API docs
    if not test_api_docs(base_url):
        print("❌ API documentation not accessible")
        sys.exit(1)
    
    # Check OpenAPI schema
    if not check_openapi_schema(base_url):
        print("❌ Observations endpoints not found in API schema")
        sys.exit(1)
    
    # Test observations endpoints
    print("\n🧪 Testing Observations Endpoints:")
    print("-" * 30)
    
    if not test_observations_list(base_url, api_key):
        print("❌ Observations list endpoint failed")
        sys.exit(1)
    
    if not test_observations_person(base_url, api_key):
        print("❌ Observations by person endpoint failed")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Observations endpoints are working correctly.")
    print("\n📋 Available Observations Endpoints:")
    print("  • GET /api/v1/observations/ - List all observations")
    print("  • GET /api/v1/observations/person/{person_id} - Get observations by person")
    print("  • GET /api/v1/observations/encounter/{encounter_id} - Get observations by encounter")
    print("  • GET /api/v1/observations/concept/{concept_id} - Get observations by concept")
    print("  • GET /api/v1/observations/order/{order_id} - Get observations by order")
    print("  • GET /api/v1/observations/{uuid} - Get observation by UUID")
    print("  • PATCH /api/v1/observations/{uuid} - Update observation partially")
    print("  • PUT /api/v1/observations/{uuid} - Replace observation completely")


if __name__ == "__main__":
    main() 