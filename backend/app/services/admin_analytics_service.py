"""
Admin Dashboard & Analytics Service
Day 7: Advanced admin dashboard with comprehensive analytics
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import statistics
from dataclasses import dataclass, asdict
from enum import Enum

from sqlalchemy import func, select, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.organization import Organization
from app.models.project import Project
from app.models.task import Task
from app.models.workflow import WorkflowTemplate, WorkflowExecution
from app.core.database import get_async_session


class AnalyticsTimeframe(str, Enum):
    """Analytics timeframe options"""
    LAST_24_HOURS = "24h"
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    LAST_YEAR = "1y"
    ALL_TIME = "all"


class MetricType(str, Enum):
    """Types of metrics we can track"""
    COUNT = "count"
    PERCENTAGE = "percentage"
    AVERAGE = "average"
    TOTAL = "total"
    RATE = "rate"


@dataclass
class AnalyticsMetric:
    """Individual analytics metric"""
    name: str
    value: float
    metric_type: MetricType
    timeframe: AnalyticsTimeframe
    change_percent: Optional[float] = None
    trend: Optional[str] = None  # "up", "down", "stable"
    unit: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DashboardSummary:
    """High-level dashboard summary"""
    total_users: int
    total_organizations: int
    total_projects: int
    total_tasks: int
    active_users_today: int
    tasks_completed_today: int
    system_health_score: float
    performance_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UserAnalytics:
    """User-focused analytics"""
    total_users: int
    active_users: Dict[str, int]  # timeframe -> count
    new_users: Dict[str, int]     # timeframe -> count
    user_engagement: Dict[str, float]  # engagement metrics
    top_organizations: List[Dict[str, Any]]
    user_activity_trends: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProjectAnalytics:
    """Project-focused analytics"""
    total_projects: int
    active_projects: int
    completed_projects: int
    project_completion_rate: float
    average_project_duration: float
    projects_by_status: Dict[str, int]
    top_performing_projects: List[Dict[str, Any]]
    project_health_distribution: Dict[str, int]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TaskAnalytics:
    """Task-focused analytics"""
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int
    task_completion_rate: float
    average_completion_time: float
    tasks_by_priority: Dict[str, int]
    tasks_by_status: Dict[str, int]
    productivity_trends: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowAnalytics:
    """Workflow automation analytics"""
    total_workflows: int
    active_workflows: int
    workflow_executions: int
    success_rate: float
    failed_executions: int
    average_execution_time: float
    most_used_workflows: List[Dict[str, Any]]
    workflow_performance: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AdminAnalyticsService:
    """
    Comprehensive admin analytics and dashboard service
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes cache
        
    def _get_timeframe_filter(self, timeframe: AnalyticsTimeframe) -> Optional[datetime]:
        """Get datetime filter for timeframe"""
        now = datetime.utcnow()
        
        if timeframe == AnalyticsTimeframe.LAST_24_HOURS:
            return now - timedelta(hours=24)
        elif timeframe == AnalyticsTimeframe.LAST_7_DAYS:
            return now - timedelta(days=7)
        elif timeframe == AnalyticsTimeframe.LAST_30_DAYS:
            return now - timedelta(days=30)
        elif timeframe == AnalyticsTimeframe.LAST_90_DAYS:
            return now - timedelta(days=90)
        elif timeframe == AnalyticsTimeframe.LAST_YEAR:
            return now - timedelta(days=365)
        else:  # ALL_TIME
            return None
    
    async def get_dashboard_summary(self, org_id: Optional[str] = None) -> DashboardSummary:
        """Get high-level dashboard summary"""
        cache_key = f"dashboard_summary_{org_id or 'global'}"
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.utcnow() - timestamp).seconds < self.cache_ttl:
                return DashboardSummary(**cached_data)
        
        async with get_async_session() as db:
            # Base queries
            user_query = select(func.count(User.id))
            org_query = select(func.count(Organization.id))
            project_query = select(func.count(Project.id))
            task_query = select(func.count(Task.id))
            
            # Apply organization filter if specified
            if org_id:
                project_query = project_query.where(Project.organization_id == org_id)
                task_query = task_query.where(Task.organization_id == org_id)
            
            # Execute queries
            total_users = (await db.execute(user_query)).scalar()
            total_organizations = (await db.execute(org_query)).scalar()
            total_projects = (await db.execute(project_query)).scalar()
            total_tasks = (await db.execute(task_query)).scalar()
            
            # Active users today
            today = datetime.utcnow().date()
            active_users_query = select(func.count(User.id)).where(
                func.date(User.last_login_at) == today
            )
            active_users_today = (await db.execute(active_users_query)).scalar() or 0
            
            # Tasks completed today
            completed_tasks_query = select(func.count(Task.id)).where(
                and_(
                    Task.status == 'completed',
                    func.date(Task.updated_at) == today
                )
            )
            if org_id:
                completed_tasks_query = completed_tasks_query.where(Task.organization_id == org_id)
            
            tasks_completed_today = (await db.execute(completed_tasks_query)).scalar() or 0
            
            # System health score (simplified calculation)
            system_health_score = min(100.0, (active_users_today / max(1, total_users)) * 200)
            
            # Performance score (based on task completion rate)
            completion_rate = (tasks_completed_today / max(1, total_tasks)) * 100
            performance_score = min(100.0, completion_rate * 10)
            
            summary = DashboardSummary(
                total_users=total_users,
                total_organizations=total_organizations,
                total_projects=total_projects,
                total_tasks=total_tasks,
                active_users_today=active_users_today,
                tasks_completed_today=tasks_completed_today,
                system_health_score=round(system_health_score, 2),
                performance_score=round(performance_score, 2)
            )
            
            # Cache the result
            self.cache[cache_key] = (summary.to_dict(), datetime.utcnow())
            
            return summary
    
    async def get_user_analytics(self, 
                                 timeframe: AnalyticsTimeframe = AnalyticsTimeframe.LAST_30_DAYS,
                                 org_id: Optional[str] = None) -> UserAnalytics:
        """Get comprehensive user analytics"""
        
        async with get_async_session() as db:
            # Base user query
            user_query = select(User)
            if org_id:
                # Filter users by organization membership (if we have such relationship)
                pass  # TODO: Add organization membership filtering
            
            # Get time filter
            time_filter = self._get_timeframe_filter(timeframe)
            
            # Total users
            total_users_query = select(func.count(User.id))
            total_users = (await db.execute(total_users_query)).scalar()
            
            # Active users by timeframe
            active_users = {}
            for tf in AnalyticsTimeframe:
                tf_filter = self._get_timeframe_filter(tf)
                if tf_filter:
                    active_query = select(func.count(User.id)).where(
                        User.last_login_at >= tf_filter
                    )
                    active_users[tf.value] = (await db.execute(active_query)).scalar() or 0
                else:
                    active_users[tf.value] = total_users
            
            # New users by timeframe
            new_users = {}
            for tf in AnalyticsTimeframe:
                tf_filter = self._get_timeframe_filter(tf)
                if tf_filter:
                    new_query = select(func.count(User.id)).where(
                        User.created_at >= tf_filter
                    )
                    new_users[tf.value] = (await db.execute(new_query)).scalar() or 0
                else:
                    new_users[tf.value] = total_users
            
            # User engagement metrics
            user_engagement = {
                "daily_active_rate": (active_users.get("24h", 0) / max(1, total_users)) * 100,
                "weekly_active_rate": (active_users.get("7d", 0) / max(1, total_users)) * 100,
                "monthly_active_rate": (active_users.get("30d", 0) / max(1, total_users)) * 100,
            }
            
            # Top organizations (placeholder)
            top_organizations = [
                {"name": "Sample Org", "user_count": 10, "activity_score": 85.5}
            ]
            
            # User activity trends (placeholder)
            user_activity_trends = [
                {"date": "2025-09-20", "active_users": 25, "new_users": 3},
                {"date": "2025-09-21", "active_users": 28, "new_users": 2},
                {"date": "2025-09-22", "active_users": 30, "new_users": 5},
                {"date": "2025-09-23", "active_users": 27, "new_users": 1},
                {"date": "2025-09-24", "active_users": 32, "new_users": 4},
            ]
            
            return UserAnalytics(
                total_users=total_users,
                active_users=active_users,
                new_users=new_users,
                user_engagement=user_engagement,
                top_organizations=top_organizations,
                user_activity_trends=user_activity_trends
            )
    
    async def get_project_analytics(self, 
                                    timeframe: AnalyticsTimeframe = AnalyticsTimeframe.LAST_30_DAYS,
                                    org_id: Optional[str] = None) -> ProjectAnalytics:
        """Get comprehensive project analytics"""
        
        async with get_async_session() as db:
            # Base project query
            project_query = select(Project)
            if org_id:
                project_query = project_query.where(Project.organization_id == org_id)
            
            # Total projects
            total_projects = (await db.execute(select(func.count(Project.id)))).scalar()
            
            # Active projects (not completed)
            active_projects_query = select(func.count(Project.id)).where(
                Project.status != 'completed'
            )
            if org_id:
                active_projects_query = active_projects_query.where(Project.organization_id == org_id)
            active_projects = (await db.execute(active_projects_query)).scalar() or 0
            
            # Completed projects
            completed_projects_query = select(func.count(Project.id)).where(
                Project.status == 'completed'
            )
            if org_id:
                completed_projects_query = completed_projects_query.where(Project.organization_id == org_id)
            completed_projects = (await db.execute(completed_projects_query)).scalar() or 0
            
            # Project completion rate
            project_completion_rate = (completed_projects / max(1, total_projects)) * 100
            
            # Average project duration (placeholder calculation)
            average_project_duration = 45.5  # days
            
            # Projects by status
            projects_by_status = {
                "active": active_projects,
                "completed": completed_projects,
                "on_hold": 0,  # TODO: Add when status field supports it
                "cancelled": 0
            }
            
            # Top performing projects (placeholder)
            top_performing_projects = [
                {
                    "name": "Project Alpha",
                    "completion_rate": 95.5,
                    "tasks_completed": 45,
                    "team_size": 8
                },
                {
                    "name": "Project Beta", 
                    "completion_rate": 87.2,
                    "tasks_completed": 32,
                    "team_size": 5
                }
            ]
            
            # Project health distribution
            project_health_distribution = {
                "excellent": int(total_projects * 0.3),
                "good": int(total_projects * 0.4),
                "fair": int(total_projects * 0.2),
                "poor": int(total_projects * 0.1)
            }
            
            return ProjectAnalytics(
                total_projects=total_projects,
                active_projects=active_projects,
                completed_projects=completed_projects,
                project_completion_rate=round(project_completion_rate, 2),
                average_project_duration=average_project_duration,
                projects_by_status=projects_by_status,
                top_performing_projects=top_performing_projects,
                project_health_distribution=project_health_distribution
            )
    
    async def get_task_analytics(self, 
                                 timeframe: AnalyticsTimeframe = AnalyticsTimeframe.LAST_30_DAYS,
                                 org_id: Optional[str] = None) -> TaskAnalytics:
        """Get comprehensive task analytics"""
        
        async with get_async_session() as db:
            # Base task query
            task_query = select(Task)
            if org_id:
                task_query = task_query.where(Task.organization_id == org_id)
            
            # Total tasks
            total_tasks_query = select(func.count(Task.id))
            if org_id:
                total_tasks_query = total_tasks_query.where(Task.organization_id == org_id)
            total_tasks = (await db.execute(total_tasks_query)).scalar()
            
            # Completed tasks
            completed_tasks_query = select(func.count(Task.id)).where(
                Task.status == 'completed'
            )
            if org_id:
                completed_tasks_query = completed_tasks_query.where(Task.organization_id == org_id)
            completed_tasks = (await db.execute(completed_tasks_query)).scalar() or 0
            
            # Pending tasks
            pending_tasks_query = select(func.count(Task.id)).where(
                Task.status.in_(['todo', 'in_progress'])
            )
            if org_id:
                pending_tasks_query = pending_tasks_query.where(Task.organization_id == org_id)
            pending_tasks = (await db.execute(pending_tasks_query)).scalar() or 0
            
            # Overdue tasks
            now = datetime.utcnow()
            overdue_tasks_query = select(func.count(Task.id)).where(
                and_(
                    Task.due_date < now,
                    Task.status != 'completed'
                )
            )
            if org_id:
                overdue_tasks_query = overdue_tasks_query.where(Task.organization_id == org_id)
            overdue_tasks = (await db.execute(overdue_tasks_query)).scalar() or 0
            
            # Task completion rate
            task_completion_rate = (completed_tasks / max(1, total_tasks)) * 100
            
            # Average completion time (placeholder)
            average_completion_time = 3.5  # days
            
            # Tasks by priority
            tasks_by_priority = {
                "high": 0,
                "medium": 0,
                "low": 0
            }
            
            # Get actual priority distribution
            priority_query = select(Task.priority, func.count(Task.id)).group_by(Task.priority)
            if org_id:
                priority_query = priority_query.where(Task.organization_id == org_id)
            
            priority_results = await db.execute(priority_query)
            for priority, count in priority_results.fetchall():
                if priority in tasks_by_priority:
                    tasks_by_priority[priority] = count
            
            # Tasks by status
            tasks_by_status = {}
            status_query = select(Task.status, func.count(Task.id)).group_by(Task.status)
            if org_id:
                status_query = status_query.where(Task.organization_id == org_id)
            
            status_results = await db.execute(status_query)
            for status, count in status_results.fetchall():
                tasks_by_status[status] = count
            
            # Productivity trends (placeholder)
            productivity_trends = [
                {"date": "2025-09-20", "completed": 15, "created": 12},
                {"date": "2025-09-21", "completed": 18, "created": 14},
                {"date": "2025-09-22", "completed": 22, "created": 16},
                {"date": "2025-09-23", "completed": 17, "created": 13},
                {"date": "2025-09-24", "completed": 25, "created": 18},
            ]
            
            return TaskAnalytics(
                total_tasks=total_tasks,
                completed_tasks=completed_tasks,
                pending_tasks=pending_tasks,
                overdue_tasks=overdue_tasks,
                task_completion_rate=round(task_completion_rate, 2),
                average_completion_time=average_completion_time,
                tasks_by_priority=tasks_by_priority,
                tasks_by_status=tasks_by_status,
                productivity_trends=productivity_trends
            )
    
    async def get_workflow_analytics(self, 
                                     timeframe: AnalyticsTimeframe = AnalyticsTimeframe.LAST_30_DAYS,
                                     org_id: Optional[str] = None) -> WorkflowAnalytics:
        """Get comprehensive workflow analytics"""
        
        async with get_async_session() as db:
            # Total workflows
            workflow_query = select(func.count(WorkflowTemplate.id))
            if org_id:
                workflow_query = workflow_query.where(WorkflowTemplate.organization_id == org_id)
            total_workflows = (await db.execute(workflow_query)).scalar() or 0
            
            # Active workflows (use is_public or is_system_template as active indicator)
            active_workflow_query = select(func.count(WorkflowTemplate.id)).where(
                or_(WorkflowTemplate.is_public == True, WorkflowTemplate.is_system_template == True)
            )
            if org_id:
                active_workflow_query = active_workflow_query.where(WorkflowTemplate.organization_id == org_id)
            active_workflows = (await db.execute(active_workflow_query)).scalar() or 0
            
            # Workflow executions (placeholder - depends on execution tracking)
            workflow_executions = 150
            
            # Success rate (placeholder)
            success_rate = 92.5
            
            # Failed executions (placeholder)
            failed_executions = int(workflow_executions * (1 - success_rate / 100))
            
            # Average execution time (placeholder)
            average_execution_time = 4.2  # seconds
            
            # Most used workflows (placeholder)
            most_used_workflows = [
                {"name": "Task Assignment", "executions": 45, "success_rate": 95.5},
                {"name": "Project Setup", "executions": 32, "success_rate": 88.2},
                {"name": "Review Process", "executions": 28, "success_rate": 94.1}
            ]
            
            # Workflow performance (placeholder)
            workflow_performance = [
                {"workflow": "Task Assignment", "avg_time": 2.1, "success_rate": 95.5},
                {"workflow": "Project Setup", "avg_time": 8.5, "success_rate": 88.2},
                {"workflow": "Review Process", "avg_time": 3.2, "success_rate": 94.1}
            ]
            
            return WorkflowAnalytics(
                total_workflows=total_workflows,
                active_workflows=active_workflows,
                workflow_executions=workflow_executions,
                success_rate=success_rate,
                failed_executions=failed_executions,
                average_execution_time=average_execution_time,
                most_used_workflows=most_used_workflows,
                workflow_performance=workflow_performance
            )
    
    async def get_custom_metrics(self, 
                                 metric_names: List[str],
                                 timeframe: AnalyticsTimeframe = AnalyticsTimeframe.LAST_30_DAYS,
                                 org_id: Optional[str] = None) -> List[AnalyticsMetric]:
        """Get custom analytics metrics"""
        
        metrics = []
        
        for metric_name in metric_names:
            # This is a placeholder implementation
            # In a real system, you'd have a registry of available metrics
            if metric_name == "user_growth_rate":
                metrics.append(AnalyticsMetric(
                    name="User Growth Rate",
                    value=12.5,
                    metric_type=MetricType.PERCENTAGE,
                    timeframe=timeframe,
                    change_percent=2.3,
                    trend="up",
                    unit="%"
                ))
            elif metric_name == "task_velocity":
                metrics.append(AnalyticsMetric(
                    name="Task Velocity",
                    value=8.2,
                    metric_type=MetricType.AVERAGE,
                    timeframe=timeframe,
                    change_percent=-1.5,
                    trend="down",
                    unit="tasks/day"
                ))
            elif metric_name == "system_uptime":
                metrics.append(AnalyticsMetric(
                    name="System Uptime",
                    value=99.8,
                    metric_type=MetricType.PERCENTAGE,
                    timeframe=timeframe,
                    change_percent=0.1,
                    trend="stable",
                    unit="%"
                ))
        
        return metrics
    
    async def export_analytics_report(self, 
                                      timeframe: AnalyticsTimeframe = AnalyticsTimeframe.LAST_30_DAYS,
                                      org_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive analytics report for export"""
        
        # Gather all analytics data
        dashboard_summary = await self.get_dashboard_summary(org_id)
        user_analytics = await self.get_user_analytics(timeframe, org_id)
        project_analytics = await self.get_project_analytics(timeframe, org_id)
        task_analytics = await self.get_task_analytics(timeframe, org_id)
        workflow_analytics = await self.get_workflow_analytics(timeframe, org_id)
        
        report = {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "timeframe": timeframe.value,
                "organization_id": org_id,
                "report_version": "1.0"
            },
            "dashboard_summary": dashboard_summary.to_dict(),
            "user_analytics": user_analytics.to_dict(),
            "project_analytics": project_analytics.to_dict(),
            "task_analytics": task_analytics.to_dict(),
            "workflow_analytics": workflow_analytics.to_dict()
        }
        
        return report


# Global analytics service instance
admin_analytics_service = AdminAnalyticsService()