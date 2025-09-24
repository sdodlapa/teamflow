"""Workflow automation API routes for Day 3 implementation."""

from datetime import datetime
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.workflow_automation import WorkflowAutomationService


router = APIRouter(prefix="/workflows", tags=["workflows"])


# Request/Response Models
class WorkflowTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str = "task_automation"
    config: Dict
    is_public: bool = False
    tags: List[str] = []


class WorkflowTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: str
    created_at: datetime
    template_uuid: str
    usage_count: int = 0


class WorkflowExecutionRequest(BaseModel):
    template_id: int
    entity_type: str  # "task", "project", "user"
    entity_id: int
    trigger_data: Optional[Dict] = None


class WorkflowExecutionResponse(BaseModel):
    execution_id: int
    status: str
    steps_completed: int
    total_steps: int
    result: Dict


class WorkflowStatusResponse(BaseModel):
    id: int
    status: str
    current_step: int
    total_steps: int
    completion_percentage: float
    started_at: Optional[str]
    completed_at: Optional[str]
    template: Dict
    steps: List[Dict]
    error_details: Optional[Dict]


@router.get("/templates", response_model=List[WorkflowTemplateResponse])
async def list_workflow_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    is_public: Optional[bool] = Query(None, description="Filter by public/private"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List available workflow templates with optional filtering.
    """
    try:
        from sqlalchemy import select
        from app.models.workflow import WorkflowTemplate
        
        query = select(WorkflowTemplate).where(WorkflowTemplate.is_system_template == True)
        
        if category:
            query = query.where(WorkflowTemplate.category == category)
        
        if is_public is not None:
            query = query.where(WorkflowTemplate.is_public == is_public)
        
        result = await db.execute(query)
        templates = result.scalars().all()
        
        return [
            WorkflowTemplateResponse(
                id=t.id,
                name=t.name,
                description=t.description,
                category=t.category,
                created_at=t.created_at,
                template_uuid=t.template_uuid,
                usage_count=t.usage_count
            ) for t in templates
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates", response_model=WorkflowTemplateResponse)
async def create_workflow_template(
    template_data: WorkflowTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new custom workflow template.
    """
    try:
        workflow_service = WorkflowAutomationService(db)
        
        template_dict = {
            "name": template_data.name,
            "description": template_data.description,
            "category": template_data.category,
            "config": template_data.config,
            "is_public": template_data.is_public,
            "tags": template_data.tags,
            "created_by": current_user.id,
            "organization_id": getattr(current_user, 'organization_id', None)
        }
        
        result = await workflow_service.create_workflow_template(template_dict)
        
        return WorkflowTemplateResponse(
            id=result["id"],
            name=result["name"],
            description=result["description"],
            category=template_dict["category"],
            created_at=datetime.fromisoformat(result["created_at"]),
            template_uuid=result["template_uuid"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    execution_request: WorkflowExecutionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute a workflow template for a specific entity.
    """
    try:
        workflow_service = WorkflowAutomationService(db)
        
        result = await workflow_service.execute_workflow(
            template_id=execution_request.template_id,
            entity_type=execution_request.entity_type,
            entity_id=execution_request.entity_id,
            trigger_data=execution_request.trigger_data
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return WorkflowExecutionResponse(
            execution_id=result["execution_id"],
            status=result["status"],
            steps_completed=result["steps_completed"],
            total_steps=result["total_steps"],
            result=result["result"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions/{execution_id}/status", response_model=WorkflowStatusResponse)
async def get_execution_status(
    execution_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed status of a workflow execution.
    """
    try:
        workflow_service = WorkflowAutomationService(db)
        
        result = await workflow_service.get_workflow_execution_status(execution_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return WorkflowStatusResponse(
            id=result["id"],
            status=result["status"],
            current_step=result["current_step"],
            total_steps=result["total_steps"],
            completion_percentage=result["completion_percentage"],
            started_at=result["started_at"],
            completed_at=result["completed_at"],
            template=result["template"],
            steps=result["steps"],
            error_details=result["error_details"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predefined", response_model=List[Dict])
async def get_predefined_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of predefined workflow templates with their configurations.
    """
    try:
        workflow_service = WorkflowAutomationService(db)
        
        templates = await workflow_service.get_predefined_workflow_templates()
        
        return templates
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predefined/install", response_model=List[WorkflowTemplateResponse])
async def install_predefined_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Install all predefined workflow templates for the organization.
    """
    try:
        workflow_service = WorkflowAutomationService(db)
        
        organization_id = getattr(current_user, 'organization_id', 1)
        
        created_templates = await workflow_service.create_predefined_templates(
            organization_id=organization_id,
            created_by=current_user.id
        )
        
        return [
            WorkflowTemplateResponse(
                id=t["id"],
                name=t["name"],
                description="",
                category=t["category"],
                created_at=datetime.utcnow(),
                template_uuid=t["template_uuid"]
            ) for t in created_templates
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/apply", response_model=WorkflowExecutionResponse)
async def apply_workflow_to_task(
    task_id: int,
    template_name: str = Query(..., description="Name of workflow template to apply"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Apply a workflow template to a specific task.
    """
    try:
        # Find template by name
        from sqlalchemy import select
        from app.models.workflow import WorkflowTemplate
        
        template_query = select(WorkflowTemplate).where(
            WorkflowTemplate.name == template_name,
            WorkflowTemplate.is_system_template == True
        )
        result = await db.execute(template_query)
        template = result.scalar_one_or_none()
        
        if not template:
            raise HTTPException(status_code=404, detail=f"Workflow template '{template_name}' not found")
        
        # Execute workflow
        workflow_service = WorkflowAutomationService(db)
        
        result = await workflow_service.execute_workflow(
            template_id=template.id,
            entity_type="task",
            entity_id=task_id,
            trigger_data={"applied_by_user": current_user.id}
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return WorkflowExecutionResponse(
            execution_id=result["execution_id"],
            status=result["status"],
            steps_completed=result["steps_completed"],
            total_steps=result["total_steps"],
            result=result["result"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_workflow_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available workflow categories with counts.
    """
    try:
        from sqlalchemy import select, func
        from app.models.workflow import WorkflowTemplate
        
        # Get category counts
        query = select(
            WorkflowTemplate.category,
            func.count(WorkflowTemplate.id).label('count')
        ).where(
            WorkflowTemplate.is_system_template == True
        ).group_by(WorkflowTemplate.category)
        
        result = await db.execute(query)
        categories = result.all()
        
        return {
            "categories": [
                {
                    "name": category,
                    "count": count,
                    "description": {
                        "task_automation": "Automate common task operations",
                        "bug_management": "Bug tracking and resolution workflows",
                        "feature_development": "Feature development pipelines",
                        "code_review": "Code review process automation",
                        "escalation": "Task escalation and prioritization",
                        "release_management": "Release preparation workflows"
                    }.get(category, f"Workflows for {category}")
                }
                for category, count in categories
            ],
            "total_templates": sum(count for _, count in categories)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions")
async def list_workflow_executions(
    status: Optional[str] = Query(None, description="Filter by execution status"),
    limit: int = Query(default=50, le=100, description="Maximum number of results"),
    offset: int = Query(default=0, description="Results offset for pagination"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List workflow executions with optional filtering and pagination.
    """
    try:
        from sqlalchemy import select, desc
        from app.models.task_analytics import WorkflowExecution
        from app.models.workflow import WorkflowTemplate
        
        query = select(WorkflowExecution).join(WorkflowTemplate).order_by(desc(WorkflowExecution.created_at))
        
        if status:
            query = query.where(WorkflowExecution.status == status)
        
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        executions = result.scalars().all()
        
        return {
            "executions": [
                {
                    "id": execution.id,
                    "status": execution.status,
                    "entity_type": execution.entity_type,
                    "entity_id": execution.entity_id,
                    "current_step": execution.current_step,
                    "total_steps": execution.total_steps,
                    "completion_percentage": execution.completion_percentage,
                    "started_at": execution.started_at.isoformat() if execution.started_at else None,
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                    "estimated_duration": execution.estimated_duration,
                    "actual_duration": execution.actual_duration
                }
                for execution in executions
            ],
            "pagination": {
                "offset": offset,
                "limit": limit,
                "total_returned": len(executions)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/executions/{execution_id}/pause")
async def pause_workflow_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Pause an active workflow execution.
    """
    try:
        from sqlalchemy import select
        from app.models.task_analytics import WorkflowExecution, WorkflowStatus
        
        query = select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
        result = await db.execute(query)
        execution = result.scalar_one_or_none()
        
        if not execution:
            raise HTTPException(status_code=404, detail="Workflow execution not found")
        
        if execution.status != WorkflowStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Can only pause active workflows")
        
        execution.status = WorkflowStatus.PAUSED
        execution.paused_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "execution_id": execution_id,
            "status": "paused",
            "paused_at": execution.paused_at.isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/executions/{execution_id}/resume")
async def resume_workflow_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Resume a paused workflow execution.
    """
    try:
        from sqlalchemy import select
        from app.models.task_analytics import WorkflowExecution, WorkflowStatus
        
        query = select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
        result = await db.execute(query)
        execution = result.scalar_one_or_none()
        
        if not execution:
            raise HTTPException(status_code=404, detail="Workflow execution not found")
        
        if execution.status != WorkflowStatus.PAUSED:
            raise HTTPException(status_code=400, detail="Can only resume paused workflows")
        
        execution.status = WorkflowStatus.ACTIVE
        execution.paused_at = None
        
        await db.commit()
        
        # In real implementation, would trigger continuation of workflow execution
        
        return {
            "execution_id": execution_id,
            "status": "active",
            "resumed_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/executions/{execution_id}")
async def cancel_workflow_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel an active or paused workflow execution.
    """
    try:
        from sqlalchemy import select
        from app.models.task_analytics import WorkflowExecution, WorkflowStatus
        
        query = select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
        result = await db.execute(query)
        execution = result.scalar_one_or_none()
        
        if not execution:
            raise HTTPException(status_code=404, detail="Workflow execution not found")
        
        if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            raise HTTPException(status_code=400, detail="Cannot cancel completed workflows")
        
        execution.status = WorkflowStatus.CANCELLED
        execution.completed_at = datetime.utcnow()
        execution.error_details = {"reason": "Cancelled by user", "cancelled_by": current_user.id}
        
        await db.commit()
        
        return {
            "execution_id": execution_id,
            "status": "cancelled",
            "cancelled_at": execution.completed_at.isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_workflow_statistics(
    period_days: int = Query(default=30, description="Statistics period in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get workflow execution statistics and analytics.
    """
    try:
        from sqlalchemy import select, func
        from app.models.task_analytics import WorkflowExecution
        
        period_start = datetime.utcnow() - timedelta(days=period_days)
        
        # Get execution counts by status
        status_query = select(
            WorkflowExecution.status,
            func.count(WorkflowExecution.id).label('count')
        ).where(
            WorkflowExecution.created_at >= period_start
        ).group_by(WorkflowExecution.status)
        
        result = await db.execute(status_query)
        status_counts = dict(result.all())
        
        # Get total executions
        total_query = select(func.count(WorkflowExecution.id)).where(
            WorkflowExecution.created_at >= period_start
        )
        result = await db.execute(total_query)
        total_executions = result.scalar()
        
        # Calculate success rate
        completed_count = status_counts.get('completed', 0)
        failed_count = status_counts.get('failed', 0)
        success_rate = (completed_count / (completed_count + failed_count)) * 100 if (completed_count + failed_count) > 0 else 0
        
        return {
            "period_days": period_days,
            "total_executions": total_executions,
            "status_breakdown": status_counts,
            "success_rate": round(success_rate, 1),
            "metrics": {
                "avg_executions_per_day": round(total_executions / period_days, 1),
                "most_common_status": max(status_counts.keys(), key=status_counts.get) if status_counts else None,
                "efficiency_score": round(success_rate * 0.8 + (total_executions / period_days) * 2, 1)
            },
            "insights": [
                f"Executed {total_executions} workflows in the last {period_days} days",
                f"Success rate of {success_rate:.1f}% indicates {'good' if success_rate > 80 else 'needs improvement'} workflow reliability",
                f"Average of {total_executions / period_days:.1f} workflow executions per day"
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))