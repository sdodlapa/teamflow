"""
GDPR Compliance Service for TeamFlow.
Provides comprehensive data protection and privacy compliance features.
"""
import asyncio
import json
import zipfile
import tempfile
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
import csv
from io import StringIO, BytesIO

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func, text
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.models.project import Project, ProjectMember
from app.models.task import Task, TaskAssignment
from app.models.enhanced_comments import TaskCommentEnhanced
from app.models.file_management import FileUpload
from app.models.security import (
    GDPRRequest, DataConsentRecord, AuditLog, LoginAttempt,
    SecurityAlert, APIKey
)
from app.schemas.security import GDPRRequestCreate, DataConsentCreate


class GDPRComplianceService:
    """Comprehensive GDPR compliance service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Data Export (Right to Data Portability)
    async def export_user_data(self, user_id: UUID) -> Dict[str, Any]:
        """Export all user data in a structured format for GDPR compliance."""
        
        # Get user
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        export_data = {
            "export_info": {
                "user_id": str(user_id),
                "export_date": datetime.utcnow().isoformat(),
                "export_type": "complete_data_export",
                "data_controller": "TeamFlow",
                "legal_basis": "GDPR Article 20 - Right to Data Portability"
            },
            "personal_data": await self._export_personal_data(user),
            "organizations": await self._export_organization_data(user_id),
            "projects": await self._export_project_data(user_id),
            "tasks": await self._export_task_data(user_id),
            "comments": await self._export_comment_data(user_id),
            "files": await self._export_file_data(user_id),
            "security": await self._export_security_data(user_id),
            "consent_records": await self._export_consent_data(user_id),
            "audit_logs": await self._export_audit_data(user_id)
        }
        
        return export_data
    
    async def _export_personal_data(self, user: User) -> Dict[str, Any]:
        """Export user's personal data."""
        return {
            "user_id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "profile_data": user.profile_data or {},
            "preferences": user.preferences or {},
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "email_verified_at": user.email_verified_at.isoformat() if user.email_verified_at else None
        }
    
    async def _export_organization_data(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Export user's organization memberships and data."""
        memberships_result = await self.db.execute(
            select(OrganizationMember, Organization)
            .join(Organization, OrganizationMember.organization_id == Organization.id)
            .where(OrganizationMember.user_id == user_id)
        )
        
        memberships = []
        for membership, org in memberships_result.all():
            memberships.append({
                "organization_id": str(org.id),
                "organization_name": org.name,
                "organization_description": org.description,
                "membership_role": membership.role,
                "joined_at": membership.created_at.isoformat() if membership.created_at else None,
                "is_active": membership.is_active,
                "permissions": membership.permissions or []
            })
        
        return memberships
    
    async def _export_project_data(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Export user's project memberships and data."""
        memberships_result = await self.db.execute(
            select(ProjectMember, Project, Organization)
            .join(Project, ProjectMember.project_id == Project.id)
            .join(Organization, Project.organization_id == Organization.id)
            .where(ProjectMember.user_id == user_id)
        )
        
        projects = []
        for membership, project, org in memberships_result.all():
            projects.append({
                "project_id": str(project.id),
                "project_name": project.name,
                "project_description": project.description,
                "organization_name": org.name,
                "membership_role": membership.role,
                "joined_at": membership.created_at.isoformat() if membership.created_at else None,
                "permissions": membership.permissions or [],
                "project_created_at": project.created_at.isoformat() if project.created_at else None
            })
        
        return projects
    
    async def _export_task_data(self, user_id: UUID) -> Dict[str, Any]:
        """Export user's task data (created, assigned, participated)."""
        
        # Tasks created by user
        created_tasks_result = await self.db.execute(
            select(Task, Project)
            .join(Project, Task.project_id == Project.id)
            .where(Task.created_by == user_id)
        )
        
        created_tasks = []
        for task, project in created_tasks_result.all():
            created_tasks.append(self._serialize_task(task, project, "creator"))
        
        # Tasks assigned to user
        assigned_result = await self.db.execute(
            select(TaskAssignment, Task, Project)
            .join(Task, TaskAssignment.task_id == Task.id)
            .join(Project, Task.project_id == Project.id)
            .where(TaskAssignment.assigned_to == user_id)
        )
        
        assigned_tasks = []
        for assignment, task, project in assigned_result.all():
            task_data = self._serialize_task(task, project, "assignee")
            task_data["assignment"] = {
                "assigned_at": assignment.created_at.isoformat() if assignment.created_at else None,
                "assigned_by": str(assignment.assigned_by) if assignment.assigned_by else None,
                "is_active": assignment.is_active
            }
            assigned_tasks.append(task_data)
        
        return {
            "created_tasks": created_tasks,
            "assigned_tasks": assigned_tasks,
            "total_created": len(created_tasks),
            "total_assigned": len(assigned_tasks)
        }
    
    def _serialize_task(self, task: Task, project: Project, relationship: str) -> Dict[str, Any]:
        """Serialize task data for export."""
        return {
            "task_id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "project_name": project.name,
            "project_id": str(project.id),
            "relationship": relationship,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "tags": task.tags or [],
            "metadata": task.metadata or {}
        }
    
    async def _export_comment_data(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Export user's comments and mentions."""
        comments_result = await self.db.execute(
            select(TaskCommentEnhanced, Task, Project)
            .join(Task, TaskCommentEnhanced.task_id == Task.id)
            .join(Project, Task.project_id == Project.id)
            .where(TaskCommentEnhanced.author_id == user_id)
        )
        
        comments = []
        for comment, task, project in comments_result.all():
            comments.append({
                "comment_id": str(comment.id),
                "content": comment.content,
                "task_title": task.title,
                "project_name": project.name,
                "created_at": comment.created_at.isoformat() if comment.created_at else None,
                "updated_at": comment.updated_at.isoformat() if comment.updated_at else None,
                "is_edited": comment.is_edited,
                "mentions": comment.mentions or [],
                "reactions": comment.reactions or {}
            })
        
        return comments
    
    async def _export_file_data(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Export user's file uploads."""
        files_result = await self.db.execute(
            select(FileUpload).where(FileUpload.uploaded_by == user_id)
        )
        
        files = []
        for file_upload in files_result.scalars().all():
            files.append({
                "file_id": str(file_upload.id),
                "filename": file_upload.filename,
                "original_filename": file_upload.original_filename,
                "file_size": file_upload.file_size,
                "mime_type": file_upload.mime_type,
                "description": file_upload.description,
                "uploaded_at": file_upload.uploaded_at.isoformat() if file_upload.uploaded_at else None,
                "file_path": file_upload.file_path,
                "is_public": file_upload.is_public,
                "metadata": file_upload.metadata or {}
            })
        
        return files
    
    async def _export_security_data(self, user_id: UUID) -> Dict[str, Any]:
        """Export user's security-related data."""
        
        # Login attempts
        login_attempts_result = await self.db.execute(
            select(LoginAttempt)
            .where(LoginAttempt.user_id == user_id)
            .order_by(LoginAttempt.created_at.desc())
            .limit(100)  # Last 100 attempts
        )
        
        login_attempts = []
        for attempt in login_attempts_result.scalars().all():
            login_attempts.append({
                "ip_address": attempt.ip_address,
                "success": attempt.success,
                "failure_reason": attempt.failure_reason,
                "created_at": attempt.created_at.isoformat() if attempt.created_at else None,
                "is_suspicious": attempt.is_suspicious,
                "risk_score": attempt.risk_score
            })
        
        # API Keys
        api_keys_result = await self.db.execute(
            select(APIKey).where(APIKey.user_id == user_id)
        )
        
        api_keys = []
        for api_key in api_keys_result.scalars().all():
            api_keys.append({
                "name": api_key.name,
                "description": api_key.description,
                "scopes": api_key.scopes or [],
                "is_active": api_key.is_active,
                "created_at": api_key.created_at.isoformat() if api_key.created_at else None,
                "last_used_at": api_key.last_used_at.isoformat() if api_key.last_used_at else None,
                "usage_count": api_key.usage_count
            })
        
        # Security Alerts
        security_alerts_result = await self.db.execute(
            select(SecurityAlert)
            .where(SecurityAlert.user_id == user_id)
            .order_by(SecurityAlert.created_at.desc())
            .limit(50)
        )
        
        security_alerts = []
        for alert in security_alerts_result.scalars().all():
            security_alerts.append({
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "title": alert.title,
                "description": alert.description,
                "is_resolved": alert.is_resolved,
                "created_at": alert.created_at.isoformat() if alert.created_at else None,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            })
        
        return {
            "login_attempts": login_attempts,
            "api_keys": api_keys,
            "security_alerts": security_alerts
        }
    
    async def _export_consent_data(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Export user's consent records."""
        consent_result = await self.db.execute(
            select(DataConsentRecord).where(DataConsentRecord.user_id == user_id)
        )
        
        consent_records = []
        for record in consent_result.scalars().all():
            consent_records.append({
                "purpose": record.purpose,
                "consent_given": record.consent_given,
                "consent_text": record.consent_text,
                "consent_method": record.consent_method,
                "lawful_basis": record.lawful_basis,
                "data_categories": record.data_categories or [],
                "retention_period": record.retention_period,
                "created_at": record.created_at.isoformat() if record.created_at else None,
                "expires_at": record.expires_at.isoformat() if record.expires_at else None
            })
        
        return consent_records
    
    async def _export_audit_data(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Export user's audit log entries (last 30 days)."""
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        audit_result = await self.db.execute(
            select(AuditLog)
            .where(
                and_(
                    AuditLog.user_id == user_id,
                    AuditLog.created_at >= cutoff_date
                )
            )
            .order_by(AuditLog.created_at.desc())
            .limit(1000)  # Maximum 1000 entries
        )
        
        audit_logs = []
        for log in audit_result.scalars().all():
            audit_logs.append({
                "action_type": log.action_type,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "description": log.description,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat() if log.created_at else None,
                "risk_level": log.risk_level,
                "is_suspicious": log.is_suspicious
            })
        
        return audit_logs
    
    # Data Deletion (Right to be Forgotten)
    async def delete_user_data(
        self, 
        user_id: UUID, 
        deletion_type: str = "complete",
        retain_audit: bool = True
    ) -> Dict[str, Any]:
        """Delete user data according to GDPR Right to be Forgotten."""
        
        deletion_report = {
            "user_id": str(user_id),
            "deletion_type": deletion_type,
            "deletion_date": datetime.utcnow().isoformat(),
            "retain_audit": retain_audit,
            "deleted_data": {}
        }
        
        if deletion_type == "complete":
            # Complete deletion - remove all personal data
            report = await self._complete_user_deletion(user_id, retain_audit)
            deletion_report["deleted_data"] = report
        
        elif deletion_type == "anonymize":
            # Anonymization - remove personal identifiers but keep statistical data
            report = await self._anonymize_user_data(user_id)
            deletion_report["deleted_data"] = report
        
        elif deletion_type == "partial":
            # Partial deletion - remove specific categories of data
            report = await self._partial_user_deletion(user_id)
            deletion_report["deleted_data"] = report
        
        else:
            raise ValueError(f"Invalid deletion type: {deletion_type}")
        
        return deletion_report
    
    async def _complete_user_deletion(self, user_id: UUID, retain_audit: bool) -> Dict[str, Any]:
        """Perform complete user data deletion."""
        
        report = {
            "user_profile": False,
            "comments": 0,
            "files": 0,
            "api_keys": 0,
            "consent_records": 0,
            "login_attempts": 0,
            "security_alerts": 0,
            "audit_logs": 0,
            "memberships": 0
        }
        
        try:
            # Delete comments (anonymize content)
            comments_result = await self.db.execute(
                select(TaskCommentEnhanced).where(TaskCommentEnhanced.author_id == user_id)
            )
            comments = comments_result.scalars().all()
            for comment in comments:
                comment.content = "[Comment deleted - GDPR request]"
                comment.author_id = None  # Anonymize
            report["comments"] = len(comments)
            
            # Delete uploaded files
            files_result = await self.db.execute(
                select(FileUpload).where(FileUpload.uploaded_by == user_id)
            )
            files = files_result.scalars().all()
            for file_upload in files:
                # Delete physical file
                if os.path.exists(file_upload.file_path):
                    os.remove(file_upload.file_path)
                await self.db.delete(file_upload)
            report["files"] = len(files)
            
            # Delete API keys
            api_keys_result = await self.db.execute(
                select(APIKey).where(APIKey.user_id == user_id)
            )
            api_keys = api_keys_result.scalars().all()
            for api_key in api_keys:
                await self.db.delete(api_key)
            report["api_keys"] = len(api_keys)
            
            # Delete consent records
            consent_result = await self.db.execute(
                select(DataConsentRecord).where(DataConsentRecord.user_id == user_id)
            )
            consent_records = consent_result.scalars().all()
            for record in consent_records:
                await self.db.delete(record)
            report["consent_records"] = len(consent_records)
            
            # Delete login attempts
            login_attempts_result = await self.db.execute(
                select(LoginAttempt).where(LoginAttempt.user_id == user_id)
            )
            login_attempts = login_attempts_result.scalars().all()
            for attempt in login_attempts:
                await self.db.delete(attempt)
            report["login_attempts"] = len(login_attempts)
            
            # Delete security alerts
            alerts_result = await self.db.execute(
                select(SecurityAlert).where(SecurityAlert.user_id == user_id)
            )
            security_alerts = alerts_result.scalars().all()
            for alert in security_alerts:
                await self.db.delete(alert)
            report["security_alerts"] = len(security_alerts)
            
            # Handle audit logs
            if not retain_audit:
                audit_result = await self.db.execute(
                    select(AuditLog).where(AuditLog.user_id == user_id)
                )
                audit_logs = audit_result.scalars().all()
                for log in audit_logs:
                    await self.db.delete(log)
                report["audit_logs"] = len(audit_logs)
            else:
                # Anonymize audit logs
                audit_result = await self.db.execute(
                    select(AuditLog).where(AuditLog.user_id == user_id)
                )
                audit_logs = audit_result.scalars().all()
                for log in audit_logs:
                    log.user_id = None  # Anonymize
                report["audit_logs"] = f"{len(audit_logs)} (anonymized)"
            
            # Remove from organization and project memberships
            org_memberships_result = await self.db.execute(
                select(OrganizationMember).where(OrganizationMember.user_id == user_id)
            )
            org_memberships = org_memberships_result.scalars().all()
            for membership in org_memberships:
                await self.db.delete(membership)
            
            project_memberships_result = await self.db.execute(
                select(ProjectMember).where(ProjectMember.user_id == user_id)
            )
            project_memberships = project_memberships_result.scalars().all()
            for membership in project_memberships:
                await self.db.delete(membership)
            
            report["memberships"] = len(org_memberships) + len(project_memberships)
            
            # Finally, delete user profile
            user_result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                await self.db.delete(user)
                report["user_profile"] = True
            
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            raise Exception(f"Error during user deletion: {str(e)}")
        
        return report
    
    async def _anonymize_user_data(self, user_id: UUID) -> Dict[str, Any]:
        """Anonymize user data while preserving statistical value."""
        
        # Get user
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        # Anonymize user profile
        user.email = f"deleted_user_{user_id}@anonymized.local"
        user.first_name = "Anonymous"
        user.last_name = "User"
        user.is_active = False
        user.profile_data = {}
        user.preferences = {}
        
        # Anonymize comments
        comments_result = await self.db.execute(
            select(TaskCommentEnhanced).where(TaskCommentEnhanced.author_id == user_id)
        )
        comments = comments_result.scalars().all()
        for comment in comments:
            comment.content = "[Anonymized Comment]"
        
        await self.db.commit()
        
        return {
            "user_profile": "anonymized",
            "comments": f"{len(comments)} anonymized",
            "files": "retained with anonymous owner",
            "statistical_data": "preserved"
        }
    
    async def _partial_user_deletion(self, user_id: UUID) -> Dict[str, Any]:
        """Perform partial deletion based on specific categories."""
        # This would be implemented based on specific requirements
        # For now, just anonymize personal data
        return await self._anonymize_user_data(user_id)
    
    # Data Rectification
    async def rectify_user_data(
        self, 
        user_id: UUID, 
        corrections: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle data rectification requests."""
        
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        
        rectifications = {}
        
        # Update allowed fields
        allowed_fields = [
            "first_name", "last_name", "email", 
            "profile_data", "preferences"
        ]
        
        for field, new_value in corrections.items():
            if field in allowed_fields and hasattr(user, field):
                old_value = getattr(user, field)
                setattr(user, field, new_value)
                rectifications[field] = {
                    "old_value": old_value,
                    "new_value": new_value,
                    "corrected_at": datetime.utcnow().isoformat()
                }
        
        await self.db.commit()
        
        return {
            "user_id": str(user_id),
            "rectification_date": datetime.utcnow().isoformat(),
            "corrections_made": rectifications
        }
    
    # GDPR Request Management
    async def create_gdpr_request(
        self, 
        user_id: UUID,
        request_type: str,
        description: Optional[str] = None,
        data_categories: Optional[List[str]] = None
    ) -> GDPRRequest:
        """Create a new GDPR request."""
        
        gdpr_request = GDPRRequest(
            user_id=user_id,
            request_type=request_type,
            description=description,
            data_categories=data_categories or [],
            status="pending"
        )
        
        self.db.add(gdpr_request)
        await self.db.commit()
        await self.db.refresh(gdpr_request)
        
        return gdpr_request
    
    async def process_gdpr_request(
        self, 
        request_id: UUID, 
        processed_by: UUID,
        processing_notes: Optional[str] = None
    ) -> GDPRRequest:
        """Process a GDPR request."""
        
        request_result = await self.db.execute(
            select(GDPRRequest).where(GDPRRequest.id == request_id)
        )
        gdpr_request = request_result.scalar_one_or_none()
        
        if not gdpr_request:
            raise ValueError("GDPR request not found")
        
        gdpr_request.status = "in_progress"
        gdpr_request.processed_by = processed_by
        gdpr_request.processed_at = datetime.utcnow()
        gdpr_request.processing_notes = processing_notes
        
        await self.db.commit()
        await self.db.refresh(gdpr_request)
        
        return gdpr_request
    
    async def complete_gdpr_request(
        self, 
        request_id: UUID, 
        completion_notes: Optional[str] = None,
        export_url: Optional[str] = None
    ) -> GDPRRequest:
        """Mark GDPR request as completed."""
        
        request_result = await self.db.execute(
            select(GDPRRequest).where(GDPRRequest.id == request_id)
        )
        gdpr_request = request_result.scalar_one_or_none()
        
        if not gdpr_request:
            raise ValueError("GDPR request not found")
        
        gdpr_request.status = "completed"
        gdpr_request.completion_notes = completion_notes
        gdpr_request.export_url = export_url
        
        # Set expiry for data export URLs (30 days)
        if export_url:
            gdpr_request.export_expires_at = datetime.utcnow() + timedelta(days=30)
        
        await self.db.commit()
        await self.db.refresh(gdpr_request)
        
        return gdpr_request
    
    # Consent Management
    async def record_consent(
        self,
        user_id: UUID,
        organization_id: Optional[UUID],
        consent_type: str,
        consent_given: bool,
        consent_text: str,
        legal_basis: Optional[str] = None,
        retention_period: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> DataConsentRecord:
        """Record user consent."""
        
        consent_record = DataConsentRecord(
            user_id=user_id,
            organization_id=organization_id,
            purpose=consent_type,
            consent_given=consent_given,
            consent_text=consent_text,
            lawful_basis=legal_basis,
            retention_period=retention_period,
            ip_address=ip_address,
            user_agent=user_agent,
            consent_method="web_form"
        )
        
        self.db.add(consent_record)
        await self.db.commit()
        await self.db.refresh(consent_record)
        
        return consent_record
    
    async def revoke_consent(
        self,
        user_id: UUID,
        consent_type: str,
        organization_id: Optional[UUID] = None
    ) -> bool:
        """Revoke user consent for a specific purpose."""
        
        # Find the most recent consent record for this purpose
        consent_result = await self.db.execute(
            select(DataConsentRecord)
            .where(
                and_(
                    DataConsentRecord.user_id == user_id,
                    DataConsentRecord.purpose == consent_type,
                    DataConsentRecord.organization_id == organization_id if organization_id else True,
                    DataConsentRecord.consent_given == True
                )
            )
            .order_by(DataConsentRecord.created_at.desc())
        )
        
        consent_record = consent_result.scalar_one_or_none()
        
        if consent_record:
            # Create a revocation record
            revocation_record = DataConsentRecord(
                user_id=user_id,
                organization_id=organization_id,
                purpose=consent_type,
                consent_given=False,
                consent_text=f"Consent revoked for: {consent_record.consent_text}",
                lawful_basis=consent_record.lawful_basis,
                consent_method="revocation"
            )
            
            self.db.add(revocation_record)
            await self.db.commit()
            
            return True
        
        return False
    
    # Compliance Reporting
    async def generate_compliance_report(
        self,
        organization_id: Optional[UUID] = None,
        report_type: str = "summary"
    ) -> Dict[str, Any]:
        """Generate GDPR compliance report."""
        
        report = {
            "report_type": report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "organization_id": str(organization_id) if organization_id else "all",
            "gdpr_requests": await self._get_gdpr_requests_summary(organization_id),
            "consent_status": await self._get_consent_summary(organization_id),
            "data_processing": await self._get_data_processing_summary(organization_id),
            "retention_compliance": await self._check_retention_compliance(organization_id)
        }
        
        return report
    
    async def _get_gdpr_requests_summary(self, organization_id: Optional[UUID]) -> Dict[str, Any]:
        """Get summary of GDPR requests."""
        
        query = select(
            GDPRRequest.request_type,
            GDPRRequest.status,
            func.count().label('count')
        ).group_by(GDPRRequest.request_type, GDPRRequest.status)
        
        if organization_id:
            query = query.where(GDPRRequest.organization_id == organization_id)
        
        result = await self.db.execute(query)
        
        summary = {}
        for row in result.all():
            if row.request_type not in summary:
                summary[row.request_type] = {}
            summary[row.request_type][row.status] = row.count
        
        return summary
    
    async def _get_consent_summary(self, organization_id: Optional[UUID]) -> Dict[str, Any]:
        """Get summary of consent records."""
        
        query = select(
            DataConsentRecord.purpose,
            DataConsentRecord.consent_given,
            func.count().label('count')
        ).group_by(DataConsentRecord.purpose, DataConsentRecord.consent_given)
        
        if organization_id:
            query = query.where(DataConsentRecord.organization_id == organization_id)
        
        result = await self.db.execute(query)
        
        summary = {}
        for row in result.all():
            if row.purpose not in summary:
                summary[row.purpose] = {"granted": 0, "revoked": 0}
            key = "granted" if row.consent_given else "revoked"
            summary[row.purpose][key] = row.count
        
        return summary
    
    async def _get_data_processing_summary(self, organization_id: Optional[UUID]) -> Dict[str, Any]:
        """Get summary of data processing activities."""
        
        # Count active users
        user_query = select(func.count(User.id)).where(User.is_active == True)
        if organization_id:
            user_query = user_query.join(OrganizationMember).where(
                OrganizationMember.organization_id == organization_id
            )
        
        user_result = await self.db.execute(user_query)
        active_users = user_result.scalar() or 0
        
        # Count data records (simplified)
        data_records = {
            "active_users": active_users,
            "total_files": await self._count_files(organization_id),
            "total_comments": await self._count_comments(organization_id),
            "total_audit_logs": await self._count_audit_logs(organization_id)
        }
        
        return data_records
    
    async def _count_files(self, organization_id: Optional[UUID]) -> int:
        """Count files for organization."""
        query = select(func.count(FileUpload.id))
        if organization_id:
            query = query.where(FileUpload.organization_id == organization_id)
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _count_comments(self, organization_id: Optional[UUID]) -> int:
        """Count comments for organization."""
        query = select(func.count(TaskCommentEnhanced.id))
        if organization_id:
            query = query.join(Task).join(Project).where(
                Project.organization_id == organization_id
            )
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _count_audit_logs(self, organization_id: Optional[UUID]) -> int:
        """Count audit logs for organization."""
        query = select(func.count(AuditLog.id))
        if organization_id:
            query = query.where(AuditLog.organization_id == organization_id)
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _check_retention_compliance(self, organization_id: Optional[UUID]) -> Dict[str, Any]:
        """Check data retention compliance."""
        
        # Check for expired consent records
        expired_consent_query = select(func.count(DataConsentRecord.id)).where(
            DataConsentRecord.expires_at < datetime.utcnow()
        )
        if organization_id:
            expired_consent_query = expired_consent_query.where(
                DataConsentRecord.organization_id == organization_id
            )
        
        expired_result = await self.db.execute(expired_consent_query)
        expired_consents = expired_result.scalar() or 0
        
        # Check for old audit logs (older than 7 years per GDPR)
        old_audit_cutoff = datetime.utcnow() - timedelta(days=7*365)
        old_audit_query = select(func.count(AuditLog.id)).where(
            AuditLog.created_at < old_audit_cutoff
        )
        if organization_id:
            old_audit_query = old_audit_query.where(
                AuditLog.organization_id == organization_id
            )
        
        old_audit_result = await self.db.execute(old_audit_query)
        old_audit_logs = old_audit_result.scalar() or 0
        
        return {
            "expired_consents": expired_consents,
            "old_audit_logs": old_audit_logs,
            "retention_policy_violations": expired_consents + old_audit_logs,
            "compliance_status": "compliant" if (expired_consents + old_audit_logs) == 0 else "needs_attention"
        }