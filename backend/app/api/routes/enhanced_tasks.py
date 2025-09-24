"""Enhanced task management API routes for Day 3 implementation."""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.task_analytics import TaskAnalyticsService


router = APIRouter(prefix="/tasks", tags=["enhanced-tasks"])


# Enhanced Request/Response Models
class TaskComplexityUpdate(BaseModel):
    complexity_score: Optional[int] = Field(None, ge=1, le=10)
    skill_requirements: Optional[List[str]] = None
    estimated_hours: Optional[float] = None


class TaskOptimizationResponse(BaseModel):
    task_id: int
    recommendations: List[Dict[str, str]]
    estimated_improvement: Dict[str, float]
    priority_suggestion: Optional[str]
    assignment_suggestion: Optional[int]


class DependencyAnalysisResponse(BaseModel):
    task_id: int
    dependency_chain: List[Dict]
    critical_path: List[int]
    bottlenecks: List[Dict]
    estimated_total_time: float
    risk_factors: List[str]


class ResourceAllocationResponse(BaseModel):
    project_id: int
    team_members: List[Dict]
    workload_distribution: Dict[int, Dict]
    recommendations: List[Dict]
    capacity_utilization: float


@router.put("/{task_id}/estimate-complexity", response_model=Dict)
async def update_task_complexity(
    task_id: int,
    complexity_data: TaskComplexityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update task complexity estimation and related metadata.
    """
    try:
        from sqlalchemy import select
        from app.models.task import Task
        
        # Get task
        task_query = select(Task).where(Task.id == task_id)
        result = await db.execute(task_query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update task complexity data
        if complexity_data.complexity_score is not None:
            task.complexity_score = complexity_data.complexity_score
        
        if complexity_data.skill_requirements is not None:
            task.skill_requirements = complexity_data.skill_requirements
        
        if complexity_data.estimated_hours is not None:
            task.estimated_hours = complexity_data.estimated_hours
        
        await db.commit()
        
        # Create or update complexity estimation record
        from app.models.task_analytics import TaskComplexityEstimation, TaskComplexityType
        
        complexity_type_map = {
            (1, 2): TaskComplexityType.TRIVIAL,
            (3, 4): TaskComplexityType.SIMPLE,
            (5, 6): TaskComplexityType.MODERATE,
            (7, 8): TaskComplexityType.COMPLEX,
            (9, 10): TaskComplexityType.CRITICAL
        }
        
        complexity_type = TaskComplexityType.MODERATE
        if task.complexity_score:
            for (min_score, max_score), ctype in complexity_type_map.items():
                if min_score <= task.complexity_score <= max_score:
                    complexity_type = ctype
                    break
        
        estimation_query = select(TaskComplexityEstimation).where(
            TaskComplexityEstimation.task_id == task_id
        )
        result = await db.execute(estimation_query)
        estimation = result.scalar_one_or_none()
        
        if not estimation:
            estimation = TaskComplexityEstimation(
                task_id=task_id,
                complexity_score=task.complexity_score or 5,
                complexity_type=complexity_type,
                confidence_level=0.8,
                model_version="manual_v1.0"
            )
            db.add(estimation)
        else:
            estimation.complexity_score = task.complexity_score or estimation.complexity_score
            estimation.complexity_type = complexity_type
        
        await db.commit()
        
        return {
            "task_id": task_id,
            "complexity_score": task.complexity_score,
            "complexity_type": complexity_type.value,
            "skill_requirements": task.skill_requirements,
            "estimated_hours": task.estimated_hours,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/auto-assign", response_model=Dict)
async def auto_assign_task(
    task_id: int,
    candidate_user_ids: List[int] = Query(..., description="List of candidate user IDs"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Automatically assign task using smart assignment algorithm.
    """
    try:
        analytics_service = TaskAnalyticsService(db)
        
        # Get task and candidate users
        from sqlalchemy import select
        from app.models.task import Task
        from app.models.user import User
        
        task_query = select(Task).where(Task.id == task_id)
        result = await db.execute(task_query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        users_query = select(User).where(User.id.in_(candidate_user_ids))
        result = await db.execute(users_query)
        candidate_users = result.scalars().all()
        
        if not candidate_users:
            raise HTTPException(status_code=400, detail="No valid candidate users found")
        
        # Get smart assignment recommendation
        assignment_result = await analytics_service.smart_task_assignment(task, candidate_users)
        
        if "error" in assignment_result:
            raise HTTPException(status_code=400, detail=assignment_result["error"])
        
        # Apply the assignment
        recommended_user_id = assignment_result["recommended_user_id"]
        old_assignee_id = task.assignee_id
        task.assignee_id = recommended_user_id
        
        # Log the smart assignment
        from app.models.task_analytics import SmartAssignmentLog
        
        assignment_log = SmartAssignmentLog(
            task_id=task_id,
            assigned_user_id=recommended_user_id,
            assignment_method="smart",
            algorithm_version="v1.0",
            candidate_users=candidate_user_ids,
            scoring_details=assignment_result["scores"],
            final_score=assignment_result["scores"][recommended_user_id]["total_score"]
        )
        
        db.add(assignment_log)
        await db.commit()
        
        return {
            "task_id": task_id,
            "previous_assignee_id": old_assignee_id,
            "new_assignee_id": recommended_user_id,
            "confidence": assignment_result["confidence"],
            "assignment_score": assignment_result["scores"][recommended_user_id]["total_score"],
            "assignment_factors": assignment_result["scores"][recommended_user_id],
            "assigned_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/optimize", response_model=TaskOptimizationResponse)
async def optimize_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get optimization recommendations for a specific task.
    """
    try:
        from sqlalchemy import select
        from app.models.task import Task, TaskStatus, TaskPriority
        
        # Get task with related data
        task_query = select(Task).where(Task.id == task_id)
        result = await db.execute(task_query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        recommendations = []
        estimated_improvement = {}
        
        # Analyze task complexity vs estimated hours
        if task.complexity_score and task.estimated_hours:
            expected_hours = task.complexity_score * 2  # Simple heuristic
            if task.estimated_hours > expected_hours * 1.5:
                recommendations.append({
                    "type": "time_estimation",
                    "message": "Estimated hours seem high for complexity level",
                    "suggestion": f"Consider reducing estimate to ~{expected_hours} hours"
                })
                estimated_improvement["time_savings"] = (task.estimated_hours - expected_hours) / task.estimated_hours
        
        # Check for missing skill requirements
        if not task.skill_requirements:
            recommendations.append({
                "type": "skill_requirements",
                "message": "No skill requirements specified",
                "suggestion": "Add skill requirements for better assignment"
            })
            estimated_improvement["assignment_accuracy"] = 0.3
        
        # Check task age and status
        task_age_days = (datetime.utcnow() - task.created_at).days
        if task_age_days > 7 and task.status == TaskStatus.TODO:
            recommendations.append({
                "type": "stale_task",
                "message": "Task has been pending for over a week",
                "suggestion": "Consider increasing priority or reassigning"
            })
            priority_suggestion = TaskPriority.HIGH.value
        else:
            priority_suggestion = None
        
        # Check for potential blockers
        if task.blocked_hours and task.blocked_hours > 8:
            recommendations.append({
                "type": "blocked_task",
                "message": f"Task has been blocked for {task.blocked_hours} hours",
                "suggestion": "Identify and resolve blocking issues"
            })
            estimated_improvement["velocity_improvement"] = 0.4
        
        # Assignment optimization
        assignment_suggestion = None
        if not task.assignee_id:
            recommendations.append({
                "type": "unassigned_task",
                "message": "Task is not assigned to anyone",
                "suggestion": "Use auto-assignment for optimal allocation"
            })
            assignment_suggestion = 0  # Placeholder for smart assignment
        
        # Due date optimization
        if not task.due_date and task.complexity_score:
            recommended_days = max(1, task.complexity_score // 2)
            recommendations.append({
                "type": "missing_due_date",
                "message": "Task has no due date set",
                "suggestion": f"Set due date to {recommended_days} days from now based on complexity"
            })
            estimated_improvement["planning_accuracy"] = 0.25
        
        return TaskOptimizationResponse(
            task_id=task_id,
            recommendations=recommendations,
            estimated_improvement=estimated_improvement,
            priority_suggestion=priority_suggestion,
            assignment_suggestion=assignment_suggestion
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}/dependencies/critical-path", response_model=DependencyAnalysisResponse)
async def analyze_task_dependencies(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze task dependencies and identify critical path.
    """
    try:
        from sqlalchemy import select
        from app.models.task import Task, TaskDependency
        
        # Get task with dependencies
        task_query = select(Task).where(Task.id == task_id)
        result = await db.execute(task_query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Get all dependencies
        deps_query = select(TaskDependency).where(TaskDependency.task_id == task_id)
        result = await db.execute(deps_query)
        dependencies = result.scalars().all()
        
        # Get dependency tasks
        dependency_task_ids = [dep.depends_on_id for dep in dependencies]
        dependency_chain = []
        
        if dependency_task_ids:
            dep_tasks_query = select(Task).where(Task.id.in_(dependency_task_ids))
            result = await db.execute(dep_tasks_query)
            dep_tasks = result.scalars().all()
            
            dependency_chain = [
                {
                    "task_id": dep_task.id,
                    "title": dep_task.title,
                    "status": dep_task.status,
                    "estimated_hours": dep_task.estimated_hours,
                    "complexity_score": dep_task.complexity_score,
                    "assignee_id": dep_task.assignee_id
                }
                for dep_task in dep_tasks
            ]
        
        # Calculate critical path (simplified)
        critical_path = dependency_task_ids + [task_id]
        
        # Identify bottlenecks
        bottlenecks = []
        for dep_task in dependency_chain:
            if not dep_task["assignee_id"]:
                bottlenecks.append({
                    "task_id": dep_task["task_id"],
                    "type": "unassigned",
                    "message": f"Dependency task '{dep_task['title']}' is not assigned"
                })
            elif dep_task["status"] == "todo" and (datetime.utcnow() - task.created_at).days > 3:
                bottlenecks.append({
                    "task_id": dep_task["task_id"],
                    "type": "stale",
                    "message": f"Dependency task '{dep_task['title']}' has not been started"
                })
        
        # Calculate estimated total time
        estimated_total_time = sum(
            dep.get("estimated_hours", 0) for dep in dependency_chain if dep.get("estimated_hours")
        ) + (task.estimated_hours or 0)
        
        # Risk factors
        risk_factors = []
        if len(dependency_chain) > 5:
            risk_factors.append("High dependency count increases coordination complexity")
        if estimated_total_time > 40:
            risk_factors.append("Long dependency chain may cause delays")
        if len(bottlenecks) > 0:
            risk_factors.append(f"{len(bottlenecks)} dependency bottlenecks identified")
        
        return DependencyAnalysisResponse(
            task_id=task_id,
            dependency_chain=dependency_chain,
            critical_path=critical_path,
            bottlenecks=bottlenecks,
            estimated_total_time=estimated_total_time,
            risk_factors=risk_factors
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/dependencies/optimize")
async def optimize_task_dependencies(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Optimize task dependency chain for better performance.
    """
    try:
        from sqlalchemy import select
        from app.models.task import Task, TaskDependency, TaskStatus
        
        # Get task dependencies
        task_query = select(Task).where(Task.id == task_id)
        result = await db.execute(task_query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        deps_query = select(TaskDependency).where(TaskDependency.task_id == task_id)
        result = await db.execute(deps_query)
        dependencies = result.scalars().all()
        
        optimizations = []
        
        # Get dependency tasks for analysis
        if dependencies:
            dependency_task_ids = [dep.depends_on_id for dep in dependencies]
            dep_tasks_query = select(Task).where(Task.id.in_(dependency_task_ids))
            result = await db.execute(dep_tasks_query)
            dep_tasks = result.scalars().all()
            
            # Identify parallel execution opportunities
            completed_deps = [t for t in dep_tasks if t.status == TaskStatus.DONE]
            if completed_deps:
                for completed_dep in completed_deps:
                    # Remove completed dependencies
                    dep_to_remove = next(d for d in dependencies if d.depends_on_id == completed_dep.id)
                    await db.delete(dep_to_remove)
                    optimizations.append({
                        "type": "removed_completed_dependency",
                        "task_id": completed_dep.id,
                        "message": f"Removed completed dependency: {completed_dep.title}"
                    })
            
            # Suggest parallel execution
            todo_deps = [t for t in dep_tasks if t.status == TaskStatus.TODO]
            if len(todo_deps) > 1:
                optimizations.append({
                    "type": "parallel_execution_opportunity",
                    "message": f"{len(todo_deps)} dependencies can potentially be executed in parallel",
                    "suggestion": "Review if dependencies are truly sequential"
                })
        
        # Check if task can be started early
        if task.status == TaskStatus.TODO and not dependencies:
            optimizations.append({
                "type": "early_start_opportunity",
                "message": "Task has no blocking dependencies and can be started immediately",
                "suggestion": "Move task to in_progress status"
            })
        
        await db.commit()
        
        return {
            "task_id": task_id,
            "optimizations_applied": len([o for o in optimizations if "removed" in o["type"]]),
            "optimizations": optimizations,
            "recommendations": [
                "Review dependency necessity - some may be organizational rather than technical",
                "Consider breaking down complex dependencies into smaller, parallelizable tasks",
                "Set up automated dependency completion notifications"
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/resource-allocation", response_model=ResourceAllocationResponse)
async def analyze_project_resource_allocation(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze resource allocation and workload distribution for a project.
    """
    try:
        from sqlalchemy import select, func
        from app.models.task import Task, TaskStatus
        from app.models.user import User
        from app.models.project import Project
        
        # Get project
        project_query = select(Project).where(Project.id == project_id)
        result = await db.execute(project_query)
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get project tasks with assignees
        tasks_query = select(Task).where(
            Task.project_id == project_id,
            Task.is_active == True
        )
        result = await db.execute(tasks_query)
        tasks = result.scalars().all()
        
        # Get unique assignees
        assignee_ids = list(set([t.assignee_id for t in tasks if t.assignee_id]))
        
        if assignee_ids:
            users_query = select(User).where(User.id.in_(assignee_ids))
            result = await db.execute(users_query)
            team_members = result.scalars().all()
        else:
            team_members = []
        
        # Analyze workload distribution
        workload_distribution = {}
        
        for user in team_members:
            user_tasks = [t for t in tasks if t.assignee_id == user.id]
            active_tasks = [t for t in user_tasks if t.status in [TaskStatus.TODO, TaskStatus.IN_PROGRESS]]
            
            total_estimated_hours = sum(t.estimated_hours or 0 for t in active_tasks)
            avg_complexity = sum(t.complexity_score or 0 for t in active_tasks) / len(active_tasks) if active_tasks else 0
            
            workload_distribution[user.id] = {
                "user_name": f"{user.first_name} {user.last_name}",
                "active_tasks": len(active_tasks),
                "total_tasks": len(user_tasks),
                "estimated_hours": total_estimated_hours,
                "avg_complexity": round(avg_complexity, 1),
                "completed_tasks": len([t for t in user_tasks if t.status == TaskStatus.DONE])
            }
        
        # Generate recommendations
        recommendations = []
        
        if workload_distribution:
            max_workload = max(wd["active_tasks"] for wd in workload_distribution.values())
            min_workload = min(wd["active_tasks"] for wd in workload_distribution.values())
            
            if max_workload - min_workload > 3:
                recommendations.append({
                    "type": "workload_imbalance",
                    "message": "Significant workload imbalance detected",
                    "suggestion": "Redistribute tasks from overloaded to underutilized team members"
                })
            
            # Find overloaded team members
            overloaded_members = [
                uid for uid, wd in workload_distribution.items() 
                if wd["active_tasks"] > 5 or wd["estimated_hours"] > 40
            ]
            
            if overloaded_members:
                recommendations.append({
                    "type": "overload_warning",
                    "message": f"{len(overloaded_members)} team member(s) may be overloaded",
                    "suggestion": "Consider reducing task assignment or extending deadlines"
                })
        
        # Calculate capacity utilization
        unassigned_tasks = [t for t in tasks if not t.assignee_id and t.status != TaskStatus.DONE]
        total_tasks = len(tasks)
        assigned_tasks = total_tasks - len(unassigned_tasks)
        capacity_utilization = (assigned_tasks / total_tasks) if total_tasks > 0 else 0
        
        if len(unassigned_tasks) > 0:
            recommendations.append({
                "type": "unassigned_tasks",
                "message": f"{len(unassigned_tasks)} tasks are unassigned",
                "suggestion": "Use smart assignment to optimally distribute unassigned tasks"
            })
        
        return ResourceAllocationResponse(
            project_id=project_id,
            team_members=[
                {
                    "user_id": member.id,
                    "name": f"{member.first_name} {member.last_name}",
                    "email": member.email
                }
                for member in team_members
            ],
            workload_distribution=workload_distribution,
            recommendations=recommendations,
            capacity_utilization=round(capacity_utilization, 2)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/optimize-schedule")
async def optimize_project_schedule(
    project_id: int,
    target_completion_days: Optional[int] = Query(None, description="Target project completion in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Optimize project schedule for better resource utilization and timeline.
    """
    try:
        from sqlalchemy import select
        from app.models.task import Task, TaskStatus, TaskPriority
        from app.models.project import Project
        
        # Get project with tasks
        project_query = select(Project).where(Project.id == project_id)
        result = await db.execute(project_query)
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        tasks_query = select(Task).where(
            Task.project_id == project_id,
            Task.is_active == True,
            Task.status != TaskStatus.DONE
        )
        result = await db.execute(tasks_query)
        tasks = result.scalars().all()
        
        optimizations = []
        
        # Prioritize high-complexity, unassigned tasks
        high_complexity_unassigned = [
            t for t in tasks 
            if (t.complexity_score or 0) > 6 and not t.assignee_id
        ]
        
        for task in high_complexity_unassigned:
            task.priority = TaskPriority.HIGH
            optimizations.append({
                "task_id": task.id,
                "action": "priority_increased",
                "reason": "High complexity task needs immediate assignment"
            })
        
        # Set due dates based on complexity and priority
        target_date = datetime.utcnow() + timedelta(days=target_completion_days or 30)
        
        for task in tasks:
            if not task.due_date:
                complexity_days = (task.complexity_score or 5) // 2
                priority_multiplier = {
                    TaskPriority.URGENT: 0.5,
                    TaskPriority.HIGH: 0.7,
                    TaskPriority.MEDIUM: 1.0,
                    TaskPriority.LOW: 1.5
                }.get(task.priority, 1.0)
                
                estimated_days = max(1, int(complexity_days * priority_multiplier))
                task.due_date = datetime.utcnow() + timedelta(days=estimated_days)
                
                optimizations.append({
                    "task_id": task.id,
                    "action": "due_date_set",
                    "due_date": task.due_date.isoformat(),
                    "estimated_days": estimated_days
                })
        
        await db.commit()
        
        # Calculate schedule metrics
        total_estimated_hours = sum(t.estimated_hours or 0 for t in tasks)
        avg_complexity = sum(t.complexity_score or 0 for t in tasks) / len(tasks) if tasks else 0
        
        return {
            "project_id": project_id,
            "optimizations_applied": len(optimizations),
            "schedule_metrics": {
                "total_remaining_tasks": len(tasks),
                "total_estimated_hours": total_estimated_hours,
                "avg_complexity": round(avg_complexity, 1),
                "projected_completion": target_date.isoformat() if target_completion_days else None
            },
            "optimizations": optimizations,
            "recommendations": [
                "Monitor high-priority tasks daily for bottlenecks",
                "Consider parallel execution for independent tasks",
                "Regular standup meetings to track progress against optimized schedule",
                "Use smart assignment for optimal resource allocation"
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))