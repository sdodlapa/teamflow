"""Import all models to ensure they are registered with SQLAlchemy."""

# Make Base available for Alembic
from app.core.database import Base
from app.models.base import BaseModel
from app.models.organization import (Organization, OrganizationMember,
                                     OrganizationMemberRole, OrganizationPlan,
                                     OrganizationStatus)
from app.models.project import (Project, ProjectMember, ProjectMemberRole,
                                ProjectPriority, ProjectStatus)
from app.models.task import (Task, TaskComment, TaskDependency, TaskPriority, 
                            TaskStatus)
from app.models.time_tracking import (TaskTimeLog, TaskTemplate, TaskActivity,
                                      TaskMention, TaskAssignmentHistory)
from app.models.user import User, UserRole, UserStatus

__all__ = [
    "Base",
    "BaseModel",
    "User",
    "UserRole",
    "UserStatus",
    "Organization",
    "OrganizationMember",
    "OrganizationPlan",
    "OrganizationStatus",
    "OrganizationMemberRole",
    "Project",
    "ProjectMember",
    "ProjectStatus",
    "ProjectPriority",
    "ProjectMemberRole",
    "Task",
    "TaskComment",
    "TaskDependency",
    "TaskStatus",
    "TaskPriority",
    "TaskTimeLog",
    "TaskTemplate",
    "TaskActivity",
    "TaskMention",
    "TaskAssignmentHistory",
]
