"""
Pydantic schemas for workflow automation and business rules.
Handles validation and serialization for workflow-related operations.
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator

from app.models.workflow import (
    TriggerType, ActionType, ConditionOperator, WorkflowStatus, ExecutionStatus
)


# ============================================================================
# Workflow Definition Schemas
# ============================================================================

class WorkflowCondition(BaseModel):
    """Schema for workflow condition definition."""
    
    field: str = Field(..., description="Field to evaluate (e.g., 'task.status', 'task.priority')")
    operator: ConditionOperator = Field(..., description="Comparison operator")
    value: Union[str, int, float, bool, List[Any]] = Field(..., description="Value to compare against")
    field_type: str = Field("string", description="Type of field (string, number, boolean, array)")
    
    class Config:
        use_enum_values = True


class WorkflowAction(BaseModel):
    """Schema for workflow action definition."""
    
    action_type: ActionType = Field(..., description="Type of action to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action-specific parameters")
    delay_seconds: int = Field(0, ge=0, description="Delay before executing this action")
    
    class Config:
        use_enum_values = True


class WorkflowDefinitionCreate(BaseModel):
    """Schema for creating workflow definitions."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Workflow name")
    description: Optional[str] = Field(None, max_length=1000, description="Workflow description")
    
    # Trigger configuration
    trigger_type: TriggerType = Field(..., description="Type of trigger")
    trigger_config: Dict[str, Any] = Field(default_factory=dict, description="Trigger configuration")
    
    # Business rules
    conditions: List[WorkflowCondition] = Field(default_factory=list, description="Workflow conditions")
    condition_logic: str = Field("AND", pattern="^(AND|OR)$", description="Logic for combining conditions")
    
    # Actions
    actions: List[WorkflowAction] = Field(..., min_items=1, description="Actions to execute")
    
    # Settings
    is_enabled: bool = Field(True, description="Whether workflow is enabled")
    max_executions_per_day: int = Field(1000, ge=1, le=10000, description="Max executions per day")
    execution_delay_seconds: int = Field(0, ge=0, description="Delay before execution")
    
    class Config:
        use_enum_values = True


class WorkflowDefinitionUpdate(BaseModel):
    """Schema for updating workflow definitions."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    trigger_config: Optional[Dict[str, Any]] = None
    conditions: Optional[List[WorkflowCondition]] = None
    condition_logic: Optional[str] = Field(None, pattern="^(AND|OR)$")
    actions: Optional[List[WorkflowAction]] = None
    is_enabled: Optional[bool] = None
    status: Optional[WorkflowStatus] = None
    max_executions_per_day: Optional[int] = Field(None, ge=1, le=10000)
    execution_delay_seconds: Optional[int] = Field(None, ge=0)
    
    class Config:
        use_enum_values = True


class WorkflowDefinitionResponse(BaseModel):
    """Schema for workflow definition responses."""
    
    id: int
    workflow_uuid: str
    name: str
    description: Optional[str]
    
    # Configuration
    trigger_type: TriggerType
    trigger_config: Dict[str, Any]
    conditions: List[Dict[str, Any]]
    condition_logic: str
    actions: List[Dict[str, Any]]
    
    # Settings
    is_enabled: bool
    status: WorkflowStatus
    max_executions_per_day: int
    execution_delay_seconds: int
    
    # Statistics
    execution_count: int
    success_count: int
    failure_count: int
    last_executed_at: Optional[datetime]
    
    # Metadata
    organization_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True


# ============================================================================
# Business Rule Schemas
# ============================================================================

class BusinessRuleCreate(BaseModel):
    """Schema for creating business rules."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Rule name")
    description: Optional[str] = Field(None, max_length=1000, description="Rule description")
    category: str = Field(..., max_length=100, description="Rule category")
    
    # Rule definition
    rule_conditions: List[WorkflowCondition] = Field(..., description="Rule conditions")
    rule_actions: List[WorkflowAction] = Field(..., min_items=1, description="Rule actions")
    
    # Configuration
    is_reusable: bool = Field(True, description="Whether rule can be reused")
    priority: int = Field(100, ge=1, le=1000, description="Execution priority")


class BusinessRuleResponse(BaseModel):
    """Schema for business rule responses."""
    
    id: int
    rule_uuid: str
    name: str
    description: Optional[str]
    category: str
    
    # Rule definition
    rule_conditions: List[Dict[str, Any]]
    rule_actions: List[Dict[str, Any]]
    
    # Configuration
    is_reusable: bool
    is_system_rule: bool
    priority: int
    
    # Usage
    usage_count: int
    last_used_at: Optional[datetime]
    
    # Metadata
    organization_id: Optional[int]
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Workflow Execution Schemas
# ============================================================================

class WorkflowExecutionResponse(BaseModel):
    """Schema for workflow execution responses."""
    
    id: int
    execution_uuid: str
    workflow_id: int
    
    # Execution details
    status: ExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime]
    execution_time_ms: Optional[int]
    
    # Results
    actions_executed: List[Dict[str, Any]]
    execution_results: Dict[str, Any]
    error_message: Optional[str]
    
    # Context
    trigger_data: Dict[str, Any]
    triggered_by_user_id: Optional[int]
    context_data: Dict[str, Any]
    
    class Config:
        from_attributes = True
        use_enum_values = True


# ============================================================================
# Automation Rule Schemas
# ============================================================================

class AutomationRuleCreate(BaseModel):
    """Schema for creating simple automation rules."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Rule name")
    description: Optional[str] = Field(None, max_length=1000, description="Rule description")
    rule_type: str = Field(..., max_length=100, description="Type of automation rule")
    
    # Configuration
    trigger_conditions: Dict[str, Any] = Field(..., description="Simple trigger conditions")
    automation_actions: Dict[str, Any] = Field(..., description="Simple automation actions")
    
    # Scope
    project_ids: List[int] = Field(default_factory=list, description="Specific projects")
    user_ids: List[int] = Field(default_factory=list, description="Specific users")
    task_types: List[str] = Field(default_factory=list, description="Specific task types")
    
    # Settings
    is_active: bool = Field(True, description="Whether rule is active")
    execution_frequency: str = Field("immediate", description="Execution frequency")


class AutomationRuleResponse(BaseModel):
    """Schema for automation rule responses."""
    
    id: int
    rule_uuid: str
    name: str
    description: Optional[str]
    rule_type: str
    
    # Configuration
    trigger_conditions: Dict[str, Any]
    automation_actions: Dict[str, Any]
    
    # Scope
    project_ids: List[int]
    user_ids: List[int]
    task_types: List[str]
    
    # Settings
    is_active: bool
    execution_frequency: str
    
    # Statistics
    execution_count: int
    last_executed_at: Optional[datetime]
    
    # Metadata
    organization_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Workflow Template Schemas
# ============================================================================

class WorkflowTemplateResponse(BaseModel):
    """Schema for workflow template responses."""
    
    id: int
    template_uuid: str
    name: str
    description: Optional[str]
    category: str
    
    # Template configuration
    template_config: Dict[str, Any]
    required_permissions: List[str]
    
    # Properties
    is_system_template: bool
    is_public: bool
    
    # Usage and ratings
    usage_count: int
    rating: float
    rating_count: int
    
    # Versioning
    version: str
    tags: List[str]
    
    # Metadata
    organization_id: Optional[int]
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Workflow Trigger Schemas
# ============================================================================

class WorkflowTriggerEvent(BaseModel):
    """Schema for triggering workflow events."""
    
    trigger_type: TriggerType = Field(..., description="Type of trigger event")
    entity_type: str = Field(..., description="Type of entity (task, project, user)")
    entity_id: int = Field(..., description="ID of the entity")
    event_data: Dict[str, Any] = Field(default_factory=dict, description="Event-specific data")
    user_id: Optional[int] = Field(None, description="User who triggered the event")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    
    class Config:
        use_enum_values = True


# ============================================================================
# Workflow Analytics Schemas
# ============================================================================

class WorkflowAnalyticsFilter(BaseModel):
    """Schema for filtering workflow analytics."""
    
    start_date: Optional[datetime] = Field(None, description="Start date for analytics")
    end_date: Optional[datetime] = Field(None, description="End date for analytics")
    workflow_ids: List[int] = Field(default_factory=list, description="Specific workflows")
    trigger_types: List[TriggerType] = Field(default_factory=list, description="Trigger types")
    status_filter: List[ExecutionStatus] = Field(default_factory=list, description="Execution status")
    
    class Config:
        use_enum_values = True


class WorkflowAnalyticsResponse(BaseModel):
    """Schema for workflow analytics responses."""
    
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float
    
    # Performance metrics
    average_execution_time_ms: float
    median_execution_time_ms: float
    max_execution_time_ms: int
    
    # Top performers
    most_active_workflows: List[Dict[str, Any]]
    most_reliable_workflows: List[Dict[str, Any]]
    most_failed_workflows: List[Dict[str, Any]]
    
    # Trend data
    executions_by_day: List[Dict[str, Any]]
    executions_by_trigger_type: List[Dict[str, Any]]
    
    # Generated metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True