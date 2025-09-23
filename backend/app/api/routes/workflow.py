"""
Workflow automation API routes.
Provides endpoints for managing workflows, business rules, and automation.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_, select, func, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.workflow import (
    WorkflowDefinition, BusinessRule, WorkflowExecution, AutomationRule,
    WorkflowTemplate, WorkflowStatus, ExecutionStatus
)
from app.schemas.workflow import (
    WorkflowDefinitionCreate, WorkflowDefinitionUpdate, WorkflowDefinitionResponse,
    BusinessRuleCreate, BusinessRuleResponse,
    AutomationRuleCreate, AutomationRuleResponse,
    WorkflowExecutionResponse, WorkflowTemplateResponse,
    WorkflowTriggerEvent, WorkflowAnalyticsFilter, WorkflowAnalyticsResponse
)
from app.services.workflow_engine import workflow_engine, BusinessRulesService

router = APIRouter(prefix="/workflows", tags=["workflow-automation"])


# ============================================================================
# Workflow Definition Endpoints
# ============================================================================

@router.post("/definitions", response_model=WorkflowDefinitionResponse)
async def create_workflow_definition(
    workflow: WorkflowDefinitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new workflow definition."""
    
    # TODO: Add organization access check
    
    workflow_def = WorkflowDefinition(
        name=workflow.name,
        description=workflow.description,
        trigger_type=workflow.trigger_type,
        trigger_config=workflow.trigger_config,
        conditions=workflow.conditions,
        condition_logic=workflow.condition_logic,
        actions=workflow.actions,
        is_enabled=workflow.is_enabled,
        max_executions_per_day=workflow.max_executions_per_day,
        execution_delay_seconds=workflow.execution_delay_seconds,
        organization_id=1,  # TODO: Get from user context
        created_by=current_user.id
    )
    
    db.add(workflow_def)
    await db.commit()
    await db.refresh(workflow_def)
    
    return workflow_def


@router.get("/definitions", response_model=List[WorkflowDefinitionResponse])
async def list_workflow_definitions(
    organization_id: Optional[int] = Query(None, description="Filter by organization"),
    trigger_type: Optional[str] = Query(None, description="Filter by trigger type"),
    is_enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List workflow definitions."""
    
    query = select(WorkflowDefinition).where(WorkflowDefinition.organization_id == 1)  # TODO: Filter by user's organizations
    
    if trigger_type:
        query = query.where(WorkflowDefinition.trigger_type == trigger_type)
    if is_enabled is not None:
        query = query.where(WorkflowDefinition.is_enabled == is_enabled)
    
    query = query.order_by(desc(WorkflowDefinition.created_at))
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/definitions/{workflow_id}", response_model=WorkflowDefinitionResponse)
async def get_workflow_definition(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific workflow definition."""
    
    query = select(WorkflowDefinition).where(WorkflowDefinition.id == workflow_id)
    result = await db.execute(query)
    workflow = result.scalar()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow definition not found"
        )
    
    # TODO: Check access permissions
    
    return workflow


@router.put("/definitions/{workflow_id}", response_model=WorkflowDefinitionResponse)
async def update_workflow_definition(
    workflow_id: int,
    workflow_update: WorkflowDefinitionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a workflow definition."""
    
    query = select(WorkflowDefinition).where(WorkflowDefinition.id == workflow_id)
    result = await db.execute(query)
    workflow = result.scalar()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow definition not found"
        )
    
    # TODO: Check edit permissions
    
    # Update fields
    update_data = workflow_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workflow, field, value)
    
    workflow.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(workflow)
    
    return workflow


@router.delete("/definitions/{workflow_id}")
async def delete_workflow_definition(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a workflow definition."""
    
    query = select(WorkflowDefinition).where(WorkflowDefinition.id == workflow_id)
    result = await db.execute(query)
    workflow = result.scalar()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow definition not found"
        )
    
    # TODO: Check delete permissions
    
    await db.delete(workflow)
    await db.commit()
    
    return {"message": "Workflow definition deleted successfully"}


# ============================================================================
# Workflow Execution Endpoints
# ============================================================================

@router.post("/trigger")
async def trigger_workflow(
    trigger_event: WorkflowTriggerEvent,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger workflows for an event."""
    
    # Set user context if not provided
    if not trigger_event.user_id:
        trigger_event.user_id = current_user.id
    
    # Process the trigger event
    results = await workflow_engine.process_trigger_event(db, trigger_event)
    
    return {
        "message": "Workflow trigger processed",
        "workflows_executed": len(results),
        "results": results
    }


@router.get("/executions", response_model=List[WorkflowExecutionResponse])
async def list_workflow_executions(
    workflow_id: Optional[int] = Query(None, description="Filter by workflow"),
    status: Optional[ExecutionStatus] = Query(None, description="Filter by execution status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List workflow executions."""
    
    query = select(WorkflowExecution).options(
        selectinload(WorkflowExecution.workflow)
    )
    
    # Apply filters
    conditions = []
    if workflow_id:
        conditions.append(WorkflowExecution.workflow_id == workflow_id)
    if status:
        conditions.append(WorkflowExecution.status == status)
    if start_date:
        conditions.append(WorkflowExecution.started_at >= start_date)
    if end_date:
        conditions.append(WorkflowExecution.started_at <= end_date)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # TODO: Filter by user's organizations
    
    query = query.order_by(desc(WorkflowExecution.started_at))
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_workflow_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific workflow execution."""
    
    query = select(WorkflowExecution).options(
        selectinload(WorkflowExecution.workflow)
    ).where(WorkflowExecution.id == execution_id)
    
    result = await db.execute(query)
    execution = result.scalar()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow execution not found"
        )
    
    # TODO: Check access permissions
    
    return execution


# ============================================================================
# Business Rules Endpoints
# ============================================================================

@router.post("/business-rules", response_model=BusinessRuleResponse)
async def create_business_rule(
    rule: BusinessRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new business rule."""
    
    business_rule = BusinessRule(
        name=rule.name,
        description=rule.description,
        category=rule.category,
        rule_conditions=rule.rule_conditions,
        rule_actions=rule.rule_actions,
        is_reusable=rule.is_reusable,
        priority=rule.priority,
        organization_id=1,  # TODO: Get from user context
        created_by=current_user.id
    )
    
    db.add(business_rule)
    await db.commit()
    await db.refresh(business_rule)
    
    return business_rule


@router.get("/business-rules", response_model=List[BusinessRuleResponse])
async def list_business_rules(
    category: Optional[str] = Query(None, description="Filter by category"),
    is_system_rule: Optional[bool] = Query(None, description="Filter system rules"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List business rules."""
    
    query = select(BusinessRule)
    
    conditions = []
    if category:
        conditions.append(BusinessRule.category == category)
    if is_system_rule is not None:
        conditions.append(BusinessRule.is_system_rule == is_system_rule)
    
    # Include system rules and user's organization rules
    org_condition = or_(
        BusinessRule.is_system_rule == True,
        BusinessRule.organization_id == 1  # TODO: User's organization
    )
    conditions.append(org_condition)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(desc(BusinessRule.usage_count), BusinessRule.name)
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


# ============================================================================
# Automation Rules Endpoints
# ============================================================================

@router.post("/automation-rules", response_model=AutomationRuleResponse)
async def create_automation_rule(
    rule: AutomationRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a simple automation rule."""
    
    automation_rule = AutomationRule(
        name=rule.name,
        description=rule.description,
        rule_type=rule.rule_type,
        trigger_conditions=rule.trigger_conditions,
        automation_actions=rule.automation_actions,
        project_ids=rule.project_ids,
        user_ids=rule.user_ids,
        task_types=rule.task_types,
        is_active=rule.is_active,
        execution_frequency=rule.execution_frequency,
        organization_id=1,  # TODO: Get from user context
        created_by=current_user.id
    )
    
    db.add(automation_rule)
    await db.commit()
    await db.refresh(automation_rule)
    
    return automation_rule


@router.get("/automation-rules", response_model=List[AutomationRuleResponse])
async def list_automation_rules(
    rule_type: Optional[str] = Query(None, description="Filter by rule type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List automation rules."""
    
    query = select(AutomationRule).where(AutomationRule.organization_id == 1)  # TODO: User's organization
    
    if rule_type:
        query = query.where(AutomationRule.rule_type == rule_type)
    if is_active is not None:
        query = query.where(AutomationRule.is_active == is_active)
    
    query = query.order_by(desc(AutomationRule.created_at))
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


# ============================================================================
# Workflow Templates Endpoints
# ============================================================================

@router.get("/templates", response_model=List[WorkflowTemplateResponse])
async def list_workflow_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    is_public: Optional[bool] = Query(None, description="Filter public templates"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List workflow templates."""
    
    query = select(WorkflowTemplate)
    
    conditions = []
    if category:
        conditions.append(WorkflowTemplate.category == category)
    if is_public is not None:
        conditions.append(WorkflowTemplate.is_public == is_public)
    
    # Include public templates and user's organization templates
    access_condition = or_(
        WorkflowTemplate.is_public == True,
        WorkflowTemplate.organization_id == 1  # TODO: User's organization
    )
    conditions.append(access_condition)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(desc(WorkflowTemplate.usage_count), WorkflowTemplate.name)
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/templates/{template_id}/apply", response_model=WorkflowDefinitionResponse)
async def apply_workflow_template(
    template_id: int,
    template_config: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apply a workflow template to create a new workflow."""
    
    # Get template
    query = select(WorkflowTemplate).where(WorkflowTemplate.id == template_id)
    result = await db.execute(query)
    template = result.scalar()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow template not found"
        )
    
    # TODO: Check template access permissions
    
    # Create workflow from template
    template_data = template.template_config.copy()
    template_data.update(template_config)  # Override with user config
    
    workflow = WorkflowDefinition(
        name=template_data.get('name', template.name),
        description=template_data.get('description', template.description),
        trigger_type=template_data['trigger_type'],
        trigger_config=template_data.get('trigger_config', {}),
        conditions=template_data.get('conditions', []),
        condition_logic=template_data.get('condition_logic', 'AND'),
        actions=template_data['actions'],
        organization_id=1,  # TODO: Get from user context
        created_by=current_user.id
    )
    
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    
    # Update template usage count
    template.usage_count += 1
    await db.commit()
    
    return workflow


# ============================================================================
# Analytics Endpoints
# ============================================================================

@router.post("/analytics", response_model=WorkflowAnalyticsResponse)
async def get_workflow_analytics(
    filters: WorkflowAnalyticsFilter,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workflow execution analytics."""
    
    # Build base query
    query = select(WorkflowExecution).options(
        selectinload(WorkflowExecution.workflow)
    )
    
    conditions = []
    
    # Apply date filters
    if filters.start_date:
        conditions.append(WorkflowExecution.started_at >= filters.start_date)
    if filters.end_date:
        conditions.append(WorkflowExecution.started_at <= filters.end_date)
    
    # Apply workflow filters
    if filters.workflow_ids:
        conditions.append(WorkflowExecution.workflow_id.in_(filters.workflow_ids))
    
    if filters.status_filter:
        conditions.append(WorkflowExecution.status.in_(filters.status_filter))
    
    # TODO: Filter by user's organizations
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Execute query
    result = await db.execute(query)
    executions = result.scalars().all()
    
    # Calculate analytics
    total_executions = len(executions)
    successful_executions = len([e for e in executions if e.status == ExecutionStatus.SUCCESS])
    failed_executions = len([e for e in executions if e.status == ExecutionStatus.FAILED])
    success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
    
    # Calculate execution times
    execution_times = [e.execution_time_ms for e in executions if e.execution_time_ms is not None]
    avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
    max_execution_time = max(execution_times) if execution_times else 0
    
    # Calculate median (simplified)
    sorted_times = sorted(execution_times)
    median_execution_time = sorted_times[len(sorted_times) // 2] if sorted_times else 0
    
    return WorkflowAnalyticsResponse(
        total_executions=total_executions,
        successful_executions=successful_executions,
        failed_executions=failed_executions,
        success_rate=round(success_rate, 2),
        average_execution_time_ms=round(avg_execution_time, 2),
        median_execution_time_ms=median_execution_time,
        max_execution_time_ms=max_execution_time,
        most_active_workflows=[],  # TODO: Implement
        most_reliable_workflows=[],  # TODO: Implement
        most_failed_workflows=[],  # TODO: Implement
        executions_by_day=[],  # TODO: Implement
        executions_by_trigger_type=[]  # TODO: Implement
    )


# ============================================================================
# System Management Endpoints
# ============================================================================

@router.post("/system/initialize-rules")
async def initialize_system_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initialize default system business rules."""
    
    # TODO: Check admin permissions
    
    created_rules = await BusinessRulesService.create_system_rules(db)
    
    return {
        "message": f"Created {len(created_rules)} system business rules",
        "rules": [rule.name for rule in created_rules]
    }