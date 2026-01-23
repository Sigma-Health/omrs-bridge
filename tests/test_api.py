#!/usr/bin/env python3
"""
Simple test script for the OpenMRS Bridge API
Run this after starting the service to test the endpoints
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:1221"
API_KEY = "omrs_test_key_1234567890abcdef"  # Replace with your actual API key

# Headers
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_generate_api_key():
    """Test API key generation"""
    print("\n🔑 Testing API key generation...")
    try:
        response = requests.post(f"{BASE_URL}/generate-api-key")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Generated API Key: {data['api_key']}")
            print(f"Message: {data['message']}")
        else:
            print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API key generation failed: {e}")
        return False


def test_list_orders():
    """Test listing orders"""
    print("\n📋 Testing list orders endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/orders", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            orders = response.json()
            print(f"Found {len(orders)} orders")
            if orders:
                print(f"First order ID: {orders[0].get('order_id', 'N/A')}")
        else:
            print(f"Response: {response.text}")
        return response.status_code in [200, 401]  # 401 is expected if API key is invalid
    except Exception as e:
        print(f"❌ List orders failed: {e}")
        return False


def test_get_order(uuid="6000e165-57fd-4ad3-af48-0df1a6b157a9"):
    """Test getting a specific order by UUID"""
    print(f"\n📄 Testing get order endpoint (UUID: {uuid})...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/orders/{uuid}", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            order = response.json()
            print(f"Order ID: {order.get('order_id')}")
            print(f"Patient ID: {order.get('patient_id')}")
            print(f"UUID: {order.get('uuid')}")
        else:
            print(f"Response: {response.text}")
        return response.status_code in [200, 404, 401]
    except Exception as e:
        print(f"❌ Get order failed: {e}")
        return False


def test_update_order_partial(uuid="6000e165-57fd-4ad3-af48-0df1a6b157a9"):
    """Test partial order update (PATCH) by UUID"""
    print(f"\n✏️ Testing partial order update (UUID: {uuid})...")
    try:
        update_data = {
            "instructions": "Updated instructions from test script",
            "urgency": "ROUTINE"
        }
        response = requests.patch(
            f"{BASE_URL}/api/v1/orders/{uuid}",
            headers=headers,
            json=update_data
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            print(f"Updated fields: {result.get('updated_fields')}")
        else:
            print(f"Response: {response.text}")
        return response.status_code in [200, 404, 401]
    except Exception as e:
        print(f"❌ Partial update failed: {e}")
        return False


def test_api_documentation():
    """Test API documentation access"""
    print("\n📚 Testing API documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ API documentation is accessible")
        else:
            print("❌ API documentation not accessible")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API documentation test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting OpenMRS Bridge API Tests")
    print("=" * 50)
    
    tests = [
        test_health,
        test_generate_api_key,
        test_api_documentation,
        test_list_orders,
        test_get_order,
        test_update_order_partial
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed. Check the output above.")
    
    print(f"\n📖 API Documentation: {BASE_URL}/docs")
    print(f"🏥 Health Check: {BASE_URL}/health")


if __name__ == "__main__":
    main() 