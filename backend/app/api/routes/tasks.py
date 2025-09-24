"""Task management API routes."""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.project import Project, ProjectMember
from app.models.task import Task, TaskComment, TaskDependency, TaskPriority, TaskStatus
from app.models.time_tracking import TaskTimeLog, TaskTemplate
from app.models.user import User
from app.schemas.task import (
    TaskBulkAssignmentUpdate,
    TaskBulkStatusUpdate,
    TaskBulkUpdate,
    TaskCommentBase,
    TaskCommentCreate,
    TaskCommentRead,
    TaskCommentUpdate,
    TaskCreate,
    TaskDependencyCreate,
    TaskDependencyRead,
    TaskList,
    TaskRead,
    TaskSearchFilters,
    TaskStats,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.schemas.user import UserRead

# Import real-time notification service
from app.services.realtime_notifications import (
    trigger_task_created_notification,
    trigger_task_updated_notification,
    trigger_comment_created_notification
)

router = APIRouter()


async def get_task_or_404(
    db: AsyncSession, task_id: int, user_id: int
) -> Task:
    """Get task by ID or raise 404. Verify user has access."""
    
    # Get task with all necessary relationships
    result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.project),
            selectinload(Task.assignee),
            selectinload(Task.creator),
        )
        .where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    
    # Check if user has access to this task's project
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == user_id,
        )
    )
    project_member = result.scalar_one_or_none()
    
    if not project_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this task"
        )
    
    return task


async def check_project_access(
    db: AsyncSession, project_id: int, user_id: int
) -> Project:
    """Verify user has access to project."""
    
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    
    # Check if user is a member of this project
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    project_member = result.scalar_one_or_none()
    
    if not project_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this project"
        )
    
    return project


def build_task_read(task: Task) -> TaskRead:
    """Build TaskRead schema from Task model."""
    task_read = TaskRead.model_validate(task)
    
    # Add computed fields
    if task.assignee:
        task_read.assignee_name = task.assignee.full_name
    if task.creator:
        task_read.creator_name = task.creator.full_name
    if task.project:
        task_read.project_name = task.project.name
    
    return task_read


@router.post("/", response_model=TaskRead)
async def create_task(
    task_data: TaskCreate,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create new task."""
    
    # Verify project access
    await check_project_access(db, task_data.project_id, current_user.id)
    
    # Get assignee if specified
    assignee_id = None
    if task_data.assignee_email:
        assignee = await User.get_by_email(db, email=task_data.assignee_email)
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee user not found"
            )
        
        # Verify assignee has access to project
        result = await db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == task_data.project_id,
                ProjectMember.user_id == assignee.id,
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee must be a member of the project"
            )
        assignee_id = assignee.id
    
    # Create task
    task = Task(
        title=task_data.title,
        description=task_data.description,
        project_id=task_data.project_id,
        assignee_id=assignee_id,
        created_by=current_user.id,
        priority=task_data.priority,
        estimated_hours=task_data.estimated_hours,
        due_date=task_data.due_date,
        tags_list=task_data.tags or [],
    )
    
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    # Load relationships for response
    result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.project),
            selectinload(Task.assignee),
            selectinload(Task.creator),
        )
        .where(Task.id == task.id)
    )
    task_with_relations = result.scalar_one()
    
    # Trigger real-time notification
    try:
        current_user_model = await User.get_by_email(db, email=current_user.email)
        if current_user_model:
            await trigger_task_created_notification(task_with_relations, current_user_model, db)
    except Exception as e:
        # Log error but don't fail the request
        import logging
        logging.getLogger(__name__).warning(f"Failed to send real-time notification: {e}")
    
    return build_task_read(task_with_relations)


@router.get("/", response_model=TaskList)
async def list_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of tasks to return"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    status: Optional[List[TaskStatus]] = Query(None, description="Filter by status"),
    priority: Optional[List[TaskPriority]] = Query(None, description="Filter by priority"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee"),
    search: Optional[str] = Query(None, max_length=100, description="Search in title/description"),
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get list of tasks for current user."""
    
    # Base query: tasks from projects where user is a member
    query = (
        select(Task)
        .join(Project, Task.project_id == Project.id)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .where(ProjectMember.user_id == current_user.id)
        .options(
            selectinload(Task.project),
            selectinload(Task.assignee),
            selectinload(Task.creator),
        )
    )
    
    count_query = (
        select(func.count(Task.id))
        .join(Project, Task.project_id == Project.id)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .where(ProjectMember.user_id == current_user.id)
    )
    
    # Apply filters
    if project_id:
        # Verify user has access to this specific project
        await check_project_access(db, project_id, current_user.id)
        query = query.where(Task.project_id == project_id)
        count_query = count_query.where(Task.project_id == project_id)
    
    if status:
        query = query.where(Task.status.in_(status))
        count_query = count_query.where(Task.status.in_(status))
    
    if priority:
        query = query.where(Task.priority.in_(priority))
        count_query = count_query.where(Task.priority.in_(priority))
    
    if assignee_id:
        query = query.where(Task.assignee_id == assignee_id)
        count_query = count_query.where(Task.assignee_id == assignee_id)
    
    if search:
        search_filter = or_(
            Task.title.ilike(f"%{search}%"),
            Task.description.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination and ordering
    query = query.offset(skip).limit(limit).order_by(Task.created_at.desc())
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    # Build response
    task_reads = [build_task_read(task) for task in tasks]
    
    return TaskList(
        tasks=task_reads,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get specific task by ID."""
    
    task = await get_task_or_404(db, task_id, current_user.id)
    return build_task_read(task)


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update task."""
    
    task = await get_task_or_404(db, task_id, current_user.id)
    
    # Handle assignee update
    if task_update.assignee_email is not None:
        assignee_id = None
        if task_update.assignee_email:
            assignee = await User.get_by_email(db, email=task_update.assignee_email)
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assignee user not found"
                )
            
            # Verify assignee has access to project
            result = await db.execute(
                select(ProjectMember).where(
                    ProjectMember.project_id == task.project_id,
                    ProjectMember.user_id == assignee.id,
                )
            )
            if not result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assignee must be a member of the project"
                )
            assignee_id = assignee.id
        task.assignee_id = assignee_id
    
    # Update other fields
    update_data = task_update.model_dump(exclude_unset=True, exclude={"assignee_email"})
    
    # Handle tags specially
    if "tags" in update_data:
        task.tags_list = update_data.pop("tags")
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    
    # Load relationships for response
    result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.project),
            selectinload(Task.assignee),
            selectinload(Task.creator),
        )
        .where(Task.id == task.id)
    )
    task_with_relations = result.scalar_one()
    
    return build_task_read(task_with_relations)


@router.patch("/{task_id}/status", response_model=TaskRead)
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update task status only."""
    
    task = await get_task_or_404(db, task_id, current_user.id)
    task.status = status_update.status
    
    await db.commit()
    await db.refresh(task)
    
    # Load relationships for response
    result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.project),
            selectinload(Task.assignee),
            selectinload(Task.creator),
        )
        .where(Task.id == task.id)
    )
    task_with_relations = result.scalar_one()
    
    return build_task_read(task_with_relations)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete task."""
    
    task = await get_task_or_404(db, task_id, current_user.id)
    
    # Soft delete - just mark as inactive
    task.is_active = False
    await db.commit()


@router.get("/{task_id}/comments", response_model=List[TaskCommentRead])
async def get_task_comments(
    task_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get comments for a task."""
    
    # Verify task access
    await get_task_or_404(db, task_id, current_user.id)
    
    # Get comments
    result = await db.execute(
        select(TaskComment)
        .options(selectinload(TaskComment.user))
        .where(
            TaskComment.task_id == task_id,
            TaskComment.is_active == True
        )
        .order_by(TaskComment.created_at)
    )
    comments = result.scalars().all()
    
    # Build response
    comment_reads = []
    for comment in comments:
        comment_read = TaskCommentRead.model_validate(comment)
        if comment.user:
            comment_read.user_name = comment.user.full_name
        comment_reads.append(comment_read)
    
    return comment_reads


@router.post("/{task_id}/comments", response_model=TaskCommentRead)
async def create_task_comment(
    task_id: int,
    comment_data: TaskCommentBase,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create comment on task."""
    
    # Verify task access
    await get_task_or_404(db, task_id, current_user.id)
    
    # Create comment
    comment = TaskComment(
        content=comment_data.content,
        task_id=task_id,
        user_id=current_user.id,
    )
    
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    # Load with user for response
    result = await db.execute(
        select(TaskComment)
        .options(selectinload(TaskComment.user))
        .where(TaskComment.id == comment.id)
    )
    comment_with_user = result.scalar_one()
    
    comment_read = TaskCommentRead.model_validate(comment_with_user)
    if comment_with_user.user:
        comment_read.user_name = comment_with_user.user.full_name
    
    return comment_read


# ===== TIME TRACKING ENDPOINTS =====

@router.post("/{task_id}/time/start")
async def start_time_tracking(
    task_id: int,
    description: Optional[str] = None,
    is_billable: bool = True,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Start time tracking for a task."""
    
    # Verify task access
    task = await get_task_or_404(db, task_id, current_user.id)
    
    # Check if user already has active time log for this task
    result = await db.execute(
        select(TaskTimeLog).where(
            and_(
                TaskTimeLog.task_id == task_id,
                TaskTimeLog.user_id == current_user.id,
                TaskTimeLog.end_time.is_(None),
                TaskTimeLog.is_active == True
            )
        )
    )
    
    active_log = result.scalar_one_or_none()
    if active_log:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time tracking already active for this task"
        )
    
    # Create new time log entry
    from datetime import datetime
    time_log = TaskTimeLog(
        task_id=task_id,
        user_id=current_user.id,
        start_time=datetime.utcnow(),
        description=description,
        is_billable=is_billable
    )
    
    db.add(time_log)
    await db.commit()
    await db.refresh(time_log)
    
    return {
        "message": "Time tracking started",
        "time_log_id": time_log.id,
        "start_time": time_log.start_time,
        "task_title": task.title,
        "is_billable": time_log.is_billable
    }


@router.post("/{task_id}/time/stop")
async def stop_time_tracking(
    task_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Stop time tracking for a task."""
    
    # Verify task access
    await get_task_or_404(db, task_id, current_user.id)
    
    # Find active time log
    result = await db.execute(
        select(TaskTimeLog).where(
            and_(
                TaskTimeLog.task_id == task_id,
                TaskTimeLog.user_id == current_user.id,
                TaskTimeLog.end_time.is_(None),
                TaskTimeLog.is_active == True
            )
        )
    )
    
    time_log = result.scalar_one_or_none()
    if not time_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active time tracking found for this task"
        )
    
    # Stop the timer
    duration_minutes = time_log.stop_timer()
    
    await db.commit()
    await db.refresh(time_log)
    
    return {
        "message": "Time tracking stopped",
        "time_log_id": time_log.id,
        "duration_minutes": duration_minutes,
        "duration_hours": round(duration_minutes / 60, 2),
        "is_billable": time_log.is_billable,
        "total_time_tracked": f"{duration_minutes // 60}h {duration_minutes % 60}m"
    }


@router.get("/{task_id}/time-logs")
async def get_task_time_logs(
    task_id: int,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get time logs for a task."""
    
    # Verify task access
    task = await get_task_or_404(db, task_id, current_user.id)
    
    # Get time logs with user information
    result = await db.execute(
        select(TaskTimeLog)
        .options(selectinload(TaskTimeLog.user))
        .where(
            and_(
                TaskTimeLog.task_id == task_id,
                TaskTimeLog.is_active == True
            )
        )
        .order_by(TaskTimeLog.start_time.desc())
    )
    
    time_logs = result.scalars().all()
    
    # Calculate totals
    total_minutes = sum(log.duration_minutes or 0 for log in time_logs if log.duration_minutes)
    billable_minutes = sum(
        log.duration_minutes or 0 for log in time_logs 
        if log.duration_minutes and log.is_billable
    )
    
    return {
        "task_id": task_id,
        "task_title": task.title,
        "time_logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "user_name": log.user.full_name if log.user else "Unknown",
                "start_time": log.start_time,
                "end_time": log.end_time,
                "duration_minutes": log.duration_minutes,
                "duration_hours": round(log.duration_minutes / 60, 2) if log.duration_minutes else None,
                "description": log.description,
                "is_billable": log.is_billable,
                "is_running": log.is_running,
                "created_at": log.created_at
            }
            for log in time_logs
        ],
        "summary": {
            "total_time_minutes": total_minutes,
            "total_time_hours": round(total_minutes / 60, 2),
            "billable_time_minutes": billable_minutes,
            "billable_time_hours": round(billable_minutes / 60, 2),
            "total_entries": len(time_logs),
            "active_entries": len([log for log in time_logs if log.is_running])
        }
    }


@router.get("/time-logs/active")
async def get_active_time_logs(
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get all active time logs for current user."""
    
    # Get active time logs across all accessible tasks
    result = await db.execute(
        select(TaskTimeLog)
        .join(Task, TaskTimeLog.task_id == Task.id)
        .join(Project, Task.project_id == Project.id)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .options(
            selectinload(TaskTimeLog.task).selectinload(Task.project),
            selectinload(TaskTimeLog.user)
        )
        .where(
            and_(
                ProjectMember.user_id == current_user.id,
                TaskTimeLog.user_id == current_user.id,
                TaskTimeLog.end_time.is_(None),
                TaskTimeLog.is_active == True
            )
        )
        .order_by(TaskTimeLog.start_time.desc())
    )
    
    active_logs = result.scalars().all()
    
    return {
        "active_time_logs": [
            {
                "id": log.id,
                "task_id": log.task_id,
                "task_title": log.task.title if log.task else "Unknown",
                "project_name": log.task.project.name if log.task and log.task.project else "Unknown",
                "start_time": log.start_time,
                "description": log.description,
                "is_billable": log.is_billable,
                "duration_so_far_minutes": log.calculate_duration() or 0,
            }
            for log in active_logs
        ],
        "total_active_logs": len(active_logs)
    }


# ===== TASK TEMPLATE ENDPOINTS =====

@router.get("/templates")
async def list_task_templates(
    category: Optional[str] = Query(None, description="Filter by template category"),
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List available task templates for the user's organization."""
    
    # Get user's organization (assuming user has organization_id)
    # This would need to be adjusted based on your user-organization relationship
    query = select(TaskTemplate).where(
        and_(
            TaskTemplate.is_active == True
        )
    )
    
    if category:
        query = query.where(TaskTemplate.category == category)
    
    result = await db.execute(
        query.order_by(TaskTemplate.usage_count.desc(), TaskTemplate.name)
    )
    templates = result.scalars().all()
    
    return {
        "templates": [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "estimated_hours": t.estimated_hours,
                "priority": t.priority,
                "usage_count": t.usage_count,
                "created_by": t.created_by,
                "created_at": t.created_at
            }
            for t in templates
        ]
    }


@router.post("/templates")
async def create_task_template(
    name: str,
    description: Optional[str] = None,
    category: Optional[str] = None,
    estimated_hours: Optional[int] = None,
    priority: Optional[str] = None,
    tags: Optional[str] = None,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create a new task template."""
    
    # Note: This assumes user has an organization_id
    # You may need to adjust this based on your user-organization relationship
    template = TaskTemplate(
        name=name,
        description=description,
        category=category,
        estimated_hours=estimated_hours,
        priority=priority,
        tags=tags,
        organization_id=1,  # This needs to be properly set based on user's org
        created_by=current_user.id
    )
    
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    return {
        "message": "Template created successfully",
        "template_id": template.id,
        "name": template.name
    }


@router.post("/templates/{template_id}/apply")
async def apply_task_template(
    template_id: int,
    project_id: int,
    title_override: Optional[str] = None,
    current_user: UserRead = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Apply a template to create a new task."""
    
    # Get template
    template = await db.get(TaskTemplate, template_id)
    if not template or not template.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Verify project access
    await check_project_access(db, project_id, current_user.id)
    
    # Create task from template
    task = Task(
        title=title_override or f"{template.name} Task",
        description=template.description,
        project_id=project_id,
        created_by=current_user.id,
        estimated_hours=template.estimated_hours,
        priority=getattr(TaskPriority, template.priority.upper()) if template.priority else TaskPriority.MEDIUM
    )
    
    # Handle tags if present
    if template.tags:
        try:
            import json
            tags_list = json.loads(template.tags)
            task.tags_list = tags_list
        except:
            pass
    
    db.add(task)
    
    # Update template usage count
    template.increment_usage()
    
    await db.commit()
    await db.refresh(task)
    
    # Load relationships for response
    result = await db.execute(
        select(Task)
        .options(
            selectinload(Task.project),
            selectinload(Task.assignee),
            selectinload(Task.creator),
        )
        .where(Task.id == task.id)
    )
    task_with_relations = result.scalar_one()
    
    return {
        "message": "Task created from template",
        "task": build_task_read(task_with_relations),
        "template_name": template.name,
        "template_usage_count": template.usage_count
    }