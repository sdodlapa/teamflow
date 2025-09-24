"""Organization model for multi-tenant support."""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class OrganizationPlan(str, enum.Enum):
    """Organization subscription plans."""

    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class OrganizationStatus(str, enum.Enum):
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
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)

    # Settings
    plan = Column(
        SQLEnum(OrganizationPlan), default=OrganizationPlan.FREE, nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    members = relationship(
        "OrganizationMember",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    projects = relationship(
        "Project", back_populates="organization", cascade="all, delete-orphan"
    )
    task_templates = relationship(
        "TaskTemplate", back_populates="organization", cascade="all, delete-orphan"
    )
    
    # Analytics relationships
    report_templates = relationship(
        "ReportTemplate", back_populates="organization", cascade="all, delete-orphan"
    )
    reports = relationship(
        "Report", back_populates="organization", cascade="all, delete-orphan"  
    )
    dashboards = relationship(
        "Dashboard", back_populates="organization", cascade="all, delete-orphan"
    )
    
    # Workflow relationships
    workflow_definitions = relationship(
        "WorkflowDefinition", back_populates="organization", cascade="all, delete-orphan"
    )
    
    # File management relationships
    files = relationship("FileUpload", back_populates="organization", cascade="all, delete-orphan")
    
    # Webhook and integration relationships
    webhook_endpoints = relationship(
        "WebhookEndpoint", back_populates="organization", cascade="all, delete-orphan"
    )
    external_integrations = relationship(
        "ExternalIntegration", back_populates="organization", cascade="all, delete-orphan"
    )
    
    # Security and compliance relationships
    audit_logs = relationship("AuditLog", back_populates="organization", cascade="all, delete-orphan")
    security_alerts = relationship("SecurityAlert", back_populates="organization", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="organization", cascade="all, delete-orphan")
    gdpr_requests = relationship("GDPRRequest", back_populates="organization", cascade="all, delete-orphan")
    consent_records = relationship("DataConsentRecord", back_populates="organization", cascade="all, delete-orphan")
    security_configurations = relationship("SecurityConfiguration", back_populates="organization", cascade="all, delete-orphan")
    login_attempts = relationship("LoginAttempt", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name='{self.name}')>"


class OrganizationMemberRole(str, enum.Enum):
    """Organization member roles."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class OrganizationMember(Base):
    """Association between users and organizations."""

    __tablename__ = "organization_members"

    # Primary identification
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    # Role and permissions
    role = Column(
        SQLEnum(OrganizationMemberRole),
        default=OrganizationMemberRole.MEMBER,
        nullable=False,
    )

    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="organization_memberships")
    organization = relationship("Organization", back_populates="members")

    def __repr__(self) -> str:
        return f"<OrganizationMember(id={self.id}, role='{self.role.value}')>"
