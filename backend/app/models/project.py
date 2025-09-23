"""Project model for project management."""

import enum
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Column, Date, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    """Project status options."""

    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectPriority(str, enum.Enum):
    """Project priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Project(Base):
    """Project model for project management."""

    __tablename__ = "projects"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Foreign keys
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    # Project properties
    status = Column(
        SQLEnum(ProjectStatus), default=ProjectStatus.PLANNING, nullable=False
    )
    priority = Column(
        SQLEnum(ProjectPriority), default=ProjectPriority.MEDIUM, nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)

    # Dates
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    organization = relationship("Organization", back_populates="projects")
    members = relationship(
        "ProjectMember", back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"


class ProjectMemberRole(str, enum.Enum):
    """Project member roles."""

    OWNER = "owner"
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class ProjectMember(Base):
    """Association between users and projects."""

    __tablename__ = "project_members"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Role and permissions
    role = Column(
        SQLEnum(ProjectMemberRole), default=ProjectMemberRole.DEVELOPER, nullable=False
    )

    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="project_memberships")
    project = relationship("Project", back_populates="members")

    def __repr__(self) -> str:
        return f"<ProjectMember(id={self.id}, role='{self.role.value}')>"
