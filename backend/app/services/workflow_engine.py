"""
Workflow Engine Service for TeamFlow.
Handles workflow execution, business rules processing, and automation.
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy import and_, or_, select, func, desc, update, text
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.workflow import (
    WorkflowDefinition, BusinessRule, WorkflowExecution, AutomationRule,
    WorkflowTemplate, TriggerType, ActionType, ConditionOperator,
    WorkflowStatus, ExecutionStatus
)
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.project import Project, ProjectStatus
from app.models.user import User
from app.models.organization import Organization
from app.schemas.workflow import (
    WorkflowTriggerEvent, WorkflowDefinitionCreate, BusinessRuleCreate,
    AutomationRuleCreate, WorkflowAnalyticsFilter
)

# Set up logging
logger = logging.getLogger(__name__)


class WorkflowEngineService:
    """
    Core workflow engine that processes triggers, evaluates conditions,
    and executes actions based on business rules.
    """
    
    def __init__(self):
        self.condition_evaluators = {
            ConditionOperator.EQUALS: self._evaluate_equals,
            ConditionOperator.NOT_EQUALS: self._evaluate_not_equals,
            ConditionOperator.GREATER_THAN: self._evaluate_greater_than,
            ConditionOperator.LESS_THAN: self._evaluate_less_than,
            ConditionOperator.GREATER_EQUAL: self._evaluate_greater_equal,
            ConditionOperator.LESS_EQUAL: self._evaluate_less_equal,
            ConditionOperator.CONTAINS: self._evaluate_contains,
            ConditionOperator.NOT_CONTAINS: self._evaluate_not_contains,
            ConditionOperator.IN: self._evaluate_in,
            ConditionOperator.NOT_IN: self._evaluate_not_in,
            ConditionOperator.IS_NULL: self._evaluate_is_null,
            ConditionOperator.IS_NOT_NULL: self._evaluate_is_not_null,
            ConditionOperator.STARTS_WITH: self._evaluate_starts_with,
            ConditionOperator.ENDS_WITH: self._evaluate_ends_with,
        }
        
        self.action_executors = {
            ActionType.ASSIGN_TASK: self._execute_assign_task,
            ActionType.UPDATE_STATUS: self._execute_update_status,
            ActionType.SET_PRIORITY: self._execute_set_priority,
            ActionType.SET_DUE_DATE: self._execute_set_due_date,
            ActionType.SEND_NOTIFICATION: self._execute_send_notification,
            ActionType.CREATE_TASK: self._execute_create_task,
            ActionType.ADD_COMMENT: self._execute_add_comment,
            ActionType.MOVE_PROJECT: self._execute_move_project,
            ActionType.WEBHOOK_CALL: self._execute_webhook_call,
            ActionType.EMAIL_NOTIFICATION: self._execute_email_notification,
            ActionType.ESCALATE_TASK: self._execute_escalate_task,
            ActionType.CREATE_SUBTASK: self._execute_create_subtask,
        }
    
    async def process_trigger_event(
        self,
        db: AsyncSession,
        trigger_event: WorkflowTriggerEvent
    ) -> List[Dict[str, Any]]:
        """
        Process a trigger event and execute matching workflows.
        
        Args:
            db: Database session
            trigger_event: The trigger event to process
            
        Returns:
            List of execution results
        """
        try:
            # Find matching workflows
            workflows = await self._find_matching_workflows(db, trigger_event)
            
            execution_results = []
            
            for workflow in workflows:
                try:
                    # Check if workflow can execute (rate limiting, etc.)
                    if not await self._can_workflow_execute(db, workflow):
                        continue
                    
                    # Evaluate conditions
                    if await self._evaluate_workflow_conditions(workflow, trigger_event):
                        # Execute workflow
                        result = await self._execute_workflow(db, workflow, trigger_event)
                        execution_results.append(result)
                    
                except Exception as e:
                    logger.error(f"Error executing workflow {workflow.id}: {str(e)}")
                    # Record failed execution
                    await self._record_execution(
                        db, workflow, trigger_event, ExecutionStatus.FAILED, error=str(e)
                    )
            
            return execution_results
            
        except Exception as e:
            logger.error(f"Error processing trigger event: {str(e)}")
            return []
    
    async def _find_matching_workflows(
        self,
        db: AsyncSession,
        trigger_event: WorkflowTriggerEvent
    ) -> List[WorkflowDefinition]:
        """Find workflows that match the trigger event."""
        
        # Get organization ID from the entity
        organization_id = await self._get_organization_id_for_entity(
            db, trigger_event.entity_type, trigger_event.entity_id
        )
        
        if not organization_id:
            return []
        
        query = select(WorkflowDefinition).where(
            and_(
                WorkflowDefinition.organization_id == organization_id,
                WorkflowDefinition.trigger_type == trigger_event.trigger_type,
                WorkflowDefinition.is_enabled == True,
                WorkflowDefinition.status == WorkflowStatus.ACTIVE
            )
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def _evaluate_workflow_conditions(
        self,
        workflow: WorkflowDefinition,
        trigger_event: WorkflowTriggerEvent
    ) -> bool:
        """Evaluate if workflow conditions are met."""
        
        conditions = workflow.conditions
        if not conditions:
            return True  # No conditions means always execute
        
        condition_results = []
        
        for condition in conditions:
            field_value = self._extract_field_value(trigger_event, condition['field'])
            operator = ConditionOperator(condition['operator'])
            expected_value = condition['value']
            
            # Evaluate condition
            evaluator = self.condition_evaluators.get(operator)
            if evaluator:
                result = evaluator(field_value, expected_value)
                condition_results.append(result)
            else:
                logger.warning(f"Unknown operator: {operator}")
                condition_results.append(False)
        
        # Apply condition logic (AND/OR)
        if workflow.condition_logic == "OR":
            return any(condition_results)
        else:  # Default to AND
            return all(condition_results)
    
    async def _execute_workflow(
        self,
        db: AsyncSession,
        workflow: WorkflowDefinition,
        trigger_event: WorkflowTriggerEvent
    ) -> Dict[str, Any]:
        """Execute a workflow's actions."""
        
        start_time = datetime.utcnow()
        execution_results = {}
        actions_executed = []
        
        try:
            # Apply execution delay if specified
            if workflow.execution_delay_seconds > 0:
                await asyncio.sleep(workflow.execution_delay_seconds)
            
            # Execute each action
            for i, action in enumerate(workflow.actions):
                action_type = ActionType(action['action_type'])
                parameters = action.get('parameters', {})
                delay = action.get('delay_seconds', 0)
                
                if delay > 0:
                    await asyncio.sleep(delay)
                
                # Execute action
                executor = self.action_executors.get(action_type)
                if executor:
                    action_result = await executor(
                        db, trigger_event, parameters
                    )
                    execution_results[f"action_{i}"] = action_result
                    actions_executed.append({
                        "action_type": action_type.value,
                        "parameters": parameters,
                        "result": action_result
                    })
                else:
                    logger.warning(f"Unknown action type: {action_type}")
            
            # Record successful execution
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            await self._record_execution(
                db, workflow, trigger_event, ExecutionStatus.SUCCESS,
                actions_executed=actions_executed,
                execution_results=execution_results,
                execution_time_ms=int(execution_time)
            )
            
            # Update workflow statistics
            await self._update_workflow_stats(db, workflow.id, success=True)
            
            return {
                "workflow_id": workflow.id,
                "status": "success",
                "actions_executed": len(actions_executed),
                "execution_time_ms": int(execution_time),
                "results": execution_results
            }
            
        except Exception as e:
            # Record failed execution
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            await self._record_execution(
                db, workflow, trigger_event, ExecutionStatus.FAILED,
                error=str(e),
                actions_executed=actions_executed,
                execution_time_ms=int(execution_time)
            )
            
            # Update workflow statistics
            await self._update_workflow_stats(db, workflow.id, success=False)
            
            raise e
    
    # ========================================================================
    # Condition Evaluators
    # ========================================================================
    
    def _evaluate_equals(self, field_value: Any, expected_value: Any) -> bool:
        return field_value == expected_value
    
    def _evaluate_not_equals(self, field_value: Any, expected_value: Any) -> bool:
        return field_value != expected_value
    
    def _evaluate_greater_than(self, field_value: Any, expected_value: Any) -> bool:
        try:
            return float(field_value) > float(expected_value)
        except (ValueError, TypeError):
            return False
    
    def _evaluate_less_than(self, field_value: Any, expected_value: Any) -> bool:
        try:
            return float(field_value) < float(expected_value)
        except (ValueError, TypeError):
            return False
    
    def _evaluate_greater_equal(self, field_value: Any, expected_value: Any) -> bool:
        try:
            return float(field_value) >= float(expected_value)
        except (ValueError, TypeError):
            return False
    
    def _evaluate_less_equal(self, field_value: Any, expected_value: Any) -> bool:
        try:
            return float(field_value) <= float(expected_value)
        except (ValueError, TypeError):
            return False
    
    def _evaluate_contains(self, field_value: Any, expected_value: Any) -> bool:
        try:
            return str(expected_value).lower() in str(field_value).lower()
        except (AttributeError, TypeError):
            return False
    
    def _evaluate_not_contains(self, field_value: Any, expected_value: Any) -> bool:
        return not self._evaluate_contains(field_value, expected_value)
    
    def _evaluate_in(self, field_value: Any, expected_value: List[Any]) -> bool:
        try:
            return field_value in expected_value
        except TypeError:
            return False
    
    def _evaluate_not_in(self, field_value: Any, expected_value: List[Any]) -> bool:
        return not self._evaluate_in(field_value, expected_value)
    
    def _evaluate_is_null(self, field_value: Any, expected_value: Any) -> bool:
        return field_value is None
    
    def _evaluate_is_not_null(self, field_value: Any, expected_value: Any) -> bool:
        return field_value is not None
    
    def _evaluate_starts_with(self, field_value: Any, expected_value: Any) -> bool:
        try:
            return str(field_value).lower().startswith(str(expected_value).lower())
        except (AttributeError, TypeError):
            return False
    
    def _evaluate_ends_with(self, field_value: Any, expected_value: Any) -> bool:
        try:
            return str(field_value).lower().endswith(str(expected_value).lower())
        except (AttributeError, TypeError):
            return False
    
    # ========================================================================
    # Action Executors
    # ========================================================================
    
    async def _execute_assign_task(
        self,
        db: AsyncSession,
        trigger_event: WorkflowTriggerEvent,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute task assignment action."""
        
        task_id = trigger_event.entity_id if trigger_event.entity_type == "task" else parameters.get('task_id')
        assignee_id = parameters.get('assignee_id')
        
        if not task_id or not assignee_id:
            return {"success": False, "error": "Missing task_id or assignee_id"}
        
        try:
            # Update task assignment
            await db.execute(
                update(Task)
                .where(Task.id == task_id)
                .values(assignee_id=assignee_id, updated_at=datetime.utcnow())
            )
            await db.commit()
            
            return {"success": True, "task_id": task_id, "assignee_id": assignee_id}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_update_status(
        self,
        db: AsyncSession,
        trigger_event: WorkflowTriggerEvent,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute status update action."""
        
        entity_id = trigger_event.entity_id
        new_status = parameters.get('status')
        entity_type = trigger_event.entity_type
        
        if not new_status:
            return {"success": False, "error": "Missing status parameter"}
        
        try:
            if entity_type == "task":
                await db.execute(
                    update(Task)
                    .where(Task.id == entity_id)
                    .values(status=new_status, updated_at=datetime.utcnow())
                )
            elif entity_type == "project":
                await db.execute(
                    update(Project)
                    .where(Project.id == entity_id)
                    .values(status=new_status, updated_at=datetime.utcnow())
                )
            
            await db.commit()
            return {"success": True, "entity_id": entity_id, "new_status": new_status}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_set_priority(
        self,
        db: AsyncSession,
        trigger_event: WorkflowTriggerEvent,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute priority setting action."""
        
        task_id = trigger_event.entity_id if trigger_event.entity_type == "task" else parameters.get('task_id')
        new_priority = parameters.get('priority')
        
        if not task_id or not new_priority:
            return {"success": False, "error": "Missing task_id or priority"}
        
        try:
            await db.execute(
                update(Task)
                .where(Task.id == task_id)
                .values(priority=new_priority, updated_at=datetime.utcnow())
            )
            await db.commit()
            
            return {"success": True, "task_id": task_id, "new_priority": new_priority}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_set_due_date(
        self,
        db: AsyncSession,
        trigger_event: WorkflowTriggerEvent,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute due date setting action."""
        
        task_id = trigger_event.entity_id if trigger_event.entity_type == "task" else parameters.get('task_id')
        due_date = parameters.get('due_date')
        
        if not task_id:
            return {"success": False, "error": "Missing task_id"}
        
        try:
            # Parse due date if it's a string
            if isinstance(due_date, str):
                due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            
            await db.execute(
                update(Task)
                .where(Task.id == task_id)
                .values(due_date=due_date, updated_at=datetime.utcnow())
            )
            await db.commit()
            
            return {"success": True, "task_id": task_id, "due_date": due_date.isoformat() if due_date else None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_send_notification(
        self,
        db: AsyncSession,
        trigger_event: WorkflowTriggerEvent,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute notification sending action."""
        
        # For now, just log the notification
        # In a real implementation, this would integrate with notification service
        message = parameters.get('message', 'Workflow notification')
        recipient_ids = parameters.get('recipient_ids', [])
        
        logger.info(f"Workflow notification: {message} to users {recipient_ids}")
        
        return {
            "success": True,
            "message": message,
            "recipient_count": len(recipient_ids)
        }
    
    async def _execute_create_task(
        self,
        db: AsyncSession,
        trigger_event: WorkflowTriggerEvent,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute task creation action."""
        
        # This would create a new task based on parameters
        # Simplified implementation for now
        return {"success": True, "action": "create_task", "parameters": parameters}
    
    async def _execute_add_comment(
        self,
        db: AsyncSession,
        trigger_event: WorkflowTriggerEvent,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute comment addition action."""
        
        # This would add a comment to the task
        # Simplified implementation for now
        return {"success": True, "action": "add_comment", "parameters": parameters}
    
    async def _execute_move_project(
        self,
        db: AsyncSession,
        trigger_event: WorkflowTriggerEvent,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute project move action."""
        
        # This would move a project to a different organization or status
        # Simplified implementation for now
        return {"success": True, "action": "move_project", "parameters": parameters}
    
    async def _execute_webhook_call(
        self,
        db: AsyncSession,
        trigger_event: WorkflowTriggerEvent,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute webhook call action."""
        
        # This would make an HTTP request to an external webhook
        # Simplified implementation for now
        webhook_url = parameters.get('webhook_url')
        return {"success": True, "webhook_url": webhook_url, "status": "sent"}
    
    async def _execute_email_notification(
        self,
        db: AsyncSession,
        trigger_event: WorkflowTriggerEvent,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute email notification action."""
        
        # This would send an email notification
        # Simplified implementation for now
        return {"success": True, "action": "email_notification", "parameters": parameters}
    
    async def _execute_escalate_task(
        self,
        db: AsyncSession,
        trigger_event: WorkflowTriggerEvent,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute task escalation action."""
        
        # This would escalate a task to a higher priority or different assignee
        # Simplified implementation for now
        return {"success": True, "action": "escalate_task", "parameters": parameters}
    
    async def _execute_create_subtask(
        self,
        db: AsyncSession,
        trigger_event: WorkflowTriggerEvent,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute subtask creation action."""
        
        # This would create a subtask
        # Simplified implementation for now
        return {"success": True, "action": "create_subtask", "parameters": parameters}
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _extract_field_value(self, trigger_event: WorkflowTriggerEvent, field_path: str) -> Any:
        """Extract field value from trigger event data."""
        
        # Simple field extraction logic
        # In a real implementation, this would support complex field paths like 'task.assignee.name'
        
        if field_path.startswith('event.'):
            # Extract from event data
            field_name = field_path.replace('event.', '')
            return trigger_event.event_data.get(field_name)
        elif field_path.startswith('context.'):
            # Extract from context
            field_name = field_path.replace('context.', '')
            return trigger_event.context.get(field_name)
        else:
            # Extract from event data by default
            return trigger_event.event_data.get(field_path)
    
    async def _get_organization_id_for_entity(
        self,
        db: AsyncSession,
        entity_type: str,
        entity_id: int
    ) -> Optional[int]:
        """Get organization ID for an entity."""
        
        try:
            if entity_type == "task":
                query = select(Task.project_id).where(Task.id == entity_id)
                result = await db.execute(query)
                project_id = result.scalar()
                if project_id:
                    query = select(Project.organization_id).where(Project.id == project_id)
                    result = await db.execute(query)
                    return result.scalar()
            elif entity_type == "project":
                query = select(Project.organization_id).where(Project.id == entity_id)
                result = await db.execute(query)
                return result.scalar()
            elif entity_type == "user":
                # This would need to determine organization from context
                pass
            
            return None
        except Exception:
            return None
    
    async def _can_workflow_execute(self, db: AsyncSession, workflow: WorkflowDefinition) -> bool:
        """Check if workflow can execute (rate limiting, etc.)."""
        
        # Check daily execution limit
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        execution_count_query = select(func.count(WorkflowExecution.id)).where(
            and_(
                WorkflowExecution.workflow_id == workflow.id,
                WorkflowExecution.started_at >= today_start,
                WorkflowExecution.started_at <= today_end
            )
        )
        
        result = await db.execute(execution_count_query)
        today_executions = result.scalar() or 0
        
        return today_executions < workflow.max_executions_per_day
    
    async def _record_execution(
        self,
        db: AsyncSession,
        workflow: WorkflowDefinition,
        trigger_event: WorkflowTriggerEvent,
        status: ExecutionStatus,
        actions_executed: List[Dict[str, Any]] = None,
        execution_results: Dict[str, Any] = None,
        execution_time_ms: int = None,
        error: str = None
    ) -> WorkflowExecution:
        """Record workflow execution in database."""
        
        execution = WorkflowExecution(
            workflow_id=workflow.id,
            trigger_data=trigger_event.dict(),
            status=status,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow() if status in [ExecutionStatus.SUCCESS, ExecutionStatus.FAILED] else None,
            execution_time_ms=execution_time_ms,
            actions_executed=actions_executed or [],
            execution_results=execution_results or {},
            error_message=error,
            triggered_by_user_id=trigger_event.user_id,
            context_data=trigger_event.context
        )
        
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        return execution
    
    async def _update_workflow_stats(self, db: AsyncSession, workflow_id: int, success: bool):
        """Update workflow execution statistics."""
        
        if success:
            await db.execute(
                update(WorkflowDefinition)
                .where(WorkflowDefinition.id == workflow_id)
                .values(
                    execution_count=WorkflowDefinition.execution_count + 1,
                    success_count=WorkflowDefinition.success_count + 1,
                    last_executed_at=datetime.utcnow()
                )
            )
        else:
            await db.execute(
                update(WorkflowDefinition)
                .where(WorkflowDefinition.id == workflow_id)
                .values(
                    execution_count=WorkflowDefinition.execution_count + 1,
                    failure_count=WorkflowDefinition.failure_count + 1,
                    last_executed_at=datetime.utcnow()
                )
            )
        
        await db.commit()


class BusinessRulesService:
    """Service for managing business rules and rule templates."""
    
    @staticmethod
    async def create_system_rules(db: AsyncSession) -> List[BusinessRule]:
        """Create default system business rules."""
        
        system_rules = [
            {
                "name": "Auto-assign urgent tasks",
                "description": "Automatically assign urgent tasks to available team members",
                "category": "task_management",
                "rule_conditions": [
                    {"field": "task.priority", "operator": "equals", "value": "URGENT"}
                ],
                "rule_actions": [
                    {"action_type": "assign_task", "parameters": {"assignment_strategy": "least_busy"}}
                ]
            },
            {
                "name": "Escalate overdue tasks",
                "description": "Escalate tasks that are overdue by more than 2 days",
                "category": "task_management",
                "rule_conditions": [
                    {"field": "task.days_overdue", "operator": "greater_than", "value": 2}
                ],
                "rule_actions": [
                    {"action_type": "escalate_task", "parameters": {"escalation_level": "manager"}},
                    {"action_type": "send_notification", "parameters": {"message": "Task is overdue"}}
                ]
            }
        ]
        
        created_rules = []
        for rule_data in system_rules:
            # Check if rule already exists
            existing = await db.execute(
                select(BusinessRule).where(
                    and_(
                        BusinessRule.name == rule_data["name"],
                        BusinessRule.is_system_rule == True
                    )
                )
            )
            
            if not existing.scalar():
                rule = BusinessRule(
                    name=rule_data["name"],
                    description=rule_data["description"],
                    category=rule_data["category"],
                    rule_conditions=rule_data["rule_conditions"],
                    rule_actions=rule_data["rule_actions"],
                    is_system_rule=True,
                    is_reusable=True,
                    created_by=1  # System user
                )
                
                db.add(rule)
                created_rules.append(rule)
        
        await db.commit()
        return created_rules


# Initialize workflow engine instance
workflow_engine = WorkflowEngineService()