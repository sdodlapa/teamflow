"""Security and compliance API routes."""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.security import (
    AuditLog, SecurityAlert, APIKey, GDPRRequest, DataConsentRecord,
    SecurityConfiguration, LoginAttempt
)
from app.schemas.security import (
    AuditLogCreate, AuditLogResponse, AuditLogFilter,
    SecurityAlertCreate, SecurityAlertResponse, SecurityAlertUpdate,
    APIKeyCreate, APIKeyResponse, APIKeyUpdate, APIKeyWithToken,
    GDPRRequestCreate, GDPRRequestResponse, GDPRRequestUpdate,
    DataConsentCreate, DataConsentResponse,
    SecurityConfigurationCreate, SecurityConfigurationResponse, SecurityConfigurationUpdate,
    LoginAttemptCreate, LoginAttemptResponse,
    SecurityDashboard, SecurityMetrics, ComplianceReport, SecurityRiskAssessment
)
from app.services.security_service import SecurityService

router = APIRouter()
security = HTTPBearer()


# Audit Logs
@router.post("/audit-logs", response_model=AuditLogResponse)
async def create_audit_log(
    audit_data: AuditLogCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create an audit log entry."""
    
    security_service = SecurityService(db)
    
    # Get request context
    request_context = {
        "ip_address": request.client.host,
        "user_agent": request.headers.get("User-Agent"),
        "method": request.method,
        "path": str(request.url.path),
        "session_id": getattr(request.state, "session_id", None)
    }
    
    audit_log = await security_service.create_audit_log(
        audit_data=audit_data,
        user_id=current_user.id,
        organization_id=getattr(current_user, "current_organization_id", None),
        request_context=request_context
    )
    
    return audit_log


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    organization_id: Optional[UUID] = Query(None),
    user_id: Optional[UUID] = Query(None),
    action_types: Optional[List[str]] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get audit logs with filtering."""
    
    security_service = SecurityService(db)
    
    # Convert string action types to enum
    action_type_enums = None
    if action_types:
        from app.models.security import AuditActionType
        try:
            action_type_enums = [AuditActionType(at) for at in action_types]
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid action type: {e}")
    
    audit_logs = await security_service.get_audit_logs(
        organization_id=organization_id,
        user_id=user_id,
        action_types=action_type_enums,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset
    )
    
    return audit_logs


# Security Alerts
@router.post("/alerts", response_model=SecurityAlertResponse)
async def create_security_alert(
    alert_data: SecurityAlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a security alert."""
    
    security_service = SecurityService(db)
    alert = await security_service.create_security_alert(alert_data)
    return alert


@router.get("/alerts", response_model=List[SecurityAlertResponse])
async def get_security_alerts(
    organization_id: Optional[UUID] = Query(None),
    severity: Optional[str] = Query(None),
    is_resolved: Optional[bool] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get security alerts."""
    
    from sqlalchemy.future import select
    from sqlalchemy import and_
    
    query = select(SecurityAlert)
    conditions = []
    
    if organization_id:
        conditions.append(SecurityAlert.organization_id == organization_id)
    if severity:
        conditions.append(SecurityAlert.severity == severity)
    if is_resolved is not None:
        conditions.append(SecurityAlert.is_resolved == is_resolved)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(SecurityAlert.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    return alerts


@router.patch("/alerts/{alert_id}", response_model=SecurityAlertResponse)
async def update_security_alert(
    alert_id: UUID,
    alert_update: SecurityAlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a security alert."""
    
    security_service = SecurityService(db)
    
    if alert_update.is_resolved:
        alert = await security_service.resolve_security_alert(
            alert_id=alert_id,
            resolved_by=current_user.id,
            resolution_notes=alert_update.resolution_notes
        )
    else:
        # Update other fields
        from sqlalchemy.future import select
        result = await db.execute(select(SecurityAlert).where(SecurityAlert.id == alert_id))
        alert = result.scalar_one_or_none()
        
        if not alert:
            raise HTTPException(status_code=404, detail="Security alert not found")
        
        if alert_update.resolution_notes is not None:
            alert.resolution_notes = alert_update.resolution_notes
        
        await db.commit()
        await db.refresh(alert)
    
    return alert


# API Keys
@router.post("/api-keys", response_model=APIKeyWithToken)
async def create_api_key(
    api_key_data: APIKeyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new API key."""
    
    security_service = SecurityService(db)
    api_key, token = await security_service.create_api_key(
        api_key_data=api_key_data,
        user_id=current_user.id
    )
    
    # Return API key with token (only shown once)
    api_key_dict = APIKeyResponse.from_orm(api_key).dict()
    api_key_dict["token"] = f"tfk_{token}"  # Add prefix for identification
    
    return APIKeyWithToken(**api_key_dict)


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def get_api_keys(
    organization_id: Optional[UUID] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's API keys."""
    
    from sqlalchemy.future import select
    from sqlalchemy import and_
    
    query = select(APIKey).where(APIKey.user_id == current_user.id)
    
    conditions = [APIKey.user_id == current_user.id]
    if organization_id:
        conditions.append(APIKey.organization_id == organization_id)
    if is_active is not None:
        conditions.append(APIKey.is_active == is_active)
    
    query = query.where(and_(*conditions)).order_by(APIKey.created_at.desc())
    
    result = await db.execute(query)
    api_keys = result.scalars().all()
    
    return api_keys


@router.patch("/api-keys/{api_key_id}", response_model=APIKeyResponse)
async def update_api_key(
    api_key_id: UUID,
    api_key_update: APIKeyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an API key."""
    
    from sqlalchemy.future import select
    
    result = await db.execute(
        select(APIKey).where(
            and_(APIKey.id == api_key_id, APIKey.user_id == current_user.id)
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Update fields
    update_data = api_key_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(api_key, field):
            setattr(api_key, field, value)
    
    await db.commit()
    await db.refresh(api_key)
    
    return api_key


@router.delete("/api-keys/{api_key_id}")
async def revoke_api_key(
    api_key_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revoke an API key."""
    
    security_service = SecurityService(db)
    
    # Verify ownership
    from sqlalchemy.future import select
    result = await db.execute(
        select(APIKey).where(
            and_(APIKey.id == api_key_id, APIKey.user_id == current_user.id)
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    await security_service.revoke_api_key(
        api_key_id=api_key_id,
        revoked_by=current_user.id
    )
    
    return {"message": "API key revoked successfully"}


# GDPR Compliance
@router.post("/gdpr/requests", response_model=GDPRRequestResponse)
async def create_gdpr_request(
    request_data: GDPRRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a GDPR request."""
    
    security_service = SecurityService(db)
    gdpr_request = await security_service.create_gdpr_request(
        request_data=request_data,
        user_id=current_user.id
    )
    
    return gdpr_request


@router.get("/gdpr/requests", response_model=List[GDPRRequestResponse])
async def get_gdpr_requests(
    request_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's GDPR requests."""
    
    from sqlalchemy.future import select
    from sqlalchemy import and_
    
    conditions = [GDPRRequest.user_id == current_user.id]
    
    if request_type:
        conditions.append(GDPRRequest.request_type == request_type)
    if status:
        conditions.append(GDPRRequest.status == status)
    
    query = select(GDPRRequest).where(and_(*conditions)).order_by(GDPRRequest.created_at.desc())
    
    result = await db.execute(query)
    requests = result.scalars().all()
    
    return requests


@router.get("/gdpr/export")
async def export_user_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export user's personal data (GDPR compliance)."""
    
    security_service = SecurityService(db)
    user_data = await security_service.export_user_data(user_id=current_user.id)
    
    return user_data


# Data Consent Management
@router.post("/consent", response_model=DataConsentResponse)
async def record_consent(
    consent_data: DataConsentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record user consent."""
    
    # Add request context
    consent_data.ip_address = request.client.host
    consent_data.user_agent = request.headers.get("User-Agent")
    
    consent_record = DataConsentRecord(
        user_id=current_user.id,
        **consent_data.dict()
    )
    
    db.add(consent_record)
    await db.commit()
    await db.refresh(consent_record)
    
    return consent_record


@router.get("/consent", response_model=List[DataConsentResponse])
async def get_consent_records(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's consent records."""
    
    from sqlalchemy.future import select
    
    result = await db.execute(
        select(DataConsentRecord).where(DataConsentRecord.user_id == current_user.id)
        .order_by(DataConsentRecord.created_at.desc())
    )
    records = result.scalars().all()
    
    return records


# Security Dashboard
@router.get("/dashboard", response_model=SecurityDashboard)
async def get_security_dashboard(
    organization_id: Optional[UUID] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get security dashboard data."""
    
    security_service = SecurityService(db)
    
    # Get metrics
    metrics = await security_service.get_security_metrics(
        organization_id=organization_id,
        days=days
    )
    
    # Get recent alerts
    from sqlalchemy.future import select
    recent_alerts_query = select(SecurityAlert).where(
        SecurityAlert.is_resolved == False
    ).order_by(SecurityAlert.created_at.desc()).limit(10)
    
    if organization_id:
        recent_alerts_query = recent_alerts_query.where(
            SecurityAlert.organization_id == organization_id
        )
    
    alerts_result = await db.execute(recent_alerts_query)
    recent_alerts = alerts_result.scalars().all()
    
    # Get recent failed logins
    failed_logins_query = select(LoginAttempt).where(
        and_(
            LoginAttempt.success == False,
            LoginAttempt.created_at >= datetime.utcnow() - timedelta(days=7)
        )
    ).order_by(LoginAttempt.created_at.desc()).limit(10)
    
    if organization_id:
        failed_logins_query = failed_logins_query.where(
            LoginAttempt.organization_id == organization_id
        )
    
    logins_result = await db.execute(failed_logins_query)
    recent_failed_logins = logins_result.scalars().all()
    
    # Get recent audit logs
    audit_logs_query = select(AuditLog).where(
        AuditLog.created_at >= datetime.utcnow() - timedelta(days=1)
    ).order_by(AuditLog.created_at.desc()).limit(20)
    
    if organization_id:
        audit_logs_query = audit_logs_query.where(
            AuditLog.organization_id == organization_id
        )
    
    audit_result = await db.execute(audit_logs_query)
    recent_audit_logs = audit_result.scalars().all()
    
    return SecurityDashboard(
        metrics=metrics,
        recent_alerts=recent_alerts,
        recent_failed_logins=recent_failed_logins,
        recent_audit_logs=recent_audit_logs
    )


@router.get("/risk-assessment", response_model=SecurityRiskAssessment)
async def get_security_risk_assessment(
    organization_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get security risk assessment."""
    
    security_service = SecurityService(db)
    assessment = await security_service.assess_security_risk(organization_id)
    
    return assessment


# Login Attempt Tracking
@router.post("/login-attempts", response_model=LoginAttemptResponse)
async def record_login_attempt(
    attempt_data: LoginAttemptCreate,
    db: AsyncSession = Depends(get_db)
):
    """Record a login attempt (used by auth system)."""
    
    security_service = SecurityService(db)
    attempt = await security_service.record_login_attempt(attempt_data)
    
    return attempt


@router.get("/login-attempts", response_model=List[LoginAttemptResponse])
async def get_login_attempts(
    username: Optional[str] = Query(None),
    ip_address: Optional[str] = Query(None),
    success: Optional[bool] = Query(None),
    is_suspicious: Optional[bool] = Query(None),
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get login attempts with filtering."""
    
    from sqlalchemy.future import select
    from sqlalchemy import and_
    
    conditions = [
        LoginAttempt.created_at >= datetime.utcnow() - timedelta(hours=hours)
    ]
    
    if username:
        conditions.append(LoginAttempt.username == username)
    if ip_address:
        conditions.append(LoginAttempt.ip_address == ip_address)
    if success is not None:
        conditions.append(LoginAttempt.success == success)
    if is_suspicious is not None:
        conditions.append(LoginAttempt.is_suspicious == is_suspicious)
    
    query = select(LoginAttempt).where(and_(*conditions)).order_by(
        LoginAttempt.created_at.desc()
    ).offset(offset).limit(limit)
    
    result = await db.execute(query)
    attempts = result.scalars().all()
    
    return attempts


# Security Configuration
@router.post("/configurations", response_model=SecurityConfigurationResponse)
async def create_security_configuration(
    config_data: SecurityConfigurationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create security configuration."""
    
    config = SecurityConfiguration(
        organization_id=config_data.organization_id,
        config_type=config_data.config_type,
        settings=config_data.settings,
        is_active=config_data.is_active,
        created_by=current_user.id
    )
    
    db.add(config)
    await db.commit()
    await db.refresh(config)
    
    return config


@router.get("/configurations", response_model=List[SecurityConfigurationResponse])
async def get_security_configurations(
    organization_id: Optional[UUID] = Query(None),
    config_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get security configurations."""
    
    from sqlalchemy.future import select
    from sqlalchemy import and_
    
    conditions = []
    
    if organization_id:
        conditions.append(SecurityConfiguration.organization_id == organization_id)
    if config_type:
        conditions.append(SecurityConfiguration.config_type == config_type)
    if is_active is not None:
        conditions.append(SecurityConfiguration.is_active == is_active)
    
    query = select(SecurityConfiguration)
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(SecurityConfiguration.created_at.desc())
    
    result = await db.execute(query)
    configurations = result.scalars().all()
    
    return configurations