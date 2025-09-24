"""Workflow automation service for Day 3 implementation."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, asc, func
from sqlalchemy.orm import joinedload

from app.models.task import Task, TaskStatus, TaskPriority
from app.models.workflow import WorkflowTemplate, WorkflowDefinition, WorkflowExecution, WorkflowStatus, ExecutionStatus
from app.models.user import User
from app.models.project import Project


class WorkflowAutomationService:
    """Service for advanced workflow automation and orchestration."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_workflow_template(self, template_data: Dict) -> Dict:
        """Create a new workflow template."""
        
        template = WorkflowTemplate(
            name=template_data["name"],
            description=template_data.get("description"),
            category=template_data.get("category", "task_automation"),
            template_config=template_data["config"],
            is_system_template=template_data.get("is_system", False),
            is_public=template_data.get("is_public", False),
            created_by=template_data["created_by"],
            organization_id=template_data.get("organization_id"),
            tags=template_data.get("tags", [])
        )
        
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        
        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "category": template.category,
            "created_at": template.created_at,
            "template_uuid": template.template_uuid
        }

    async def execute_workflow(
        self, 
        template_id: int, 
        entity_type: str, 
        entity_id: int,
        trigger_data: Dict = None
    ) -> Dict:
        """Execute a workflow for a specific entity."""
        
        # Get workflow template
        template_query = select(WorkflowTemplate).where(
            WorkflowTemplate.id == template_id
        )
        result = await self.db.execute(template_query)
        template = result.scalar_one_or_none()
        
        if not template:
            return {"error": "Workflow template not found"}
        
        # Create workflow execution
        execution = WorkflowExecution(
            workflow_template_id=template_id,
            trigger_data=trigger_data or {},
            status=ExecutionStatus.PENDING,
            started_at=datetime.utcnow(),
            context_data={
                "entity_type": entity_type,
                "entity_id": entity_id
            }
        )
        
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        
        # Execute workflow steps
        result = await self._execute_workflow_steps(execution, template)
        
        return {
            "execution_id": execution.id,
            "status": execution.status.value,
            "steps_completed": len(result.get("steps", [])),
            "total_steps": len(template.template_config.get("steps", [])),
            "result": result
        }
    
    async def _execute_workflow_steps(
        self, 
        execution: WorkflowExecution, 
        template: WorkflowTemplate
    ) -> Dict:
        """Execute all steps in a workflow."""
        
        steps = template.template_config.get("steps", [])
        results = {"steps": [], "overall_success": True}
        actions_executed = []
        
        for i, step_config in enumerate(steps):
            step_result = await self._execute_single_step(execution, i, step_config)
            results["steps"].append(step_result)
            actions_executed.append({
                "step_number": i + 1,
                "step_name": step_config.get("name", f"Step {i + 1}"),
                "action": step_config.get("type"),
                "result": step_result
            })
            
            if not step_result["success"]:
                execution.status = ExecutionStatus.FAILED
                execution.error_message = step_result.get("error", "Step execution failed")
                results["overall_success"] = False
                break
        
        # Update execution with results
        execution.actions_executed = actions_executed
        execution.execution_results = results
        
        # Complete or fail execution
        if results["overall_success"]:
            execution.status = ExecutionStatus.SUCCESS
            execution.completed_at = datetime.utcnow()
            execution.execution_time_ms = int((execution.completed_at - execution.started_at).total_seconds() * 1000)
        
        await self.db.commit()
        return results
    
    async def _execute_single_step(
        self, 
        execution: WorkflowExecution, 
        step_index: int, 
        step_config: Dict
    ) -> Dict:
        """Execute a single workflow step."""
        
        step_type = step_config.get("type")
        
        try:
            if step_type == "update_task_status":
                return await self._step_update_task_status(execution, step_config)
            elif step_type == "assign_task":
                return await self._step_assign_task(execution, step_config)
            elif step_type == "create_comment":
                return await self._step_create_comment(execution, step_config)
            elif step_type == "set_priority":
                return await self._step_set_priority(execution, step_config)
            elif step_type == "set_due_date":
                return await self._step_set_due_date(execution, step_config)
            elif step_type == "send_notification":
                return await self._step_send_notification(execution, step_config)
            elif step_type == "create_subtask":
                return await self._step_create_subtask(execution, step_config)
            elif step_type == "condition_check":
                return await self._step_condition_check(execution, step_config)
            elif step_type == "wait_delay":
                return await self._step_wait_delay(execution, step_config)
            else:
                return {"success": False, "error": f"Unknown step type: {step_type}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _step_update_task_status(self, execution: WorkflowExecution, config: Dict) -> Dict:
        """Update task status workflow step."""
        entity_type = execution.context_data.get("entity_type")
        entity_id = execution.context_data.get("entity_id")
        
        if entity_type != "task":
            return {"success": False, "error": "Can only update status for tasks"}
        
        task_query = select(Task).where(Task.id == entity_id)
        result = await self.db.execute(task_query)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        new_status = config.get("status")
        if not new_status:
            return {"success": False, "error": "No status specified"}
        
        old_status = task.status
        task.status = TaskStatus(new_status)
        
        await self.db.commit()
        
        return {
            "success": True, 
            "action": "status_updated",
            "old_status": old_status,
            "new_status": new_status
        }
    
    async def _step_assign_task(self, execution: WorkflowExecution, config: Dict) -> Dict:
        """Assign task workflow step."""
        entity_type = execution.context_data.get("entity_type")
        entity_id = execution.context_data.get("entity_id")
        
        if entity_type != "task":
            return {"success": False, "error": "Can only assign tasks"}
        
        task_query = select(Task).where(Task.id == entity_id)
        result = await self.db.execute(task_query)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        # Get assignee (could be specified by ID or by rule)
        assignee_id = config.get("assignee_id")
        if not assignee_id and config.get("assign_to") == "creator":
            assignee_id = task.created_by
        elif not assignee_id and config.get("assign_to") == "project_manager":
            # Would implement project manager lookup
            assignee_id = task.created_by  # Fallback
        
        if not assignee_id:
            return {"success": False, "error": "No assignee specified"}
        
        old_assignee = task.assignee_id
        task.assignee_id = assignee_id
        
        await self.db.commit()
        
        return {
            "success": True,
            "action": "task_assigned", 
            "old_assignee": old_assignee,
            "new_assignee": assignee_id
        }
    
    async def _step_create_comment(self, execution: WorkflowExecution, config: Dict) -> Dict:
        """Create automated comment workflow step."""
        # Import here to avoid circular imports
        from app.models.task import TaskComment
        
        if execution.entity_type != "task":
            return {"success": False, "error": "Can only comment on tasks"}
        
        comment_text = config.get("comment", "Automated workflow comment")
        user_id = config.get("user_id", 1)  # System user
        
        comment = TaskComment(
            content=comment_text,
            task_id=execution.entity_id,
            user_id=user_id
        )
        
        self.db.add(comment)
        await self.db.commit()
        
        return {
            "success": True,
            "action": "comment_created",
            "comment_id": comment.id
        }
    
    async def _step_set_priority(self, execution: WorkflowExecution, config: Dict) -> Dict:
        """Set task priority workflow step."""
        if execution.entity_type != "task":
            return {"success": False, "error": "Can only set priority for tasks"}
        
        task_query = select(Task).where(Task.id == execution.entity_id)
        result = await self.db.execute(task_query)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        new_priority = config.get("priority")
        if not new_priority:
            return {"success": False, "error": "No priority specified"}
        
        old_priority = task.priority
        task.priority = TaskPriority(new_priority)
        
        await self.db.commit()
        
        return {
            "success": True,
            "action": "priority_updated",
            "old_priority": old_priority,
            "new_priority": new_priority
        }
    
    async def _step_set_due_date(self, execution: WorkflowExecution, config: Dict) -> Dict:
        """Set task due date workflow step."""
        if execution.entity_type != "task":
            return {"success": False, "error": "Can only set due date for tasks"}
        
        task_query = select(Task).where(Task.id == execution.entity_id)
        result = await self.db.execute(task_query)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        # Calculate due date based on config
        due_date = None
        if config.get("due_date"):
            due_date = datetime.fromisoformat(config["due_date"])
        elif config.get("days_from_now"):
            due_date = datetime.utcnow() + timedelta(days=config["days_from_now"])
        
        if not due_date:
            return {"success": False, "error": "No valid due date specified"}
        
        old_due_date = task.due_date
        task.due_date = due_date
        
        await self.db.commit()
        
        return {
            "success": True,
            "action": "due_date_updated",
            "old_due_date": old_due_date.isoformat() if old_due_date else None,
            "new_due_date": due_date.isoformat()
        }
    
    async def _step_send_notification(self, execution: WorkflowExecution, config: Dict) -> Dict:
        """Send notification workflow step."""
        # Mock notification - in real implementation would integrate with notification service
        
        notification_type = config.get("type", "info")
        message = config.get("message", "Workflow notification")
        recipients = config.get("recipients", [])
        
        # Log notification (mock)
        print(f"NOTIFICATION: {notification_type} - {message} to {recipients}")
        
        return {
            "success": True,
            "action": "notification_sent",
            "type": notification_type,
            "recipients": recipients
        }
    
    async def _step_create_subtask(self, execution: WorkflowExecution, config: Dict) -> Dict:
        """Create subtask workflow step."""
        if execution.entity_type != "task":
            return {"success": False, "error": "Can only create subtasks for tasks"}
        
        # Get parent task
        parent_query = select(Task).where(Task.id == execution.entity_id)
        result = await self.db.execute(parent_query)
        parent_task = result.scalar_one_or_none()
        
        if not parent_task:
            return {"success": False, "error": "Parent task not found"}
        
        # Create subtask
        subtask = Task(
            title=config.get("title", f"Subtask of {parent_task.title}"),
            description=config.get("description", "Automatically created subtask"),
            project_id=parent_task.project_id,
            created_by=parent_task.created_by,
            assignee_id=config.get("assignee_id", parent_task.assignee_id),
            status=TaskStatus(config.get("status", "todo")),
            priority=TaskPriority(config.get("priority", "medium"))
        )
        
        self.db.add(subtask)
        await self.db.commit()
        await self.db.refresh(subtask)
        
        return {
            "success": True,
            "action": "subtask_created",
            "subtask_id": subtask.id,
            "parent_task_id": parent_task.id
        }
    
    async def _step_condition_check(self, execution: WorkflowExecution, config: Dict) -> Dict:
        """Check condition workflow step."""
        condition_type = config.get("condition_type")
        
        if condition_type == "task_status":
            return await self._check_task_status_condition(execution, config)
        elif condition_type == "task_age":
            return await self._check_task_age_condition(execution, config)
        elif condition_type == "assignee_workload":
            return await self._check_assignee_workload_condition(execution, config)
        else:
            return {"success": False, "error": f"Unknown condition type: {condition_type}"}
    
    async def _check_task_status_condition(self, execution: WorkflowExecution, config: Dict) -> Dict:
        """Check task status condition."""
        if execution.entity_type != "task":
            return {"success": False, "condition_met": False}
        
        task_query = select(Task).where(Task.id == execution.entity_id)
        result = await self.db.execute(task_query)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "condition_met": False}
        
        expected_status = config.get("expected_status")
        condition_met = task.status == expected_status
        
        return {
            "success": True,
            "condition_met": condition_met,
            "actual_status": task.status,
            "expected_status": expected_status
        }
    
    async def _check_task_age_condition(self, execution: WorkflowExecution, config: Dict) -> Dict:
        """Check task age condition."""
        if execution.entity_type != "task":
            return {"success": False, "condition_met": False}
        
        task_query = select(Task).where(Task.id == execution.entity_id)
        result = await self.db.execute(task_query)
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "condition_met": False}
        
        task_age_hours = (datetime.utcnow() - task.created_at).total_seconds() / 3600
        max_age_hours = config.get("max_age_hours", 24)
        
        condition_met = task_age_hours > max_age_hours
        
        return {
            "success": True,
            "condition_met": condition_met,
            "task_age_hours": task_age_hours,
            "max_age_hours": max_age_hours
        }
    
    async def _check_assignee_workload_condition(self, execution: WorkflowExecution, config: Dict) -> Dict:
        """Check assignee workload condition."""
        if execution.entity_type != "task":
            return {"success": False, "condition_met": False}
        
        task_query = select(Task).where(Task.id == execution.entity_id)
        result = await self.db.execute(task_query)
        task = result.scalar_one_or_none()
        
        if not task or not task.assignee_id:
            return {"success": False, "condition_met": False}
        
        # Count assignee's active tasks
        workload_query = select(func.count(Task.id)).where(
            and_(
                Task.assignee_id == task.assignee_id,
                Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS]),
                Task.is_active == True
            )
        )
        result = await self.db.execute(workload_query)
        current_workload = result.scalar()
        
        max_workload = config.get("max_tasks", 5)
        condition_met = current_workload > max_workload
        
        return {
            "success": True,
            "condition_met": condition_met,
            "current_workload": current_workload,
            "max_workload": max_workload
        }
    
    async def _step_wait_delay(self, execution: WorkflowExecution, config: Dict) -> Dict:
        """Wait/delay workflow step."""
        delay_seconds = config.get("delay_seconds", 0)
        delay_minutes = config.get("delay_minutes", 0)
        delay_hours = config.get("delay_hours", 0)
        
        total_delay = delay_seconds + (delay_minutes * 60) + (delay_hours * 3600)
        
        if total_delay > 0:
            # In real implementation, this would schedule the next step
            # For now, we'll just log the delay
            print(f"WORKFLOW DELAY: {total_delay} seconds")
        
        return {
            "success": True,
            "action": "delay_completed",
            "delay_seconds": total_delay
        }
    
    async def get_workflow_execution_status(self, execution_id: int) -> Dict:
        """Get detailed workflow execution status."""
        
        execution_query = select(WorkflowExecution).options(
            joinedload(WorkflowExecution.workflow_template),
            joinedload(WorkflowExecution.step_logs)
        ).where(WorkflowExecution.id == execution_id)
        
        result = await self.db.execute(execution_query)
        execution = result.unique().scalar_one_or_none()
        
        if not execution:
            return {"error": "Execution not found"}
        
        return {
            "id": execution.id,
            "status": execution.status,
            "current_step": execution.current_step,
            "total_steps": execution.total_steps,
            "completion_percentage": execution.completion_percentage,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "template": {
                "id": execution.workflow_template.id,
                "name": execution.workflow_template.name,
                "category": execution.workflow_template.category
            },
            "steps": [
                {
                    "step_number": log.step_number,
                    "step_name": log.step_name,
                    "status": log.status,
                    "duration_seconds": log.duration_seconds,
                    "error_message": log.error_message
                } for log in execution.step_logs
            ],
            "error_details": execution.error_details
        }
    
    async def get_predefined_workflow_templates(self) -> List[Dict]:
        """Get list of predefined workflow templates."""
        return [
            {
                "name": "Bug Fix Workflow",
                "description": "Automated workflow for bug resolution process",
                "category": "bug_management",
                "config": {
                    "steps": [
                        {"type": "update_task_status", "status": "in_progress"},
                        {"type": "set_priority", "priority": "high"},
                        {"type": "create_comment", "comment": "Bug fix workflow initiated"},
                        {"type": "condition_check", "condition_type": "task_age", "max_age_hours": 48},
                        {"type": "send_notification", "type": "urgent", "message": "Bug requires immediate attention"}
                    ]
                }
            },
            {
                "name": "Feature Development Pipeline", 
                "description": "Complete feature development workflow",
                "category": "feature_development",
                "config": {
                    "steps": [
                        {"type": "create_subtask", "title": "Design Review", "status": "todo"},
                        {"type": "create_subtask", "title": "Implementation", "status": "todo"},
                        {"type": "create_subtask", "title": "Testing", "status": "todo"},
                        {"type": "create_subtask", "title": "Documentation", "status": "todo"},
                        {"type": "set_due_date", "days_from_now": 14}
                    ]
                }
            },
            {
                "name": "Code Review Process",
                "description": "Automated code review workflow",
                "category": "code_review",
                "config": {
                    "steps": [
                        {"type": "update_task_status", "status": "in_review"},
                        {"type": "create_comment", "comment": "Code ready for review"},
                        {"type": "send_notification", "type": "review_request", "message": "Code review requested"},
                        {"type": "wait_delay", "delay_hours": 24},
                        {"type": "condition_check", "condition_type": "task_status", "expected_status": "in_review"},
                        {"type": "send_notification", "type": "reminder", "message": "Code review reminder"}
                    ]
                }
            },
            {
                "name": "Task Escalation",
                "description": "Escalate overdue or blocked tasks",
                "category": "escalation",
                "config": {
                    "steps": [
                        {"type": "condition_check", "condition_type": "task_age", "max_age_hours": 72},
                        {"type": "set_priority", "priority": "urgent"},
                        {"type": "create_comment", "comment": "Task escalated due to age"},
                        {"type": "send_notification", "type": "escalation", "message": "Task requires immediate attention"}
                    ]
                }
            },
            {
                "name": "Release Management",
                "description": "Complete release preparation workflow",
                "category": "release_management",
                "config": {
                    "steps": [
                        {"type": "create_subtask", "title": "Version Bump", "status": "todo"},
                        {"type": "create_subtask", "title": "Release Notes", "status": "todo"},
                        {"type": "create_subtask", "title": "Quality Assurance", "status": "todo"},
                        {"type": "create_subtask", "title": "Deployment", "status": "todo"},
                        {"type": "create_subtask", "title": "Post-Release Monitoring", "status": "todo"},
                        {"type": "send_notification", "type": "info", "message": "Release workflow initiated"}
                    ]
                }
            }
        ]
    
    async def create_predefined_templates(self, organization_id: int, created_by: int) -> List[Dict]:
        """Create all predefined workflow templates."""
        templates = await self.get_predefined_workflow_templates()
        created_templates = []
        
        for template_data in templates:
            template = WorkflowTemplate(
                name=template_data["name"],
                description=template_data["description"],
                category=template_data["category"],
                template_config=template_data["config"],
                is_system_template=True,
                is_public=True,
                organization_id=organization_id,
                created_by=created_by,
                tags=["predefined", template_data["category"]]
            )
            
            self.db.add(template)
            created_templates.append(template)
        
        await self.db.commit()
        
        return [
            {
                "id": t.id,
                "name": t.name,
                "category": t.category,
                "template_uuid": t.template_uuid
            } for t in created_templates
        ]