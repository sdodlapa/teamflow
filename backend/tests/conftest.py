"""
Test configuration and fixtures for the TeamFlow application.

This module provides shared test fixtures, database setup, and authentication
utilities for comprehensive testing of the FastAPI application.
"""

import asyncio
import sqlite3
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.base import Base
from app.models.organization import Organization
from app.models.project import Project
from app.models.user import User

# Test database URL - use in-memory SQLite for fast tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True if settings.ENVIRONMENT == "development" else False,
    future=True,
)

# Create test session factory
TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Enable foreign key constraints for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@pytest_asyncio.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.

    This fixture:
    1. Creates all tables in the test database
    2. Provides a clean database session
    3. Rolls back all changes after the test
    4. Drops all tables to ensure test isolation
    """
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestAsyncSessionLocal() as session:
        yield session
        await session.rollback()

    # Drop all tables to ensure clean state
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test client with dependency overrides.

    This fixture overrides the database dependency to use the test database
    and provides an AsyncClient for making HTTP requests to the test app.
    """

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://testserver") as test_client:
        yield test_client

    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user in the database."""
    user_data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "hashed_password": get_password_hash("testpassword123"),
        "is_verified": True,
        "role": "user",
        "status": "active",
    }

    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin_user(db_session: AsyncSession) -> User:
    """Create a test admin user in the database."""
    admin_data = {
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "hashed_password": get_password_hash("adminpassword123"),
        "is_verified": True,
        "role": "admin",
        "status": "active",
    }

    admin = User(**admin_data)
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture
async def test_organization(db_session: AsyncSession, test_user: User) -> Organization:
    """Create a test organization with the test user as owner."""
    from app.models.organization import (OrganizationMember,
                                         OrganizationMemberRole)

    org_data = {
        "name": "Test Organization",
        "description": "A test organization for testing purposes",
        "plan": "free",
        "is_active": True,
    }

    organization = Organization(**org_data)
    db_session.add(organization)
    await db_session.commit()
    await db_session.refresh(organization)

    # Create membership with owner role
    membership = OrganizationMember(
        user_id=test_user.id,
        organization_id=organization.id,
        role=OrganizationMemberRole.OWNER,
    )
    db_session.add(membership)
    await db_session.commit()

    return organization


@pytest_asyncio.fixture
async def test_project(
    db_session: AsyncSession, test_organization: Organization, test_user: User
) -> Project:
    """Create a test project within the test organization."""
    project_data = {
        "name": "Test Project",
        "description": "A test project for testing purposes",
        "organization_id": test_organization.id,
        "status": "active",
        "priority": "medium",
    }

    project = Project(**project_data)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict[str, str]:
    """Create authentication headers for the test user."""
    access_token = create_access_token(subject=test_user.email)
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def admin_auth_headers(test_admin_user: User) -> dict[str, str]:
    """Create authentication headers for the admin user."""
    access_token = create_access_token(subject=test_admin_user.email)
    return {"Authorization": f"Bearer {access_token}"}


@pytest_asyncio.fixture
async def authenticated_client(
    client: AsyncClient, auth_headers: dict[str, str]
) -> AsyncClient:
    """Create an authenticated test client."""
    client.headers.update(auth_headers)
    return client


@pytest_asyncio.fixture
async def admin_client(
    client: AsyncClient, admin_auth_headers: dict[str, str]
) -> AsyncClient:
    """Create an authenticated admin test client."""
    client.headers.update(admin_auth_headers)
    return client


# Test data factories
class TestDataFactory:
    """Factory class for creating test data."""

    @staticmethod
    def user_data(
        email: str = "user@example.com",
        first_name: str = "User",
        last_name: str = "Test",
        password: str = "password123",
    ) -> dict:
        """Generate user registration data."""
        return {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "password": password,
        }

    @staticmethod
    def organization_data(
        name: str = "Test Org", description: str = "Test organization"
    ) -> dict:
        """Generate organization creation data."""
        return {"name": name, "description": description}

    @staticmethod
    def project_data(
        name: str = "Test Project", description: str = "Test project description"
    ) -> dict:
        """Generate project creation data."""
        return {
            "name": name,
            "description": description,
            "status": "active",
            "priority": "medium",
        }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "asyncio: mark test as async")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "auth: mark test as authentication related")
    config.addinivalue_line("markers", "database: mark test as database related")
    config.addinivalue_line("markers", "api: mark test as API endpoint test")
