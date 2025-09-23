"""Import all models to ensure they are registered with SQLAlchemy."""

from app.models.base import BaseModel
from app.models.user import User, UserRole, UserStatus
from app.models.organization import Organization, OrganizationMember, OrganizationPlan, OrganizationStatus, OrganizationMemberRole
from app.models.project import Project, ProjectMember, ProjectStatus, ProjectPriority, ProjectMemberRole

# Make Base available for Alembic
from app.core.database import Base

__all__ = [
    "Base", "BaseModel",
    "User", "UserRole", "UserStatus",
    "Organization", "OrganizationMember", "OrganizationPlan", "OrganizationStatus", "OrganizationMemberRole",
    "Project", "ProjectMember", "ProjectStatus", "ProjectPriority", "ProjectMemberRole"
]