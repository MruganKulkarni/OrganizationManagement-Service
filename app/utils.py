"""
Utility functions for the Organization Management Service.
"""
import re
import secrets
import string
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import hashlib


class ValidationUtils:
    """Utility class for data validation."""
    
    @staticmethod
    def is_valid_organization_name(name: str) -> bool:
        """Validate organization name format."""
        if not name or len(name) < 3 or len(name) > 50:
            return False
        return bool(re.match(r'^[a-zA-Z0-9_]+$', name))
    
    @staticmethod
    def is_strong_password(password: str) -> Dict[str, Any]:
        """Check password strength and return detailed feedback."""
        checks = {
            'length': len(password) >= 8,
            'uppercase': bool(re.search(r'[A-Z]', password)),
            'lowercase': bool(re.search(r'[a-z]', password)),
            'digit': bool(re.search(r'\d', password)),
            'special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
        }
        
        score = sum(checks.values())
        strength = 'weak' if score < 3 else 'medium' if score < 5 else 'strong'
        
        return {
            'is_strong': score >= 4,
            'strength': strength,
            'score': score,
            'checks': checks,
            'suggestions': ValidationUtils._get_password_suggestions(checks)
        }
    
    @staticmethod
    def _get_password_suggestions(checks: Dict[str, bool]) -> List[str]:
        """Get password improvement suggestions."""
        suggestions = []
        if not checks['length']:
            suggestions.append("Use at least 8 characters")
        if not checks['uppercase']:
            suggestions.append("Add uppercase letters")
        if not checks['lowercase']:
            suggestions.append("Add lowercase letters")
        if not checks['digit']:
            suggestions.append("Add numbers")
        if not checks['special']:
            suggestions.append("Add special characters (!@#$%^&*)")
        return suggestions


class SecurityUtils:
    """Utility class for security operations."""
    
    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """Generate a secure API key."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_organization_id() -> str:
        """Generate a unique organization identifier."""
        timestamp = str(int(datetime.utcnow().timestamp()))
        random_part = secrets.token_hex(8)
        return f"org_{timestamp}_{random_part}"
    
    @staticmethod
    def hash_sensitive_data(data: str) -> str:
        """Hash sensitive data for logging/storage."""
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 255) -> str:
        """Sanitize user input."""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', text)
        
        # Limit length
        return sanitized[:max_length].strip()


class DateTimeUtils:
    """Utility class for date/time operations."""
    
    @staticmethod
    def get_utc_now() -> datetime:
        """Get current UTC datetime."""
        return datetime.utcnow()
    
    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S UTC") -> str:
        """Format datetime for display."""
        return dt.strftime(format_str)
    
    @staticmethod
    def get_expiry_time(minutes: int = 30) -> datetime:
        """Get expiry time from now."""
        return datetime.utcnow() + timedelta(minutes=minutes)
    
    @staticmethod
    def is_expired(expiry_time: datetime) -> bool:
        """Check if a datetime has expired."""
        return datetime.utcnow() > expiry_time


class ResponseUtils:
    """Utility class for API response formatting."""
    
    @staticmethod
    def success_response(
        message: str,
        data: Optional[Dict[str, Any]] = None,
        status_code: int = 200
    ) -> Dict[str, Any]:
        """Create a standardized success response."""
        response = {
            "success": True,
            "message": message,
            "timestamp": DateTimeUtils.get_utc_now().isoformat(),
            "status_code": status_code
        }
        
        if data:
            response.update(data)
        
        return response
    
    @staticmethod
    def error_response(
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400
    ) -> Dict[str, Any]:
        """Create a standardized error response."""
        response = {
            "success": False,
            "message": message,
            "timestamp": DateTimeUtils.get_utc_now().isoformat(),
            "status_code": status_code
        }
        
        if error_code:
            response["error_code"] = error_code
        
        if details:
            response["details"] = details
        
        return response


class MetricsUtils:
    """Utility class for metrics and monitoring."""
    
    @staticmethod
    def calculate_uptime(start_time: datetime) -> Dict[str, Any]:
        """Calculate service uptime."""
        uptime_delta = datetime.utcnow() - start_time
        
        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            "total_seconds": uptime_delta.total_seconds(),
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "formatted": f"{days}d {hours}h {minutes}m {seconds}s"
        }
    
    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        """Format bytes in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"


class DatabaseUtils:
    """Utility class for database operations."""
    
    @staticmethod
    def sanitize_collection_name(name: str) -> str:
        """Sanitize collection name for MongoDB."""
        # Convert to lowercase and replace invalid characters
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
        
        # Ensure it starts with a letter or underscore
        if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
            sanitized = f"_{sanitized}"
        
        # Limit length (MongoDB collection names have limits)
        return sanitized[:64]
    
    @staticmethod
    def build_query_filter(
        filters: Dict[str, Any],
        allowed_fields: List[str]
    ) -> Dict[str, Any]:
        """Build MongoDB query filter safely."""
        query = {}
        
        for field, value in filters.items():
            if field in allowed_fields and value is not None:
                if isinstance(value, str):
                    # Case-insensitive regex for string fields
                    query[field] = {"$regex": re.escape(value), "$options": "i"}
                else:
                    query[field] = value
        
        return query