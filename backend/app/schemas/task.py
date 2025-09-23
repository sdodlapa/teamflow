"""Task schemas for API requests and responses."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict, EmailStr

from app.models.task import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    """Base task schema with common fields."""

    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    estimated_hours: Optional[int] = Field(None, ge=0, le=1000)
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = Field(default_factory=list)


class TaskCreate(TaskBase):
    """Schema for creating a new task."""

    project_id: int = Field(..., gt=0)
    assignee_email: Optional[EmailStr] = None


class TaskUpdate(BaseModel):
    """Schema for updating task information."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_email: Optional[EmailStr] = None
    estimated_hours: Optional[int] = Field(None, ge=0, le=1000)
    actual_hours: Optional[int] = Field(None, ge=0, le=1000)
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None


class TaskStatusUpdate(BaseModel):
    """Schema for updating task status only."""

    status: TaskStatus


class TaskAssignmentUpdate(BaseModel):
    """Schema for updating task assignment."""

    assignee_email: Optional[EmailStr] = None


class TaskRead(TaskBase):
    """Schema for reading task data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    assignee_id: Optional[int]
    created_by: int
    status: TaskStatus
    actual_hours: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Computed fields
    assignee_name: Optional[str] = None
    creator_name: Optional[str] = None
    project_name: Optional[str] = None


class TaskList(BaseModel):
    """Schema for paginated task list."""

    tasks: List[TaskRead]
    total: int
    skip: int
    limit: int


class TaskCommentBase(BaseModel):
    """Base task comment schema."""

    content: str = Field(..., min_length=1, max_length=5000)


class TaskCommentCreate(TaskCommentBase):
    """Schema for creating a task comment."""

    task_id: int = Field(..., gt=0)


class TaskCommentUpdate(BaseModel):
    """Schema for updating task comment."""

    content: str = Field(..., min_length=1, max_length=5000)


class TaskCommentRead(TaskCommentBase):
    """Schema for reading task comment data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Computed fields
    user_name: Optional[str] = None


class TaskDependencyCreate(BaseModel):
    """Schema for creating task dependency."""

    task_id: int = Field(..., gt=0)
    depends_on_id: int = Field(..., gt=0)


class TaskDependencyRead(BaseModel):
    """Schema for reading task dependency data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    depends_on_id: int
    created_at: datetime

    # Computed fields
    task_title: Optional[str] = None
    depends_on_title: Optional[str] = None


class TaskBulkUpdate(BaseModel):
    """Schema for bulk task updates."""

    task_ids: List[int] = Field(..., min_length=1, max_length=100)
    updates: TaskUpdate


class TaskBulkStatusUpdate(BaseModel):
    """Schema for bulk status updates."""

    task_ids: List[int] = Field(..., min_length=1, max_length=100)
    status: TaskStatus


class TaskBulkAssignmentUpdate(BaseModel):
    """Schema for bulk assignment updates."""

    task_ids: List[int] = Field(..., min_length=1, max_length=100)
    assignee_email: Optional[EmailStr] = None


class TaskSearchFilters(BaseModel):
    """Schema for task search and filtering."""

    status: Optional[List[TaskStatus]] = None
    priority: Optional[List[TaskPriority]] = None
    assignee_id: Optional[int] = None
    created_by: Optional[int] = None
    project_id: Optional[int] = None
    tags: Optional[List[str]] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None
    search_text: Optional[str] = Field(None, max_length=100)


class TaskStats(BaseModel):
    """Schema for task statistics."""

    total_tasks: int
    by_status: dict[TaskStatus, int]
    by_priority: dict[TaskPriority, int]
    overdue_tasks: int
    completed_tasks: int
    avg_completion_time: Optional[float] = None