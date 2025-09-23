"""
Unit tests for database models.

Tests the SQLAlchemy models including User, Organization, and Project
to ensure proper field validation, relationships, and model methods.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.organization import (Organization, OrganizationMember,
                                     OrganizationMemberRole)
from app.models.project import Project, ProjectPriority, ProjectStatus
from app.models.user import User, UserRole, UserStatus


@pytest.mark.unit
@pytest.mark.database
class TestUserModel:
    """Test the User model."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        """Test creating a user with valid data."""
        user_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.USER,
            "status": UserStatus.ACTIVE,
        }

        user = User(**user_data)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.full_name == "Test User"  # Property
        assert user.is_verified is False  # Default value
        assert user.role == UserRole.USER
        assert user.status == UserStatus.ACTIVE
        assert user.created_at is not None
        assert user.updated_at is not None

    @pytest.mark.asyncio
    async def test_user_email_unique(self, db_session: AsyncSession):
        """Test that user email must be unique."""
        user1_data = {
            "email": "test@example.com",
            "first_name": "User",
            "last_name": "One",
            "hashed_password": get_password_hash("password123"),
        }

        user2_data = {
            "email": "test@example.com",  # Same email
            "first_name": "User",
            "last_name": "Two",
            "hashed_password": get_password_hash("password123"),
        }

        user1 = User(**user1_data)
        user2 = User(**user2_data)

        db_session.add(user1)
        await db_session.commit()

        db_session.add(user2)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_user_string_representation(self, db_session: AsyncSession):
        """Test user string representation."""
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            hashed_password="hashed_password",
        )

        # The __repr__ method includes email and role
        repr_str = repr(user)
        assert "test@example.com" in repr_str
        assert "User" in repr_str

    @pytest.mark.asyncio
    async def test_user_role_enum(self, db_session: AsyncSession):
        """Test user role enumeration."""
        # Test Admin role
        admin_user = User(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            hashed_password="hashed_password",
            role=UserRole.ADMIN,
        )

        db_session.add(admin_user)
        await db_session.commit()
        await db_session.refresh(admin_user)

        assert admin_user.role == UserRole.ADMIN
        assert admin_user.role.value == "admin"


@pytest.mark.unit
@pytest.mark.database
class TestOrganizationModel:
    """Test the Organization model."""

    @pytest.mark.asyncio
    async def test_create_organization(self, db_session: AsyncSession, test_user: User):
        """Test creating an organization with valid data."""
        org_data = {
            "name": "Test Organization",
            "description": "A test organization",
            "plan": "free",
            "is_active": True,
        }

        organization = Organization(**org_data)
        db_session.add(organization)
        await db_session.commit()
        await db_session.refresh(organization)

        assert organization.id is not None
        assert organization.name == "Test Organization"
        assert organization.description == "A test organization"
        assert organization.plan.value == "free"
        assert organization.is_active is True
        assert organization.created_at is not None
        assert organization.updated_at is not None

    @pytest.mark.asyncio
    async def test_organization_member_relationship(
        self, db_session: AsyncSession, test_organization: Organization, test_user: User
    ):
        """Test organization-member relationship."""
        # Load the organization with the members relationship
        await db_session.refresh(test_organization, ["members"])

        assert test_organization.members is not None
        assert len(test_organization.members) == 1

        member = test_organization.members[0]
        assert member.user_id == test_user.id
        assert member.role == OrganizationMemberRole.OWNER

    @pytest.mark.asyncio
    async def test_organization_name_required(self, db_session: AsyncSession):
        """Test that organization name is required."""
        org_data = {
            "description": "A test organization",
            # Missing name
        }

        organization = Organization(**org_data)
        db_session.add(organization)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_organization_string_representation(
        self, test_organization: Organization
    ):
        """Test organization string representation."""
        assert (
            str(test_organization) == "<Organization(id=1, name='Test Organization')>"
        )


@pytest.mark.unit
@pytest.mark.database
class TestProjectModel:
    """Test the Project model."""

    @pytest.mark.asyncio
    async def test_create_project(
        self, db_session: AsyncSession, test_organization: Organization
    ):
        """Test creating a project with valid data."""
        project_data = {
            "name": "Test Project",
            "description": "A test project",
            "organization_id": test_organization.id,
            "status": ProjectStatus.ACTIVE,
            "priority": ProjectPriority.MEDIUM,
        }

        project = Project(**project_data)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)

        assert project.id is not None
        assert project.name == "Test Project"
        assert project.description == "A test project"
        assert project.organization_id == test_organization.id
        assert project.status == ProjectStatus.ACTIVE
        assert project.priority == ProjectPriority.MEDIUM
        assert project.is_active is True  # Default value
        assert project.created_at is not None
        assert project.updated_at is not None

    @pytest.mark.asyncio
    async def test_project_organization_relationship(
        self,
        db_session: AsyncSession,
        test_project: Project,
        test_organization: Organization,
    ):
        """Test project-organization relationship."""
        # Load the project with the organization relationship
        await db_session.refresh(test_project, ["organization"])

        assert test_project.organization is not None
        assert test_project.organization.id == test_organization.id
        assert test_project.organization.name == test_organization.name

    @pytest.mark.asyncio
    async def test_project_status_enum(
        self, db_session: AsyncSession, test_organization: Organization
    ):
        """Test project status enumeration."""
        # Test all status values
        statuses = [
            ProjectStatus.PLANNING,
            ProjectStatus.ACTIVE,
            ProjectStatus.ON_HOLD,
            ProjectStatus.COMPLETED,
            ProjectStatus.CANCELLED,
        ]

        for i, status in enumerate(statuses):
            project = Project(
                name=f"Test Project {i}",
                organization_id=test_organization.id,
                status=status,
            )
            db_session.add(project)

        await db_session.commit()

        # Verify all projects were created with correct statuses
        from sqlalchemy import select

        result = await db_session.execute(select(Project).order_by(Project.name))
        project_list = result.scalars().all()

        assert len(project_list) >= len(statuses)  # Including test_project fixture

    @pytest.mark.asyncio
    async def test_project_priority_enum(
        self, db_session: AsyncSession, test_organization: Organization
    ):
        """Test project priority enumeration."""
        # Test all priority values
        priorities = [
            ProjectPriority.LOW,
            ProjectPriority.MEDIUM,
            ProjectPriority.HIGH,
            ProjectPriority.URGENT,
        ]

        for i, priority in enumerate(priorities):
            project = Project(
                name=f"Priority Test Project {i}",
                organization_id=test_organization.id,
                priority=priority,
            )
            db_session.add(project)

        await db_session.commit()

        # Verify all projects were created with correct priorities
        from sqlalchemy import select

        result = await db_session.execute(
            select(Project)
            .where(Project.name.like("Priority Test Project%"))
            .order_by(Project.name)
        )
        project_list = result.scalars().all()

        assert len(project_list) == len(priorities)

    @pytest.mark.asyncio
    async def test_project_name_required(
        self, db_session: AsyncSession, test_organization: Organization
    ):
        """Test that project name is required."""
        project_data = {
            "description": "A test project",
            "organization_id": test_organization.id
            # Missing name
        }

        project = Project(**project_data)
        db_session.add(project)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_project_string_representation(self, test_project: Project):
        """Test project string representation."""
        assert (
            str(test_project)
            == "<Project(id=1, name='Test Project', status='ProjectStatus.ACTIVE')>"
        )


@pytest.mark.unit
@pytest.mark.database
class TestModelRelationships:
    """Test relationships between models."""

    @pytest.mark.asyncio
    async def test_user_organization_memberships(
        self, db_session: AsyncSession, test_user: User, test_organization: Organization
    ):
        """Test that a user can be a member of multiple organizations."""
        # Create multiple organizations for the same user
        org1 = Organization(name="Organization 1", plan="free")
        org2 = Organization(name="Organization 2", plan="free")

        db_session.add(org1)
        db_session.add(org2)
        await db_session.commit()

        # Create memberships
        membership1 = OrganizationMember(
            user_id=test_user.id,
            organization_id=org1.id,
            role=OrganizationMemberRole.ADMIN,
        )
        membership2 = OrganizationMember(
            user_id=test_user.id,
            organization_id=org2.id,
            role=OrganizationMemberRole.MEMBER,
        )

        db_session.add(membership1)
        db_session.add(membership2)
        await db_session.commit()

        # Load user with organization memberships
        await db_session.refresh(test_user, ["organization_memberships"])

        assert (
            len(test_user.organization_memberships) == 3
        )  # Including test_organization fixture        # Check that we have the correct organizations
        org_ids = [m.organization_id for m in test_user.organization_memberships]
        assert org1.id in org_ids
        assert org2.id in org_ids

    @pytest.mark.asyncio
    async def test_organization_projects(
        self,
        db_session: AsyncSession,
        test_organization: Organization,
        test_project: Project,
    ):
        """Test that an organization can have multiple projects."""
        # Create multiple projects for the same organization
        project1 = Project(name="Project 1", organization_id=test_organization.id)
        project2 = Project(name="Project 2", organization_id=test_organization.id)

        db_session.add(project1)
        db_session.add(project2)
        await db_session.commit()

        # Load organization with projects
        await db_session.refresh(test_organization, ["projects"])

        assert len(test_organization.projects) == 3  # Including test_project fixture
        project_names = [proj.name for proj in test_organization.projects]
        assert "Project 1" in project_names
        assert "Project 2" in project_names
