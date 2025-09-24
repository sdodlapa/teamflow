"""User model for authentication and user management."""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles in the system."""

    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserStatus(str, enum.Enum):
    """User account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(Base):
    """User model for authentication and profile management."""

    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)

    # Profile
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)

    # System
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    organization_memberships = relationship(
        "OrganizationMember", back_populates="user", cascade="all, delete-orphan"
    )
    project_memberships = relationship(
        "ProjectMember", back_populates="user", cascade="all, delete-orphan"
    )
    
    # Task relationships
    assigned_tasks = relationship(
        "Task", foreign_keys="Task.assignee_id", back_populates="assignee"
    )
    created_tasks = relationship(
        "Task", foreign_keys="Task.created_by", back_populates="creator"
    )
    task_comments = relationship(
        "TaskComment", back_populates="user", cascade="all, delete-orphan"
    )
    
    # Advanced feature relationships
    time_logs = relationship("TaskTimeLog", back_populates="user", cascade="all, delete-orphan")
    task_activities = relationship("TaskActivity", back_populates="user", cascade="all, delete-orphan")
    created_task_templates = relationship("TaskTemplate", back_populates="creator", cascade="all, delete-orphan")
    
    # Mention relationships
    received_mentions = relationship(
        "TaskMention", foreign_keys="TaskMention.mentioned_user_id", 
        back_populates="mentioned_user", cascade="all, delete-orphan"
    )
    created_mentions = relationship(
        "TaskMention", foreign_keys="TaskMention.mentioning_user_id", 
        back_populates="mentioning_user", cascade="all, delete-orphan"
    )
    
    # Assignment history relationships
    previous_assignments = relationship(
        "TaskAssignmentHistory", foreign_keys="TaskAssignmentHistory.previous_assignee_id",
        back_populates="previous_assignee", cascade="all, delete-orphan"
    )
    new_assignments = relationship(
        "TaskAssignmentHistory", foreign_keys="TaskAssignmentHistory.new_assignee_id",
        back_populates="new_assignee", cascade="all, delete-orphan"
    )
    assignments_made = relationship(
        "TaskAssignmentHistory", foreign_keys="TaskAssignmentHistory.assigned_by",
        back_populates="assigner", cascade="all, delete-orphan"
    )
    
    # Security and compliance relationships
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    security_alerts = relationship("SecurityAlert", foreign_keys="SecurityAlert.user_id", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    gdpr_requests = relationship("GDPRRequest", foreign_keys="GDPRRequest.user_id", back_populates="user", cascade="all, delete-orphan")
    consent_records = relationship("DataConsentRecord", back_populates="user", cascade="all, delete-orphan")
    login_attempts = relationship("LoginAttempt", back_populates="user", cascade="all, delete-orphan")
    
    # Enhanced comment system relationships
    enhanced_comments = relationship("TaskCommentEnhanced", foreign_keys="TaskCommentEnhanced.user_id", back_populates="user", cascade="all, delete-orphan")
    received_comment_mentions = relationship("CommentMention", foreign_keys="CommentMention.mentioned_user_id", back_populates="mentioned_user", cascade="all, delete-orphan")
    created_comment_mentions = relationship("CommentMention", foreign_keys="CommentMention.mentioning_user_id", back_populates="mentioning_user", cascade="all, delete-orphan")
    comment_likes = relationship("CommentLike", back_populates="user", cascade="all, delete-orphan")
    comment_reactions = relationship("CommentReaction", back_populates="user", cascade="all, delete-orphan")
    comment_activities = relationship("CommentActivity", back_populates="user", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    @classmethod
    async def get_by_email(cls, db: AsyncSession, email: str) -> Optional["User"]:
        """Get user by email address."""
        result = await db.execute(select(cls).where(cls.email == email))
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_id(cls, db: AsyncSession, user_id: int) -> Optional["User"]:
        """Get user by ID."""
        result = await db.execute(select(cls).where(cls.id == user_id))
        return result.scalar_one_or_none()

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs) -> "User":
        """Create a new user."""
        user = cls(**kwargs)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def update(self, db: AsyncSession, **kwargs) -> "User":
        """Update user fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(self)
        return self

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
