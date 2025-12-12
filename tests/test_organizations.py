"""
Test cases for organization management endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestOrganizations:
    """Test organization CRUD operations."""
    
    def test_create_organization_success(self):
        """Test successful organization creation."""
        org_data = {
            "organization_name": "test_org",
            "email": "admin@test.com",
            "password": "TestPass123!"
        }
        
        response = client.post("/org/create", json=org_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["organization_name"] == "test_org"
        assert data["admin_email"] == "admin@test.com"
        assert "organization_id" in data
    
    def test_create_organization_duplicate(self):
        """Test organization creation with duplicate name."""
        org_data = {
            "organization_name": "duplicate_org",
            "email": "admin1@test.com",
            "password": "TestPass123!"
        }
        
        # Create first organization
        response1 = client.post("/org/create", json=org_data)
        assert response1.status_code == 200
        
        # Try to create duplicate
        org_data["email"] = "admin2@test.com"
        response2 = client.post("/org/create", json=org_data)
        assert response2.status_code == 400
    
    def test_create_organization_invalid_password(self):
        """Test organization creation with weak password."""
        org_data = {
            "organization_name": "weak_pass_org",
            "email": "admin@test.com",
            "password": "weak"
        }
        
        response = client.post("/org/create", json=org_data)
        assert response.status_code == 422  # Validation error
    
    def test_get_organization_success(self):
        """Test successful organization retrieval."""
        # First create an organization
        org_data = {
            "organization_name": "get_test_org",
            "email": "admin@gettest.com",
            "password": "TestPass123!"
        }
        
        create_response = client.post("/org/create", json=org_data)
        assert create_response.status_code == 200
        
        # Then retrieve it
        response = client.get("/org/get", params={"organization_name": "get_test_org"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["organization_name"] == "get_test_org"
    
    def test_get_organization_not_found(self):
        """Test organization retrieval for non-existent organization."""
        response = client.get("/org/get", params={"organization_name": "nonexistent"})
        assert response.status_code == 404
    
    def test_get_organization_stats(self):
        """Test organization statistics endpoint."""
        response = client.get("/org/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_organizations" in data
        assert "total_admin_users" in data
        assert "recent_organizations" in data
        assert "database_health" in data