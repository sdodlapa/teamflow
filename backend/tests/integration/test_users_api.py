"""
Integration tests for user management API endpoints.

Tests user CRUD operations, admin functionality, and user management
features with proper authentication and authorization.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole, UserStatus
from tests.conftest import TestDataFactory


@pytest.mark.integration
@pytest.mark.api
class TestUsersAPI:
    """Test user management API endpoints."""

    @pytest.mark.asyncio
    async def test_list_users_as_admin(
        self, admin_client: AsyncClient, test_user: User, test_admin_user: User
    ):
        """Test listing users as admin."""
        response = await admin_client.get("/api/v1/users/")

        assert response.status_code == 200
        data = response.json()

        assert "users" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data

        # Should have at least our test users
        assert data["total"] >= 2
        assert len(data["users"]) >= 2

        # Check that users don't include sensitive data
        for user in data["users"]:
            assert "password" not in user
            assert "hashed_password" not in user
            assert "id" in user
            assert "email" in user
            assert "first_name" in user
            assert "last_name" in user

    @pytest.mark.asyncio
    async def test_list_users_unauthorized(self, client: AsyncClient):
        """Test listing users without authentication."""
        response = await client.get("/api/v1/users/")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_users_as_regular_user(self, authenticated_client: AsyncClient):
        """Test listing users as regular user (should be forbidden)."""
        response = await authenticated_client.get("/api/v1/users/")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_list_users_pagination(
        self, admin_client: AsyncClient, db_session: AsyncSession
    ):
        """Test user listing with pagination."""
        # Create additional users for pagination testing
        from app.core.security import get_password_hash

        for i in range(5):
            user = User(
                email=f"user{i}@example.com",
                first_name=f"User{i}",
                last_name="Test",
                hashed_password=get_password_hash("password123"),
                role=UserRole.USER,
            )
            db_session.add(user)

        await db_session.commit()

        # Test pagination with limit
        response = await admin_client.get("/api/v1/users/?skip=0&limit=3")

        assert response.status_code == 200
        data = response.json()

        assert data["skip"] == 0
        assert data["limit"] == 3
        assert len(data["users"]) == 3
        assert data["total"] >= 6  # 1 admin + 5 created

    @pytest.mark.asyncio
    async def test_get_user_by_id_as_admin(
        self, admin_client: AsyncClient, test_user: User
    ):
        """Test getting specific user by ID as admin."""
        response = await admin_client.get(f"/api/v1/users/{test_user.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name
        assert data["full_name"] == test_user.full_name
        assert "password" not in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_get_user_by_id_unauthorized(
        self, client: AsyncClient, test_user: User
    ):
        """Test getting user by ID without authentication."""
        response = await client.get(f"/api/v1/users/{test_user.id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_user_by_id_as_regular_user(
        self, authenticated_client: AsyncClient, test_admin_user: User
    ):
        """Test getting user by ID as regular user (should be forbidden)."""
        response = await authenticated_client.get(f"/api/v1/users/{test_admin_user.id}")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, admin_client: AsyncClient):
        """Test getting non-existent user."""
        response = await admin_client.get("/api/v1/users/99999")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_user_as_admin(
        self, admin_client: AsyncClient, test_user: User, db_session: AsyncSession
    ):
        """Test updating user as admin."""
        update_data = {"first_name": "Updated", "last_name": "Name", "status": "inactive"}

        response = await admin_client.put(
            f"/api/v1/users/{test_user.id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()

        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["status"] == "inactive"
        assert data["email"] == test_user.email  # Unchanged

        # Verify database was updated
        await db_session.refresh(test_user)
        assert test_user.first_name == "Updated"
        assert test_user.last_name == "Name"
        assert test_user.status.value == "inactive"

    @pytest.mark.asyncio
    async def test_update_user_role_as_admin(
        self, admin_client: AsyncClient, test_user: User, db_session: AsyncSession
    ):
        """Test updating user role as admin."""
        update_data = {"role": "admin"}

        response = await admin_client.put(
            f"/api/v1/users/{test_user.id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()

        assert data["role"] == "admin"

        # Verify in database
        await db_session.refresh(test_user)
        assert test_user.role == UserRole.ADMIN

    @pytest.mark.asyncio
    async def test_update_user_unauthorized(self, client: AsyncClient, test_user: User):
        """Test updating user without authentication."""
        update_data = {"full_name": "Hacker Name"}

        response = await client.put(f"/api/v1/users/{test_user.id}", json=update_data)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_user_as_regular_user(
        self, authenticated_client: AsyncClient, test_admin_user: User
    ):
        """Test updating user as regular user (should be forbidden)."""
        update_data = {"full_name": "Hacker Name"}

        response = await authenticated_client.put(
            f"/api/v1/users/{test_admin_user.id}", json=update_data
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_nonexistent_user(self, admin_client: AsyncClient):
        """Test updating non-existent user."""
        update_data = {"full_name": "New Name"}

        response = await admin_client.put("/api/v1/users/99999", json=update_data)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user_as_admin(
        self, admin_client: AsyncClient, db_session: AsyncSession
    ):
        """Test deleting user as admin."""
        # Create a user to delete
        from app.core.security import get_password_hash

        user_to_delete = User(
            email="deleteme@example.com",
            first_name="Delete",
            last_name="Me",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )

        db_session.add(user_to_delete)
        await db_session.commit()
        await db_session.refresh(user_to_delete)

        user_id = user_to_delete.id

        # Delete the user
        response = await admin_client.delete(f"/api/v1/users/{user_id}")

        assert response.status_code == 204

        # Verify user is deleted
        get_response = await admin_client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user_unauthorized(self, client: AsyncClient, test_user: User):
        """Test deleting user without authentication."""
        response = await client.delete(f"/api/v1/users/{test_user.id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_user_as_regular_user(
        self, authenticated_client: AsyncClient, test_admin_user: User
    ):
        """Test deleting user as regular user (should be forbidden)."""
        response = await authenticated_client.delete(f"/api/v1/users/{test_admin_user.id}")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self, admin_client: AsyncClient):
        """Test deleting non-existent user."""
        response = await admin_client.delete("/api/v1/users/99999")

        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.api
class TestUserManagementFlow:
    """Test complete user management workflows."""

    @pytest.mark.asyncio
    async def test_admin_user_lifecycle(
        self, admin_client: AsyncClient, db_session: AsyncSession
    ):
        """Test complete admin user management lifecycle."""
        # 1. Create user via registration (simulated)
        from app.core.security import get_password_hash

        new_user = User(
            email="lifecycle@example.com",
            first_name="Lifecycle",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )

        db_session.add(new_user)
        await db_session.commit()
        await db_session.refresh(new_user)

        # 2. Admin lists users and finds the new user
        list_response = await admin_client.get("/api/v1/users/")
        assert list_response.status_code == 200

        users = list_response.json()["users"]
        lifecycle_user = next(
            user for user in users if user["email"] == "lifecycle@example.com"
        )
        assert lifecycle_user is not None

        # 3. Admin gets user details
        get_response = await admin_client.get(f"/api/v1/users/{new_user.id}")
        assert get_response.status_code == 200

        user_details = get_response.json()
        assert user_details["role"] == "user"
        assert user_details["status"] == "pending"

        # 4. Admin updates user role to Admin
        update_response = await admin_client.put(
            f"/api/v1/users/{new_user.id}", json={"role": "admin"}
        )
        assert update_response.status_code == 200

        updated_user = update_response.json()
        assert updated_user["role"] == "admin"

        # 5. Admin deactivates user
        deactivate_response = await admin_client.put(
            f"/api/v1/users/{new_user.id}", json={"status": "inactive"}
        )
        assert deactivate_response.status_code == 200

        deactivated_user = deactivate_response.json()
        assert deactivated_user["status"] == "inactive"

        # 6. Admin deletes user
        delete_response = await admin_client.delete(f"/api/v1/users/{new_user.id}")
        assert delete_response.status_code == 204

        # 7. Verify user is gone
        final_get_response = await admin_client.get(f"/api/v1/users/{new_user.id}")
        assert final_get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_user_search_and_filtering(
        self, admin_client: AsyncClient, db_session: AsyncSession
    ):
        """Test user search and filtering capabilities."""
        # Create users with different attributes for filtering
        from app.core.security import get_password_hash

        test_users = [
            {
                "email": "active1@company.com",
                "first_name": "Active1",
                "last_name": "User",
                "status": UserStatus.ACTIVE,
                "role": UserRole.USER,
            },
            {
                "email": "active2@company.com",
                "first_name": "Active2", 
                "last_name": "User",
                "status": UserStatus.ACTIVE,
                "role": UserRole.ADMIN,
            },
            {
                "email": "inactive@company.com",
                "first_name": "Inactive",
                "last_name": "User",
                "status": UserStatus.INACTIVE,
                "role": UserRole.USER,
            },
        ]

        for user_data in test_users:
            user = User(**user_data, hashed_password=get_password_hash("password123"))
            db_session.add(user)

        await db_session.commit()

        # Test filtering by active status (if implemented)
        all_users_response = await admin_client.get("/api/v1/users/")
        assert all_users_response.status_code == 200

        all_users = all_users_response.json()["users"]

        # Verify we have users with different statuses
        active_users = [user for user in all_users if user["status"] == "active"]
        inactive_users = [user for user in all_users if user["status"] == "inactive"]

        assert len(active_users) >= 3  # 1 admin + 2 created active users
        assert len(inactive_users) >= 1  # 1 created
