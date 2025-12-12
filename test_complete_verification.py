#!/usr/bin/env python3
"""
Complete verification test for all fixed issues.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_complete_workflow():
    """Test the complete organization management workflow."""
    print("🧪 Complete Organization Management Workflow Test")
    print("=" * 60)
    
    # Test data
    org_name = f"complete_test_{int(time.time())}"
    admin_email = f"admin_{int(time.time())}@example.com"
    password = "CompleteTest123!"
    
    print(f"📝 Testing with organization: {org_name}")
    print(f"📧 Admin email: {admin_email}")
    
    # Step 1: Health Check
    print("\n1️⃣ Health Check")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code != 200:
        print(f"❌ Health check failed: {response.status_code}")
        return False
    
    health_data = response.json()
    print(f"✅ System Status: {health_data['status']}")
    print(f"   Database: {health_data['database']['status']}")
    
    # Step 2: Create Organization
    print("\n2️⃣ Create Organization")
    org_data = {
        "organization_name": org_name,
        "email": admin_email,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/org/create", json=org_data)
    if response.status_code != 200:
        print(f"❌ Organization creation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    create_result = response.json()
    if not create_result.get("success"):
        print(f"❌ Organization creation failed: {create_result.get('message')}")
        return False
    
    print("✅ Organization created successfully")
    print(f"   ID: {create_result['organization_id']}")
    print(f"   Collection: {create_result['collection_name']}")
    
    # Step 3: Test Duplicate Creation (should fail)
    print("\n3️⃣ Test Duplicate Prevention")
    response = requests.post(f"{BASE_URL}/org/create", json=org_data)
    if response.status_code != 400:
        print(f"❌ Duplicate check failed: Expected 400, got {response.status_code}")
        return False
    
    duplicate_result = response.json()
    if "already exists" not in duplicate_result.get("message", ""):
        print(f"❌ Wrong duplicate message: {duplicate_result.get('message')}")
        return False
    
    print("✅ Duplicate organization properly rejected")
    
    # Step 4: Admin Login
    print("\n4️⃣ Admin Authentication")
    login_data = {
        "email": admin_email,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/admin/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    login_result = response.json()
    if not login_result.get("success"):
        print(f"❌ Login failed: {login_result.get('message')}")
        return False
    
    access_token = login_result["access_token"]
    print("✅ Admin login successful")
    print(f"   Token expires in: {login_result['expires_in']} seconds")
    
    # Step 5: Get Admin Profile
    print("\n5️⃣ Admin Profile Access")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(f"{BASE_URL}/admin/profile", headers=headers)
    if response.status_code != 200:
        print(f"❌ Profile access failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    profile_result = response.json()
    if not profile_result.get("success"):
        print(f"❌ Profile access failed: {profile_result.get('message')}")
        return False
    
    print("✅ Admin profile retrieved successfully")
    print(f"   Email: {profile_result['email']}")
    print(f"   Organization ID: {profile_result['organization_id']}")
    
    # Step 6: Get Organization Details
    print("\n6️⃣ Organization Retrieval")
    response = requests.get(f"{BASE_URL}/org/get", params={"organization_name": org_name})
    if response.status_code != 200:
        print(f"❌ Organization retrieval failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    get_result = response.json()
    if not get_result.get("success"):
        print(f"❌ Organization retrieval failed: {get_result.get('message')}")
        return False
    
    print("✅ Organization retrieved successfully")
    print(f"   Name: {get_result['organization_name']}")
    print(f"   Admin Email: {get_result['admin_email']}")
    
    # Step 7: Test Organization Statistics
    print("\n7️⃣ Organization Statistics")
    response = requests.get(f"{BASE_URL}/org/stats")
    if response.status_code != 200:
        print(f"❌ Stats retrieval failed: {response.status_code}")
        return False
    
    stats_result = response.json()
    print("✅ Organization statistics retrieved")
    print(f"   Total Organizations: {stats_result['total_organizations']}")
    print(f"   Total Admin Users: {stats_result['total_admin_users']}")
    
    # Step 8: Test Invalid Login
    print("\n8️⃣ Invalid Login Test")
    invalid_login = {
        "email": admin_email,
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/admin/login", json=invalid_login)
    if response.status_code != 401:
        print(f"❌ Invalid login should return 401, got: {response.status_code}")
        return False
    
    print("✅ Invalid login properly rejected")
    
    # Step 9: Test Unauthorized Access
    print("\n9️⃣ Unauthorized Access Test")
    response = requests.get(f"{BASE_URL}/admin/profile")
    if response.status_code not in [401, 403]:
        print(f"❌ Unauthorized access should return 401 or 403, got: {response.status_code}")
        return False
    
    print("✅ Unauthorized access properly blocked")
    
    print("\n🎉 All Tests Passed Successfully!")
    print("=" * 60)
    print("✅ Organization creation works correctly")
    print("✅ Duplicate key error has been fixed")
    print("✅ Authentication system works properly")
    print("✅ Authorization is functioning correctly")
    print("✅ All API endpoints are responding correctly")
    
    return True

if __name__ == "__main__":
    try:
        if test_complete_workflow():
            print("\n🎯 VERIFICATION COMPLETE: All systems are working correctly!")
            exit(0)
        else:
            print("\n❌ VERIFICATION FAILED: Some issues were found.")
            exit(1)
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)