"""Security and compliance models for TeamFlow."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.models.base import Base


class AuditActionType(str, Enum):
    """Types of audit actions."""
    
    # Authentication actions
    LOGIN = "login"
    LOGOUT = "logout"
    FAILED_LOGIN = "failed_login"
    PASSWORD_CHANGE = "password_change"
    ACCOUNT_LOCKED = "account_locked"
    
    # Data actions
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    
    # Permission actions
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    
    # Security actions
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SECURITY_VIOLATION = "security_violation"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    
    # GDPR actions
    DATA_EXPORT_REQUEST = "data_export_request"
    DATA_DELETION_REQUEST = "data_deletion_request"
    CONSENT_GRANTED = "consent_granted"
    CONSENT_REVOKED = "consent_revoked"


class SecurityRiskLevel(str, Enum):
    """Security risk levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataProcessingPurpose(str, Enum):
    """Purposes for data processing under GDPR."""
    
    ESSENTIAL = "essential"  # Essential for service delivery
    ANALYTICS = "analytics"  # Analytics and improvements
    MARKETING = "marketing"  # Marketing communications
    RESEARCH = "research"  # Research and development


class APIKeyScope(str, Enum):
    """API key access scopes."""
    
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"
    WEBHOOK = "webhook"
    INTEGRATION = "integration"


class AuditLog(Base):
    """Comprehensive audit logging for security and compliance."""
    
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Action details
    action_type = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=False)
    
    # User and context
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    
    # Request details
    ip_address = Column(String(45), nullable=True, index=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)
    request_method = Column(String(10), nullable=True)
    request_path = Column(String(500), nullable=True)
    
    # Security context
    risk_level = Column(String(20), nullable=False, default=SecurityRiskLevel.LOW)
    is_suspicious = Column(Boolean, default=False, index=True)
    
    # Metadata
    extra_data = Column(JSON, nullable=True)  # Additional context data
    before_data = Column(JSON, nullable=True)  # Data before change
    after_data = Column(JSON, nullable=True)  # Data after change
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    organization = relationship("Organization", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog {self.action_type} on {self.resource_type} by {self.user_id}>"


class SecurityAlert(Base):
    """Security alerts and monitoring."""
    
    __tablename__ = "security_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, default=SecurityRiskLevel.MEDIUM)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Context
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True, index=True)
    
    # Alert data
    alert_data = Column(JSON, nullable=True)  # Additional alert context
    threshold_breached = Column(String(100), nullable=True)  # What threshold was breached
    
    # Status
    is_resolved = Column(Boolean, default=False, index=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="security_alerts")
    organization = relationship("Organization", back_populates="security_alerts")
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])
    
    def __repr__(self):
        return f"<SecurityAlert {self.alert_type} - {self.severity}>"


class APIKey(Base):
    """API keys for programmatic access."""
    
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Key details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    key_hash = Column(String(255), nullable=False, unique=True, index=True)  # Hashed API key
    prefix = Column(String(10), nullable=False, index=True)  # First few chars for identification
    
    # Access control
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    scopes = Column(JSON, nullable=False)  # List of allowed scopes
    
    # Restrictions
    allowed_ips = Column(JSON, nullable=True)  # List of allowed IP addresses
    rate_limit = Column(Integer, nullable=True)  # Requests per hour
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    last_used_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    organization = relationship("Organization", back_populates="api_keys")
    
    @hybrid_property
    def is_expired(self):
        """Check if API key has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f"<APIKey {self.name} ({self.prefix}...)>"


class GDPRRequest(Base):
    """GDPR compliance requests (data export, deletion, etc.)."""
    
    __tablename__ = "gdpr_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Request details
    request_type = Column(String(50), nullable=False, index=True)  # export, deletion, portability
    status = Column(String(50), nullable=False, default="pending", index=True)
    description = Column(Text, nullable=True)
    
    # User context
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True)
    
    # Request data
    data_categories = Column(JSON, nullable=True)  # Categories of data requested
    processing_purposes = Column(JSON, nullable=True)  # Purposes for processing
    legal_basis = Column(String(100), nullable=True)  # Legal basis for processing
    
    # Processing
    processed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    processed_at = Column(DateTime, nullable=True)
    completion_notes = Column(Text, nullable=True)
    
    # Data export
    export_url = Column(String(500), nullable=True)  # URL to download exported data
    export_expires_at = Column(DateTime, nullable=True)
    
    # Verification
    verification_token = Column(String(255), nullable=True, unique=True)
    verified_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="gdpr_requests")
    organization = relationship("Organization", back_populates="gdpr_requests")
    processed_by_user = relationship("User", foreign_keys=[processed_by])
    
    def __repr__(self):
        return f"<GDPRRequest {self.request_type} for {self.user_id}>"


class DataConsentRecord(Base):
    """User consent records for GDPR compliance."""
    
    __tablename__ = "data_consent_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Consent details
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True)
    
    # Consent specifics
    purpose = Column(String(50), nullable=False, index=True)  # What data is used for
    consent_given = Column(Boolean, nullable=False, index=True)
    consent_text = Column(Text, nullable=False)  # The consent text shown to user
    
    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    consent_method = Column(String(50), nullable=False)  # web, api, email, etc.
    
    # Legal requirements
    lawful_basis = Column(String(100), nullable=True)  # GDPR lawful basis
    data_categories = Column(JSON, nullable=True)  # Categories of personal data
    retention_period = Column(String(100), nullable=True)  # How long data is kept
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)  # When consent expires
    
    # Relationships
    user = relationship("User", back_populates="consent_records")
    organization = relationship("Organization", back_populates="consent_records")
    
    @hybrid_property
    def is_expired(self):
        """Check if consent has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @hybrid_property
    def is_active(self):
        """Check if consent is currently active."""
        return self.consent_given and not self.is_expired
    
    def __repr__(self):
        return f"<DataConsentRecord {self.purpose} for {self.user_id}>"


class SecurityConfiguration(Base):
    """Security configuration settings."""
    
    __tablename__ = "security_configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Configuration scope
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True)
    config_type = Column(String(50), nullable=False, index=True)  # password_policy, session, etc.
    
    # Configuration data
    settings = Column(JSON, nullable=False)  # Flexible configuration storage
    is_active = Column(Boolean, default=True, index=True)
    
    # Management
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="security_configurations")
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])
    
    def __repr__(self):
        return f"<SecurityConfiguration {self.config_type} for {self.organization_id}>"


class LoginAttempt(Base):
    """Track login attempts for security monitoring."""
    
    __tablename__ = "login_attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Attempt details
    username = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    user_agent = Column(Text, nullable=True)
    
    # Result
    success = Column(Boolean, nullable=False, index=True)
    failure_reason = Column(String(100), nullable=True)  # invalid_password, account_locked, etc.
    
    # Context
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True)
    
    # Security flags
    is_suspicious = Column(Boolean, default=False, index=True)
    risk_score = Column(Integer, default=0)  # Calculated risk score
    
    # Additional data
    extra_data = Column(JSON, nullable=True)  # Additional context
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="login_attempts")
    organization = relationship("Organization", back_populates="login_attempts")
    
    def __repr__(self):
        return f"<LoginAttempt {self.username} from {self.ip_address} - {'Success' if self.success else 'Failed'}>"