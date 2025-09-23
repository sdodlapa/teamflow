"""
Webhook models for external integrations and event notifications.
Provides webhook management, delivery tracking, and retry mechanisms.
"""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any, List
import uuid

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.database import Base


class WebhookEventType(str, Enum):
    """Types of webhook events."""
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_DELETED = "project.deleted"
    USER_INVITED = "user.invited"
    USER_JOINED = "user.joined"
    COMMENT_ADDED = "comment.added"
    FILE_UPLOADED = "file.uploaded"
    WORKFLOW_EXECUTED = "workflow.executed"
    CUSTOM_EVENT = "custom.event"


class WebhookStatus(str, Enum):
    """Webhook endpoint status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DISABLED = "disabled"


class DeliveryStatus(str, Enum):
    """Webhook delivery status."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class WebhookEndpoint(Base):
    """
    Webhook endpoint configuration.
    Manages external webhook destinations and their settings.
    """
    __tablename__ = "webhook_endpoints"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    url = Column(String(2048), nullable=False)
    secret = Column(String(255))  # For signature verification
    
    # Event configuration
    event_types = Column(ARRAY(String), nullable=False, default=[])
    filters = Column(JSON, default={})  # Additional filtering conditions
    
    # Delivery settings
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default=WebhookStatus.ACTIVE)
    timeout_seconds = Column(Integer, default=30)
    max_retries = Column(Integer, default=3)
    retry_delay_seconds = Column(Integer, default=60)
    
    # Headers and authentication
    headers = Column(JSON, default={})  # Custom headers to include
    auth_type = Column(String(50))  # bearer, basic, api_key, custom
    auth_config = Column(JSON, default={})  # Auth configuration
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=60)
    rate_limit_per_hour = Column(Integer, default=1000)
    
    # Organization and ownership
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_delivery_at = Column(DateTime)
    last_success_at = Column(DateTime)
    last_failure_at = Column(DateTime)
    
    # Statistics
    total_deliveries = Column(Integer, default=0)
    successful_deliveries = Column(Integer, default=0)
    failed_deliveries = Column(Integer, default=0)
    
    # Relationships
    organization = relationship("Organization", back_populates="webhook_endpoints")
    creator = relationship("User", foreign_keys=[created_by])
    deliveries = relationship("WebhookDelivery", back_populates="endpoint", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_webhook_endpoints_org_status", "organization_id", "status"),
        Index("idx_webhook_endpoints_active", "is_active"),
        Index("idx_webhook_endpoints_events", "event_types"),
    )
    
    @hybrid_property
    def success_rate(self) -> float:
        """Calculate delivery success rate."""
        if self.total_deliveries == 0:
            return 0.0
        return (self.successful_deliveries / self.total_deliveries) * 100
    
    @hybrid_property
    def is_healthy(self) -> bool:
        """Check if webhook endpoint is healthy."""
        if not self.is_active or self.status != WebhookStatus.ACTIVE:
            return False
        
        # Check recent failures
        if self.last_failure_at and self.last_success_at:
            return self.last_success_at > self.last_failure_at
        
        return self.success_rate >= 80.0


class WebhookDelivery(Base):
    """
    Individual webhook delivery attempts.
    Tracks delivery status, response, and retry attempts.
    """
    __tablename__ = "webhook_deliveries"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # Webhook and event information
    endpoint_id = Column(Integer, ForeignKey("webhook_endpoints.id"), nullable=False)
    event_type = Column(String(100), nullable=False)
    event_id = Column(String(255))  # Original event ID
    
    # Delivery details
    status = Column(String(20), default=DeliveryStatus.PENDING)
    attempt_number = Column(Integer, default=1)
    max_attempts = Column(Integer, default=3)
    
    # Request data
    payload = Column(JSON, nullable=False)
    headers = Column(JSON, default={})
    url = Column(String(2048), nullable=False)
    signature = Column(String(255))  # HMAC signature
    
    # Response data
    response_status_code = Column(Integer)
    response_headers = Column(JSON)
    response_body = Column(Text)
    response_time_ms = Column(Integer)
    
    # Error information
    error_message = Column(Text)
    error_code = Column(String(100))
    
    # Timing
    scheduled_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    next_retry_at = Column(DateTime)
    
    # Organization for filtering
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Relationships
    endpoint = relationship("WebhookEndpoint", back_populates="deliveries")
    organization = relationship("Organization")
    
    # Indexes
    __table_args__ = (
        Index("idx_webhook_deliveries_endpoint_status", "endpoint_id", "status"),
        Index("idx_webhook_deliveries_scheduled", "scheduled_at"),
        Index("idx_webhook_deliveries_retry", "next_retry_at"),
        Index("idx_webhook_deliveries_event", "event_type", "event_id"),
    )
    
    @hybrid_property
    def is_successful(self) -> bool:
        """Check if delivery was successful."""
        return (
            self.status == DeliveryStatus.DELIVERED and
            self.response_status_code and
            200 <= self.response_status_code < 300
        )
    
    @hybrid_property
    def can_retry(self) -> bool:
        """Check if delivery can be retried."""
        return (
            self.status in [DeliveryStatus.FAILED, DeliveryStatus.RETRYING] and
            self.attempt_number < self.max_attempts and
            datetime.utcnow() >= (self.next_retry_at or datetime.utcnow())
        )


class WebhookEvent(Base):
    """
    Webhook events queue for processing.
    Manages event generation and delivery scheduling.
    """
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # Event details
    event_type = Column(String(100), nullable=False)
    event_source = Column(String(100), nullable=False)  # task, project, user, etc.
    source_id = Column(Integer, nullable=False)  # ID of the source object
    
    # Event data
    payload = Column(JSON, nullable=False)
    context = Column(JSON, default={})  # Additional context
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)
    processing_errors = Column(JSON, default=[])
    
    # Targeting
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))  # Triggering user
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    scheduled_for = Column(DateTime, default=datetime.utcnow)  # Delayed processing support
    
    # Relationships
    organization = relationship("Organization")
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index("idx_webhook_events_processing", "is_processed", "scheduled_for"),
        Index("idx_webhook_events_type_org", "event_type", "organization_id"),
        Index("idx_webhook_events_source", "event_source", "source_id"),
    )


class ExternalIntegration(Base):
    """
    External service integrations configuration.
    Manages OAuth2 connections and API credentials.
    """
    __tablename__ = "external_integrations"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # Integration details
    name = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False)  # slack, github, jira, etc.
    provider_type = Column(String(50), nullable=False)  # oauth2, api_key, webhook
    
    # Configuration
    config = Column(JSON, nullable=False, default={})
    credentials = Column(JSON, default={})  # Encrypted credentials
    scopes = Column(ARRAY(String), default=[])
    
    # OAuth2 specific
    client_id = Column(String(255))
    client_secret = Column(String(255))  # Encrypted
    access_token = Column(Text)  # Encrypted
    refresh_token = Column(Text)  # Encrypted
    token_expires_at = Column(DateTime)
    
    # Status and health
    is_active = Column(Boolean, default=True)
    is_connected = Column(Boolean, default=False)
    last_sync_at = Column(DateTime)
    last_error = Column(Text)
    sync_frequency_minutes = Column(Integer, default=60)
    
    # Organization and ownership
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    connected_at = Column(DateTime)
    
    # Relationships
    organization = relationship("Organization", back_populates="external_integrations")
    creator = relationship("User", foreign_keys=[created_by])
    
    # Indexes
    __table_args__ = (
        Index("idx_external_integrations_org_provider", "organization_id", "provider"),
        Index("idx_external_integrations_active", "is_active", "is_connected"),
        Index("idx_external_integrations_sync", "last_sync_at", "sync_frequency_minutes"),
    )
    
    @hybrid_property
    def needs_token_refresh(self) -> bool:
        """Check if OAuth2 token needs refresh."""
        if not self.token_expires_at or not self.refresh_token:
            return False
        return datetime.utcnow() >= (self.token_expires_at - timedelta(minutes=5))


class APIRateLimit(Base):
    """
    API rate limiting tracking.
    Manages rate limits for API keys and webhook endpoints.
    """
    __tablename__ = "api_rate_limits"

    id = Column(Integer, primary_key=True, index=True)
    
    # Rate limit subject
    subject_type = Column(String(50), nullable=False)  # api_key, webhook, user, organization
    subject_id = Column(String(255), nullable=False)  # API key, webhook ID, user ID, etc.
    
    # Rate limit configuration
    limit_type = Column(String(50), nullable=False)  # minute, hour, day
    max_requests = Column(Integer, nullable=False)
    window_size_seconds = Column(Integer, nullable=False)
    
    # Current usage
    current_count = Column(Integer, default=0)
    window_start = Column(DateTime, default=datetime.utcnow)
    last_request_at = Column(DateTime)
    
    # Organization for filtering
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Relationships
    organization = relationship("Organization")
    
    # Indexes
    __table_args__ = (
        Index("idx_api_rate_limits_subject", "subject_type", "subject_id"),
        Index("idx_api_rate_limits_window", "window_start", "window_size_seconds"),
        Index("idx_api_rate_limits_org", "organization_id"),
    )
    
    @hybrid_property
    def is_exceeded(self) -> bool:
        """Check if rate limit is exceeded."""
        # Check if we're in a new window
        if datetime.utcnow() >= (self.window_start + timedelta(seconds=self.window_size_seconds)):
            return False  # New window, not exceeded
        
        return self.current_count >= self.max_requests
    
    @hybrid_property
    def remaining_requests(self) -> int:
        """Calculate remaining requests in current window."""
        if self.is_exceeded:
            return 0
        return max(0, self.max_requests - self.current_count)