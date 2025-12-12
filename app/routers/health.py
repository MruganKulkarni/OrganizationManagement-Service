"""
Health monitoring and system status API endpoints.
"""
import logging
from fastapi import APIRouter, HTTPException, status
from app.models import HealthResponse
from app.services import HealthService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health & Monitoring"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    System health check endpoint.
    
    Returns:
    - Overall system status (healthy/unhealthy)
    - Current timestamp
    - Database connectivity and statistics
    - API version information
    
    Use this endpoint for:
    - Load balancer health checks
    - Monitoring system integration
    - Deployment verification
    """
    try:
        return HealthService.get_health_status()
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable"
        )


@router.get("/ping")
async def ping():
    """
    Simple ping endpoint for basic connectivity testing.
    
    Returns a minimal response to verify the service is running.
    Useful for basic uptime monitoring.
    """
    return {"status": "ok", "message": "pong"}


@router.get("/version")
async def get_version():
    """
    Get API version and build information.
    
    Returns:
    - API version
    - Service name
    - Build timestamp (if available)
    """
    return {
        "service": "Organization Management Service",
        "version": "1.0.0",
        "api_version": "v1",
        "description": "Multi-tenant organization management system"
    }