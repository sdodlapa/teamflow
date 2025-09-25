"""
Template persistence models for the template builder system
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
import uuid
from enum import Enum

from sqlalchemy import Column, String, Text, JSON, Integer, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class TemplateStatus(str, Enum):
    """Status of a template"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class CollaboratorPermissions(str, Enum):
    """Permissions for template collaborators"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class CollaborationAction(str, Enum):
    """Actions that can be performed in collaboration"""
    JOIN = "join"
    LEAVE = "leave"
    EDIT = "edit"
    COMMENT = "comment"
    SAVE = "save"
    PUBLISH = "publish"
    ARCHIVE = "archive"


class Template(BaseModel):
    """
    Main template model that stores template configurations
    """
    __tablename__ = "templates"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    domain_config = Column(JSON, nullable=False)
    entities = Column(JSON, nullable=False)
    relationships = Column(JSON, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    status = Column(String, nullable=False, default=TemplateStatus.DRAFT.value)
    tags = Column(JSON, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    
    # Foreign keys
    user_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organization_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="templates")
    organization = relationship("Organization", back_populates="templates")
    versions = relationship("TemplateVersion", back_populates="template", cascade="all, delete-orphan")
    collaborators = relationship("TemplateCollaborator", back_populates="template", cascade="all, delete-orphan")
    collaboration_history = relationship("TemplateCollaborationHistory", back_populates="template", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("ix_templates_status", "status"),
        Index("ix_templates_is_public", "is_public"),
        Index("ix_templates_organization_id", "organization_id"),
    )

    def __repr__(self):
        return f"<Template {self.name} ({self.id})>"

    @property
    def is_draft(self) -> bool:
        return self.status == TemplateStatus.DRAFT.value

    @property
    def is_published(self) -> bool:
        return self.status == TemplateStatus.PUBLISHED.value

    @property
    def is_archived(self) -> bool:
        return self.status == TemplateStatus.ARCHIVED.value

    def get_latest_version(self) -> Optional["TemplateVersion"]:
        """Get the latest version of this template"""
        if not self.versions:
            return None
        return max(self.versions, key=lambda v: v.version_number)

    def get_active_collaborators(self) -> List["TemplateCollaborator"]:
        """Get list of active collaborators"""
        return [collab for collab in self.collaborators if collab.is_active]

    def has_collaborator_permission(self, user_id: UUID, permission: CollaboratorPermissions) -> bool:
        """Check if a user has specific permission on this template"""
        if self.user_id == user_id:  # Owner has all permissions
            return True
        
        for collab in self.get_active_collaborators():
            if collab.user_id == user_id:
                if permission == CollaboratorPermissions.READ:
                    return True
                elif permission == CollaboratorPermissions.WRITE:
                    return collab.permissions in [CollaboratorPermissions.WRITE.value, CollaboratorPermissions.ADMIN.value]
                elif permission == CollaboratorPermissions.ADMIN:
                    return collab.permissions == CollaboratorPermissions.ADMIN.value
        
        return False


class TemplateVersion(BaseModel):
    """
    Version history for templates
    """
    __tablename__ = "template_versions"
    
    template_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("templates.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    domain_config = Column(JSON, nullable=False)
    entities = Column(JSON, nullable=False)
    relationships = Column(JSON, nullable=False)
    changes = Column(JSON, nullable=True)
    change_description = Column(Text, nullable=True)
    created_by_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    template = relationship("Template", back_populates="versions")
    created_by = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index("ix_template_versions_template_id", "template_id"),
    )

    def __repr__(self):
        return f"<TemplateVersion {self.template_id} v{self.version_number}>"


class TemplateCollaborator(BaseModel):
    """
    Template collaborators and their permissions
    """
    __tablename__ = "template_collaborators"
    
    template_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("templates.id"), nullable=False)
    user_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    permissions = Column(String, nullable=False, default=CollaboratorPermissions.READ.value)
    
    # Relationships
    template = relationship("Template", back_populates="collaborators")
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index("ix_template_collaborators_template_id", "template_id"),
        Index("ix_template_collaborators_user_id", "user_id"),
    )

    def __repr__(self):
        return f"<TemplateCollaborator {self.user_id} on {self.template_id} ({self.permissions})>"

    @property
    def can_read(self) -> bool:
        return True  # All collaborators can read

    @property
    def can_write(self) -> bool:
        return self.permissions in [CollaboratorPermissions.WRITE.value, CollaboratorPermissions.ADMIN.value]

    @property
    def can_admin(self) -> bool:
        return self.permissions == CollaboratorPermissions.ADMIN.value


class TemplateCollaborationHistory(BaseModel):
    """
    History of collaboration actions on templates
    """
    __tablename__ = "template_collaboration_history"
    
    template_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("templates.id"), nullable=False)
    user_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    action_data = Column(JSON, nullable=True)
    
    # Relationships
    template = relationship("Template", back_populates="collaboration_history")
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index("ix_template_collaboration_history_template_id", "template_id"),
        Index("ix_template_collaboration_history_user_id", "user_id"),
    )

    def __repr__(self):
        return f"<TemplateCollaborationHistory {self.user_id} {self.action} on {self.template_id}>"

    @classmethod
    def log_action(
        cls,
        template_id: UUID,
        user_id: UUID,
        action: CollaborationAction,
        action_data: Optional[Dict[str, Any]] = None
    ) -> "TemplateCollaborationHistory":
        """Helper method to log collaboration actions"""
        return cls(
            template_id=template_id,
            user_id=user_id,
            action=action.value,
            action_data=action_data or {}
        )