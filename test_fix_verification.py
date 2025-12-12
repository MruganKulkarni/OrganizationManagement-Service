#!/usr/bin/env python3
"""
Simple test to verify the duplicate key error fix is working.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_organization_creation():
    """Test organization creation and duplicate handling."""
    print("🧪 Testing Organization Creation Fix")
    print("=" * 50)
    
    # Test data
    org_name = f"testfix_{int(time.time())}"
    test_data = {
        "organization_name": org_name,
        "email": f"admin_{int(time.time())}@test.com",
        "password": "SecurePass123!"
    }
    
    print(f"📝 Creating organization: {org_name}")
    
    # Test 1: Create organization (should succeed)
    response = requests.post(f"{BASE_URL}/org/create", json=test_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print("✅ Organization created successfully")
            print(f"   Organization ID: {data.get('organization_id')}")
            print(f"   Collection Name: {data.get('collection_name')}")
        else:
            print(f"❌ Creation failed: {data.get('message')}")
            return False
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # Test 2: Try to create same organization again (should fail gracefully)
    print(f"\n🔄 Attempting to create duplicate organization: {org_name}")
    response = requests.post(f"{BASE_URL}/org/create", json=test_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 400:
        data = response.json()
        if "already exists" in data.get("message", ""):
            print("✅ Duplicate organization properly rejected")
            print(f"   Message: {data.get('message')}")
        else:
            print(f"❌ Unexpected error message: {data.get('message')}")
            return False
    else:
        print(f"❌ Expected 400 status code, got: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # Test 3: Create different organization (should succeed)
    org_name2 = f"testfix2_{int(time.time())}"
    test_data2 = {
        "organization_name": org_name2,
        "email": f"admin2_{int(time.time())}@test.com",
        "password": "SecurePass456!"
    }
    
    print(f"\n📝 Creating second organization: {org_name2}")
    response = requests.post(f"{BASE_URL}/org/create", json=test_data2)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print("✅ Second organization created successfully")
            print(f"   Organization ID: {data.get('organization_id')}")
        else:
            print(f"❌ Creation failed: {data.get('message')}")
            return False
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    print("\n🎉 All tests passed! The duplicate key error fix is working correctly.")
    return True

def test_health_check():
    """Test health endpoint."""
    print("\n🏥 Testing Health Check")
    print("=" * 30)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health Status: {data.get('status')}")
        print(f"   Database Status: {data.get('database', {}).get('status')}")
        print(f"   Collections: {data.get('database', {}).get('collections')}")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

if __name__ == "__main__":
    try:
        # Test health first
        if not test_health_check():
            print("❌ Health check failed. Make sure the server is running.")
            exit(1)
        
        # Test organization creation
        if test_organization_creation():
            print("\n🎯 Summary: All tests passed successfully!")
            print("   ✅ Duplicate key error has been fixed")
            print("   ✅ Organization creation works correctly")
            print("   ✅ Duplicate detection works properly")
        else:
            print("\n❌ Some tests failed. Please check the output above.")
            exit(1)
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server. Make sure it's running on http://localhost:8000")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)