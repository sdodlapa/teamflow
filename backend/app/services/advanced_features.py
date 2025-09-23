"""
Business logic services for advanced task features.
Handles complex operations, analytics calculations, and workflow automation.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import json
from collections import defaultdict

from sqlalchemy import and_, func, select, desc, asc, text, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.time_tracking import (
    TaskTimeLog, TaskTemplate, TaskActivity, TaskMention, TaskAssignmentHistory
)
from app.models.organization import Organization
from app.models.project import Project
from app.schemas.advanced_features import (
    ProductivityMetrics, TeamPerformanceMetrics, ProjectHealthMetrics,
    AnalyticsDashboardData, TaskAnalyticsFilter
)


class TimeTrackingService:
    """Service for time tracking operations and calculations."""
    
    @staticmethod
    async def get_user_daily_summary(
        db: AsyncSession, 
        user_id: int, 
        date: datetime
    ) -> Dict[str, Any]:
        """Get daily time tracking summary for a user."""
        
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        query = select(
            func.sum(TaskTimeLog.duration_minutes).label('total_minutes'),
            func.sum(func.case((TaskTimeLog.is_billable == True, TaskTimeLog.duration_minutes), else_=0)).label('billable_minutes'),
            func.count(TaskTimeLog.id).label('entries_count'),
            func.count(func.distinct(TaskTimeLog.task_id)).label('tasks_count')
        ).where(
            and_(
                TaskTimeLog.user_id == user_id,
                TaskTimeLog.start_time >= start_of_day,
                TaskTimeLog.start_time < end_of_day,
                TaskTimeLog.is_active == True,
                TaskTimeLog.end_time.isnot(None)
            )
        )
        
        result = await db.execute(query)
        row = result.first()
        
        return {
            "date": date.date(),
            "total_minutes": row.total_minutes or 0,
            "total_hours": round((row.total_minutes or 0) / 60, 2),
            "billable_minutes": row.billable_minutes or 0,
            "billable_hours": round((row.billable_minutes or 0) / 60, 2),
            "entries_count": row.entries_count or 0,
            "tasks_count": row.tasks_count or 0
        }
    
    @staticmethod
    async def get_project_time_breakdown(
        db: AsyncSession,
        project_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get time breakdown by user for a project."""
        
        query = select(
            TaskTimeLog.user_id,
            User.full_name,
            func.sum(TaskTimeLog.duration_minutes).label('total_minutes'),
            func.sum(func.case((TaskTimeLog.is_billable == True, TaskTimeLog.duration_minutes), else_=0)).label('billable_minutes'),
            func.count(TaskTimeLog.id).label('entries_count')
        ).select_from(
            TaskTimeLog
        ).join(
            Task, TaskTimeLog.task_id == Task.id
        ).join(
            User, TaskTimeLog.user_id == User.id
        ).where(
            and_(
                Task.project_id == project_id,
                TaskTimeLog.is_active == True,
                TaskTimeLog.end_time.isnot(None)
            )
        )
        
        if start_date:
            query = query.where(TaskTimeLog.start_time >= start_date)
        if end_date:
            query = query.where(TaskTimeLog.start_time <= end_date)
        
        query = query.group_by(TaskTimeLog.user_id, User.full_name)
        query = query.order_by(desc('total_minutes'))
        
        result = await db.execute(query)
        rows = result.all()
        
        return [
            {
                "user_id": row.user_id,
                "user_name": row.full_name,
                "total_minutes": row.total_minutes,
                "total_hours": round(row.total_minutes / 60, 2),
                "billable_minutes": row.billable_minutes,
                "billable_hours": round(row.billable_minutes / 60, 2),
                "entries_count": row.entries_count
            }
            for row in rows
        ]
    
    @staticmethod
    async def calculate_productivity_score(
        db: AsyncSession,
        user_id: int,
        days: int = 30
    ) -> float:
        """Calculate productivity score based on various metrics."""
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get time tracking data
        time_query = select(
            func.sum(TaskTimeLog.duration_minutes).label('total_minutes'),
            func.count(TaskTimeLog.id).label('entries_count')
        ).where(
            and_(
                TaskTimeLog.user_id == user_id,
                TaskTimeLog.start_time >= start_date,
                TaskTimeLog.is_active == True,
                TaskTimeLog.end_time.isnot(None)
            )
        )
        
        time_result = await db.execute(time_query)
        time_row = time_result.first()
        
        # Get task completion data
        task_query = select(
            func.count(func.case((Task.status == TaskStatus.DONE.value, 1))).label('completed_tasks'),
            func.count(Task.id).label('total_tasks'),
            func.avg(
                func.extract('epoch', Task.updated_at - Task.created_at) / 3600
            ).label('avg_completion_hours')
        ).where(
            and_(
                or_(Task.assignee_id == user_id, Task.created_by == user_id),
                Task.created_at >= start_date,
                Task.is_active == True
            )
        )
        
        task_result = await db.execute(task_query)
        task_row = task_result.first()
        
        # Calculate productivity components
        time_logged_hours = (time_row.total_minutes or 0) / 60
        completion_rate = (
            (task_row.completed_tasks or 0) / (task_row.total_tasks or 1)
        ) * 100
        
        avg_completion_time = task_row.avg_completion_hours or 24
        time_efficiency = max(0, 100 - (avg_completion_time / 24) * 100)
        
        activity_score = min(100, (time_logged_hours / (days * 8)) * 100)
        
        # Weighted productivity score
        productivity_score = (
            completion_rate * 0.4 +
            time_efficiency * 0.3 +
            activity_score * 0.3
        )
        
        return min(100, max(0, productivity_score))


class AnalyticsService:
    """Service for advanced analytics and reporting."""
    
    @staticmethod
    async def get_team_performance_metrics(
        db: AsyncSession,
        team_user_ids: List[int],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> TeamPerformanceMetrics:
        """Calculate comprehensive team performance metrics."""
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Task completion metrics
        task_query = select(
            func.count(func.case((Task.status == TaskStatus.DONE.value, 1))).label('completed_tasks'),
            func.count(Task.id).label('total_tasks'),
            func.avg(
                func.extract('epoch', Task.updated_at - Task.created_at) / 3600
            ).label('avg_completion_hours'),
            func.count(func.case((Task.due_date < Task.updated_at, 1))).label('overdue_completed')
        ).where(
            and_(
                Task.assignee_id.in_(team_user_ids),
                Task.created_at >= start_date,
                Task.created_at <= end_date,
                Task.is_active == True
            )
        )
        
        task_result = await db.execute(task_query)
        task_row = task_result.first()
        
        # Time tracking metrics
        time_query = select(
            func.sum(TaskTimeLog.duration_minutes).label('total_minutes'),
            func.avg(TaskTimeLog.duration_minutes).label('avg_session_minutes')
        ).select_from(TaskTimeLog).join(Task).where(
            and_(
                TaskTimeLog.user_id.in_(team_user_ids),
                TaskTimeLog.start_time >= start_date,
                TaskTimeLog.start_time <= end_date,
                TaskTimeLog.is_active == True,
                TaskTimeLog.end_time.isnot(None)
            )
        )
        
        time_result = await db.execute(time_query)
        time_row = time_result.first()
        
        # Calculate metrics
        total_tasks = task_row.total_tasks or 0
        completed_tasks = task_row.completed_tasks or 0
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        total_hours = (time_row.total_minutes or 0) / 60
        avg_completion_time = task_row.avg_completion_hours or 0
        on_time_completion_rate = (
            ((completed_tasks - (task_row.overdue_completed or 0)) / completed_tasks * 100)
            if completed_tasks > 0 else 100
        )
        
        return TeamPerformanceMetrics(
            total_tasks_completed=completed_tasks,
            average_completion_time_hours=round(avg_completion_time, 2),
            team_completion_rate=round(completion_rate, 2),
            total_hours_logged=round(total_hours, 2),
            average_session_length_minutes=round(time_row.avg_session_minutes or 0, 2),
            on_time_completion_rate=round(on_time_completion_rate, 2),
            team_size=len(team_user_ids)
        )
    
    @staticmethod
    async def get_project_health_metrics(
        db: AsyncSession,
        project_id: int
    ) -> ProjectHealthMetrics:
        """Calculate project health indicators."""
        
        # Task status distribution
        status_query = select(
            Task.status,
            func.count(Task.id).label('count')
        ).where(
            and_(Task.project_id == project_id, Task.is_active == True)
        ).group_by(Task.status)
        
        status_result = await db.execute(status_query)
        status_data = {row.status: row.count for row in status_result.all()}
        
        total_tasks = sum(status_data.values())
        
        # Progress calculation
        completed_tasks = status_data.get(TaskStatus.DONE.value, 0)
        in_progress_tasks = status_data.get(TaskStatus.IN_PROGRESS.value, 0)
        progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Overdue tasks
        overdue_query = select(func.count(Task.id)).where(
            and_(
                Task.project_id == project_id,
                Task.due_date < datetime.utcnow(),
                Task.status != TaskStatus.DONE.value,
                Task.is_active == True
            )
        )
        overdue_result = await db.execute(overdue_query)
        overdue_tasks = overdue_result.scalar() or 0
        
        # Risk assessment
        overdue_percentage = (overdue_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        if overdue_percentage > 20:
            risk_level = "high"
        elif overdue_percentage > 10:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Team activity
        activity_query = select(
            func.count(func.distinct(TaskActivity.user_id))
        ).select_from(TaskActivity).join(Task).where(
            and_(
                Task.project_id == project_id,
                TaskActivity.created_at >= datetime.utcnow() - timedelta(days=7)
            )
        )
        
        activity_result = await db.execute(activity_query)
        active_team_members = activity_result.scalar() or 0
        
        return ProjectHealthMetrics(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            in_progress_tasks=in_progress_tasks,
            overdue_tasks=overdue_tasks,
            progress_percentage=round(progress_percentage, 2),
            risk_level=risk_level,
            active_team_members=active_team_members,
            task_status_distribution=status_data
        )


class MentionService:
    """Service for handling @mentions and notifications."""
    
    @staticmethod
    async def process_mentions_in_text(
        db: AsyncSession,
        text: str,
        task_id: int,
        mentioned_by_user_id: int,
        context_type: str = "comment"
    ) -> List[TaskMention]:
        """Extract and process @mentions from text."""
        
        import re
        
        # Extract @username patterns
        mention_pattern = r'@(\w+)'
        mentioned_usernames = re.findall(mention_pattern, text)
        
        if not mentioned_usernames:
            return []
        
        # Find users by username
        users_query = select(User).where(User.username.in_(mentioned_usernames))
        users_result = await db.execute(users_query)
        users = {user.username: user for user in users_result.scalars().all()}
        
        mentions = []
        for username in mentioned_usernames:
            if username in users:
                user = users[username]
                
                # Create mention record
                mention = TaskMention(
                    task_id=task_id,
                    mentioned_user_id=user.id,
                    mentioned_by_user_id=mentioned_by_user_id,
                    context=text[:500],  # Limit context length
                    context_type=context_type
                )
                
                db.add(mention)
                mentions.append(mention)
        
        return mentions
    
    @staticmethod
    async def mark_mentions_as_read(
        db: AsyncSession,
        user_id: int,
        mention_ids: List[int]
    ) -> int:
        """Mark multiple mentions as read for a user."""
        
        from sqlalchemy import update
        
        stmt = update(TaskMention).where(
            and_(
                TaskMention.id.in_(mention_ids),
                TaskMention.mentioned_user_id == user_id,
                TaskMention.is_read == False
            )
        ).values(
            is_read=True,
            read_at=datetime.utcnow()
        )
        
        result = await db.execute(stmt)
        await db.commit()
        
        return result.rowcount


class TaskTemplateService:
    """Service for task template operations."""
    
    @staticmethod
    async def get_popular_templates(
        db: AsyncSession,
        organization_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get most used templates in an organization."""
        
        query = select(TaskTemplate).where(
            and_(
                TaskTemplate.organization_id == organization_id,
                TaskTemplate.is_active == True
            )
        ).order_by(desc(TaskTemplate.usage_count)).limit(limit)
        
        result = await db.execute(query)
        templates = result.scalars().all()
        
        return [
            {
                "id": template.id,
                "name": template.name,
                "category": template.category,
                "usage_count": template.usage_count,
                "estimated_hours": template.estimated_hours,
                "priority": template.priority
            }
            for template in templates
        ]
    
    @staticmethod
    async def analyze_template_effectiveness(
        db: AsyncSession,
        template_id: int
    ) -> Dict[str, Any]:
        """Analyze how effectively a template is being used."""
        
        # Get tasks created from this template
        tasks_query = select(Task).join(TaskActivity).where(
            and_(
                TaskActivity.activity_type == "task_created_from_template",
                TaskActivity.activity_data.like(f'%"template_id": {template_id}%'),
                Task.is_active == True
            )
        )
        
        tasks_result = await db.execute(tasks_query)
        tasks = tasks_result.scalars().all()
        
        if not tasks:
            return {
                "template_id": template_id,
                "tasks_created": 0,
                "completion_rate": 0,
                "average_completion_time_hours": 0,
                "effectiveness_score": 0
            }
        
        completed_tasks = [t for t in tasks if t.status == TaskStatus.DONE.value]
        completion_rate = len(completed_tasks) / len(tasks) * 100
        
        # Calculate average completion time for completed tasks
        completion_times = []
        for task in completed_tasks:
            if task.updated_at and task.created_at:
                completion_time = (task.updated_at - task.created_at).total_seconds() / 3600
                completion_times.append(completion_time)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # Calculate effectiveness score
        # Based on completion rate and reasonable completion time
        time_score = max(0, 100 - (avg_completion_time / 168))  # 168 hours = 1 week
        effectiveness_score = (completion_rate * 0.7) + (time_score * 0.3)
        
        return {
            "template_id": template_id,
            "tasks_created": len(tasks),
            "completion_rate": round(completion_rate, 2),
            "average_completion_time_hours": round(avg_completion_time, 2),
            "effectiveness_score": round(effectiveness_score, 2)
        }


class WorkflowAutomationService:
    """Service for automated workflows and task management."""
    
    @staticmethod
    async def auto_assign_tasks(
        db: AsyncSession,
        project_id: int,
        task_ids: List[int]
    ) -> Dict[int, int]:
        """Automatically assign tasks based on workload and expertise."""
        
        # Get project team members
        # This would integrate with existing project membership logic
        
        # Get team members' current workload
        workload_query = select(
            Task.assignee_id,
            func.count(Task.id).label('active_tasks'),
            func.sum(Task.estimated_hours).label('estimated_hours')
        ).where(
            and_(
                Task.project_id == project_id,
                Task.status.in_([TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value]),
                Task.assignee_id.isnot(None),
                Task.is_active == True
            )
        ).group_by(Task.assignee_id)
        
        workload_result = await db.execute(workload_query)
        workloads = {row.assignee_id: row.active_tasks for row in workload_result.all()}
        
        # Simple round-robin assignment for now
        # In a real implementation, this would consider skills, availability, etc.
        
        assignments = {}
        team_members = list(workloads.keys()) if workloads else []
        
        if team_members:
            for i, task_id in enumerate(task_ids):
                # Assign to team member with least current workload
                assignee_id = min(team_members, key=lambda x: workloads.get(x, 0))
                assignments[task_id] = assignee_id
                workloads[assignee_id] = workloads.get(assignee_id, 0) + 1
        
        return assignments
    
    @staticmethod
    async def escalate_overdue_tasks(
        db: AsyncSession,
        organization_id: int
    ) -> List[Dict[str, Any]]:
        """Identify and escalate overdue tasks."""
        
        overdue_query = select(Task).options(
            selectinload(Task.assignee),
            selectinload(Task.project)
        ).where(
            and_(
                Task.due_date < datetime.utcnow(),
                Task.status != TaskStatus.DONE.value,
                Task.is_active == True
            )
        ).join(Project).where(Project.organization_id == organization_id)
        
        overdue_result = await db.execute(overdue_query)
        overdue_tasks = overdue_result.scalars().all()
        
        escalations = []
        for task in overdue_tasks:
            days_overdue = (datetime.utcnow() - task.due_date).days
            
            escalation_level = "low"
            if days_overdue > 7:
                escalation_level = "high"
            elif days_overdue > 3:
                escalation_level = "medium"
            
            escalations.append({
                "task_id": task.id,
                "task_title": task.title,
                "assignee_name": task.assignee.full_name if task.assignee else None,
                "project_name": task.project.name if task.project else None,
                "days_overdue": days_overdue,
                "escalation_level": escalation_level,
                "priority": task.priority
            })
        
        return escalations