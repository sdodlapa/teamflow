"""
Advanced task feature schemas for time tracking, templates, and analytics.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Time Tracking Schemas
# ============================================================================

class TaskTimeLogBase(BaseModel):
    """Base schema for task time logs."""
    description: Optional[str] = Field(None, description="Description of work performed")
    is_billable: bool = Field(False, description="Whether this time is billable")


class TaskTimeLogCreate(TaskTimeLogBase):
    """Schema for creating a new time log entry."""
    task_id: int = Field(..., description="ID of the task being tracked")


class TaskTimeLogUpdate(BaseModel):
    """Schema for updating a time log entry."""
    description: Optional[str] = None
    is_billable: Optional[bool] = None
    end_time: Optional[datetime] = None


class TaskTimeLogResponse(TaskTimeLogBase):
    """Schema for time log responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    task_id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: Optional[int]
    is_running: bool = Field(..., description="Whether timer is currently running")
    created_at: datetime
    updated_at: datetime
    
    # Related data
    user_name: Optional[str] = Field(None, description="Name of user who logged time")
    task_title: Optional[str] = Field(None, description="Title of associated task")


class TimeTrackingStartRequest(BaseModel):
    """Schema for starting time tracking."""
    task_id: int = Field(..., description="ID of the task to track time for")
    description: Optional[str] = Field(None, description="Optional description of work being done")


class TimeTrackingStopRequest(BaseModel):
    """Schema for stopping time tracking."""
    description: Optional[str] = Field(None, description="Final description of work completed")
    is_billable: bool = Field(False, description="Whether this time should be marked as billable")


class TimeReportFilter(BaseModel):
    """Schema for time reporting filters."""
    user_id: Optional[int] = None
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_billable: Optional[bool] = None


class TimeReportSummary(BaseModel):
    """Schema for time report summaries."""
    total_minutes: int = Field(..., description="Total minutes tracked")
    total_hours: float = Field(..., description="Total hours tracked (rounded)")
    billable_minutes: int = Field(..., description="Billable minutes tracked")
    billable_hours: float = Field(..., description="Billable hours tracked")
    entries_count: int = Field(..., description="Number of time entries")
    tasks_count: int = Field(..., description="Number of unique tasks")
    date_range: Dict[str, Optional[datetime]] = Field(..., description="Start and end dates of report")


# ============================================================================
# Task Template Schemas
# ============================================================================

class TaskTemplateBase(BaseModel):
    """Base schema for task templates."""
    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    category: Optional[str] = Field(None, max_length=100, description="Template category")
    estimated_hours: Optional[int] = Field(None, ge=0, description="Default estimated hours")
    priority: Optional[str] = Field(None, description="Default priority level")
    tags: Optional[List[str]] = Field(None, description="Default tags for tasks created from template")


class TaskTemplateCreate(TaskTemplateBase):
    """Schema for creating a new task template."""
    organization_id: int = Field(..., description="Organization ID for the template")


class TaskTemplateUpdate(BaseModel):
    """Schema for updating a task template."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    estimated_hours: Optional[int] = Field(None, ge=0)
    priority: Optional[str] = None
    tags: Optional[List[str]] = None


class TaskTemplateResponse(TaskTemplateBase):
    """Schema for task template responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    organization_id: int
    created_by: int
    usage_count: int = Field(..., description="How many times this template has been used")
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Related data
    creator_name: Optional[str] = Field(None, description="Name of template creator")
    organization_name: Optional[str] = Field(None, description="Organization name")


class TaskFromTemplateRequest(BaseModel):
    """Schema for creating a task from a template."""
    template_id: int = Field(..., description="ID of the template to use")
    project_id: int = Field(..., description="Project ID for the new task")
    title: Optional[str] = Field(None, description="Override template name")
    assignee_id: Optional[int] = Field(None, description="User to assign the task to")
    due_date: Optional[datetime] = Field(None, description="Due date for the task")
    
    # Override template defaults
    description: Optional[str] = None
    priority: Optional[str] = None
    estimated_hours: Optional[int] = None
    tags: Optional[List[str]] = None


class BulkTaskFromTemplateRequest(BaseModel):
    """Schema for creating multiple tasks from templates."""
    template_id: int = Field(..., description="ID of the template to use")
    project_id: int = Field(..., description="Project ID for all new tasks")
    tasks: List[Dict[str, Any]] = Field(..., description="List of task overrides")


# ============================================================================
# Activity and Mention Schemas
# ============================================================================

class TaskActivityResponse(BaseModel):
    """Schema for task activity responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    task_id: int
    user_id: int
    activity_type: str = Field(..., description="Type of activity (created, updated, assigned, etc.)")
    description: str = Field(..., description="Human-readable activity description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional activity data")
    created_at: datetime
    
    # Related data
    user_name: Optional[str] = Field(None, description="Name of user who performed the activity")


class TaskMentionResponse(BaseModel):
    """Schema for task mention responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    task_id: int
    comment_id: Optional[int]
    mentioned_user_id: int
    mentioning_user_id: int
    context: Optional[str] = Field(None, description="Text context around the mention")
    is_read: bool = Field(..., description="Whether the mention has been read")
    created_at: datetime
    
    # Related data
    task_title: Optional[str] = Field(None, description="Title of the task containing the mention")
    mentioning_user_name: Optional[str] = Field(None, description="Name of user who made the mention")


class MentionMarkReadRequest(BaseModel):
    """Schema for marking mentions as read."""
    mention_ids: List[int] = Field(..., description="List of mention IDs to mark as read")


# ============================================================================
# Assignment and Workflow Schemas
# ============================================================================

class TaskAssignmentRequest(BaseModel):
    """Schema for task assignment requests."""
    assignee_id: Optional[int] = Field(None, description="User to assign task to (null to unassign)")
    reason: Optional[str] = Field(None, description="Reason for assignment change")


class TaskAssignmentHistoryResponse(BaseModel):
    """Schema for task assignment history."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    task_id: int
    previous_assignee_id: Optional[int]
    new_assignee_id: Optional[int]
    assigned_by: int
    reason: Optional[str]
    created_at: datetime
    
    # Related data
    previous_assignee_name: Optional[str] = Field(None, description="Previous assignee name")
    new_assignee_name: Optional[str] = Field(None, description="New assignee name")
    assigner_name: Optional[str] = Field(None, description="Name of user who made the assignment")


# ============================================================================
# Analytics Schemas
# ============================================================================

class TaskAnalyticsFilter(BaseModel):
    """Schema for task analytics filters."""
    project_id: Optional[int] = None
    assignee_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class ProductivityMetrics(BaseModel):
    """Schema for productivity metrics."""
    tasks_completed: int = Field(..., description="Number of tasks completed")
    tasks_created: int = Field(..., description="Number of tasks created")
    average_completion_time_hours: Optional[float] = Field(None, description="Average time to complete tasks")
    total_time_logged_hours: float = Field(..., description="Total time logged in hours")
    completion_rate: float = Field(..., description="Percentage of tasks completed on time")
    productivity_score: float = Field(..., description="Overall productivity score (0-100)")


class TeamPerformanceMetrics(BaseModel):
    """Schema for team performance metrics."""
    total_team_members: int = Field(..., description="Number of active team members")
    active_tasks: int = Field(..., description="Number of currently active tasks")
    overdue_tasks: int = Field(..., description="Number of overdue tasks")
    average_task_completion_days: Optional[float] = Field(None, description="Average days to complete tasks")
    team_productivity_score: float = Field(..., description="Team productivity score (0-100)")
    workload_distribution: Dict[str, int] = Field(..., description="Tasks per team member")


class ProjectHealthMetrics(BaseModel):
    """Schema for project health metrics."""
    project_id: int
    project_name: str
    total_tasks: int = Field(..., description="Total number of tasks in project")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    in_progress_tasks: int = Field(..., description="Number of tasks in progress")
    overdue_tasks: int = Field(..., description="Number of overdue tasks")
    completion_percentage: float = Field(..., description="Project completion percentage")
    estimated_vs_actual_hours: Dict[str, float] = Field(..., description="Estimated vs actual time comparison")
    bottlenecks: List[str] = Field(..., description="Identified project bottlenecks")
    health_score: float = Field(..., description="Overall project health score (0-100)")


class AnalyticsDashboardData(BaseModel):
    """Schema for complete analytics dashboard data."""
    productivity_metrics: ProductivityMetrics
    team_performance: TeamPerformanceMetrics
    project_health: List[ProjectHealthMetrics]
    time_summary: TimeReportSummary
    recent_activities: List[TaskActivityResponse]
    pending_mentions: List[TaskMentionResponse]
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When this report was generated")


# ============================================================================
# Search and Filter Schemas
# ============================================================================

class AdvancedTaskSearch(BaseModel):
    """Schema for advanced task search and filtering."""
    query: Optional[str] = Field(None, description="Text search in title and description")
    project_ids: Optional[List[int]] = Field(None, description="Filter by project IDs")
    assignee_ids: Optional[List[int]] = Field(None, description="Filter by assignee IDs")
    creator_ids: Optional[List[int]] = Field(None, description="Filter by creator IDs")
    statuses: Optional[List[str]] = Field(None, description="Filter by task statuses")
    priorities: Optional[List[str]] = Field(None, description="Filter by priorities")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    
    # Date filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    due_after: Optional[datetime] = None
    due_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    
    # Advanced filters
    has_time_logged: Optional[bool] = Field(None, description="Filter tasks with/without time logs")
    has_comments: Optional[bool] = Field(None, description="Filter tasks with/without comments")
    has_dependencies: Optional[bool] = Field(None, description="Filter tasks with/without dependencies")
    is_overdue: Optional[bool] = Field(None, description="Filter overdue tasks")
    estimated_hours_min: Optional[int] = Field(None, description="Minimum estimated hours")
    estimated_hours_max: Optional[int] = Field(None, description="Maximum estimated hours")
    
    # Sorting
    sort_by: Optional[str] = Field("created_at", description="Field to sort by")
    sort_order: Optional[str] = Field("desc", description="Sort order (asc/desc)")
    
    # Pagination
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(20, ge=1, le=100, description="Number of records to return")


class TaskSearchResponse(BaseModel):
    """Schema for task search results."""
    tasks: List[Dict[str, Any]] = Field(..., description="List of matching tasks")
    total: int = Field(..., description="Total number of matching tasks")
    filters_applied: Dict[str, Any] = Field(..., description="Summary of applied filters")
    search_metadata: Dict[str, Any] = Field(..., description="Search execution metadata")
    skip: int
    limit: int