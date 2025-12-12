"""
Pydantic models for request/response validation.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, validator, Field
import re
from app.utils import ValidationUtils


class OrganizationCreate(BaseModel):
    """Model for creating a new organization."""
    organization_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('organization_name')
    def validate_organization_name(cls, v):
        if not ValidationUtils.is_valid_organization_name(v):
            raise ValueError('Organization name must be 3-50 characters and contain only letters, numbers, and underscores')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        password_check = ValidationUtils.is_strong_password(v)
        if not password_check['is_strong']:
            suggestions = ', '.join(password_check['suggestions'])
            raise ValueError(f'Password is too weak. {suggestions}')
        return v


class OrganizationUpdate(BaseModel):
    """Model for updating an organization."""
    organization_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('organization_name')
    def validate_organization_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Organization name can only contain letters, numbers, and underscores')
        return v.lower()


class OrganizationGet(BaseModel):
    """Model for getting organization details."""
    organization_name: str


class OrganizationDelete(BaseModel):
    """Model for deleting an organization."""
    organization_name: str


class AdminLogin(BaseModel):
    """Model for admin login."""
    email: EmailStr
    password: str


class OrganizationResponse(BaseModel):
    """Response model for organization operations."""
    success: bool
    message: str
    organization_id: Optional[str] = None
    organization_name: Optional[str] = None
    collection_name: Optional[str] = None
    admin_email: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LoginResponse(BaseModel):
    """Response model for login operations."""
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = "bearer"
    expires_in: Optional[int] = None
    admin_id: Optional[str] = None
    organization_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: datetime
    database: Dict[str, Any]
    version: str = "1.0.0"


class OrganizationStats(BaseModel):
    """Response model for organization statistics."""
    total_organizations: int
    total_admin_users: int
    recent_organizations: list
    database_health: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Standard error response model."""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# Internal models for database operations
class OrganizationDB(BaseModel):
    """Database model for organization storage."""
    organization_name: str
    collection_name: str
    admin_user_id: str
    created_at: datetime
    updated_at: datetime
    status: str = "active"
    metadata: Optional[Dict[str, Any]] = {}


class AdminUserDB(BaseModel):
    """Database model for admin user storage."""
    email: str
    password_hash: str
    organization_id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    last_login: Optional[datetime] = None


class AuditLogDB(BaseModel):
    """Database model for audit logging."""
    action: str
    organization_name: Optional[str] = None
    admin_email: Optional[str] = None
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[Dict[str, Any]] = {}
    success: bool


class DashboardMetrics(BaseModel):
    """Response model for dashboard metrics."""
    success: bool
    message: str
    organization: Dict[str, Any]
    activity: Dict[str, int]
    collection: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]
    uptime: Dict[str, Any]


class SystemMetrics(BaseModel):
    """Response model for system metrics."""
    success: bool
    message: str
    timestamp: str
    uptime: Dict[str, Any]
    database: Dict[str, Any]
    statistics: Dict[str, int]
    activity: Dict[str, int]
    service_info: Dict[str, str]


class AuditLogsResponse(BaseModel):
    """Response model for audit logs."""
    success: bool
    message: str
    pagination: Dict[str, Any]
    filters: Dict[str, Optional[str]]
    logs: List[Dict[str, Any]]


class PerformanceMetrics(BaseModel):
    """Response model for performance metrics."""
    success: bool
    message: str
    timestamp: str
    response_time_ms: float
    database: Dict[str, Any]
    uptime: Dict[str, Any]
    benchmarks: Dict[str, str]


class PasswordStrengthResponse(BaseModel):
    """Response model for password strength check."""
    is_strong: bool
    strength: str
    score: int
    checks: Dict[str, bool]
    suggestions: List[str]