"""
Integration tests for user management API endpoints.

Tests user CRUD operations, admin functionality, and user management
features with proper authentication and authorization.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
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
        response = await admin_client.get("/api/users/")

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data

        # Should have at least our test users
        assert data["total"] >= 2
        assert len(data["items"]) >= 2

        # Check that users don't include sensitive data
        for user in data["items"]:
            assert "password" not in user
            assert "hashed_password" not in user
            assert "id" in user
            assert "email" in user
            assert "username" in user

    @pytest.mark.asyncio
    async def test_list_users_unauthorized(self, client: AsyncClient):
        """Test listing users without authentication."""
        response = await client.get("/api/users/")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_users_as_regular_user(self, authenticated_client: AsyncClient):
        """Test listing users as regular user (should be forbidden)."""
        response = await authenticated_client.get("/api/users/")

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
                username=f"user{i}",
                hashed_password=get_password_hash("password123"),
            )
            db_session.add(user)

        await db_session.commit()

        # Test first page with limit
        response = await admin_client.get("/api/users/?page=1&size=3")

        assert response.status_code == 200
        data = response.json()

        assert data["page"] == 1
        assert data["size"] == 3
        assert len(data["items"]) == 3
        assert data["total"] >= 7  # 2 test users + 5 created
        assert data["pages"] >= 3

    @pytest.mark.asyncio
    async def test_get_user_by_id_as_admin(
        self, admin_client: AsyncClient, test_user: User
    ):
        """Test getting specific user by ID as admin."""
        response = await admin_client.get(f"/api/users/{test_user.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert data["full_name"] == test_user.full_name
        assert "password" not in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_get_user_by_id_unauthorized(
        self, client: AsyncClient, test_user: User
    ):
        """Test getting user by ID without authentication."""
        response = await client.get(f"/api/users/{test_user.id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_user_by_id_as_regular_user(
        self, authenticated_client: AsyncClient, test_admin_user: User
    ):
        """Test getting user by ID as regular user (should be forbidden)."""
        response = await authenticated_client.get(f"/api/users/{test_admin_user.id}")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, admin_client: AsyncClient):
        """Test getting non-existent user."""
        response = await admin_client.get("/api/users/99999")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_user_as_admin(
        self, admin_client: AsyncClient, test_user: User, db_session: AsyncSession
    ):
        """Test updating user as admin."""
        update_data = {"full_name": "Updated Full Name", "is_active": False}

        response = await admin_client.put(
            f"/api/users/{test_user.id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()

        assert data["full_name"] == "Updated Full Name"
        assert data["is_active"] is False
        assert data["email"] == test_user.email  # Unchanged
        assert data["username"] == test_user.username  # Unchanged

        # Verify in database
        await db_session.refresh(test_user)
        assert test_user.full_name == "Updated Full Name"
        assert test_user.is_active is False

    @pytest.mark.asyncio
    async def test_update_user_role_as_admin(
        self, admin_client: AsyncClient, test_user: User, db_session: AsyncSession
    ):
        """Test updating user role as admin."""
        update_data = {"role": "Admin"}

        response = await admin_client.put(
            f"/api/users/{test_user.id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()

        assert data["role"] == "Admin"

        # Verify in database
        await db_session.refresh(test_user)
        assert test_user.role == UserRole.ADMIN

    @pytest.mark.asyncio
    async def test_update_user_unauthorized(self, client: AsyncClient, test_user: User):
        """Test updating user without authentication."""
        update_data = {"full_name": "Hacker Name"}

        response = await client.put(f"/api/users/{test_user.id}", json=update_data)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_user_as_regular_user(
        self, authenticated_client: AsyncClient, test_admin_user: User
    ):
        """Test updating user as regular user (should be forbidden)."""
        update_data = {"full_name": "Hacker Name"}

        response = await authenticated_client.put(
            f"/api/users/{test_admin_user.id}", json=update_data
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_nonexistent_user(self, admin_client: AsyncClient):
        """Test updating non-existent user."""
        update_data = {"full_name": "New Name"}

        response = await admin_client.put("/api/users/99999", json=update_data)

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user_as_admin(
        self, admin_client: AsyncClient, db_session: AsyncSession
    ):
        """Test deleting user as admin."""
        # Create a user to delete
        from app.core.security import get_password_hash

        user_to_delete = User(
            email="delete@example.com",
            username="deleteme",
            hashed_password=get_password_hash("password123"),
        )

        db_session.add(user_to_delete)
        await db_session.commit()
        await db_session.refresh(user_to_delete)

        user_id = user_to_delete.id

        # Delete the user
        response = await admin_client.delete(f"/api/users/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "User deleted successfully"

        # Verify user is deleted
        get_response = await admin_client.get(f"/api/users/{user_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_user_unauthorized(self, client: AsyncClient, test_user: User):
        """Test deleting user without authentication."""
        response = await client.delete(f"/api/users/{test_user.id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_user_as_regular_user(
        self, authenticated_client: AsyncClient, test_admin_user: User
    ):
        """Test deleting user as regular user (should be forbidden)."""
        response = await authenticated_client.delete(f"/api/users/{test_admin_user.id}")

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self, admin_client: AsyncClient):
        """Test deleting non-existent user."""
        response = await admin_client.delete("/api/users/99999")

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
            username="lifecycle",
            full_name="Lifecycle Test User",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )

        db_session.add(new_user)
        await db_session.commit()
        await db_session.refresh(new_user)

        # 2. Admin lists users and finds the new user
        list_response = await admin_client.get("/api/users/")
        assert list_response.status_code == 200

        users = list_response.json()["items"]
        lifecycle_user = next(
            user for user in users if user["email"] == "lifecycle@example.com"
        )
        assert lifecycle_user is not None

        # 3. Admin gets user details
        get_response = await admin_client.get(f"/api/users/{new_user.id}")
        assert get_response.status_code == 200

        user_details = get_response.json()
        assert user_details["role"] == "User"
        assert user_details["is_active"] is True

        # 4. Admin updates user role to Admin
        update_response = await admin_client.put(
            f"/api/users/{new_user.id}", json={"role": "Admin"}
        )
        assert update_response.status_code == 200

        updated_user = update_response.json()
        assert updated_user["role"] == "Admin"

        # 5. Admin deactivates user
        deactivate_response = await admin_client.put(
            f"/api/users/{new_user.id}", json={"is_active": False}
        )
        assert deactivate_response.status_code == 200

        deactivated_user = deactivate_response.json()
        assert deactivated_user["is_active"] is False

        # 6. Admin deletes user
        delete_response = await admin_client.delete(f"/api/users/{new_user.id}")
        assert delete_response.status_code == 200

        # 7. Verify user is gone
        final_get_response = await admin_client.get(f"/api/users/{new_user.id}")
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
                "username": "active1",
                "full_name": "Active User One",
                "is_active": True,
                "role": UserRole.USER,
            },
            {
                "email": "active2@company.com",
                "username": "active2",
                "full_name": "Active User Two",
                "is_active": True,
                "role": UserRole.ADMIN,
            },
            {
                "email": "inactive@company.com",
                "username": "inactive",
                "full_name": "Inactive User",
                "is_active": False,
                "role": UserRole.USER,
            },
        ]

        for user_data in test_users:
            user = User(**user_data, hashed_password=get_password_hash("password123"))
            db_session.add(user)

        await db_session.commit()

        # Test filtering by active status (if implemented)
        all_users_response = await admin_client.get("/api/users/")
        assert all_users_response.status_code == 200

        all_users = all_users_response.json()["items"]

        # Verify we have users with different statuses
        active_users = [user for user in all_users if user["is_active"]]
        inactive_users = [user for user in all_users if not user["is_active"]]

        assert len(active_users) >= 4  # 2 test fixtures + 2 created
        assert len(inactive_users) >= 1  # 1 created
