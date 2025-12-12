"""
Test cases for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAuthentication:
    """Test authentication operations."""
    
    def test_admin_login_success(self):
        """Test successful admin login."""
        # First create an organization with admin
        org_data = {
            "organization_name": "auth_test_org",
            "email": "admin@authtest.com",
            "password": "TestPass123!"
        }
        
        create_response = client.post("/org/create", json=org_data)
        assert create_response.status_code == 200
        
        # Then login
        login_data = {
            "email": "admin@authtest.com",
            "password": "TestPass123!"
        }
        
        response = client.post("/admin/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_admin_login_invalid_credentials(self):
        """Test admin login with invalid credentials."""
        login_data = {
            "email": "nonexistent@test.com",
            "password": "WrongPass123!"
        }
        
        response = client.post("/admin/login", json=login_data)
        assert response.status_code == 401
        
        data = response.json()
        assert data["success"] is False
    
    def test_admin_profile_with_token(self):
        """Test getting admin profile with valid token."""
        # Create organization and login
        org_data = {
            "organization_name": "profile_test_org",
            "email": "admin@profiletest.com",
            "password": "TestPass123!"
        }
        
        create_response = client.post("/org/create", json=org_data)
        assert create_response.status_code == 200
        
        login_data = {
            "email": "admin@profiletest.com",
            "password": "TestPass123!"
        }
        
        login_response = client.post("/admin/login", json=login_data)
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        
        # Get profile
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/admin/profile", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["email"] == "admin@profiletest.com"
    
    def test_admin_profile_without_token(self):
        """Test getting admin profile without token."""
        response = client.get("/admin/profile")
        assert response.status_code == 403  # Forbidden
    
    def test_admin_logout(self):
        """Test admin logout."""
        # Create organization and login
        org_data = {
            "organization_name": "logout_test_org",
            "email": "admin@logouttest.com",
            "password": "TestPass123!"
        }
        
        create_response = client.post("/org/create", json=org_data)
        assert create_response.status_code == 200
        
        login_data = {
            "email": "admin@logouttest.com",
            "password": "TestPass123!"
        }
        
        login_response = client.post("/admin/login", json=login_data)
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        
        # Logout
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/admin/logout", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True