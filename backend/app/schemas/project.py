"""Project Pydantic schemas for API serialization."""

from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from app.models.project import ProjectStatus, ProjectPriority, ProjectMemberRole


class ProjectBase(BaseModel):
    """Base project schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    key: str = Field(..., min_length=2, max_length=10, pattern=r'^[A-Z][A-Z0-9]*$')
    organization_id: int
    priority: ProjectPriority = Field(default=ProjectPriority.MEDIUM)
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    color: str = Field(default="#1f2937", pattern=r'^#[0-9A-Fa-f]{6}$')
    is_public: bool = Field(default=False)


class ProjectUpdate(BaseModel):
    """Schema for updating project information."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    icon: Optional[str] = Field(None, max_length=50)
    is_public: Optional[bool] = None


class ProjectRead(ProjectBase):
    """Schema for reading project data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    key: str
    organization_id: int
    owner_id: int
    status: ProjectStatus
    priority: ProjectPriority
    start_date: Optional[date]
    due_date: Optional[date]
    completed_at: Optional[datetime]
    is_public: bool
    is_archived: bool
    color: str
    icon: Optional[str]
    created_at: datetime
    updated_at: datetime


class ProjectMemberBase(BaseModel):
    """Base project member schema."""
    role: ProjectMemberRole = Field(default=ProjectMemberRole.DEVELOPER)


class ProjectMemberCreate(ProjectMemberBase):
    """Schema for adding a member to project."""
    user_id: int
    project_id: int


class ProjectMemberUpdate(BaseModel):
    """Schema for updating project member."""
    role: Optional[ProjectMemberRole] = None
    is_active: Optional[bool] = None


class ProjectMemberRead(ProjectMemberBase):
    """Schema for reading project member data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    project_id: int
    is_active: bool
    joined_at: datetime
    updated_at: datetime


class ProjectInvite(BaseModel):
    """Schema for inviting users to project."""
    user_id: int
    role: ProjectMemberRole = Field(default=ProjectMemberRole.DEVELOPER)


class ProjectStats(BaseModel):
    """Schema for project statistics."""
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    todo_tasks: int
    total_members: int
    active_members: int
    progress_percentage: float