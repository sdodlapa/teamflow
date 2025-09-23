"""Core configuration for the TeamFlow application."""

from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    ENVIRONMENT: str = Field(
        default="development", description="Application environment"
    )
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./backend/teamflow_dev.db",
        description="Database connection URL",
    )
    TEST_DATABASE_URL: Optional[str] = Field(
        default="sqlite+aiosqlite:///./backend/teamflow_test.db",
        description="Test database connection URL",
    )

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379", description="Redis connection URL"
    )
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    
    # Performance Settings
    ENABLE_REDIS_CACHE: bool = Field(default=True, description="Enable Redis caching")
    CACHE_TTL_DEFAULT: int = Field(default=3600, description="Default cache TTL in seconds")
    CACHE_TTL_SHORT: int = Field(default=300, description="Short cache TTL in seconds")
    CACHE_TTL_LONG: int = Field(default=86400, description="Long cache TTL in seconds")
    
    # Performance Monitoring
    ENABLE_PERFORMANCE_MONITORING: bool = Field(default=True, description="Enable performance monitoring")
    METRICS_COLLECTION_INTERVAL: int = Field(default=30, description="Metrics collection interval in seconds")
    SLOW_QUERY_THRESHOLD_MS: float = Field(default=100, description="Slow query threshold in milliseconds")
    
    # Database Performance
    DB_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=30, description="Database connection pool max overflow")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Database connection pool timeout")
    DB_POOL_RECYCLE: int = Field(default=3600, description="Database connection pool recycle time")
    
    # API Performance
    ENABLE_RESPONSE_COMPRESSION: bool = Field(default=True, description="Enable response compression")
    COMPRESSION_LEVEL: int = Field(default=6, description="Compression level (1-9)")
    COMPRESSION_MIN_SIZE: int = Field(default=1000, description="Minimum size for compression")
    
    # Background Tasks
    ENABLE_BACKGROUND_TASKS: bool = Field(default=True, description="Enable background task processing")
    MAX_BACKGROUND_TASKS: int = Field(default=100, description="Maximum concurrent background tasks")

    # Security
    SECRET_KEY: str = Field(
        default="your-super-secret-jwt-key-change-in-production",
        description="Secret key for JWT token generation",
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15, description="Access token expiration time in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="Refresh token expiration time in days"
    )

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="Allowed CORS origins",
    )

    # Email Configuration
    SMTP_HOST: str = Field(default="localhost", description="SMTP server host")
    SMTP_PORT: int = Field(default=1025, description="SMTP server port")
    SMTP_USER: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    SMTP_TLS: bool = Field(default=False, description="Use TLS for SMTP")
    FROM_EMAIL: str = Field(
        default="noreply@teamflow.dev", description="Default from email address"
    )

    # File Upload
    UPLOAD_DIR: str = Field(default="./uploads", description="File upload directory")
    MAX_UPLOAD_SIZE: int = Field(
        default=10485760, description="Maximum file upload size in bytes"  # 10MB
    )
    
    # File Management Settings
    FILE_UPLOAD_PATH: str = Field(default="./uploads", description="File storage path")
    MAX_FILE_SIZE: int = Field(default=100 * 1024 * 1024, description="Maximum file size in bytes")  # 100MB
    ALLOWED_FILE_EXTENSIONS: List[str] = Field(
        default=[
            ".pdf", ".doc", ".docx", ".txt", ".rtf",  # Documents
            ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp",  # Images
            ".xls", ".xlsx", ".csv",  # Spreadsheets
            ".ppt", ".pptx",  # Presentations
            ".zip", ".rar", ".tar", ".gz",  # Archives
            ".mp4", ".avi", ".mov", ".mp3", ".wav"  # Media
        ],
        description="Allowed file extensions"
    )
    
    # File Processing Settings
    ENABLE_FILE_COMPRESSION: bool = Field(default=True, description="Enable file compression")
    ENABLE_THUMBNAIL_GENERATION: bool = Field(default=True, description="Enable thumbnail generation")
    THUMBNAIL_QUALITY: int = Field(default=85, description="Thumbnail JPEG quality")
    
    # File Security Settings
    ENABLE_VIRUS_SCANNING: bool = Field(default=False, description="Enable virus scanning")
    FILE_SCAN_TIMEOUT: int = Field(default=30, description="File scan timeout in seconds")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60, description="Rate limit per minute per IP"
    )

    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=20, description="Default page size")
    MAX_PAGE_SIZE: int = Field(default=100, description="Maximum page size")

    # Celery (Background Tasks)
    CELERY_BROKER_URL: Optional[str] = Field(
        default=None, description="Celery broker URL (defaults to REDIS_URL)"
    )
    CELERY_RESULT_BACKEND: Optional[str] = Field(
        default=None, description="Celery result backend URL (defaults to REDIS_URL)"
    )

    # AWS Configuration (for production)
    AWS_REGION: str = Field(default="us-west-2", description="AWS region")
    AWS_S3_BUCKET: Optional[str] = Field(
        default=None, description="S3 bucket for file storage"
    )

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
            return self.DATABASE_URL.replace(
                "postgresql://", "postgresql+psycopg2://", 1
            )
        elif self.DATABASE_URL.startswith("sqlite+aiosqlite://"):
            return self.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://", 1)
        return self.DATABASE_URL


# Create settings instance
settings = Settings()
