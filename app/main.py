"""
FastAPI application main module.
Organization Management Service - A modern multi-tenant organization management system.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import db_manager
from app.routers import organizations, auth, health, analytics
from app.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware, RateLimitingMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Organization Management Service...")
    try:
        db_manager.connect()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Organization Management Service...")
    db_manager.disconnect()
    logger.info("Database connection closed")


# Create FastAPI application with enhanced documentation
app = FastAPI(
    title=settings.api_title,
    description="Multi-tenant organization management system with secure authentication and dynamic data isolation.",
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Organization Management Service",
        "url": "https://github.com/MruganKulkarni/OrganizationManagement-Service",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    swagger_ui_parameters={
        "customCssUrl": "/static/custom.css"
    }
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitingMiddleware, calls=100, period=60)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.status_code,
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": 500,
            "path": str(request.url)
        }
    )


# Include routers
app.include_router(organizations.router)
app.include_router(auth.router)
app.include_router(health.router)
app.include_router(analytics.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health",
        "status": "running"
    }


@app.get("/info")
async def api_info():
    """Detailed API information and available endpoints."""
    return {
        "service": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "environment": settings.environment,
        "endpoints": {
            "organizations": {
                "create": "POST /org/create",
                "get": "GET /org/get",
                "update": "PUT /org/update",
                "delete": "DELETE /org/delete",
                "stats": "GET /org/stats"
            },
            "authentication": {
                "login": "POST /admin/login",
                "profile": "GET /admin/profile",
                "logout": "POST /admin/logout"
            },
            "monitoring": {
                "health": "GET /health",
                "ping": "GET /ping",
                "version": "GET /version"
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )