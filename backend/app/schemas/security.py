"""Security and compliance schemas for API validation."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator
from enum import Enum

from app.models.security import (
    AuditActionType,
    SecurityRiskLevel,
    DataProcessingPurpose,
    APIKeyScope,
)


# Base schemas
class SecurityBase(BaseModel):
    """Base schema for security-related models."""
    
    class Config:
        from_attributes = True


# Audit Log Schemas
class AuditLogBase(SecurityBase):
    """Base audit log schema."""
    
    action_type: AuditActionType
    resource_type: str = Field(..., max_length=50)
    resource_id: Optional[str] = Field(None, max_length=255)
    description: str
    risk_level: SecurityRiskLevel = SecurityRiskLevel.LOW
    is_suspicious: bool = False
    extra_data: Optional[Dict[str, Any]] = None


class AuditLogCreate(AuditLogBase):
    """Schema for creating audit logs."""
    
    user_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    session_id: Optional[str] = Field(None, max_length=255)
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None
    request_method: Optional[str] = Field(None, max_length=10)
    request_path: Optional[str] = Field(None, max_length=500)
    before_data: Optional[Dict[str, Any]] = None
    after_data: Optional[Dict[str, Any]] = None


class AuditLogResponse(AuditLogBase):
    """Schema for audit log responses."""
    
    id: UUID
    user_id: Optional[UUID]
    organization_id: Optional[UUID]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_method: Optional[str]
    request_path: Optional[str]
    before_data: Optional[Dict[str, Any]]
    after_data: Optional[Dict[str, Any]]
    extra_data: Optional[Dict[str, Any]]
    created_at: datetime


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs."""
    
    action_types: Optional[List[AuditActionType]] = None
    resource_types: Optional[List[str]] = None
    user_ids: Optional[List[UUID]] = None
    organization_ids: Optional[List[UUID]] = None
    risk_levels: Optional[List[SecurityRiskLevel]] = None
    is_suspicious: Optional[bool] = None
    ip_addresses: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# Security Alert Schemas
class SecurityAlertBase(SecurityBase):
    """Base security alert schema."""
    
    alert_type: str = Field(..., max_length=50)
    severity: SecurityRiskLevel = SecurityRiskLevel.MEDIUM
    title: str = Field(..., max_length=255)
    description: str
    alert_data: Optional[Dict[str, Any]] = None
    threshold_breached: Optional[str] = Field(None, max_length=100)


class SecurityAlertCreate(SecurityAlertBase):
    """Schema for creating security alerts."""
    
    user_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None
    ip_address: Optional[str] = Field(None, max_length=45)


class SecurityAlertUpdate(BaseModel):
    """Schema for updating security alerts."""
    
    is_resolved: Optional[bool] = None
    resolution_notes: Optional[str] = None


class SecurityAlertResponse(SecurityAlertBase):
    """Schema for security alert responses."""
    
    id: UUID
    user_id: Optional[UUID]
    organization_id: Optional[UUID]
    ip_address: Optional[str]
    is_resolved: bool
    resolved_at: Optional[datetime]
    resolved_by: Optional[UUID]
    resolution_notes: Optional[str]
    created_at: datetime
    updated_at: datetime


# API Key Schemas
class APIKeyBase(SecurityBase):
    """Base API key schema."""
    
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    scopes: List[APIKeyScope]
    allowed_ips: Optional[List[str]] = None
    rate_limit: Optional[int] = Field(None, gt=0)
    expires_at: Optional[datetime] = None


class APIKeyCreate(APIKeyBase):
    """Schema for creating API keys."""
    
    organization_id: UUID


class APIKeyUpdate(BaseModel):
    """Schema for updating API keys."""
    
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    scopes: Optional[List[APIKeyScope]] = None
    allowed_ips: Optional[List[str]] = None
    rate_limit: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class APIKeyResponse(APIKeyBase):
    """Schema for API key responses."""
    
    id: UUID
    prefix: str
    user_id: UUID
    organization_id: UUID
    is_active: bool
    is_expired: bool
    last_used_at: Optional[datetime]
    usage_count: int
    created_at: datetime
    updated_at: datetime


class APIKeyWithToken(APIKeyResponse):
    """Schema for API key response with the actual token (only on creation)."""
    
    token: str = Field(..., description="Full API token - only shown once!")


# GDPR Request Schemas
class GDPRRequestBase(SecurityBase):
    """Base GDPR request schema."""
    
    request_type: str = Field(..., max_length=50)
    description: Optional[str] = None
    data_categories: Optional[List[str]] = None
    processing_purposes: Optional[List[DataProcessingPurpose]] = None
    legal_basis: Optional[str] = Field(None, max_length=100)


class GDPRRequestCreate(GDPRRequestBase):
    """Schema for creating GDPR requests."""
    
    organization_id: Optional[UUID] = None


class GDPRRequestUpdate(BaseModel):
    """Schema for updating GDPR requests."""
    
    status: Optional[str] = Field(None, max_length=50)
    completion_notes: Optional[str] = None


class GDPRRequestResponse(GDPRRequestBase):
    """Schema for GDPR request responses."""
    
    id: UUID
    status: str
    user_id: UUID
    organization_id: Optional[UUID]
    processed_by: Optional[UUID]
    processed_at: Optional[datetime]
    completion_notes: Optional[str]
    export_url: Optional[str]
    export_expires_at: Optional[datetime]
    verification_token: Optional[str]
    verified_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


# Data Consent Schemas
class DataConsentBase(SecurityBase):
    """Base data consent schema."""
    
    purpose: DataProcessingPurpose
    consent_given: bool
    consent_text: str
    lawful_basis: Optional[str] = Field(None, max_length=100)
    data_categories: Optional[List[str]] = None
    retention_period: Optional[str] = Field(None, max_length=100)
    expires_at: Optional[datetime] = None


class DataConsentCreate(DataConsentBase):
    """Schema for creating data consent records."""
    
    organization_id: Optional[UUID] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None
    consent_method: str = Field(..., max_length=50)


class DataConsentResponse(DataConsentBase):
    """Schema for data consent responses."""
    
    id: UUID
    user_id: UUID
    organization_id: Optional[UUID]
    ip_address: Optional[str]
    user_agent: Optional[str]
    consent_method: str
    is_expired: bool
    is_active: bool
    created_at: datetime


# Security Configuration Schemas
class SecurityConfigurationBase(SecurityBase):
    """Base security configuration schema."""
    
    config_type: str = Field(..., max_length=50)
    settings: Dict[str, Any]
    is_active: bool = True


class SecurityConfigurationCreate(SecurityConfigurationBase):
    """Schema for creating security configurations."""
    
    organization_id: Optional[UUID] = None


class SecurityConfigurationUpdate(BaseModel):
    """Schema for updating security configurations."""
    
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class SecurityConfigurationResponse(SecurityConfigurationBase):
    """Schema for security configuration responses."""
    
    id: UUID
    organization_id: Optional[UUID]
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime


# Login Attempt Schemas
class LoginAttemptBase(SecurityBase):
    """Base login attempt schema."""
    
    username: str = Field(..., max_length=255)
    ip_address: str = Field(..., max_length=45)
    user_agent: Optional[str] = None
    success: bool
    failure_reason: Optional[str] = Field(None, max_length=100)
    is_suspicious: bool = False
    risk_score: int = 0
    extra_data: Optional[Dict[str, Any]] = None


class LoginAttemptCreate(LoginAttemptBase):
    """Schema for creating login attempts."""
    
    user_id: Optional[UUID] = None
    organization_id: Optional[UUID] = None


class LoginAttemptResponse(LoginAttemptBase):
    """Schema for login attempt responses."""
    
    id: UUID
    user_id: Optional[UUID]
    organization_id: Optional[UUID]
    created_at: datetime


# Security Dashboard Schemas
class SecurityMetrics(BaseModel):
    """Security metrics for dashboard."""
    
    total_login_attempts: int
    failed_login_attempts: int
    suspicious_activities: int
    active_security_alerts: int
    gdpr_requests_pending: int
    api_keys_active: int
    audit_logs_today: int


class SecurityDashboard(BaseModel):
    """Security dashboard data."""
    
    metrics: SecurityMetrics
    recent_alerts: List[SecurityAlertResponse]
    recent_failed_logins: List[LoginAttemptResponse]
    recent_audit_logs: List[AuditLogResponse]


# Compliance Report Schemas
class ComplianceReport(BaseModel):
    """GDPR compliance report."""
    
    organization_id: Optional[UUID]
    report_date: datetime
    total_users: int
    active_consents: int
    expired_consents: int
    pending_gdpr_requests: int
    completed_gdpr_requests: int
    data_retention_compliance: Dict[str, Any]
    recommendations: List[str]


# Security Risk Assessment Schemas
class RiskFactor(BaseModel):
    """Individual risk factor."""
    
    factor: str
    risk_level: SecurityRiskLevel
    description: str
    mitigation: Optional[str] = None


class SecurityRiskAssessment(BaseModel):
    """Security risk assessment."""
    
    overall_risk: SecurityRiskLevel
    risk_factors: List[RiskFactor]
    recommendations: List[str]
    last_assessment: datetime


# Validation helpers
@validator("scopes")
def validate_scopes(cls, v):
    """Validate API key scopes."""
    if not v:
        raise ValueError("At least one scope is required")
    return v


@validator("allowed_ips")
def validate_ips(cls, v):
    """Validate IP addresses."""
    if v:
        import ipaddress
        for ip in v:
            try:
                ipaddress.ip_address(ip)
            except ValueError:
                raise ValueError(f"Invalid IP address: {ip}")
    return v