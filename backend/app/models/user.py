"""User model for authentication and user management."""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class UserRole(enum.Enum):
    """User roles within the application."""
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"


class UserStatus(enum.Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class User(Base):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Profile information
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    full_name = Column(String(100), nullable=True)  # Computed field
    avatar_url = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    
    # Role and status
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # Verification and password reset
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # Relationships (will be added as we create more models)
    # organizations = relationship("OrganizationMember", back_populates="user")
    # projects = relationship("ProjectMember", back_populates="user")
    # created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.creator_id")
    # assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
    
    @property
    def display_name(self) -> str:
        """Get the user's display name."""
        if self.full_name:
            return self.full_name
        return f"{self.first_name} {self.last_name}".strip()
    
    def update_full_name(self) -> None:
        """Update the full_name field based on first_name and last_name."""
        self.full_name = f"{self.first_name} {self.last_name}".strip()
    
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN
    
    def is_manager(self) -> bool:
        """Check if user has manager role or higher."""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]