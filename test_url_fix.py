#!/usr/bin/env python3
"""
Test script to verify URL paths are correct
"""

import requests
import sys


def test_url_paths(base_url: str, api_key: str) -> bool:
    """Test that URL paths are correct"""
    print("🔍 Testing URL Paths")
    print("=" * 30)
    
    # Test orders endpoints
    print("\n📋 Testing Orders Endpoints:")
    
    # Test orders list (should be /api/v1/orders/)
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{base_url}/api/v1/orders/", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ GET /api/v1/orders/ - Working correctly")
        else:
            print(f"❌ GET /api/v1/orders/ - Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GET /api/v1/orders/ - Error: {e}")
        return False
    
    # Test observations endpoints
    print("\n📋 Testing Observations Endpoints:")
    
    # Test observations list (should be /api/v1/observations/)
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{base_url}/api/v1/observations/", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ GET /api/v1/observations/ - Working correctly")
        else:
            print(f"❌ GET /api/v1/observations/ - Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GET /api/v1/observations/ - Error: {e}")
        return False
    
    # Test health endpoint
    print("\n📋 Testing Health Endpoint:")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ GET /health - Working correctly")
        else:
            print(f"❌ GET /health - Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GET /health - Error: {e}")
        return False
    
    return True


def check_openapi_schema(base_url: str) -> bool:
    """Check OpenAPI schema for correct paths"""
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=10)
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get("paths", {})
            
            print("\n🔍 Checking OpenAPI Schema Paths:")
            
            # Check for correct orders paths
            orders_paths = [path for path in paths.keys() if path.startswith("/api/v1/orders")]
            if orders_paths:
                print("✅ Orders paths found:")
                for path in orders_paths:
                    print(f"   • {path}")
                
                # Check for incorrect paths
                incorrect_paths = [path for path in orders_paths if "/orders/orders" in path]
                if incorrect_paths:
                    print("❌ Found incorrect paths with duplicate 'orders':")
                    for path in incorrect_paths:
                        print(f"   • {path}")
                    return False
                else:
                    print("✅ No duplicate 'orders' in paths")
            else:
                print("❌ No orders paths found")
                return False
            
            # Check for correct observations paths
            obs_paths = [path for path in paths.keys() if path.startswith("/api/v1/observations")]
            if obs_paths:
                print("✅ Observations paths found:")
                for path in obs_paths:
                    print(f"   • {path}")
            else:
                print("❌ No observations paths found")
                return False
            
            return True
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
    
    print("🧪 Testing URL Path Fix")
    print("=" * 50)
    
    # Test URL paths
    if not test_url_paths(base_url, api_key):
        print("❌ URL path tests failed")
        sys.exit(1)
    
    # Check OpenAPI schema
    if not check_openapi_schema(base_url):
        print("❌ OpenAPI schema check failed")
        sys.exit(1)
    
    print("\n🎉 All tests passed! URL paths are correct.")
    print("\n📋 Correct URL Structure:")
    print("  • Orders: /api/v1/orders/")
    print("  • Observations: /api/v1/observations/")
    print("  • Health: /health")
    print("  • Documentation: /docs")


if __name__ == "__main__":
    main() 