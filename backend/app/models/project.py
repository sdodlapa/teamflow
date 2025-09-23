"""Project model for project management."""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum, Date
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class ProjectStatus(enum.Enum):
    """Project status options."""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectPriority(enum.Enum):
    """Project priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Project(Base):
    """Project model for project management."""
    
    __tablename__ = "projects"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    key = Column(String(10), nullable=False, index=True)  # e.g., "TEAM", "PROJ"
    description = Column(Text, nullable=True)
    
    # Foreign keys (will be added when we create relationships)
    # organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    # owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Project details
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.PLANNING, nullable=False)
    priority = Column(SQLEnum(ProjectPriority), default=ProjectPriority.MEDIUM, nullable=False)
    
    # Dates
    start_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Settings
    is_public = Column(Boolean, default=False, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    color = Column(String(7), default="#1f2937", nullable=False)  # Hex color code
    icon = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships (will be added when we create foreign keys)
    # organization = relationship("Organization", back_populates="projects")
    # owner = relationship("User", back_populates="owned_projects")
    # members = relationship("ProjectMember", back_populates="project")
    # tasks = relationship("Task", back_populates="project")
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', key='{self.key}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if project is active."""
        return self.status == ProjectStatus.ACTIVE and not self.is_archived
    
    @property
    def is_completed(self) -> bool:
        """Check if project is completed."""
        return self.status == ProjectStatus.COMPLETED
    
    @property
    def is_overdue(self) -> bool:
        """Check if project is overdue."""
        if not self.due_date:
            return False
        return datetime.now().date() > self.due_date and not self.is_completed
    
    def can_be_edited(self) -> bool:
        """Check if project can be edited."""
        return self.status not in [ProjectStatus.COMPLETED, ProjectStatus.CANCELLED] and not self.is_archived


class ProjectMemberRole(enum.Enum):
    """Project member roles."""
    OWNER = "owner"
    MANAGER = "manager"
    DEVELOPER = "developer"
    DESIGNER = "designer"
    TESTER = "tester"
    VIEWER = "viewer"


class ProjectMember(Base):
    """Association between users and projects."""
    
    __tablename__ = "project_members"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys (will be added when we create relationships)
    # user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Role and permissions
    role = Column(SQLEnum(ProjectMemberRole), default=ProjectMemberRole.DEVELOPER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships (will be added when we create foreign keys)
    # user = relationship("User", back_populates="projects")
    # project = relationship("Project", back_populates="members")
    
    def __repr__(self) -> str:
        return f"<ProjectMember(id={self.id}, role='{self.role.value}')>"
    
    def is_owner(self) -> bool:
        """Check if member is project owner."""
        return self.role == ProjectMemberRole.OWNER
    
    def is_manager(self) -> bool:
        """Check if member has manager role or higher."""
        return self.role in [ProjectMemberRole.OWNER, ProjectMemberRole.MANAGER]
    
    def can_manage_tasks(self) -> bool:
        """Check if member can manage tasks."""
        return self.role in [ProjectMemberRole.OWNER, ProjectMemberRole.MANAGER]
    
    def can_edit_project(self) -> bool:
        """Check if member can edit project settings."""
        return self.role in [ProjectMemberRole.OWNER, ProjectMemberRole.MANAGER]