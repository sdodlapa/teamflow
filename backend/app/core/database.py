"""
Simplified database configuration - no hanging, lazy initialization
"""
from typing import AsyncGenerator, Optional
import os
from contextlib import asynccontextmanager

from sqlalchemy import text, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# Create Base class for models
Base = declarative_base()

# Global variables for lazy initialization
_async_engine = None
_async_session_maker = None


def get_database_url() -> str:
    """Get database URL with proper configuration."""
    return str(settings.DATABASE_URL)


def create_sync_engine():
    """Create synchronous engine for setup operations."""
    db_url = get_database_url()
    
    if "sqlite" in db_url.lower():
        # SQLite sync engine
        sync_url = db_url.replace("sqlite+aiosqlite://", "sqlite://")
        return create_engine(
            sync_url,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        # PostgreSQL sync engine
        sync_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        return create_engine(sync_url, echo=settings.DEBUG)


def get_async_engine():
    """Get or create async engine (lazy initialization)."""
    global _async_engine
    
    if _async_engine is None:
        db_url = get_database_url()
        
        connect_args = {}
        if "sqlite" in db_url.lower():
            connect_args = {
                "check_same_thread": False,
                "timeout": 20,
            }
        
        _async_engine = create_async_engine(
            db_url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args=connect_args,
            future=True,
        )
    
    return _async_engine


def get_async_session_maker():
    """Get or create async session maker (lazy initialization)."""
    global _async_session_maker
    
    if _async_session_maker is None:
        engine = get_async_engine()
        _async_session_maker = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    
    return _async_session_maker


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.
    
    Usage:
        async with get_async_session() as session:
            # use session
    """
    session_maker = get_async_session_maker()
    
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    
    Usage:
        def my_endpoint(db: AsyncSession = Depends(get_db)):
    """
    async with get_async_session() as session:
        yield session


def create_tables_sync():
    """Create tables using synchronous engine (for setup/testing)."""
    try:
        print("🔧 Creating database tables synchronously...")
        
        # Import all models to ensure they're registered
        from app.models import user, organization  # Import the models we need
        
        # Create sync engine and tables
        sync_engine = create_sync_engine()
        Base.metadata.create_all(bind=sync_engine)
        
        print("✅ Database tables created successfully")
        return True
        
    except Exception as e:
        print(f"⚠️ Failed to create tables: {e}")
        return False


def check_database_exists() -> bool:
    """Check if database exists and has tables."""
    try:
        db_url = get_database_url()
        
        if "sqlite" in db_url.lower():
            # Check SQLite file
            db_path = db_url.replace("sqlite+aiosqlite://", "").replace("sqlite://", "")
            if not os.path.exists(db_path):
                return False
            
            # Check if it has tables
            sync_engine = create_sync_engine()
            with sync_engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = result.fetchall()
                return len(tables) > 0
        else:
            # For PostgreSQL, assume it exists
            return True
            
    except Exception:
        return False


def ensure_database_ready():
    """Ensure database is ready for use (sync operation)."""
    if not check_database_exists():
        print("📊 Database not found, creating tables...")
        return create_tables_sync()
    else:
        print("📊 Database already exists")
        return True


# Optional: cleanup function
async def close_database():
    """Close database connections."""
    global _async_engine, _async_session_maker
    
    if _async_engine:
        await _async_engine.dispose()
        _async_engine = None
        _async_session_maker = None


# Legacy compatibility for existing code
async def create_tables():
    """Legacy function - use create_tables_sync() instead."""
    print("⚠️ create_tables() is deprecated, use setup_database.py instead")
    return create_tables_sync()


async def drop_tables():
    """Drop all database tables."""
    try:
        sync_engine = create_sync_engine()
        Base.metadata.drop_all(bind=sync_engine)
        print("✅ All tables dropped")
    except Exception as e:
        print(f"⚠️ Failed to drop tables: {e}")
