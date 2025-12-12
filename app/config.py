"""
Configuration management for the Organization Management Service.
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator
from pydantic import validator


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "org_master_db"
    
    # JWT Configuration
    jwt_secret_key: str = "your-super-secret-jwt-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    
    # Application Configuration
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # API Configuration
    api_title: str = "Organization Management Service"
    api_description: str = "A modern multi-tenant organization management system"
    api_version: str = "1.0.0"
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()