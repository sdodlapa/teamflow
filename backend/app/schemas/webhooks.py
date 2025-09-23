"""
Webhook schemas for request/response validation.
Provides Pydantic models for webhook endpoints, deliveries, and integrations.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum

from app.models.webhooks import WebhookEventType, WebhookStatus, DeliveryStatus


# ============================================================================
# Webhook Endpoint Schemas
# ============================================================================

class WebhookEndpointBase(BaseModel):
    """Base webhook endpoint schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    url: HttpUrl = Field(..., description="Webhook endpoint URL")
    secret: Optional[str] = Field(None, description="Secret for signature verification")
    
    # Event configuration
    event_types: List[WebhookEventType] = Field(default=[], description="Event types to subscribe to")
    filters: Dict[str, Any] = Field(default={}, description="Additional filtering conditions")
    
    # Delivery settings
    is_active: bool = Field(default=True)
    timeout_seconds: int = Field(default=30, ge=5, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay_seconds: int = Field(default=60, ge=10, le=3600)
    
    # Headers and authentication
    headers: Dict[str, str] = Field(default={}, description="Custom headers")
    auth_type: Optional[str] = Field(None, pattern=r"^(bearer|basic|api_key|custom)$")
    auth_config: Dict[str, Any] = Field(default={})
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, ge=1, le=1000)
    rate_limit_per_hour: int = Field(default=1000, ge=1, le=10000)


class WebhookEndpointCreate(WebhookEndpointBase):
    """Schema for creating webhook endpoints."""
    pass


class WebhookEndpointUpdate(BaseModel):
    """Schema for updating webhook endpoints."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    url: Optional[HttpUrl] = None
    secret: Optional[str] = None
    event_types: Optional[List[WebhookEventType]] = None
    filters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    timeout_seconds: Optional[int] = Field(None, ge=5, le=300)
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    retry_delay_seconds: Optional[int] = Field(None, ge=10, le=3600)
    headers: Optional[Dict[str, str]] = None
    auth_type: Optional[str] = Field(None, pattern=r"^(bearer|basic|api_key|custom)$")
    auth_config: Optional[Dict[str, Any]] = None
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=1000)
    rate_limit_per_hour: Optional[int] = Field(None, ge=1, le=10000)


class WebhookEndpointResponse(WebhookEndpointBase):
    """Schema for webhook endpoint responses."""
    id: int
    uuid: UUID
    status: WebhookStatus
    organization_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    last_delivery_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    last_failure_at: Optional[datetime] = None
    total_deliveries: int = 0
    successful_deliveries: int = 0
    failed_deliveries: int = 0
    success_rate: float = 0.0
    is_healthy: bool = True

    class Config:
        from_attributes = True


# ============================================================================
# Webhook Delivery Schemas
# ============================================================================

class WebhookDeliveryBase(BaseModel):
    """Base webhook delivery schema."""
    event_type: WebhookEventType
    event_id: Optional[str] = None
    payload: Dict[str, Any]
    headers: Dict[str, str] = Field(default={})


class WebhookDeliveryCreate(WebhookDeliveryBase):
    """Schema for creating webhook deliveries."""
    endpoint_id: int


class WebhookDeliveryResponse(WebhookDeliveryBase):
    """Schema for webhook delivery responses."""
    id: int
    uuid: UUID
    endpoint_id: int
    status: DeliveryStatus
    attempt_number: int = 1
    max_attempts: int = 3
    url: str
    signature: Optional[str] = None
    response_status_code: Optional[int] = None
    response_headers: Optional[Dict[str, Any]] = None
    response_body: Optional[str] = None
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    scheduled_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    is_successful: bool = False
    can_retry: bool = False

    class Config:
        from_attributes = True


# ============================================================================
# Webhook Event Schemas
# ============================================================================

class WebhookEventBase(BaseModel):
    """Base webhook event schema."""
    event_type: WebhookEventType
    event_source: str = Field(..., description="Source type (task, project, user, etc.)")
    source_id: int = Field(..., description="ID of the source object")
    payload: Dict[str, Any]
    context: Dict[str, Any] = Field(default={})


class WebhookEventCreate(WebhookEventBase):
    """Schema for creating webhook events."""
    user_id: Optional[int] = None
    scheduled_for: Optional[datetime] = None


class WebhookEventResponse(WebhookEventBase):
    """Schema for webhook event responses."""
    id: int
    uuid: UUID
    is_processed: bool = False
    processed_at: Optional[datetime] = None
    processing_errors: List[str] = Field(default=[])
    organization_id: int
    user_id: Optional[int] = None
    created_at: datetime
    scheduled_for: datetime

    class Config:
        from_attributes = True


# ============================================================================
# External Integration Schemas
# ============================================================================

class ExternalIntegrationBase(BaseModel):
    """Base external integration schema."""
    name: str = Field(..., min_length=1, max_length=255)
    provider: str = Field(..., pattern=r"^[a-z_]+$", description="Provider identifier")
    provider_type: str = Field(..., pattern=r"^(oauth2|api_key|webhook)$")
    config: Dict[str, Any] = Field(default={})
    scopes: List[str] = Field(default=[])
    is_active: bool = Field(default=True)
    sync_frequency_minutes: int = Field(default=60, ge=5, le=1440)


class ExternalIntegrationCreate(ExternalIntegrationBase):
    """Schema for creating external integrations."""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    credentials: Dict[str, Any] = Field(default={})


class ExternalIntegrationUpdate(BaseModel):
    """Schema for updating external integrations."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    config: Optional[Dict[str, Any]] = None
    scopes: Optional[List[str]] = None
    is_active: Optional[bool] = None
    sync_frequency_minutes: Optional[int] = Field(None, ge=5, le=1440)
    credentials: Optional[Dict[str, Any]] = None


class ExternalIntegrationResponse(ExternalIntegrationBase):
    """Schema for external integration responses."""
    id: int
    uuid: UUID
    is_connected: bool = False
    last_sync_at: Optional[datetime] = None
    last_error: Optional[str] = None
    organization_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    connected_at: Optional[datetime] = None
    needs_token_refresh: bool = False

    class Config:
        from_attributes = True


# ============================================================================
# OAuth2 Schemas
# ============================================================================

class OAuth2AuthorizeRequest(BaseModel):
    """Schema for OAuth2 authorization requests."""
    provider: str = Field(..., pattern=r"^[a-z_]+$")
    scopes: List[str] = Field(default=[])
    redirect_uri: Optional[HttpUrl] = None
    state: Optional[str] = None


class OAuth2CallbackRequest(BaseModel):
    """Schema for OAuth2 callback requests."""
    code: str
    state: Optional[str] = None
    integration_id: Optional[int] = None


class OAuth2TokenResponse(BaseModel):
    """Schema for OAuth2 token responses."""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


# ============================================================================
# Rate Limit Schemas
# ============================================================================

class RateLimitStatus(BaseModel):
    """Schema for rate limit status."""
    limit_type: str
    max_requests: int
    current_count: int
    remaining_requests: int
    window_start: datetime
    window_size_seconds: int
    is_exceeded: bool
    reset_at: datetime


class RateLimitConfig(BaseModel):
    """Schema for rate limit configuration."""
    subject_type: str = Field(..., pattern=r"^(api_key|webhook|user|organization)$")
    subject_id: str
    limit_type: str = Field(..., pattern=r"^(minute|hour|day)$")
    max_requests: int = Field(..., ge=1)
    window_size_seconds: int = Field(default=60, description="Window size in seconds")
    
    @validator('window_size_seconds', pre=True, always=True)
    def set_window_size(cls, v, values):
        """Set window size based on limit type."""
        limit_type = values.get('limit_type')
        if limit_type == 'minute':
            return 60
        elif limit_type == 'hour':
            return 3600
        elif limit_type == 'day':
            return 86400
        return v


# ============================================================================
# Webhook Testing Schemas
# ============================================================================

class WebhookTestRequest(BaseModel):
    """Schema for webhook testing requests."""
    endpoint_id: int
    event_type: WebhookEventType = WebhookEventType.CUSTOM_EVENT
    test_payload: Dict[str, Any] = Field(default={"test": True, "timestamp": None})


class WebhookTestResponse(BaseModel):
    """Schema for webhook test responses."""
    success: bool
    delivery_id: int
    status_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None


# ============================================================================
# Webhook Analytics Schemas
# ============================================================================

class WebhookAnalyticsFilter(BaseModel):
    """Schema for webhook analytics filters."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    endpoint_ids: Optional[List[int]] = None
    event_types: Optional[List[WebhookEventType]] = None
    status_filter: Optional[List[DeliveryStatus]] = None


class WebhookDeliveryStats(BaseModel):
    """Schema for webhook delivery statistics."""
    total_deliveries: int
    successful_deliveries: int
    failed_deliveries: int
    success_rate: float
    average_response_time_ms: float
    median_response_time_ms: int
    max_response_time_ms: int


class WebhookAnalyticsResponse(BaseModel):
    """Schema for webhook analytics responses."""
    overall_stats: WebhookDeliveryStats
    deliveries_by_day: List[Dict[str, Any]]
    deliveries_by_event_type: List[Dict[str, Any]]
    top_failing_endpoints: List[Dict[str, Any]]
    response_time_trends: List[Dict[str, Any]]


# ============================================================================
# Integration Provider Schemas
# ============================================================================

class IntegrationProvider(BaseModel):
    """Schema for integration provider information."""
    id: str
    name: str
    description: str
    provider_type: str
    supported_scopes: List[str]
    auth_url: Optional[str] = None
    token_url: Optional[str] = None
    api_base_url: Optional[str] = None
    documentation_url: Optional[str] = None


class IntegrationProviderList(BaseModel):
    """Schema for listing integration providers."""
    providers: List[IntegrationProvider]


# ============================================================================
# Webhook Signature Verification
# ============================================================================

class WebhookSignature(BaseModel):
    """Schema for webhook signature verification."""
    signature: str
    timestamp: str
    body: str
    secret: str