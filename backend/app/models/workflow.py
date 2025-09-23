"""
Workflow automation and business rules models for TeamFlow.
Handles automated task processing, business rule definitions, and workflow execution.
"""
import uuid
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, JSON, 
    ForeignKey, Enum as SQLEnum, Float, Index
)
from sqlalchemy.orm import relationship

from app.models.base import Base


class TriggerType(PyEnum):
    """Types of workflow triggers."""
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_STATUS_CHANGED = "task_status_changed"
    TASK_ASSIGNED = "task_assigned"
    TASK_OVERDUE = "task_overdue"
    TASK_COMPLETED = "task_completed"
    PROJECT_CREATED = "project_created"
    PROJECT_MILESTONE = "project_milestone"
    TIME_BASED = "time_based"
    USER_ACTION = "user_action"
    CUSTOM_EVENT = "custom_event"


class ActionType(PyEnum):
    """Types of workflow actions."""
    ASSIGN_TASK = "assign_task"
    UPDATE_STATUS = "update_status"
    SET_PRIORITY = "set_priority"
    SET_DUE_DATE = "set_due_date"
    SEND_NOTIFICATION = "send_notification"
    CREATE_TASK = "create_task"
    ADD_COMMENT = "add_comment"
    MOVE_PROJECT = "move_project"
    WEBHOOK_CALL = "webhook_call"
    EMAIL_NOTIFICATION = "email_notification"
    ESCALATE_TASK = "escalate_task"
    CREATE_SUBTASK = "create_subtask"


class ConditionOperator(PyEnum):
    """Operators for business rule conditions."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"


class WorkflowStatus(PyEnum):
    """Status of workflow execution."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"


class ExecutionStatus(PyEnum):
    """Status of workflow execution."""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    CANCELLED = "cancelled"


class WorkflowDefinition(Base):
    """
    Defines automated workflows with triggers, conditions, and actions.
    Enables complex business rule automation across the platform.
    """
    __tablename__ = "workflow_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Workflow configuration
    trigger_type = Column(SQLEnum(TriggerType), nullable=False, index=True)
    trigger_config = Column(JSON, nullable=False, default={})  # Trigger-specific configuration
    
    # Conditions (business rules)
    conditions = Column(JSON, nullable=False, default=[])  # List of condition objects
    condition_logic = Column(String(10), default="AND")  # AND/OR logic for conditions
    
    # Actions to execute
    actions = Column(JSON, nullable=False, default=[])  # List of action objects
    
    # Execution settings
    is_enabled = Column(Boolean, default=True, index=True)
    status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.ACTIVE, index=True)
    
    # Scheduling and limits
    max_executions_per_day = Column(Integer, default=1000)
    execution_delay_seconds = Column(Integer, default=0)  # Delay before execution
    
    # Metadata
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Statistics
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    last_executed_at = Column(DateTime)
    
    # Relationships
    organization = relationship("Organization", back_populates="workflow_definitions")
    creator = relationship("User", foreign_keys=[created_by])
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_workflows_org_trigger", "organization_id", "trigger_type"),
        Index("ix_workflows_enabled_status", "is_enabled", "status"),
    )


class BusinessRule(Base):
    """
    Reusable business rules that can be applied across different contexts.
    Provides a library of common business logic patterns.
    """
    __tablename__ = "business_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(100), index=True)  # task_management, project_management, etc.
    
    # Rule definition
    rule_conditions = Column(JSON, nullable=False, default=[])  # Condition definitions
    rule_actions = Column(JSON, nullable=False, default=[])  # Action definitions
    
    # Configuration
    is_reusable = Column(Boolean, default=True)
    is_system_rule = Column(Boolean, default=False, index=True)  # Built-in rules
    priority = Column(Integer, default=100, index=True)  # Execution priority
    
    # Metadata
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    
    # Relationships
    organization = relationship("Organization", foreign_keys=[organization_id])
    creator = relationship("User", foreign_keys=[created_by])
    
    __table_args__ = (
        Index("ix_business_rules_category_system", "category", "is_system_rule"),
        Index("ix_business_rules_org_reusable", "organization_id", "is_reusable"),
    )


class WorkflowExecution(Base):
    """
    Records of workflow executions for auditing and debugging.
    Tracks success/failure and execution details.
    """
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Execution details
    workflow_id = Column(Integer, ForeignKey("workflow_definitions.id"), nullable=False, index=True)
    trigger_data = Column(JSON, nullable=False, default={})  # Data that triggered the workflow
    
    # Execution results
    status = Column(SQLEnum(ExecutionStatus), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    execution_time_ms = Column(Integer)  # Execution time in milliseconds
    
    # Results and errors
    actions_executed = Column(JSON, default=[])  # Actions that were executed
    execution_results = Column(JSON, default={})  # Results of each action
    error_message = Column(Text)
    stack_trace = Column(Text)
    
    # Context
    triggered_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    context_data = Column(JSON, default={})  # Additional context information
    
    # Relationships
    workflow = relationship("WorkflowDefinition", back_populates="executions")
    triggered_by_user = relationship("User", foreign_keys=[triggered_by_user_id])
    
    __table_args__ = (
        Index("ix_workflow_executions_workflow_status", "workflow_id", "status"),
        Index("ix_workflow_executions_started_at", "started_at"),
    )


class AutomationRule(Base):
    """
    Simple automation rules for common task management scenarios.
    Provides quick setup for standard automation patterns.
    """
    __tablename__ = "automation_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    rule_type = Column(String(100), nullable=False, index=True)  # auto_assign, escalation, etc.
    
    # Simple configuration
    trigger_conditions = Column(JSON, nullable=False, default={})  # Simple trigger conditions
    automation_actions = Column(JSON, nullable=False, default={})  # Simple actions
    
    # Scope and targeting
    project_ids = Column(JSON, default=[])  # Specific projects, empty = all projects
    user_ids = Column(JSON, default=[])  # Specific users, empty = all users
    task_types = Column(JSON, default=[])  # Specific task types/categories
    
    # Settings
    is_active = Column(Boolean, default=True, index=True)
    execution_frequency = Column(String(50), default="immediate")  # immediate, hourly, daily
    
    # Metadata
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Statistics
    execution_count = Column(Integer, default=0)
    last_executed_at = Column(DateTime)
    
    # Relationships
    organization = relationship("Organization", foreign_keys=[organization_id])
    creator = relationship("User", foreign_keys=[created_by])
    
    __table_args__ = (
        Index("ix_automation_rules_org_type", "organization_id", "rule_type"),
        Index("ix_automation_rules_active_frequency", "is_active", "execution_frequency"),
    )


class WorkflowTemplate(Base):
    """
    Pre-built workflow templates for common business scenarios.
    Allows quick setup of standard workflow patterns.
    """
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    template_uuid = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(100), index=True)  # task_automation, project_management, etc.
    
    # Template definition
    template_config = Column(JSON, nullable=False, default={})  # Complete workflow configuration
    required_permissions = Column(JSON, default=[])  # Required permissions to use template
    
    # Metadata
    is_system_template = Column(Boolean, default=False, index=True)  # Built-in templates
    is_public = Column(Boolean, default=False, index=True)  # Available to all organizations
    
    # Usage and ratings
    usage_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Versioning
    version = Column(String(20), default="1.0.0")
    tags = Column(JSON, default=[])  # Searchable tags
    
    # Metadata
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", foreign_keys=[organization_id])
    creator = relationship("User", foreign_keys=[created_by])
    
    __table_args__ = (
        Index("ix_workflow_templates_category_public", "category", "is_public"),
        Index("ix_workflow_templates_system_usage", "is_system_template", "usage_count"),
    )