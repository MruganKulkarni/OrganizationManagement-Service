"""
Business logic services for organization management.
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from app.database import db_manager
from app.auth import auth_manager
from app.config import settings
from app.models import (
    OrganizationCreate, OrganizationUpdate, OrganizationResponse,
    LoginResponse, HealthResponse, OrganizationStats, ErrorResponse
)

logger = logging.getLogger(__name__)


class OrganizationService:
    """Service class for organization management operations."""
    
    @staticmethod
    def create_organization(org_data: OrganizationCreate) -> OrganizationResponse:
        """Create a new organization with admin user."""
        try:
            # Check if organization already exists
            org_collection = db_manager.get_organizations_collection()
            existing_org = org_collection.find_one({
                "organization_name": org_data.organization_name
            })
            
            if existing_org:
                return OrganizationResponse(
                    success=False,
                    message=f"Organization '{org_data.organization_name}' already exists"
                )
            
            # Check if admin email already exists
            admin_collection = db_manager.get_admin_users_collection()
            existing_admin = admin_collection.find_one({"email": org_data.email})
            
            if existing_admin:
                return OrganizationResponse(
                    success=False,
                    message=f"Admin email '{org_data.email}' is already registered"
                )
            
            # Create organization collection
            collection_name = f"org_{org_data.organization_name}"
            org_db_collection = db_manager.create_organization_collection(org_data.organization_name)
            
            # Create admin user
            admin_id = ObjectId()
            password_hash = auth_manager.hash_password(org_data.password)
            
            admin_user = {
                "_id": admin_id,
                "email": org_data.email,
                "password_hash": password_hash,
                "organization_id": None,  # Will be set after org creation
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True,
                "last_login": None
            }
            
            # Create organization record
            org_id = ObjectId()
            organization = {
                "_id": org_id,
                "organization_name": org_data.organization_name,
                "collection_name": collection_name,
                "admin_user_id": str(admin_id),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "active",
                "metadata": {
                    "admin_email": org_data.email,
                    "total_users": 1,
                    "plan": "basic"
                }
            }
            
            # Update admin user with organization ID
            admin_user["organization_id"] = str(org_id)
            
            # Insert records
            org_collection.insert_one(organization)
            admin_collection.insert_one(admin_user)
            
            # Update organization collection metadata
            org_db_collection.update_one(
                {"_id": "metadata"},
                {"$set": {"created_at": datetime.utcnow()}}
            )
            
            # Log audit trail
            AuditService.log_action(
                action="organization_created",
                organization_name=org_data.organization_name,
                admin_email=org_data.email,
                details={"collection_name": collection_name}
            )
            
            logger.info(f"Created organization: {org_data.organization_name}")
            
            return OrganizationResponse(
                success=True,
                message="Organization created successfully",
                organization_id=str(org_id),
                organization_name=org_data.organization_name,
                collection_name=collection_name,
                admin_email=org_data.email,
                created_at=organization["created_at"]
            )
            
        except Exception as e:
            logger.error(f"Failed to create organization: {e}")
            return OrganizationResponse(
                success=False,
                message=f"Failed to create organization: {str(e)}"
            )
    
    @staticmethod
    def get_organization(org_name: str) -> OrganizationResponse:
        """Get organization details by name."""
        try:
            org_collection = db_manager.get_organizations_collection()
            organization = org_collection.find_one({
                "organization_name": org_name.lower()
            })
            
            if not organization:
                return OrganizationResponse(
                    success=False,
                    message=f"Organization '{org_name}' not found"
                )
            
            return OrganizationResponse(
                success=True,
                message="Organization found",
                organization_id=str(organization["_id"]),
                organization_name=organization["organization_name"],
                collection_name=organization["collection_name"],
                admin_email=organization["metadata"].get("admin_email"),
                created_at=organization["created_at"],
                updated_at=organization["updated_at"]
            )
            
        except Exception as e:
            logger.error(f"Failed to get organization: {e}")
            return OrganizationResponse(
                success=False,
                message=f"Failed to retrieve organization: {str(e)}"
            )
    
    @staticmethod
    def update_organization(org_data: OrganizationUpdate, current_admin: Dict[str, Any]) -> OrganizationResponse:
        """Update organization with data migration."""
        try:
            org_collection = db_manager.get_organizations_collection()
            admin_collection = db_manager.get_admin_users_collection()
            
            # Get current organization
            current_org = org_collection.find_one({
                "_id": ObjectId(current_admin["organization_id"])
            })
            
            if not current_org:
                return OrganizationResponse(
                    success=False,
                    message="Current organization not found"
                )
            
            old_org_name = current_org["organization_name"]
            new_org_name = org_data.organization_name
            
            # Check if new name conflicts with existing organization
            if old_org_name != new_org_name:
                existing_org = org_collection.find_one({
                    "organization_name": new_org_name
                })
                
                if existing_org:
                    return OrganizationResponse(
                        success=False,
                        message=f"Organization name '{new_org_name}' already exists"
                    )
            
            # Update admin credentials if changed
            admin_updates = {}
            if org_data.email != current_admin["email"]:
                # Check if new email conflicts
                existing_admin = admin_collection.find_one({
                    "email": org_data.email,
                    "_id": {"$ne": ObjectId(current_admin["admin_id"])}
                })
                
                if existing_admin:
                    return OrganizationResponse(
                        success=False,
                        message=f"Email '{org_data.email}' is already registered"
                    )
                
                admin_updates["email"] = org_data.email
            
            # Update password
            admin_updates["password_hash"] = auth_manager.hash_password(org_data.password)
            admin_updates["updated_at"] = datetime.utcnow()
            
            # Handle organization name change with data migration
            if old_org_name != new_org_name:
                # Create new collection
                new_collection = db_manager.create_organization_collection(new_org_name)
                old_collection = db_manager.get_organization_collection(old_org_name)
                
                # Migrate data (excluding metadata document)
                old_docs = list(old_collection.find({"_id": {"$ne": "metadata"}}))
                if old_docs:
                    new_collection.insert_many(old_docs)
                
                # Delete old collection
                db_manager.delete_organization_collection(old_org_name)
                
                # Update organization record
                org_updates = {
                    "organization_name": new_org_name,
                    "collection_name": f"org_{new_org_name}",
                    "updated_at": datetime.utcnow(),
                    "metadata.admin_email": org_data.email
                }
            else:
                org_updates = {
                    "updated_at": datetime.utcnow(),
                    "metadata.admin_email": org_data.email
                }
            
            # Apply updates
            org_collection.update_one(
                {"_id": ObjectId(current_admin["organization_id"])},
                {"$set": org_updates}
            )
            
            admin_collection.update_one(
                {"_id": ObjectId(current_admin["admin_id"])},
                {"$set": admin_updates}
            )
            
            # Log audit trail
            AuditService.log_action(
                action="organization_updated",
                organization_name=new_org_name,
                admin_email=org_data.email,
                details={
                    "old_name": old_org_name,
                    "new_name": new_org_name,
                    "data_migrated": old_org_name != new_org_name
                }
            )
            
            logger.info(f"Updated organization: {old_org_name} -> {new_org_name}")
            
            return OrganizationResponse(
                success=True,
                message="Organization updated successfully",
                organization_id=current_admin["organization_id"],
                organization_name=new_org_name,
                collection_name=f"org_{new_org_name}",
                admin_email=org_data.email,
                updated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Failed to update organization: {e}")
            return OrganizationResponse(
                success=False,
                message=f"Failed to update organization: {str(e)}"
            )
    
    @staticmethod
    def delete_organization(org_name: str, current_admin: Dict[str, Any]) -> OrganizationResponse:
        """Delete organization and cleanup resources."""
        try:
            org_collection = db_manager.get_organizations_collection()
            admin_collection = db_manager.get_admin_users_collection()
            
            # Get organization
            organization = org_collection.find_one({
                "_id": ObjectId(current_admin["organization_id"]),
                "organization_name": org_name.lower()
            })
            
            if not organization:
                return OrganizationResponse(
                    success=False,
                    message="Organization not found or access denied"
                )
            
            # Delete organization collection
            success = db_manager.delete_organization_collection(org_name)
            
            if not success:
                return OrganizationResponse(
                    success=False,
                    message="Failed to delete organization data"
                )
            
            # Delete admin user
            admin_collection.delete_one({"_id": ObjectId(current_admin["admin_id"])})
            
            # Delete organization record
            org_collection.delete_one({"_id": ObjectId(current_admin["organization_id"])})
            
            # Log audit trail
            AuditService.log_action(
                action="organization_deleted",
                organization_name=org_name,
                admin_email=current_admin["email"],
                details={"collection_name": organization["collection_name"]}
            )
            
            logger.info(f"Deleted organization: {org_name}")
            
            return OrganizationResponse(
                success=True,
                message="Organization deleted successfully",
                organization_name=org_name
            )
            
        except Exception as e:
            logger.error(f"Failed to delete organization: {e}")
            return OrganizationResponse(
                success=False,
                message=f"Failed to delete organization: {str(e)}"
            )


class AuthService:
    """Service class for authentication operations."""
    
    @staticmethod
    def login_admin(email: str, password: str) -> LoginResponse:
        """Authenticate admin and return JWT token."""
        try:
            # Authenticate admin
            admin_data = auth_manager.authenticate_admin(email, password)
            
            if not admin_data:
                return LoginResponse(
                    success=False,
                    message="Invalid email or password"
                )
            
            # Create JWT token
            token_data = {
                "admin_id": admin_data["admin_id"],
                "email": admin_data["email"],
                "organization_id": admin_data["organization_id"]
            }
            
            access_token = auth_manager.create_access_token(token_data)
            
            # Log audit trail
            AuditService.log_action(
                action="admin_login",
                admin_email=email,
                details={"organization_id": admin_data["organization_id"]}
            )
            
            logger.info(f"Admin login successful: {email}")
            
            return LoginResponse(
                success=True,
                message="Login successful",
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.jwt_expire_minutes * 60,
                admin_id=admin_data["admin_id"],
                organization_id=admin_data["organization_id"]
            )
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return LoginResponse(
                success=False,
                message=f"Login failed: {str(e)}"
            )


class HealthService:
    """Service class for health monitoring."""
    
    @staticmethod
    def get_health_status() -> HealthResponse:
        """Get system health status."""
        try:
            db_health = db_manager.health_check()
            
            return HealthResponse(
                status="healthy" if db_health["status"] == "healthy" else "unhealthy",
                timestamp=datetime.utcnow(),
                database=db_health
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthResponse(
                status="unhealthy",
                timestamp=datetime.utcnow(),
                database={"status": "unhealthy", "error": str(e)}
            )
    
    @staticmethod
    def get_organization_stats() -> OrganizationStats:
        """Get organization statistics."""
        try:
            org_collection = db_manager.get_organizations_collection()
            admin_collection = db_manager.get_admin_users_collection()
            
            total_orgs = org_collection.count_documents({})
            total_admins = admin_collection.count_documents({})
            
            # Get recent organizations (last 10)
            recent_orgs = list(org_collection.find(
                {},
                {"organization_name": 1, "created_at": 1, "metadata.admin_email": 1}
            ).sort("created_at", -1).limit(10))
            
            # Convert ObjectId to string for JSON serialization
            for org in recent_orgs:
                org["_id"] = str(org["_id"])
            
            db_health = db_manager.health_check()
            
            return OrganizationStats(
                total_organizations=total_orgs,
                total_admin_users=total_admins,
                recent_organizations=recent_orgs,
                database_health=db_health
            )
            
        except Exception as e:
            logger.error(f"Failed to get organization stats: {e}")
            return OrganizationStats(
                total_organizations=0,
                total_admin_users=0,
                recent_organizations=[],
                database_health={"status": "unhealthy", "error": str(e)}
            )


class AuditService:
    """Service class for audit logging."""
    
    @staticmethod
    def log_action(
        action: str,
        organization_name: Optional[str] = None,
        admin_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True
    ) -> None:
        """Log an audit trail entry."""
        try:
            audit_collection = db_manager.get_audit_logs_collection()
            
            audit_log = {
                "action": action,
                "organization_name": organization_name,
                "admin_email": admin_email,
                "timestamp": datetime.utcnow(),
                "ip_address": ip_address,
                "user_agent": user_agent,
                "details": details or {},
                "success": success
            }
            
            audit_collection.insert_one(audit_log)
            
        except Exception as e:
            logger.error(f"Failed to log audit action: {e}")