"""
Organization management API endpoints.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from app.models import (
    OrganizationCreate, OrganizationUpdate, OrganizationGet, OrganizationDelete,
    OrganizationResponse, OrganizationStats, ErrorResponse
)
from app.services import OrganizationService, HealthService
from app.auth import auth_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/org", tags=["Organizations"])


@router.post("/create", response_model=OrganizationResponse)
async def create_organization(org_data: OrganizationCreate):
    """
    Create a new organization with dynamic collection and admin user.
    
    - **organization_name**: Unique organization identifier (alphanumeric + underscores)
    - **email**: Admin email address
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit)
    
    Creates:
    - Organization record in master database
    - Dynamic MongoDB collection for the organization
    - Admin user with hashed password
    - Audit log entry
    """
    try:
        result = OrganizationService.create_organization(org_data)
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/get", response_model=OrganizationResponse)
async def get_organization(organization_name: str):
    """
    Retrieve organization details by name.
    
    - **organization_name**: Name of the organization to retrieve
    
    Returns organization metadata including:
    - Organization ID and name
    - Collection name
    - Admin email
    - Creation and update timestamps
    """
    try:
        result = OrganizationService.get_organization(organization_name)
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.message
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/update", response_model=OrganizationResponse)
async def update_organization(
    org_data: OrganizationUpdate,
    current_admin: dict = Depends(auth_manager.get_current_admin)
):
    """
    Update organization details with automatic data migration.
    
    Requires authentication. Only the organization's admin can update it.
    
    - **organization_name**: New organization name (triggers data migration if changed)
    - **email**: New admin email
    - **password**: New admin password
    
    Features:
    - Automatic data migration when organization name changes
    - Email uniqueness validation
    - Password strength validation
    - Audit logging
    """
    try:
        result = OrganizationService.update_organization(org_data, current_admin)
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/delete", response_model=OrganizationResponse)
async def delete_organization(
    organization_name: str,
    current_admin: dict = Depends(auth_manager.get_current_admin)
):
    """
    Delete organization and all associated data.
    
    Requires authentication. Only the organization's admin can delete it.
    
    - **organization_name**: Name of organization to delete
    
    This operation:
    - Deletes the organization's MongoDB collection
    - Removes admin user record
    - Removes organization metadata
    - Creates audit log entry
    
    **Warning**: This action is irreversible!
    """
    try:
        result = OrganizationService.delete_organization(organization_name, current_admin)
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in delete_organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/stats", response_model=OrganizationStats)
async def get_organization_stats():
    """
    Get system-wide organization statistics.
    
    Returns:
    - Total number of organizations
    - Total number of admin users
    - List of recent organizations
    - Database health information
    
    Useful for monitoring and analytics.
    """
    try:
        return HealthService.get_organization_stats()
        
    except Exception as e:
        logger.error(f"Unexpected error in get_organization_stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )