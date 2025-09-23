"""
Integration tests for authentication API endpoints.

Tests the complete authentication flow including user registration,
login, token validation, and protected endpoint access.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from tests.conftest import TestDataFactory


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.auth
class TestAuthenticationAPI:
    """Test authentication API endpoints."""

    @pytest.mark.asyncio
    async def test_register_new_user(self, client: AsyncClient):
        """Test user registration with valid data."""
        user_data = TestDataFactory.user_data(
            email="newuser@example.com",
            username="newuser",
            password="securepassword123",
        )

        response = await client.post("/api/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()

        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert data["is_active"] is True
        assert data["role"] == "User"
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Password should not be returned
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Test registration with existing email fails."""
        user_data = TestDataFactory.user_data(
            email=test_user.email,  # Use existing email
            username="differentuser",
            password="password123",
        )

        response = await client.post("/api/auth/register", json=user_data)

        assert response.status_code == 400
        data = response.json()
        assert "email" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_duplicate_username(
        self, client: AsyncClient, test_user: User
    ):
        """Test registration with existing username fails."""
        user_data = TestDataFactory.user_data(
            email="different@example.com",
            username=test_user.username,  # Use existing username
            password="password123",
        )

        response = await client.post("/api/auth/register", json=user_data)

        assert response.status_code == 400
        data = response.json()
        assert "username" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email format."""
        user_data = TestDataFactory.user_data(
            email="invalid-email",  # Invalid format
            username="user",
            password="password123",
        )

        response = await client.post("/api/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        user_data = TestDataFactory.user_data(
            email="user@example.com", username="user", password="123"  # Too short
        )

        response = await client.post("/api/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert any("password" in str(error).lower() for error in data["detail"])

    @pytest.mark.asyncio
    async def test_login_valid_credentials(self, client: AsyncClient, test_user: User):
        """Test login with valid credentials."""
        login_data = {
            "username": test_user.email,  # Can use email as username
            "password": "testpassword123",  # From fixture
        }

        response = await client.post(
            "/api/auth/login",
            data=login_data,  # Form data for OAuth2
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 100  # JWT tokens are long

    @pytest.mark.asyncio
    async def test_login_with_username(self, client: AsyncClient, test_user: User):
        """Test login using username instead of email."""
        login_data = {"username": test_user.username, "password": "testpassword123"}

        response = await client.post(
            "/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword",
        }

        response = await client.post(
            "/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        """Test login with correct email but wrong password."""
        login_data = {"username": test_user.email, "password": "wrongpassword"}

        response = await client.post(
            "/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_user(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test login with inactive user account."""
        # Create inactive user
        from app.core.security import get_password_hash

        inactive_user = User(
            email="inactive@example.com",
            username="inactive",
            hashed_password=get_password_hash("password123"),
            is_active=False,
        )

        db_session.add(inactive_user)
        await db_session.commit()

        login_data = {"username": "inactive@example.com", "password": "password123"}

        response = await client.post(
            "/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(
        self, authenticated_client: AsyncClient, test_user: User
    ):
        """Test getting current user information."""
        response = await authenticated_client.get("/api/auth/me")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert data["full_name"] == test_user.full_name
        assert data["is_active"] is True
        assert data["role"] == test_user.role.value
        assert "password" not in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client: AsyncClient):
        """Test getting current user without authentication."""
        response = await client.get("/api/auth/me")

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token."""
        response = await client.get(
            "/api/auth/me", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.auth
class TestAuthenticationFlow:
    """Test complete authentication flows."""

    @pytest.mark.asyncio
    async def test_complete_registration_login_flow(self, client: AsyncClient):
        """Test complete flow: register -> login -> access protected endpoint."""
        # 1. Register new user
        user_data = TestDataFactory.user_data(
            email="flowtest@example.com",
            username="flowtest",
            password="securepassword123",
        )

        register_response = await client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201

        # 2. Login with new user
        login_data = {"username": user_data["email"], "password": user_data["password"]}

        login_response = await client.post(
            "/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login_response.status_code == 200

        token_data = login_response.json()
        access_token = token_data["access_token"]

        # 3. Access protected endpoint
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        me_response = await client.get("/api/auth/me", headers=auth_headers)

        assert me_response.status_code == 200
        user_info = me_response.json()
        assert user_info["email"] == user_data["email"]
        assert user_info["username"] == user_data["username"]

    @pytest.mark.asyncio
    async def test_token_persistence_across_requests(
        self, authenticated_client: AsyncClient
    ):
        """Test that token works for multiple requests."""
        # Make multiple requests with the same token
        endpoints = ["/api/auth/me", "/api/auth/me", "/api/auth/me"]

        for endpoint in endpoints:
            response = await authenticated_client.get(endpoint)
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_concurrent_login_requests(
        self, client: AsyncClient, test_user: User
    ):
        """Test handling concurrent login requests."""
        import asyncio

        login_data = {"username": test_user.email, "password": "testpassword123"}

        # Make 5 concurrent login requests
        tasks = []
        for _ in range(5):
            task = client.post(
                "/api/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
