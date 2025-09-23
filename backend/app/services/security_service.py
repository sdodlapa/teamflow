"""Security and compliance service for TeamFlow."""

import hashlib
import secrets
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID
import json
import ipaddress

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import selectinload

from app.models.security import (
    AuditLog, SecurityAlert, APIKey, GDPRRequest, DataConsentRecord,
    SecurityConfiguration, LoginAttempt, AuditActionType, SecurityRiskLevel
)
from app.models.user import User
from app.models.organization import Organization
from app.schemas.security import (
    AuditLogCreate, SecurityAlertCreate, APIKeyCreate, GDPRRequestCreate,
    DataConsentCreate, SecurityConfigurationCreate, LoginAttemptCreate,
    SecurityMetrics, SecurityDashboard, ComplianceReport, SecurityRiskAssessment,
    RiskFactor
)


class SecurityService:
    """Comprehensive security and compliance service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Audit Logging
    async def create_audit_log(
        self,
        audit_data: AuditLogCreate,
        user_id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None,
        request_context: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Create an audit log entry."""
        
        # Extract request context if provided
        if request_context:
            audit_data.ip_address = request_context.get("ip_address")
            audit_data.user_agent = request_context.get("user_agent")
            audit_data.request_method = request_context.get("method")
            audit_data.request_path = request_context.get("path")
            audit_data.session_id = request_context.get("session_id")
        
        # Set user and organization context
        if user_id:
            audit_data.user_id = user_id
        if organization_id:
            audit_data.organization_id = organization_id
        
        # Create audit log
        audit_log = AuditLog(**audit_data.dict())
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        
        # Check for suspicious activity
        await self._check_suspicious_activity(audit_log)
        
        return audit_log
    
    async def get_audit_logs(
        self,
        organization_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        action_types: Optional[List[AuditActionType]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        risk_levels: Optional[List[SecurityRiskLevel]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Get audit logs with filtering."""
        
        query = select(AuditLog)
        
        # Apply filters
        conditions = []
        if organization_id:
            conditions.append(AuditLog.organization_id == organization_id)
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        if action_types:
            conditions.append(AuditLog.action_type.in_([at.value for at in action_types]))
        if date_from:
            conditions.append(AuditLog.created_at >= date_from)
        if date_to:
            conditions.append(AuditLog.created_at <= date_to)
        if risk_levels:
            conditions.append(AuditLog.risk_level.in_([rl.value for rl in risk_levels]))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(desc(AuditLog.created_at)).offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    # Security Alerts
    async def create_security_alert(
        self,
        alert_data: SecurityAlertCreate,
        auto_resolve: bool = False
    ) -> SecurityAlert:
        """Create a security alert."""
        
        alert = SecurityAlert(**alert_data.dict())
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        
        # Log the alert creation
        await self.create_audit_log(
            AuditLogCreate(
                action_type=AuditActionType.SECURITY_VIOLATION,
                resource_type="security_alert",
                resource_id=str(alert.id),
                description=f"Security alert created: {alert.title}",
                risk_level=SecurityRiskLevel(alert.severity),
                extra_data={"alert_type": alert.alert_type}
            ),
            user_id=alert.user_id,
            organization_id=alert.organization_id
        )
        
        return alert
    
    async def resolve_security_alert(
        self,
        alert_id: UUID,
        resolved_by: UUID,
        resolution_notes: Optional[str] = None
    ) -> SecurityAlert:
        """Resolve a security alert."""
        
        result = await self.db.execute(
            select(SecurityAlert).where(SecurityAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        
        if not alert:
            raise ValueError("Security alert not found")
        
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = resolved_by
        alert.resolution_notes = resolution_notes
        
        await self.db.commit()
        await self.db.refresh(alert)
        
        # Log the resolution
        await self.create_audit_log(
            AuditLogCreate(
                action_type=AuditActionType.SECURITY_VIOLATION,
                resource_type="security_alert",
                resource_id=str(alert.id),
                description=f"Security alert resolved: {alert.title}",
                risk_level=SecurityRiskLevel.LOW,
                extra_data={"resolution_notes": resolution_notes}
            ),
            user_id=resolved_by,
            organization_id=alert.organization_id
        )
        
        return alert
    
    # API Key Management
    async def create_api_key(
        self,
        api_key_data: APIKeyCreate,
        user_id: UUID
    ) -> Tuple[APIKey, str]:
        """Create a new API key and return it with the token."""
        
        # Generate API key
        key_bytes = secrets.token_bytes(32)
        key_token = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(key_token.encode()).hexdigest()
        prefix = key_token[:8]
        
        # Create API key record
        api_key = APIKey(
            name=api_key_data.name,
            description=api_key_data.description,
            key_hash=key_hash,
            prefix=prefix,
            user_id=user_id,
            organization_id=api_key_data.organization_id,
            scopes=[scope.value for scope in api_key_data.scopes],
            allowed_ips=api_key_data.allowed_ips,
            rate_limit=api_key_data.rate_limit,
            expires_at=api_key_data.expires_at
        )
        
        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
        
        # Log API key creation
        await self.create_audit_log(
            AuditLogCreate(
                action_type=AuditActionType.API_KEY_CREATED,
                resource_type="api_key",
                resource_id=str(api_key.id),
                description=f"API key created: {api_key.name}",
                risk_level=SecurityRiskLevel.MEDIUM,
                extra_data={"scopes": api_key.scopes, "prefix": prefix}
            ),
            user_id=user_id,
            organization_id=api_key_data.organization_id
        )
        
        return api_key, key_token
    
    async def validate_api_key(
        self,
        token: str,
        required_scopes: Optional[List[str]] = None,
        ip_address: Optional[str] = None
    ) -> Optional[APIKey]:
        """Validate an API key and check permissions."""
        
        key_hash = hashlib.sha256(token.encode()).hexdigest()
        
        result = await self.db.execute(
            select(APIKey).where(
                and_(
                    APIKey.key_hash == key_hash,
                    APIKey.is_active == True
                )
            ).options(
                selectinload(APIKey.user),
                selectinload(APIKey.organization)
            )
        )
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            return None
        
        # Check expiration
        if api_key.is_expired:
            return None
        
        # Check IP restrictions
        if api_key.allowed_ips and ip_address:
            allowed = False
            for allowed_ip in api_key.allowed_ips:
                try:
                    if ipaddress.ip_address(ip_address) in ipaddress.ip_network(allowed_ip, strict=False):
                        allowed = True
                        break
                except ValueError:
                    continue
            if not allowed:
                return None
        
        # Check scopes
        if required_scopes:
            api_key_scopes = api_key.scopes if isinstance(api_key.scopes, list) else [api_key.scopes]
            if not any(scope in api_key_scopes for scope in required_scopes):
                return None
        
        # Update usage
        api_key.last_used_at = datetime.utcnow()
        api_key.usage_count += 1
        await self.db.commit()
        
        return api_key
    
    async def revoke_api_key(self, api_key_id: UUID, revoked_by: UUID) -> APIKey:
        """Revoke an API key."""
        
        result = await self.db.execute(
            select(APIKey).where(APIKey.id == api_key_id)
        )
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            raise ValueError("API key not found")
        
        api_key.is_active = False
        await self.db.commit()
        await self.db.refresh(api_key)
        
        # Log API key revocation
        await self.create_audit_log(
            AuditLogCreate(
                action_type=AuditActionType.API_KEY_REVOKED,
                resource_type="api_key",
                resource_id=str(api_key.id),
                description=f"API key revoked: {api_key.name}",
                risk_level=SecurityRiskLevel.MEDIUM,
                extra_data={"prefix": api_key.prefix}
            ),
            user_id=revoked_by,
            organization_id=api_key.organization_id
        )
        
        return api_key
    
    # GDPR Compliance
    async def create_gdpr_request(
        self,
        request_data: GDPRRequestCreate,
        user_id: UUID
    ) -> GDPRRequest:
        """Create a GDPR request."""
        
        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        
        gdpr_request = GDPRRequest(
            request_type=request_data.request_type,
            description=request_data.description,
            user_id=user_id,
            organization_id=request_data.organization_id,
            data_categories=request_data.data_categories,
            processing_purposes=[p.value for p in request_data.processing_purposes] if request_data.processing_purposes else None,
            legal_basis=request_data.legal_basis,
            verification_token=verification_token
        )
        
        self.db.add(gdpr_request)
        await self.db.commit()
        await self.db.refresh(gdpr_request)
        
        # Log GDPR request
        await self.create_audit_log(
            AuditLogCreate(
                action_type=AuditActionType.DATA_EXPORT_REQUEST if "export" in request_data.request_type else AuditActionType.DATA_DELETION_REQUEST,
                resource_type="gdpr_request",
                resource_id=str(gdpr_request.id),
                description=f"GDPR {request_data.request_type} request created",
                risk_level=SecurityRiskLevel.MEDIUM,
                extra_data={"request_type": request_data.request_type}
            ),
            user_id=user_id,
            organization_id=request_data.organization_id
        )
        
        return gdpr_request
    
    async def export_user_data(self, user_id: UUID) -> Dict[str, Any]:
        """Export all user data for GDPR compliance."""
        
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id).options(
                selectinload(User.organization_memberships),
                selectinload(User.project_memberships),
                selectinload(User.assigned_tasks),
                selectinload(User.task_comments),
                selectinload(User.audit_logs),
                selectinload(User.api_keys),
                selectinload(User.consent_records)
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Compile user data
        user_data = {
            "personal_information": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "bio": user.bio,
                "avatar_url": user.avatar_url,
                "role": user.role.value,
                "status": user.status.value,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
            },
            "organization_memberships": [
                {
                    "organization_id": str(membership.organization_id),
                    "role": membership.role.value,
                    "joined_at": membership.joined_at.isoformat()
                }
                for membership in user.organization_memberships
            ],
            "project_memberships": [
                {
                    "project_id": str(membership.project_id),
                    "role": membership.role.value,
                    "joined_at": membership.joined_at.isoformat()
                }
                for membership in user.project_memberships
            ],
            "tasks": [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                for task in user.assigned_tasks
            ],
            "comments": [
                {
                    "id": str(comment.id),
                    "content": comment.content,
                    "task_id": str(comment.task_id),
                    "created_at": comment.created_at.isoformat()
                }
                for comment in user.task_comments
            ],
            "api_keys": [
                {
                    "id": str(key.id),
                    "name": key.name,
                    "description": key.description,
                    "scopes": key.scopes,
                    "created_at": key.created_at.isoformat(),
                    "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None
                }
                for key in user.api_keys
            ],
            "consent_records": [
                {
                    "id": str(record.id),
                    "purpose": record.purpose,
                    "consent_given": record.consent_given,
                    "created_at": record.created_at.isoformat(),
                    "expires_at": record.expires_at.isoformat() if record.expires_at else None
                }
                for record in user.consent_records
            ],
            "export_metadata": {
                "export_date": datetime.utcnow().isoformat(),
                "export_version": "1.0",
                "total_records": sum([
                    len(user.organization_memberships),
                    len(user.project_memberships),
                    len(user.assigned_tasks),
                    len(user.task_comments),
                    len(user.api_keys),
                    len(user.consent_records)
                ])
            }
        }
        
        return user_data
    
    # Login Attempt Tracking
    async def record_login_attempt(
        self,
        attempt_data: LoginAttemptCreate
    ) -> LoginAttempt:
        """Record a login attempt."""
        
        # Calculate risk score
        risk_score = await self._calculate_login_risk(attempt_data)
        attempt_data.risk_score = risk_score
        attempt_data.is_suspicious = risk_score > 50
        
        login_attempt = LoginAttempt(**attempt_data.dict())
        self.db.add(login_attempt)
        await self.db.commit()
        await self.db.refresh(login_attempt)
        
        # Create alert for suspicious activity
        if login_attempt.is_suspicious:
            await self.create_security_alert(
                SecurityAlertCreate(
                    alert_type="suspicious_login",
                    severity=SecurityRiskLevel.HIGH,
                    title=f"Suspicious login attempt for {attempt_data.username}",
                    description=f"High-risk login attempt detected from {attempt_data.ip_address}",
                    user_id=attempt_data.user_id,
                    organization_id=attempt_data.organization_id,
                    ip_address=attempt_data.ip_address,
                    alert_data={"risk_score": risk_score, "failure_reason": attempt_data.failure_reason}
                )
            )
        
        return login_attempt
    
    # Security Dashboard
    async def get_security_metrics(
        self,
        organization_id: Optional[UUID] = None,
        days: int = 30
    ) -> SecurityMetrics:
        """Get security metrics for dashboard."""
        
        since_date = datetime.utcnow() - timedelta(days=days)
        conditions = [LoginAttempt.created_at >= since_date]
        
        if organization_id:
            conditions.append(LoginAttempt.organization_id == organization_id)
        
        # Login attempts
        total_logins_result = await self.db.execute(
            select(func.count(LoginAttempt.id)).where(and_(*conditions))
        )
        total_login_attempts = total_logins_result.scalar()
        
        failed_logins_result = await self.db.execute(
            select(func.count(LoginAttempt.id)).where(
                and_(LoginAttempt.success == False, *conditions)
            )
        )
        failed_login_attempts = failed_logins_result.scalar()
        
        # Security alerts
        alert_conditions = [SecurityAlert.created_at >= since_date]
        if organization_id:
            alert_conditions.append(SecurityAlert.organization_id == organization_id)
        
        active_alerts_result = await self.db.execute(
            select(func.count(SecurityAlert.id)).where(
                and_(SecurityAlert.is_resolved == False, *alert_conditions)
            )
        )
        active_security_alerts = active_alerts_result.scalar()
        
        # Suspicious activities
        suspicious_result = await self.db.execute(
            select(func.count(LoginAttempt.id)).where(
                and_(LoginAttempt.is_suspicious == True, *conditions)
            )
        )
        suspicious_activities = suspicious_result.scalar()
        
        # Other metrics would be calculated similarly...
        
        return SecurityMetrics(
            total_login_attempts=total_login_attempts or 0,
            failed_login_attempts=failed_login_attempts or 0,
            suspicious_activities=suspicious_activities or 0,
            active_security_alerts=active_security_alerts or 0,
            gdpr_requests_pending=0,  # Would calculate from GDPR requests
            api_keys_active=0,  # Would calculate from API keys
            audit_logs_today=0  # Would calculate from audit logs
        )
    
    # Security Risk Assessment
    async def assess_security_risk(
        self,
        organization_id: Optional[UUID] = None
    ) -> SecurityRiskAssessment:
        """Perform security risk assessment."""
        
        risk_factors = []
        
        # Check for recent failed logins
        failed_logins = await self.db.execute(
            select(func.count(LoginAttempt.id)).where(
                and_(
                    LoginAttempt.success == False,
                    LoginAttempt.created_at >= datetime.utcnow() - timedelta(days=1),
                    LoginAttempt.organization_id == organization_id if organization_id else True
                )
            )
        )
        failed_count = failed_logins.scalar()
        
        if failed_count > 10:
            risk_factors.append(RiskFactor(
                factor="High failed login attempts",
                risk_level=SecurityRiskLevel.HIGH,
                description=f"{failed_count} failed login attempts in the last 24 hours",
                mitigation="Consider implementing account lockout policies"
            ))
        
        # Check for unresolved security alerts
        unresolved_alerts = await self.db.execute(
            select(func.count(SecurityAlert.id)).where(
                and_(
                    SecurityAlert.is_resolved == False,
                    SecurityAlert.organization_id == organization_id if organization_id else True
                )
            )
        )
        alert_count = unresolved_alerts.scalar()
        
        if alert_count > 0:
            risk_factors.append(RiskFactor(
                factor="Unresolved security alerts",
                risk_level=SecurityRiskLevel.MEDIUM,
                description=f"{alert_count} unresolved security alerts",
                mitigation="Review and resolve pending security alerts"
            ))
        
        # Calculate overall risk
        if any(rf.risk_level == SecurityRiskLevel.CRITICAL for rf in risk_factors):
            overall_risk = SecurityRiskLevel.CRITICAL
        elif any(rf.risk_level == SecurityRiskLevel.HIGH for rf in risk_factors):
            overall_risk = SecurityRiskLevel.HIGH
        elif any(rf.risk_level == SecurityRiskLevel.MEDIUM for rf in risk_factors):
            overall_risk = SecurityRiskLevel.MEDIUM
        else:
            overall_risk = SecurityRiskLevel.LOW
        
        recommendations = [
            "Regular security training for users",
            "Enable two-factor authentication",
            "Review API key permissions regularly",
            "Monitor audit logs for suspicious activity"
        ]
        
        return SecurityRiskAssessment(
            overall_risk=overall_risk,
            risk_factors=risk_factors,
            recommendations=recommendations,
            last_assessment=datetime.utcnow()
        )
    
    # Private helper methods
    async def _check_suspicious_activity(self, audit_log: AuditLog):
        """Check if audit log indicates suspicious activity."""
        
        # Example suspicious activity detection
        if audit_log.action_type in [AuditActionType.FAILED_LOGIN, AuditActionType.PERMISSION_REVOKED]:
            # Check for multiple failed attempts from same IP
            recent_failures = await self.db.execute(
                select(func.count(AuditLog.id)).where(
                    and_(
                        AuditLog.action_type == AuditActionType.FAILED_LOGIN,
                        AuditLog.ip_address == audit_log.ip_address,
                        AuditLog.created_at >= datetime.utcnow() - timedelta(minutes=15)
                    )
                )
            )
            
            if recent_failures.scalar() > 5:
                await self.create_security_alert(
                    SecurityAlertCreate(
                        alert_type="multiple_failed_logins",
                        severity=SecurityRiskLevel.HIGH,
                        title=f"Multiple failed login attempts from {audit_log.ip_address}",
                        description="Potential brute force attack detected",
                        ip_address=audit_log.ip_address,
                        alert_data={"audit_log_id": str(audit_log.id)}
                    )
                )
    
    async def _calculate_login_risk(self, attempt_data: LoginAttemptCreate) -> int:
        """Calculate risk score for login attempt."""
        
        risk_score = 0
        
        # Failed login increases risk
        if not attempt_data.success:
            risk_score += 20
        
        # Check for recent failed attempts from same IP
        recent_failures = await self.db.execute(
            select(func.count(LoginAttempt.id)).where(
                and_(
                    LoginAttempt.ip_address == attempt_data.ip_address,
                    LoginAttempt.success == False,
                    LoginAttempt.created_at >= datetime.utcnow() - timedelta(hours=1)
                )
            )
        )
        
        failure_count = recent_failures.scalar()
        risk_score += min(failure_count * 10, 50)  # Max 50 points for failures
        
        # Check for unusual timing (e.g., outside business hours)
        current_hour = datetime.utcnow().hour
        if current_hour < 6 or current_hour > 22:
            risk_score += 15
        
        return min(risk_score, 100)  # Max risk score of 100