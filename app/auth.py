"""
Authentication and authorization utilities.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from app.database import db_manager

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()


class AuthManager:
    """Handles authentication and authorization operations."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any]) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.jwt_secret_key, 
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def authenticate_admin(email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate an admin user."""
        try:
            admin_collection = db_manager.get_admin_users_collection()
            admin_user = admin_collection.find_one({"email": email})
            
            if not admin_user:
                logger.warning(f"Admin user not found: {email}")
                return None
            
            if not AuthManager.verify_password(password, admin_user["password_hash"]):
                logger.warning(f"Invalid password for admin: {email}")
                return None
            
            # Update last login
            admin_collection.update_one(
                {"_id": admin_user["_id"]},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            return {
                "admin_id": str(admin_user["_id"]),
                "email": admin_user["email"],
                "organization_id": admin_user["organization_id"],
                "is_active": admin_user.get("is_active", True)
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    @staticmethod
    def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Get current authenticated admin from JWT token."""
        try:
            payload = AuthManager.verify_token(credentials.credentials)
            admin_id = payload.get("admin_id")
            organization_id = payload.get("organization_id")
            
            if not admin_id or not organization_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            # Verify admin still exists and is active
            admin_collection = db_manager.get_admin_users_collection()
            admin_user = admin_collection.find_one({
                "_id": admin_id,
                "is_active": True
            })
            
            if not admin_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Admin user not found or inactive"
                )
            
            return {
                "admin_id": admin_id,
                "email": admin_user["email"],
                "organization_id": organization_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )


# Global auth manager instance
auth_manager = AuthManager()