"""Core configuration for the TeamFlow application."""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="Application environment")
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./teamflow_dev.db",
        description="Database connection URL"
    )
    TEST_DATABASE_URL: Optional[str] = Field(
        default="sqlite+aiosqlite:///./teamflow_test.db",
        description="Test database connection URL"
    )
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    
    # Security
    SECRET_KEY: str = Field(
        default="your-super-secret-jwt-key-change-in-production",
        description="Secret key for JWT token generation"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15, 
        description="Access token expiration time in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, 
        description="Refresh token expiration time in days"
    )
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="Allowed CORS origins"
    )
    
    # Email Configuration
    SMTP_HOST: str = Field(default="localhost", description="SMTP server host")
    SMTP_PORT: int = Field(default=1025, description="SMTP server port")
    SMTP_USER: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    SMTP_TLS: bool = Field(default=False, description="Use TLS for SMTP")
    FROM_EMAIL: str = Field(
        default="noreply@teamflow.dev", 
        description="Default from email address"
    )
    
    # File Upload
    UPLOAD_DIR: str = Field(default="./uploads", description="File upload directory")
    MAX_UPLOAD_SIZE: int = Field(
        default=10485760,  # 10MB
        description="Maximum file upload size in bytes"
    )
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60, 
        description="Rate limit per minute per IP"
    )
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=20, description="Default page size")
    MAX_PAGE_SIZE: int = Field(default=100, description="Maximum page size")
    
    # Celery (Background Tasks)
    CELERY_BROKER_URL: Optional[str] = Field(
        default=None, 
        description="Celery broker URL (defaults to REDIS_URL)"
    )
    CELERY_RESULT_BACKEND: Optional[str] = Field(
        default=None, 
        description="Celery result backend URL (defaults to REDIS_URL)"
    )
    
    # AWS Configuration (for production)
    AWS_REGION: str = Field(default="us-west-2", description="AWS region")
    AWS_S3_BUCKET: Optional[str] = Field(default=None, description="S3 bucket for file storage")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def celery_broker_url(self) -> str:
        """Get Celery broker URL, defaulting to Redis URL."""
        return self.CELERY_BROKER_URL or self.REDIS_URL
    
    @property
    def celery_result_backend(self) -> str:
        """Get Celery result backend URL, defaulting to Redis URL."""
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for SQLAlchemy."""
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
        elif self.DATABASE_URL.startswith("sqlite+aiosqlite://"):
            return self.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://", 1)
        return self.DATABASE_URL


# Create settings instance
settings = Settings()