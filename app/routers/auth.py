"""
Authentication API endpoints.
"""
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import AdminLogin, LoginResponse
from app.services import AuthService
from app.auth import auth_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def admin_login(login_data: AdminLogin):
    """
    Authenticate admin user and return JWT access token.
    
    - **email**: Admin email address
    - **password**: Admin password
    
    Returns:
    - **access_token**: JWT token for authenticated requests
    - **token_type**: Always "bearer"
    - **expires_in**: Token expiration time in seconds
    - **admin_id**: Unique admin identifier
    - **organization_id**: Associated organization identifier
    
    Use the access token in the Authorization header:
    `Authorization: Bearer <access_token>`
    """
    try:
        result = AuthService.login_admin(login_data.email, login_data.password)
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.message,
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in admin_login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/profile")
async def get_admin_profile(current_admin: dict = Depends(auth_manager.get_current_admin)):
    """
    Get current authenticated admin profile information.
    
    Requires valid JWT token in Authorization header.
    
    Returns:
    - Admin ID and email
    - Associated organization ID
    - Authentication status
    """
    try:
        return {
            "success": True,
            "message": "Profile retrieved successfully",
            "admin_id": current_admin["admin_id"],
            "email": current_admin["email"],
            "organization_id": current_admin["organization_id"]
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in get_admin_profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout")
async def admin_logout(current_admin: dict = Depends(auth_manager.get_current_admin)):
    """
    Logout admin user (client-side token invalidation).
    
    Note: JWT tokens are stateless, so logout is handled client-side
    by discarding the token. This endpoint confirms successful logout
    and can be used for audit logging.
    """
    try:
        # Log the logout action for audit purposes
        from app.services import AuditService
        AuditService.log_action(
            action="admin_logout",
            admin_email=current_admin["email"],
            details={"organization_id": current_admin["organization_id"]}
        )
        
        return {
            "success": True,
            "message": "Logout successful. Please discard your access token."
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in admin_logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )