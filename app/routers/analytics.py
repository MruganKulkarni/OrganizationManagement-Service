"""
Analytics and monitoring API endpoints.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.database import db_manager
from app.auth import auth_manager
from app.utils import MetricsUtils, DateTimeUtils
from app.services import AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics & Monitoring"])

# Service start time for uptime calculation
SERVICE_START_TIME = datetime.utcnow()


@router.get("/dashboard")
async def get_dashboard_metrics(
    current_admin: dict = Depends(auth_manager.get_current_admin)
):
    """
    Get comprehensive dashboard metrics for the authenticated organization.
    
    Requires authentication. Returns organization-specific analytics including:
    - Organization overview
    - Recent activity
    - Performance metrics
    - System health
    """
    try:
        org_collection = db_manager.get_organizations_collection()
        audit_collection = db_manager.get_audit_logs_collection()
        
        # Get organization details
        organization = org_collection.find_one({
            "_id": current_admin["organization_id"]
        })
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Calculate organization age
        created_at = organization.get("created_at", datetime.utcnow())
        age_days = (datetime.utcnow() - created_at).days
        
        # Get recent audit logs for this organization
        recent_logs = list(audit_collection.find(
            {"organization_name": organization["organization_name"]},
            {"_id": 0}
        ).sort("timestamp", -1).limit(10))
        
        # Get activity statistics
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        
        activity_stats = {
            "today": audit_collection.count_documents({
                "organization_name": organization["organization_name"],
                "timestamp": {"$gte": today}
            }),
            "this_week": audit_collection.count_documents({
                "organization_name": organization["organization_name"],
                "timestamp": {"$gte": week_ago}
            }),
            "total": audit_collection.count_documents({
                "organization_name": organization["organization_name"]
            })
        }
        
        # Get organization collection stats
        org_db_collection = db_manager.get_organization_collection(
            organization["organization_name"]
        )
        
        collection_stats = {
            "document_count": org_db_collection.count_documents({}),
            "estimated_size": "N/A"  # Would need additional MongoDB commands
        }
        
        return {
            "success": True,
            "message": "Dashboard metrics retrieved successfully",
            "organization": {
                "name": organization["organization_name"],
                "created_at": created_at.isoformat(),
                "age_days": age_days,
                "status": organization.get("status", "active"),
                "metadata": organization.get("metadata", {})
            },
            "activity": activity_stats,
            "collection": collection_stats,
            "recent_activity": recent_logs,
            "uptime": MetricsUtils.calculate_uptime(SERVICE_START_TIME)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard metrics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard metrics"
        )


@router.get("/system")
async def get_system_metrics():
    """
    Get system-wide metrics and health information.
    
    Returns:
    - Service uptime
    - Database statistics
    - Overall system health
    - Performance metrics
    
    Public endpoint for monitoring purposes.
    """
    try:
        # Get database health
        db_health = db_manager.health_check()
        
        # Get collection statistics
        org_collection = db_manager.get_organizations_collection()
        admin_collection = db_manager.get_admin_users_collection()
        audit_collection = db_manager.get_audit_logs_collection()
        
        total_orgs = org_collection.count_documents({})
        total_admins = admin_collection.count_documents({})
        total_audit_logs = audit_collection.count_documents({})
        
        # Calculate activity metrics
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        
        activity_metrics = {
            "organizations_created_today": org_collection.count_documents({
                "created_at": {"$gte": today}
            }),
            "organizations_created_this_week": org_collection.count_documents({
                "created_at": {"$gte": week_ago}
            }),
            "audit_logs_today": audit_collection.count_documents({
                "timestamp": {"$gte": today}
            }),
            "audit_logs_yesterday": audit_collection.count_documents({
                "timestamp": {"$gte": yesterday, "$lt": today}
            })
        }
        
        # System uptime
        uptime = MetricsUtils.calculate_uptime(SERVICE_START_TIME)
        
        return {
            "success": True,
            "message": "System metrics retrieved successfully",
            "timestamp": DateTimeUtils.get_utc_now().isoformat(),
            "uptime": uptime,
            "database": db_health,
            "statistics": {
                "total_organizations": total_orgs,
                "total_admin_users": total_admins,
                "total_audit_logs": total_audit_logs
            },
            "activity": activity_metrics,
            "service_info": {
                "version": "1.0.0",
                "environment": "production",
                "started_at": SERVICE_START_TIME.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"System metrics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system metrics"
        )


@router.get("/audit-logs")
async def get_audit_logs(
    limit: int = Query(50, ge=1, le=1000, description="Number of logs to retrieve"),
    skip: int = Query(0, ge=0, description="Number of logs to skip"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    current_admin: dict = Depends(auth_manager.get_current_admin)
):
    """
    Get audit logs for the authenticated organization.
    
    Requires authentication. Returns paginated audit logs with optional filtering.
    
    - **limit**: Maximum number of logs to return (1-1000)
    - **skip**: Number of logs to skip for pagination
    - **action**: Optional filter by action type
    """
    try:
        audit_collection = db_manager.get_audit_logs_collection()
        
        # Get organization name
        org_collection = db_manager.get_organizations_collection()
        organization = org_collection.find_one({
            "_id": current_admin["organization_id"]
        })
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        
        # Build query filter
        query_filter = {
            "organization_name": organization["organization_name"]
        }
        
        if action:
            query_filter["action"] = {"$regex": action, "$options": "i"}
        
        # Get total count
        total_count = audit_collection.count_documents(query_filter)
        
        # Get logs with pagination
        logs = list(audit_collection.find(
            query_filter,
            {"_id": 0}
        ).sort("timestamp", -1).skip(skip).limit(limit))
        
        return {
            "success": True,
            "message": "Audit logs retrieved successfully",
            "pagination": {
                "total": total_count,
                "limit": limit,
                "skip": skip,
                "has_more": skip + limit < total_count
            },
            "filters": {
                "action": action,
                "organization": organization["organization_name"]
            },
            "logs": logs
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audit logs error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs"
        )


@router.get("/performance")
async def get_performance_metrics():
    """
    Get performance metrics and benchmarks.
    
    Returns:
    - Response time statistics
    - Database performance metrics
    - System resource usage (if available)
    
    Public endpoint for performance monitoring.
    """
    try:
        # Get database performance stats
        db_health = db_manager.health_check()
        
        # Calculate some basic performance metrics
        start_time = datetime.utcnow()
        
        # Test database query performance
        org_collection = db_manager.get_organizations_collection()
        query_start = datetime.utcnow()
        org_collection.count_documents({})
        query_time = (datetime.utcnow() - query_start).total_seconds() * 1000
        
        total_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "success": True,
            "message": "Performance metrics retrieved successfully",
            "timestamp": DateTimeUtils.get_utc_now().isoformat(),
            "response_time_ms": round(total_time, 2),
            "database": {
                "status": db_health.get("status", "unknown"),
                "query_time_ms": round(query_time, 2),
                "collections": db_health.get("collections", 0),
                "data_size": db_health.get("data_size", 0),
                "storage_size": db_health.get("storage_size", 0)
            },
            "uptime": MetricsUtils.calculate_uptime(SERVICE_START_TIME),
            "benchmarks": {
                "avg_response_time_ms": "< 100",
                "database_query_time_ms": "< 50",
                "uptime_target": "99.9%"
            }
        }
        
    except Exception as e:
        logger.error(f"Performance metrics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performance metrics"
        )