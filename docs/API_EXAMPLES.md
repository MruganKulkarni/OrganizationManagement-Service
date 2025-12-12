# 📚 API Usage Examples

This document provides comprehensive examples of how to use the Organization Management Service API.

## 🔧 Base URL

```
http://localhost:8000
```

## 📋 Table of Contents

1. [Organization Management](#organization-management)
2. [Authentication](#authentication)
3. [Health Monitoring](#health-monitoring)
4. [Error Handling](#error-handling)

## 🏢 Organization Management

### Create Organization

Create a new organization with an admin user.

```bash
curl -X POST "http://localhost:8000/org/create" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "acme_corp",
    "email": "admin@acme.com",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Organization created successfully",
  "organization_id": "507f1f77bcf86cd799439011",
  "organization_name": "acme_corp",
  "collection_name": "org_acme_corp",
  "admin_email": "admin@acme.com",
  "created_at": "2024-12-12T10:30:00Z"
}
```

### Get Organization

Retrieve organization details by name.

```bash
curl -X GET "http://localhost:8000/org/get?organization_name=acme_corp"
```

**Response:**
```json
{
  "success": true,
  "message": "Organization found",
  "organization_id": "507f1f77bcf86cd799439011",
  "organization_name": "acme_corp",
  "collection_name": "org_acme_corp",
  "admin_email": "admin@acme.com",
  "created_at": "2024-12-12T10:30:00Z",
  "updated_at": "2024-12-12T10:30:00Z"
}
```

### Update Organization

Update organization details (requires authentication).

```bash
# First, get the access token by logging in
TOKEN=$(curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@acme.com",
    "password": "SecurePass123!"
  }' | jq -r '.access_token')

# Then update the organization
curl -X PUT "http://localhost:8000/org/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "organization_name": "acme_corporation",
    "email": "admin@acme-corp.com",
    "password": "NewSecurePass123!"
  }'
```

### Delete Organization

Delete an organization (requires authentication).

```bash
curl -X DELETE "http://localhost:8000/org/delete?organization_name=acme_corp" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Organization Statistics

Get system-wide organization statistics.

```bash
curl -X GET "http://localhost:8000/org/stats"
```

**Response:**
```json
{
  "total_organizations": 5,
  "total_admin_users": 5,
  "recent_organizations": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "organization_name": "acme_corp",
      "created_at": "2024-12-12T10:30:00Z",
      "metadata": {
        "admin_email": "admin@acme.com"
      }
    }
  ],
  "database_health": {
    "status": "healthy",
    "collections": 8,
    "data_size": 1024
  }
}
```

## 🔐 Authentication

### Admin Login

Authenticate and receive a JWT token.

```bash
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@acme.com",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "admin_id": "507f1f77bcf86cd799439012",
  "organization_id": "507f1f77bcf86cd799439011"
}
```

### Get Admin Profile

Get current admin profile information.

```bash
curl -X GET "http://localhost:8000/admin/profile" \
  -H "Authorization: Bearer $TOKEN"
```

### Admin Logout

Logout (client-side token invalidation).

```bash
curl -X POST "http://localhost:8000/admin/logout" \
  -H "Authorization: Bearer $TOKEN"
```

## 🏥 Health Monitoring

### Health Check

Check system health status.

```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-12T10:30:00Z",
  "database": {
    "status": "healthy",
    "database": "org_master_db",
    "collections": 8,
    "data_size": 1024,
    "storage_size": 4096
  },
  "version": "1.0.0"
}
```

### Simple Ping

Basic connectivity test.

```bash
curl -X GET "http://localhost:8000/ping"
```

### Version Information

Get API version details.

```bash
curl -X GET "http://localhost:8000/version"
```

## ❌ Error Handling

### Validation Errors

When request data is invalid:

```json
{
  "success": false,
  "message": "Validation error",
  "error_code": 422,
  "details": {
    "field": "password",
    "message": "Password must contain at least one uppercase letter"
  }
}
```

### Authentication Errors

When authentication fails:

```json
{
  "success": false,
  "message": "Invalid authentication credentials",
  "error_code": 401
}
```

### Not Found Errors

When resource doesn't exist:

```json
{
  "success": false,
  "message": "Organization 'nonexistent' not found",
  "error_code": 404
}
```

### Server Errors

When internal server error occurs:

```json
{
  "success": false,
  "message": "Internal server error",
  "error_code": 500
}
```

## 🔄 Complete Workflow Example

Here's a complete workflow showing organization lifecycle:

```bash
# 1. Create organization
curl -X POST "http://localhost:8000/org/create" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "demo_org",
    "email": "admin@demo.com",
    "password": "DemoPass123!"
  }'

# 2. Login as admin
TOKEN=$(curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@demo.com",
    "password": "DemoPass123!"
  }' | jq -r '.access_token')

# 3. Get admin profile
curl -X GET "http://localhost:8000/admin/profile" \
  -H "Authorization: Bearer $TOKEN"

# 4. Update organization
curl -X PUT "http://localhost:8000/org/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "organization_name": "demo_organization",
    "email": "admin@demo-org.com",
    "password": "NewDemoPass123!"
  }'

# 5. Check organization stats
curl -X GET "http://localhost:8000/org/stats"

# 6. Delete organization
curl -X DELETE "http://localhost:8000/org/delete?organization_name=demo_organization" \
  -H "Authorization: Bearer $TOKEN"
```

## 🐍 Python Client Example

Here's how to use the API with Python:

```python
import requests
import json

class OrgManagementClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
    
    def create_organization(self, org_name, email, password):
        """Create a new organization."""
        response = requests.post(
            f"{self.base_url}/org/create",
            json={
                "organization_name": org_name,
                "email": email,
                "password": password
            }
        )
        return response.json()
    
    def login(self, email, password):
        """Login and store token."""
        response = requests.post(
            f"{self.base_url}/admin/login",
            json={"email": email, "password": password}
        )
        data = response.json()
        if data.get("success"):
            self.token = data["access_token"]
        return data
    
    def get_headers(self):
        """Get headers with authorization."""
        return {"Authorization": f"Bearer {self.token}"}
    
    def update_organization(self, org_name, email, password):
        """Update organization."""
        response = requests.put(
            f"{self.base_url}/org/update",
            json={
                "organization_name": org_name,
                "email": email,
                "password": password
            },
            headers=self.get_headers()
        )
        return response.json()

# Usage example
client = OrgManagementClient()

# Create organization
result = client.create_organization("test_org", "admin@test.com", "TestPass123!")
print(json.dumps(result, indent=2))

# Login
login_result = client.login("admin@test.com", "TestPass123!")
print(json.dumps(login_result, indent=2))
```

This completes the API usage examples. The service provides a comprehensive set of endpoints for managing organizations in a multi-tenant architecture with proper authentication and validation.