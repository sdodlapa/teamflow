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