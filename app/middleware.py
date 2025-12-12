"""
Custom middleware for enhanced functionality and monitoring.
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from app.services import AuditService

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all requests with timing and audit trail."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # Extract client information
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        url = str(request.url)
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log request details
        logger.info(
            f"{method} {url} - {response.status_code} - "
            f"{process_time:.3f}s - {client_ip} - {user_agent[:100]}"
        )
        
        # Add custom headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-API-Version"] = "1.0.0"
        
        # Audit sensitive operations
        if method in ["POST", "PUT", "DELETE"] and response.status_code < 400:
            try:
                # Extract organization info from path or body if available
                org_name = None
                if "/org/" in url:
                    path_parts = url.split("/")
                    if "org" in path_parts:
                        org_idx = path_parts.index("org")
                        if org_idx + 1 < len(path_parts):
                            operation = path_parts[org_idx + 1]
                            if operation in ["create", "update", "delete"]:
                                AuditService.log_action(
                                    action=f"api_{operation}_request",
                                    ip_address=client_ip,
                                    user_agent=user_agent,
                                    details={
                                        "method": method,
                                        "url": url,
                                        "status_code": response.status_code,
                                        "process_time": process_time
                                    }
                                )
            except Exception as e:
                logger.warning(f"Failed to log audit trail: {e}")
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # More permissive CSP for API documentation with custom styling
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "connect-src 'self'"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        # Remove server header for security
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware."""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries
        self.clients = {
            ip: timestamps for ip, timestamps in self.clients.items()
            if any(t > current_time - self.period for t in timestamps)
        }
        
        # Check rate limit
        if client_ip in self.clients:
            # Filter recent requests
            recent_requests = [
                t for t in self.clients[client_ip] 
                if t > current_time - self.period
            ]
            
            if len(recent_requests) >= self.calls:
                return Response(
                    content='{"error": "Rate limit exceeded"}',
                    status_code=429,
                    headers={"Content-Type": "application/json"}
                )
            
            self.clients[client_ip] = recent_requests + [current_time]
        else:
            self.clients[client_ip] = [current_time]
        
        return await call_next(request)