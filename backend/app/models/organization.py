"""Organization model for multi-tenant support."""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class OrganizationPlan(enum.Enum):
    """Organization subscription plans."""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class OrganizationStatus(enum.Enum):
    """Organization status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TRIAL = "trial"


class Organization(Base):
    """Organization model for multi-tenant support."""
    
    __tablename__ = "organizations"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    slug = Column(String(50), unique=True, index=True, nullable=False)
    
    # Organization details
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    logo_url = Column(String(255), nullable=True)
    
    # Settings
    plan = Column(SQLEnum(OrganizationPlan), default=OrganizationPlan.FREE, nullable=False)
    status = Column(SQLEnum(OrganizationStatus), default=OrganizationStatus.TRIAL, nullable=False)
    max_members = Column(Integer, default=5, nullable=False)
    max_projects = Column(Integer, default=3, nullable=False)
    
    # Features enabled
    features_enabled = Column(Text, nullable=True)  # JSON string of enabled features
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    trial_ends_at = Column(DateTime, nullable=True)
    
    # Relationships (will be added as we create more models)
    # members = relationship("OrganizationMember", back_populates="organization")
    # projects = relationship("Project", back_populates="organization")
    
    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name='{self.name}', slug='{self.slug}')>"
    
    @property
    def is_trial(self) -> bool:
        """Check if organization is in trial period."""
        return self.status == OrganizationStatus.TRIAL
    
    @property
    def is_active(self) -> bool:
        """Check if organization is active."""
        return self.status == OrganizationStatus.ACTIVE
    
    def can_add_members(self, current_count: int) -> bool:
        """Check if organization can add more members."""
        return current_count < self.max_members
    
    def can_create_projects(self, current_count: int) -> bool:
        """Check if organization can create more projects."""
        return current_count < self.max_projects


class OrganizationMemberRole(enum.Enum):
    """Organization member roles."""
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


class OrganizationMember(Base):
    """Association between users and organizations."""
    
    __tablename__ = "organization_members"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys (will be added when we create relationships)
    # user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Role and permissions
    role = Column(SQLEnum(OrganizationMemberRole), default=OrganizationMemberRole.MEMBER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships (will be added when we create foreign keys)
    # user = relationship("User", back_populates="organizations")
    # organization = relationship("Organization", back_populates="members")
    
    def __repr__(self) -> str:
        return f"<OrganizationMember(id={self.id}, role='{self.role.value}')>"
    
    def is_owner(self) -> bool:
        """Check if member is organization owner."""
        return self.role == OrganizationMemberRole.OWNER
    
    def is_admin(self) -> bool:
        """Check if member has admin role or higher."""
        return self.role in [OrganizationMemberRole.OWNER, OrganizationMemberRole.ADMIN]
    
    def can_manage_members(self) -> bool:
        """Check if member can manage other members."""
        return self.role in [OrganizationMemberRole.OWNER, OrganizationMemberRole.ADMIN]
    
    def can_manage_projects(self) -> bool:
        """Check if member can manage projects."""
        return self.role in [OrganizationMemberRole.OWNER, OrganizationMemberRole.ADMIN, OrganizationMemberRole.MANAGER]