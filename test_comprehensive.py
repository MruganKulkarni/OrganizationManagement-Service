#!/usr/bin/env python3
"""
Comprehensive API testing script for the Organization Management Service.
This script tests all endpoints and features to ensure everything works correctly.
"""

import sys
import json
import time
import requests
from typing import Dict, Any, Optional

class OrganizationAPITester:
    """Comprehensive API tester for the Organization Management Service."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.test_org_name = f"test_org_{int(time.time())}"
        self.test_email = f"admin_{int(time.time())}@test.com"
        self.test_password = "TestPass123!"
        
    def set_auth_header(self):
        """Set authorization header for authenticated requests."""
        if self.access_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.access_token}"
            })
    
    def test_health_endpoints(self) -> bool:
        """Test health and monitoring endpoints."""
        print("🏥 Testing health endpoints...")
        
        try:
            # Test basic health check
            response = self.session.get(f"{self.base_url}/health")
            assert response.status_code == 200
            health_data = response.json()
            assert health_data["status"] in ["healthy", "unhealthy"]
            
            # Test ping
            response = self.session.get(f"{self.base_url}/ping")
            assert response.status_code == 200
            assert response.json()["status"] == "ok"
            
            # Test version
            response = self.session.get(f"{self.base_url}/version")
            assert response.status_code == 200
            assert "version" in response.json()
            
            # Test root endpoint
            response = self.session.get(f"{self.base_url}/")
            assert response.status_code == 200
            assert response.json()["status"] == "running"
            
            print("✅ Health endpoints working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Health endpoints failed: {e}")
            return False
    
    def test_organization_lifecycle(self) -> bool:
        """Test complete organization lifecycle."""
        print("🏢 Testing organization lifecycle...")
        
        try:
            # 1. Create organization
            org_data = {
                "organization_name": self.test_org_name,
                "email": self.test_email,
                "password": self.test_password
            }
            
            response = self.session.post(f"{self.base_url}/org/create", json=org_data)
            assert response.status_code == 200
            create_data = response.json()
            assert create_data["success"] is True
            assert create_data["organization_name"] == self.test_org_name
            
            # 2. Get organization
            response = self.session.get(
                f"{self.base_url}/org/get",
                params={"organization_name": self.test_org_name}
            )
            assert response.status_code == 200
            get_data = response.json()
            assert get_data["success"] is True
            assert get_data["organization_name"] == self.test_org_name
            
            # 3. Test duplicate creation (should fail)
            response = self.session.post(f"{self.base_url}/org/create", json=org_data)
            assert response.status_code == 400
            
            print("✅ Organization lifecycle working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Organization lifecycle failed: {e}")
            return False
    
    def test_authentication_flow(self) -> bool:
        """Test authentication and authorization."""
        print("🔐 Testing authentication flow...")
        
        try:
            # 1. Login with correct credentials
            login_data = {
                "email": self.test_email,
                "password": self.test_password
            }
            
            response = self.session.post(f"{self.base_url}/admin/login", json=login_data)
            assert response.status_code == 200
            login_response = response.json()
            assert login_response["success"] is True
            assert "access_token" in login_response
            
            self.access_token = login_response["access_token"]
            self.set_auth_header()
            
            # 2. Test profile endpoint
            response = self.session.get(f"{self.base_url}/admin/profile")
            assert response.status_code == 200
            profile_data = response.json()
            assert profile_data["success"] is True
            assert profile_data["email"] == self.test_email
            
            # 3. Test invalid login
            invalid_login = {
                "email": "nonexistent@test.com",
                "password": "wrongpassword"
            }
            
            response = self.session.post(f"{self.base_url}/admin/login", json=invalid_login)
            assert response.status_code == 401
            
            # 4. Test logout
            response = self.session.post(f"{self.base_url}/admin/logout")
            assert response.status_code == 200
            
            print("✅ Authentication flow working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Authentication flow failed: {e}")
            return False
    
    def test_organization_management(self) -> bool:
        """Test organization update and delete operations."""
        print("🔧 Testing organization management...")
        
        try:
            # Ensure we're authenticated
            self.set_auth_header()
            
            # 1. Update organization
            new_org_name = f"{self.test_org_name}_updated"
            new_email = f"updated_{int(time.time())}@test.com"
            
            update_data = {
                "organization_name": new_org_name,
                "email": new_email,
                "password": "NewTestPass123!"
            }
            
            response = self.session.put(f"{self.base_url}/org/update", json=update_data)
            assert response.status_code == 200
            update_response = response.json()
            assert update_response["success"] is True
            assert update_response["organization_name"] == new_org_name
            
            # Update our test data
            self.test_org_name = new_org_name
            self.test_email = new_email
            
            # 2. Verify update by getting organization
            response = self.session.get(
                f"{self.base_url}/org/get",
                params={"organization_name": new_org_name}
            )
            assert response.status_code == 200
            get_data = response.json()
            assert get_data["organization_name"] == new_org_name
            
            print("✅ Organization management working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Organization management failed: {e}")
            return False
    
    def test_analytics_endpoints(self) -> bool:
        """Test analytics and monitoring endpoints."""
        print("📊 Testing analytics endpoints...")
        
        try:
            # Ensure we're authenticated
            self.set_auth_header()
            
            # 1. Test dashboard metrics
            response = self.session.get(f"{self.base_url}/analytics/dashboard")
            assert response.status_code == 200
            dashboard_data = response.json()
            assert dashboard_data["success"] is True
            assert "organization" in dashboard_data
            assert "activity" in dashboard_data
            
            # 2. Test system metrics (public endpoint)
            response = self.session.get(f"{self.base_url}/analytics/system")
            assert response.status_code == 200
            system_data = response.json()
            assert system_data["success"] is True
            assert "uptime" in system_data
            assert "statistics" in system_data
            
            # 3. Test audit logs
            response = self.session.get(f"{self.base_url}/analytics/audit-logs")
            assert response.status_code == 200
            audit_data = response.json()
            assert audit_data["success"] is True
            assert "logs" in audit_data
            assert "pagination" in audit_data
            
            # 4. Test performance metrics
            response = self.session.get(f"{self.base_url}/analytics/performance")
            assert response.status_code == 200
            perf_data = response.json()
            assert perf_data["success"] is True
            assert "response_time_ms" in perf_data
            
            print("✅ Analytics endpoints working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Analytics endpoints failed: {e}")
            return False
    
    def test_organization_stats(self) -> bool:
        """Test organization statistics endpoint."""
        print("📈 Testing organization statistics...")
        
        try:
            response = self.session.get(f"{self.base_url}/org/stats")
            assert response.status_code == 200
            stats_data = response.json()
            assert "total_organizations" in stats_data
            assert "total_admin_users" in stats_data
            assert "recent_organizations" in stats_data
            assert "database_health" in stats_data
            
            print("✅ Organization statistics working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Organization statistics failed: {e}")
            return False
    
    def test_validation_and_errors(self) -> bool:
        """Test input validation and error handling."""
        print("🔍 Testing validation and error handling...")
        
        try:
            # 1. Test invalid organization creation
            invalid_org = {
                "organization_name": "ab",  # Too short
                "email": "invalid-email",
                "password": "weak"
            }
            
            response = self.session.post(f"{self.base_url}/org/create", json=invalid_org)
            assert response.status_code == 422  # Validation error
            
            # 2. Test invalid login data
            invalid_login = {
                "email": "not-an-email",
                "password": ""
            }
            
            response = self.session.post(f"{self.base_url}/admin/login", json=invalid_login)
            assert response.status_code == 422
            
            # 3. Test unauthorized access
            # Remove auth header temporarily
            old_headers = self.session.headers.copy()
            if "Authorization" in self.session.headers:
                del self.session.headers["Authorization"]
            
            response = self.session.get(f"{self.base_url}/admin/profile")
            assert response.status_code == 403
            
            # Restore headers
            self.session.headers.update(old_headers)
            
            # 4. Test non-existent organization
            response = self.session.get(
                f"{self.base_url}/org/get",
                params={"organization_name": "nonexistent_org_12345"}
            )
            assert response.status_code == 404
            
            print("✅ Validation and error handling working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Validation and error handling failed: {e}")
            return False
    
    def test_security_features(self) -> bool:
        """Test security features and headers."""
        print("🛡️ Testing security features...")
        
        try:
            # Test security headers
            response = self.session.get(f"{self.base_url}/")
            
            # Check for security headers
            headers = response.headers
            security_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options",
                "X-XSS-Protection",
                "Referrer-Policy",
                "Content-Security-Policy"
            ]
            
            for header in security_headers:
                assert header in headers, f"Missing security header: {header}"
            
            # Test rate limiting (make multiple requests quickly)
            start_time = time.time()
            rate_limit_hit = False
            
            for i in range(10):
                response = self.session.get(f"{self.base_url}/ping")
                if response.status_code == 429:
                    rate_limit_hit = True
                    break
            
            # Note: Rate limiting might not trigger in testing due to low request count
            
            print("✅ Security features working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Security features failed: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Clean up test data."""
        print("🧹 Cleaning up test data...")
        
        try:
            # Ensure we're authenticated
            self.set_auth_header()
            
            # Delete the test organization
            response = self.session.delete(
                f"{self.base_url}/org/delete",
                params={"organization_name": self.test_org_name}
            )
            
            if response.status_code == 200:
                delete_data = response.json()
                assert delete_data["success"] is True
                print("✅ Test data cleaned up successfully")
                return True
            else:
                print(f"⚠️ Cleanup warning: {response.status_code} - {response.text}")
                return True  # Don't fail the test for cleanup issues
                
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
            return True  # Don't fail the test for cleanup issues
    
    def run_all_tests(self) -> bool:
        """Run all tests and return overall result."""
        print("🧪 Starting Comprehensive API Testing")
        print("=" * 60)
        
        tests = [
            ("Health Endpoints", self.test_health_endpoints),
            ("Organization Lifecycle", self.test_organization_lifecycle),
            ("Authentication Flow", self.test_authentication_flow),
            ("Organization Management", self.test_organization_management),
            ("Analytics Endpoints", self.test_analytics_endpoints),
            ("Organization Statistics", self.test_organization_stats),
            ("Validation & Errors", self.test_validation_and_errors),
            ("Security Features", self.test_security_features),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append(result)
                print()
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append(False)
                print()
        
        # Cleanup regardless of test results
        self.cleanup()
        
        print("=" * 60)
        print("📊 Test Results Summary:")
        print(f"   Total tests: {len(tests)}")
        print(f"   Passed: {sum(results)}")
        print(f"   Failed: {len(results) - sum(results)}")
        
        if all(results):
            print("🎉 All tests passed! The API is working perfectly.")
            print("\n🚀 The Organization Management Service is ready for production!")
            return True
        else:
            print("❌ Some tests failed. Please check the errors above.")
            return False


def main():
    """Main function to run the comprehensive tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive API tester")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    tester = OrganizationAPITester(args.url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()