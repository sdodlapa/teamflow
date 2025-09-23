"""
Advanced analytics service for TeamFlow.
Provides comprehensive business intelligence and reporting capabilities.
"""
import json
import asyncio
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from sqlalchemy import and_, or_, text, func, desc, asc, between
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import get_db
from app.models.analytics import (
    ReportTemplate, Report, ReportExport, ReportSchedule,
    Dashboard, DashboardWidget, AnalyticsMetric, ReportAlert,
    ReportType, ReportFormat, ChartType, MetricType
)
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.project import Project, ProjectStatus
from app.models.user import User, UserStatus
from app.models.time_tracking import TaskTimeLog
from app.schemas.analytics import (
    ReportGenerationRequest, ReportResponse, DashboardRequest,
    DashboardWidgetRequest, AnalyticsMetricRequest, MetricsQueryRequest,
    DateRangeRequest
)
from app.schemas.user import UserRead


class AnalyticsCalculatorService:
    """Service for calculating analytics metrics and KPIs."""
    
    def __init__(self):
        self.metric_calculators = {
            "task_completion_rate": self._calculate_task_completion_rate,
            "project_progress": self._calculate_project_progress,
            "user_productivity": self._calculate_user_productivity,
            "time_utilization": self._calculate_time_utilization,
            "deadline_adherence": self._calculate_deadline_adherence,
            "workload_distribution": self._calculate_workload_distribution,
            "team_velocity": self._calculate_team_velocity,
            "bug_resolution_time": self._calculate_bug_resolution_time,
            "resource_allocation": self._calculate_resource_allocation,
            "milestone_achievement": self._calculate_milestone_achievement,
        }
    
    async def calculate_metric(
        self,
        metric_name: str,
        organization_id: int,
        period_start: date,
        period_end: date,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Calculate a specific metric for the given parameters."""
        
        calculator = self.metric_calculators.get(metric_name)
        if not calculator:
            raise ValueError(f"Unknown metric: {metric_name}")
        
        try:
            return await calculator(
                organization_id, period_start, period_end, entity_type, entity_id, db
            )
        except Exception as e:
            return {
                "value": 0.0,
                "error": str(e),
                "confidence_score": 0.0,
                "is_estimated": True
            }
    
    async def _calculate_task_completion_rate(
        self, organization_id: int, period_start: date, period_end: date,
        entity_type: Optional[str], entity_id: Optional[int], db: Session
    ) -> Dict[str, Any]:
        """Calculate task completion rate for the period."""
        
        # Base query for tasks in the period
        query = db.query(Task).filter(
            Task.organization_id == organization_id,
            Task.created_at >= period_start,
            Task.created_at <= period_end
        )
        
        # Apply entity filter if specified
        if entity_type == "project" and entity_id:
            query = query.filter(Task.project_id == entity_id)
        elif entity_type == "user" and entity_id:
            query = query.filter(Task.assigned_to == entity_id)
        
        total_tasks = query.count()
        if total_tasks == 0:
            return {"value": 0.0, "unit": "percentage", "confidence_score": 0.0}
        
        completed_tasks = query.filter(Task.status == TaskStatus.COMPLETED).count()
        completion_rate = (completed_tasks / total_tasks) * 100
        
        return {
            "value": completion_rate,
            "unit": "percentage",
            "confidence_score": 1.0,
            "calculation_method": f"Completed tasks ({completed_tasks}) / Total tasks ({total_tasks}) * 100",
            "source_data": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks
            }
        }
    
    async def _calculate_project_progress(
        self, organization_id: int, period_start: date, period_end: date,
        entity_type: Optional[str], entity_id: Optional[int], db: Session
    ) -> Dict[str, Any]:
        """Calculate overall project progress."""
        
        # Query projects in the organization
        query = db.query(Project).filter(
            Project.organization_id == organization_id
        )
        
        if entity_type == "project" and entity_id:
            query = query.filter(Project.id == entity_id)
        
        projects = query.all()
        if not projects:
            return {"value": 0.0, "unit": "percentage", "confidence_score": 0.0}
        
        total_progress = 0.0
        valid_projects = 0
        
        for project in projects:
            # Calculate progress based on completed tasks
            total_tasks = len(project.tasks) if project.tasks else 0
            if total_tasks > 0:
                completed_tasks = sum(1 for task in project.tasks if task.status == TaskStatus.COMPLETED)
                project_progress = (completed_tasks / total_tasks) * 100
                total_progress += project_progress
                valid_projects += 1
        
        if valid_projects == 0:
            return {"value": 0.0, "unit": "percentage", "confidence_score": 0.0}
        
        average_progress = total_progress / valid_projects
        
        return {
            "value": average_progress,
            "unit": "percentage",
            "confidence_score": 1.0,
            "calculation_method": f"Average progress across {valid_projects} projects",
            "source_data": {
                "total_projects": len(projects),
                "valid_projects": valid_projects,
                "total_progress": total_progress
            }
        }
    
    async def _calculate_user_productivity(
        self, organization_id: int, period_start: date, period_end: date,
        entity_type: Optional[str], entity_id: Optional[int], db: Session
    ) -> Dict[str, Any]:
        """Calculate user productivity metrics."""
        
        # Query time logs for the period
        query = db.query(TaskTimeLog).filter(
            TaskTimeLog.organization_id == organization_id,
            TaskTimeLog.logged_date >= period_start,
            TaskTimeLog.logged_date <= period_end
        )
        
        if entity_type == "user" and entity_id:
            query = query.filter(TaskTimeLog.user_id == entity_id)
        elif entity_type == "project" and entity_id:
            query = query.join(Task).filter(Task.project_id == entity_id)
        
        time_logs = query.all()
        if not time_logs:
            return {"value": 0.0, "unit": "hours_per_day", "confidence_score": 0.0}
        
        # Calculate total hours and working days
        total_hours = sum(float(log.hours_logged) for log in time_logs if log.hours_logged)
        unique_dates = set(log.logged_date for log in time_logs)
        working_days = len(unique_dates)
        
        if working_days == 0:
            return {"value": 0.0, "unit": "hours_per_day", "confidence_score": 0.0}
        
        productivity = total_hours / working_days
        
        return {
            "value": productivity,
            "unit": "hours_per_day",
            "confidence_score": 1.0,
            "calculation_method": f"Total hours ({total_hours}) / Working days ({working_days})",
            "source_data": {
                "total_hours": total_hours,
                "working_days": working_days,
                "total_logs": len(time_logs)
            }
        }
    
    async def _calculate_time_utilization(
        self, organization_id: int, period_start: date, period_end: date,
        entity_type: Optional[str], entity_id: Optional[int], db: Session
    ) -> Dict[str, Any]:
        """Calculate time utilization efficiency."""
        
        # Get estimated vs actual time for completed tasks
        query = db.query(Task).filter(
            Task.organization_id == organization_id,
            Task.status == TaskStatus.COMPLETED,
            Task.completed_at >= period_start,
            Task.completed_at <= period_end,
            Task.estimated_hours.isnot(None)
        )
        
        if entity_type == "project" and entity_id:
            query = query.filter(Task.project_id == entity_id)
        elif entity_type == "user" and entity_id:
            query = query.filter(Task.assigned_to == entity_id)
        
        tasks = query.all()
        if not tasks:
            return {"value": 0.0, "unit": "percentage", "confidence_score": 0.0}
        
        total_estimated = 0.0
        total_actual = 0.0
        valid_tasks = 0
        
        for task in tasks:
            if task.estimated_hours and task.time_logs:
                estimated = float(task.estimated_hours)
                actual = sum(float(log.hours_logged) for log in task.time_logs if log.hours_logged)
                
                if estimated > 0 and actual > 0:
                    total_estimated += estimated
                    total_actual += actual
                    valid_tasks += 1
        
        if total_estimated == 0 or valid_tasks == 0:
            return {"value": 0.0, "unit": "percentage", "confidence_score": 0.0}
        
        # Calculate efficiency as estimated/actual (values closer to 100% are better)
        utilization = (total_estimated / total_actual) * 100
        utilization = min(utilization, 200)  # Cap at 200% to handle extreme cases
        
        return {
            "value": utilization,
            "unit": "percentage",
            "confidence_score": 1.0,
            "calculation_method": f"Estimated hours ({total_estimated}) / Actual hours ({total_actual}) * 100",
            "source_data": {
                "total_estimated": total_estimated,
                "total_actual": total_actual,
                "valid_tasks": valid_tasks
            }
        }
    
    async def _calculate_deadline_adherence(
        self, organization_id: int, period_start: date, period_end: date,
        entity_type: Optional[str], entity_id: Optional[int], db: Session
    ) -> Dict[str, Any]:
        """Calculate deadline adherence rate."""
        
        query = db.query(Task).filter(
            Task.organization_id == organization_id,
            Task.status == TaskStatus.COMPLETED,
            Task.completed_at >= period_start,
            Task.completed_at <= period_end,
            Task.due_date.isnot(None)
        )
        
        if entity_type == "project" and entity_id:
            query = query.filter(Task.project_id == entity_id)
        elif entity_type == "user" and entity_id:
            query = query.filter(Task.assigned_to == entity_id)
        
        tasks = query.all()
        if not tasks:
            return {"value": 0.0, "unit": "percentage", "confidence_score": 0.0}
        
        on_time_tasks = sum(1 for task in tasks if task.completed_at.date() <= task.due_date)
        adherence_rate = (on_time_tasks / len(tasks)) * 100
        
        return {
            "value": adherence_rate,
            "unit": "percentage",
            "confidence_score": 1.0,
            "calculation_method": f"On-time tasks ({on_time_tasks}) / Total tasks ({len(tasks)}) * 100",
            "source_data": {
                "total_tasks": len(tasks),
                "on_time_tasks": on_time_tasks,
                "late_tasks": len(tasks) - on_time_tasks
            }
        }
    
    async def _calculate_workload_distribution(
        self, organization_id: int, period_start: date, period_end: date,
        entity_type: Optional[str], entity_id: Optional[int], db: Session
    ) -> Dict[str, Any]:
        """Calculate workload distribution balance."""
        
        # Get active users in the organization
        users = db.query(User).filter(
            User.organization_id == organization_id,
            User.status == UserStatus.ACTIVE
        ).all()
        
        if not users:
            return {"value": 0.0, "unit": "balance_score", "confidence_score": 0.0}
        
        # Calculate task count per user
        user_task_counts = []
        for user in users:
            task_count = db.query(Task).filter(
                Task.assigned_to == user.id,
                Task.created_at >= period_start,
                Task.created_at <= period_end
            ).count()
            user_task_counts.append(task_count)
        
        if not user_task_counts or sum(user_task_counts) == 0:
            return {"value": 100.0, "unit": "balance_score", "confidence_score": 0.0}
        
        # Calculate standard deviation to measure distribution
        mean_tasks = sum(user_task_counts) / len(user_task_counts)
        variance = sum((x - mean_tasks) ** 2 for x in user_task_counts) / len(user_task_counts)
        std_dev = variance ** 0.5
        
        # Convert to balance score (100 = perfect balance, lower = more imbalanced)
        if mean_tasks == 0:
            balance_score = 100.0
        else:
            coefficient_variation = (std_dev / mean_tasks) * 100
            balance_score = max(0, 100 - coefficient_variation)
        
        return {
            "value": balance_score,
            "unit": "balance_score",
            "confidence_score": 1.0,
            "calculation_method": f"100 - (std_dev / mean * 100), std_dev: {std_dev:.2f}, mean: {mean_tasks:.2f}",
            "source_data": {
                "user_count": len(users),
                "task_counts": user_task_counts,
                "mean_tasks": mean_tasks,
                "std_deviation": std_dev
            }
        }
    
    async def _calculate_team_velocity(
        self, organization_id: int, period_start: date, period_end: date,
        entity_type: Optional[str], entity_id: Optional[int], db: Session
    ) -> Dict[str, Any]:
        """Calculate team velocity (tasks completed per time period)."""
        
        query = db.query(Task).filter(
            Task.organization_id == organization_id,
            Task.status == TaskStatus.COMPLETED,
            Task.completed_at >= period_start,
            Task.completed_at <= period_end
        )
        
        if entity_type == "project" and entity_id:
            query = query.filter(Task.project_id == entity_id)
        
        completed_tasks = query.count()
        period_days = (period_end - period_start).days + 1
        
        if period_days == 0:
            return {"value": 0.0, "unit": "tasks_per_day", "confidence_score": 0.0}
        
        velocity = completed_tasks / period_days
        
        return {
            "value": velocity,
            "unit": "tasks_per_day",
            "confidence_score": 1.0,
            "calculation_method": f"Completed tasks ({completed_tasks}) / Period days ({period_days})",
            "source_data": {
                "completed_tasks": completed_tasks,
                "period_days": period_days
            }
        }
    
    async def _calculate_bug_resolution_time(
        self, organization_id: int, period_start: date, period_end: date,
        entity_type: Optional[str], entity_id: Optional[int], db: Session
    ) -> Dict[str, Any]:
        """Calculate average bug resolution time."""
        
        # Assuming bug tasks have a label or tag
        query = db.query(Task).filter(
            Task.organization_id == organization_id,
            Task.status == TaskStatus.COMPLETED,
            Task.completed_at >= period_start,
            Task.completed_at <= period_end
        )
        
        # Filter for bug-related tasks (this would need to be customized based on how bugs are tagged)
        tasks = query.all()
        bug_tasks = [task for task in tasks if task.labels and 'bug' in [label.lower() for label in task.labels]]
        
        if not bug_tasks:
            return {"value": 0.0, "unit": "hours", "confidence_score": 0.0}
        
        total_resolution_time = 0.0
        valid_bugs = 0
        
        for task in bug_tasks:
            if task.created_at and task.completed_at:
                resolution_time = (task.completed_at - task.created_at).total_seconds() / 3600  # Convert to hours
                total_resolution_time += resolution_time
                valid_bugs += 1
        
        if valid_bugs == 0:
            return {"value": 0.0, "unit": "hours", "confidence_score": 0.0}
        
        average_resolution_time = total_resolution_time / valid_bugs
        
        return {
            "value": average_resolution_time,
            "unit": "hours",
            "confidence_score": 1.0,
            "calculation_method": f"Total resolution time ({total_resolution_time:.2f}) / Valid bugs ({valid_bugs})",
            "source_data": {
                "total_bugs": len(bug_tasks),
                "valid_bugs": valid_bugs,
                "total_resolution_time": total_resolution_time
            }
        }
    
    async def _calculate_resource_allocation(
        self, organization_id: int, period_start: date, period_end: date,
        entity_type: Optional[str], entity_id: Optional[int], db: Session
    ) -> Dict[str, Any]:
        """Calculate resource allocation efficiency."""
        
        # Get time logged vs available time
        time_logs = db.query(TaskTimeLog).filter(
            TaskTimeLog.organization_id == organization_id,
            TaskTimeLog.logged_date >= period_start,
            TaskTimeLog.logged_date <= period_end
        ).all()
        
        if not time_logs:
            return {"value": 0.0, "unit": "percentage", "confidence_score": 0.0}
        
        # Calculate total hours logged
        total_logged_hours = sum(float(log.hours_logged) for log in time_logs if log.hours_logged)
        
        # Get unique users and calculate available time
        unique_users = set(log.user_id for log in time_logs)
        period_days = (period_end - period_start).days + 1
        working_days = period_days * 5 / 7  # Assume 5-day work week
        
        # Assume 8 hours per working day per user
        total_available_hours = len(unique_users) * working_days * 8
        
        if total_available_hours == 0:
            return {"value": 0.0, "unit": "percentage", "confidence_score": 0.0}
        
        allocation_rate = (total_logged_hours / total_available_hours) * 100
        allocation_rate = min(allocation_rate, 100)  # Cap at 100%
        
        return {
            "value": allocation_rate,
            "unit": "percentage",
            "confidence_score": 0.8,  # Lower confidence due to assumptions
            "calculation_method": f"Logged hours ({total_logged_hours}) / Available hours ({total_available_hours}) * 100",
            "source_data": {
                "total_logged_hours": total_logged_hours,
                "total_available_hours": total_available_hours,
                "unique_users": len(unique_users),
                "working_days": working_days
            }
        }
    
    async def _calculate_milestone_achievement(
        self, organization_id: int, period_start: date, period_end: date,
        entity_type: Optional[str], entity_id: Optional[int], db: Session
    ) -> Dict[str, Any]:
        """Calculate milestone achievement rate."""
        
        # Get projects with milestones (end dates)
        query = db.query(Project).filter(
            Project.organization_id == organization_id,
            Project.end_date >= period_start,
            Project.end_date <= period_end,
            Project.end_date.isnot(None)
        )
        
        if entity_type == "project" and entity_id:
            query = query.filter(Project.id == entity_id)
        
        projects_with_milestones = query.all()
        
        if not projects_with_milestones:
            return {"value": 0.0, "unit": "percentage", "confidence_score": 0.0}
        
        achieved_milestones = 0
        for project in projects_with_milestones:
            if project.status == ProjectStatus.COMPLETED:
                achieved_milestones += 1
        
        achievement_rate = (achieved_milestones / len(projects_with_milestones)) * 100
        
        return {
            "value": achievement_rate,
            "unit": "percentage",
            "confidence_score": 1.0,
            "calculation_method": f"Achieved milestones ({achieved_milestones}) / Total milestones ({len(projects_with_milestones)}) * 100",
            "source_data": {
                "total_milestones": len(projects_with_milestones),
                "achieved_milestones": achieved_milestones
            }
        }


class ReportGenerationService:
    """Service for generating various types of reports."""
    
    def __init__(self):
        self.calculator_service = AnalyticsCalculatorService()
        self.report_generators = {
            ReportType.PROJECT_OVERVIEW: self._generate_project_overview,
            ReportType.TASK_ANALYTICS: self._generate_task_analytics,
            ReportType.TIME_TRACKING: self._generate_time_tracking,
            ReportType.USER_PRODUCTIVITY: self._generate_user_productivity,
            ReportType.TEAM_PERFORMANCE: self._generate_team_performance,
            ReportType.RESOURCE_UTILIZATION: self._generate_resource_utilization,
            ReportType.BUDGET_ANALYSIS: self._generate_budget_analysis,
            ReportType.MILESTONE_TRACKING: self._generate_milestone_tracking,
            ReportType.WORKFLOW_ANALYSIS: self._generate_workflow_analysis,
        }
    
    async def generate_report(
        self,
        template: ReportTemplate,
        request: ReportGenerationRequest,
        user: UserRead,
        db: Session
    ) -> Report:
        """Generate a report based on the template and request."""
        
        start_time = datetime.utcnow()
        
        try:
            # Get the appropriate report generator
            generator = self.report_generators.get(template.report_type)
            if not generator:
                raise ValueError(f"No generator available for report type: {template.report_type}")
            
            # Generate report data
            report_data = await generator(
                template, request, user.organization_id, db
            )
            
            # Calculate generation time
            generation_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Create report record
            report = Report(
                name=request.name or f"{template.name} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                description=request.description,
                data=report_data,
                metadata={
                    "template_type": template.report_type,
                    "generation_timestamp": start_time.isoformat(),
                    "filters_count": len(request.filters),
                    "includes_raw_data": request.include_raw_data
                },
                filters_applied={
                    "date_range": {
                        "start": request.date_range.start_date.isoformat(),
                        "end": request.date_range.end_date.isoformat()
                    },
                    "additional_filters": [filter.dict() for filter in request.filters]
                },
                template_id=template.id,
                organization_id=user.organization_id,
                generated_by=user.id,
                data_start_date=request.date_range.start_date,
                data_end_date=request.date_range.end_date,
                generation_duration_ms=int(generation_time),
                data_points_count=report_data.get("summary", {}).get("total_data_points", 0),
                file_size_bytes=len(json.dumps(report_data).encode('utf-8'))
            )
            
            db.add(report)
            db.commit()
            db.refresh(report)
            
            # Update template usage
            template.usage_count += 1
            template.last_used_at = datetime.utcnow()
            db.commit()
            
            return report
            
        except Exception as e:
            db.rollback()
            raise Exception(f"Report generation failed: {str(e)}")
    
    async def _generate_project_overview(
        self, template: ReportTemplate, request: ReportGenerationRequest, 
        organization_id: int, db: Session
    ) -> Dict[str, Any]:
        """Generate project overview report."""
        
        # Get projects in date range
        projects = db.query(Project).filter(
            Project.organization_id == organization_id,
            Project.created_at >= request.date_range.start_date,
            Project.created_at <= request.date_range.end_date
        ).all()
        
        # Calculate metrics for each project
        project_data = []
        for project in projects:
            # Get project metrics
            progress_metric = await self.calculator_service.calculate_metric(
                "project_progress", organization_id, 
                request.date_range.start_date, request.date_range.end_date,
                "project", project.id, db
            )
            
            project_info = {
                "id": project.id,
                "name": project.name,
                "status": project.status,
                "progress": progress_metric.get("value", 0),
                "task_count": len(project.tasks) if project.tasks else 0,
                "completed_tasks": sum(1 for task in (project.tasks or []) if task.status == TaskStatus.COMPLETED),
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "end_date": project.end_date.isoformat() if project.end_date else None,
                "created_at": project.created_at.isoformat()
            }
            project_data.append(project_info)
        
        # Generate summary statistics
        total_projects = len(projects)
        active_projects = sum(1 for p in projects if p.status == ProjectStatus.ACTIVE)
        completed_projects = sum(1 for p in projects if p.status == ProjectStatus.COMPLETED)
        
        summary = {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": completed_projects,
            "completion_rate": (completed_projects / total_projects * 100) if total_projects > 0 else 0,
            "total_data_points": total_projects
        }
        
        return {
            "report_type": "project_overview",
            "summary": summary,
            "projects": project_data,
            "charts": {
                "status_distribution": {
                    "type": "pie",
                    "data": {
                        "labels": ["Active", "Completed", "Cancelled", "On Hold"],
                        "values": [
                            sum(1 for p in projects if p.status == ProjectStatus.ACTIVE),
                            sum(1 for p in projects if p.status == ProjectStatus.COMPLETED),
                            sum(1 for p in projects if p.status == ProjectStatus.CANCELLED),
                            sum(1 for p in projects if p.status == ProjectStatus.ON_HOLD)
                        ]
                    }
                },
                "progress_timeline": {
                    "type": "line",
                    "data": {
                        "projects": [{"name": p["name"], "progress": p["progress"]} for p in project_data]
                    }
                }
            }
        }
    
    async def _generate_task_analytics(
        self, template: ReportTemplate, request: ReportGenerationRequest,
        organization_id: int, db: Session
    ) -> Dict[str, Any]:
        """Generate task analytics report."""
        
        # Get tasks in date range
        tasks = db.query(Task).filter(
            Task.organization_id == organization_id,
            Task.created_at >= request.date_range.start_date,
            Task.created_at <= request.date_range.end_date
        ).all()
        
        # Calculate task metrics
        completion_rate = await self.calculator_service.calculate_metric(
            "task_completion_rate", organization_id,
            request.date_range.start_date, request.date_range.end_date,
            None, None, db
        )
        
        deadline_adherence = await self.calculator_service.calculate_metric(
            "deadline_adherence", organization_id,
            request.date_range.start_date, request.date_range.end_date,
            None, None, db
        )
        
        # Analyze task distribution
        status_distribution = {}
        priority_distribution = {}
        
        for task in tasks:
            # Status distribution
            status = task.status
            status_distribution[status] = status_distribution.get(status, 0) + 1
            
            # Priority distribution
            priority = task.priority
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
        
        summary = {
            "total_tasks": len(tasks),
            "completion_rate": completion_rate.get("value", 0),
            "deadline_adherence": deadline_adherence.get("value", 0),
            "avg_completion_time": 0,  # Would need more complex calculation
            "total_data_points": len(tasks)
        }
        
        return {
            "report_type": "task_analytics",
            "summary": summary,
            "metrics": {
                "completion_rate": completion_rate,
                "deadline_adherence": deadline_adherence
            },
            "distributions": {
                "status": status_distribution,
                "priority": priority_distribution
            },
            "charts": {
                "status_breakdown": {
                    "type": "doughnut",
                    "data": {
                        "labels": list(status_distribution.keys()),
                        "values": list(status_distribution.values())
                    }
                },
                "priority_analysis": {
                    "type": "bar",
                    "data": {
                        "labels": list(priority_distribution.keys()),
                        "values": list(priority_distribution.values())
                    }
                }
            }
        }
    
    async def _generate_time_tracking(
        self, template: ReportTemplate, request: ReportGenerationRequest,
        organization_id: int, db: Session
    ) -> Dict[str, Any]:
        """Generate time tracking report."""
        
        # Get time logs in date range
        time_logs = db.query(TaskTimeLog).filter(
            TaskTimeLog.organization_id == organization_id,
            TaskTimeLog.logged_date >= request.date_range.start_date,
            TaskTimeLog.logged_date <= request.date_range.end_date
        ).all()
        
        # Calculate time metrics
        productivity = await self.calculator_service.calculate_metric(
            "user_productivity", organization_id,
            request.date_range.start_date, request.date_range.end_date,
            None, None, db
        )
        
        utilization = await self.calculator_service.calculate_metric(
            "time_utilization", organization_id,
            request.date_range.start_date, request.date_range.end_date,
            None, None, db
        )
        
        # Analyze time distribution
        total_hours = sum(float(log.hours_logged) for log in time_logs if log.hours_logged)
        billable_hours = sum(float(log.hours_logged) for log in time_logs if log.hours_logged and log.is_billable)
        
        # Group by user
        user_hours = {}
        for log in time_logs:
            user_id = log.user_id
            if user_id not in user_hours:
                user_hours[user_id] = {"total": 0, "billable": 0, "entries": 0}
            
            if log.hours_logged:
                user_hours[user_id]["total"] += float(log.hours_logged)
                if log.is_billable:
                    user_hours[user_id]["billable"] += float(log.hours_logged)
                user_hours[user_id]["entries"] += 1
        
        summary = {
            "total_hours": total_hours,
            "billable_hours": billable_hours,
            "billable_rate": (billable_hours / total_hours * 100) if total_hours > 0 else 0,
            "productivity_score": productivity.get("value", 0),
            "utilization_rate": utilization.get("value", 0),
            "total_data_points": len(time_logs)
        }
        
        return {
            "report_type": "time_tracking",
            "summary": summary,
            "metrics": {
                "productivity": productivity,
                "utilization": utilization
            },
            "user_breakdown": user_hours,
            "charts": {
                "daily_hours": {
                    "type": "line",
                    "data": {
                        # Would need to group by date for timeline
                        "labels": [],
                        "values": []
                    }
                },
                "billable_vs_non_billable": {
                    "type": "pie",
                    "data": {
                        "labels": ["Billable", "Non-Billable"],
                        "values": [billable_hours, total_hours - billable_hours]
                    }
                }
            }
        }
    
    async def _generate_user_productivity(
        self, template: ReportTemplate, request: ReportGenerationRequest,
        organization_id: int, db: Session
    ) -> Dict[str, Any]:
        """Generate user productivity report."""
        
        # This would be similar to time tracking but focused on individual productivity metrics
        # Implementation would follow similar pattern to above methods
        return {
            "report_type": "user_productivity",
            "summary": {"message": "User productivity report generated"},
            "charts": {}
        }
    
    async def _generate_team_performance(
        self, template: ReportTemplate, request: ReportGenerationRequest,
        organization_id: int, db: Session
    ) -> Dict[str, Any]:
        """Generate team performance report."""
        
        # Implementation for team performance metrics
        return {
            "report_type": "team_performance", 
            "summary": {"message": "Team performance report generated"},
            "charts": {}
        }
    
    async def _generate_resource_utilization(
        self, template: ReportTemplate, request: ReportGenerationRequest,
        organization_id: int, db: Session
    ) -> Dict[str, Any]:
        """Generate resource utilization report."""
        
        # Implementation for resource utilization analysis
        return {
            "report_type": "resource_utilization",
            "summary": {"message": "Resource utilization report generated"},
            "charts": {}
        }
    
    async def _generate_budget_analysis(
        self, template: ReportTemplate, request: ReportGenerationRequest,
        organization_id: int, db: Session
    ) -> Dict[str, Any]:
        """Generate budget analysis report."""
        
        # Implementation for budget and cost analysis
        return {
            "report_type": "budget_analysis",
            "summary": {"message": "Budget analysis report generated"},
            "charts": {}
        }
    
    async def _generate_milestone_tracking(
        self, template: ReportTemplate, request: ReportGenerationRequest,
        organization_id: int, db: Session
    ) -> Dict[str, Any]:
        """Generate milestone tracking report."""
        
        # Implementation for milestone and deadline tracking
        return {
            "report_type": "milestone_tracking",
            "summary": {"message": "Milestone tracking report generated"},
            "charts": {}
        }
    
    async def _generate_workflow_analysis(
        self, template: ReportTemplate, request: ReportGenerationRequest,
        organization_id: int, db: Session
    ) -> Dict[str, Any]:
        """Generate workflow analysis report."""
        
        # Implementation for workflow and process analysis
        return {
            "report_type": "workflow_analysis",
            "summary": {"message": "Workflow analysis report generated"},
            "charts": {}
        }


class DashboardService:
    """Service for managing dashboards and widgets."""
    
    async def create_dashboard(
        self, request: DashboardRequest, user: UserRead, db: Session
    ) -> Dashboard:
        """Create a new dashboard."""
        
        dashboard = Dashboard(
            name=request.name,
            description=request.description,
            layout_config=request.layout_config,
            theme_settings=request.theme_settings,
            refresh_interval=request.refresh_interval,
            organization_id=user.organization_id,
            created_by=user.id,
            is_public=request.is_public,
            is_default=request.is_default,
            shared_with_users=request.shared_with_users
        )
        
        db.add(dashboard)
        db.commit()
        db.refresh(dashboard)
        
        return dashboard
    
    async def get_widget_data(
        self, widget: DashboardWidget, user: UserRead, db: Session
    ) -> Dict[str, Any]:
        """Get data for a specific widget."""
        
        # Check cache first
        if (widget.cached_data and widget.last_data_update and 
            widget.cache_duration_seconds and
            (datetime.utcnow() - widget.last_data_update).total_seconds() < widget.cache_duration_seconds):
            return widget.cached_data
        
        # Generate fresh data based on widget configuration
        widget_data = await self._generate_widget_data(widget, user, db)
        
        # Update cache
        widget.cached_data = widget_data
        widget.last_data_update = datetime.utcnow()
        db.commit()
        
        return widget_data
    
    async def _generate_widget_data(
        self, widget: DashboardWidget, user: UserRead, db: Session
    ) -> Dict[str, Any]:
        """Generate data for a widget based on its configuration."""
        
        query_config = widget.query_config
        
        # Basic implementation - would need to be expanded based on widget types
        if widget.widget_type == ChartType.LINE:
            return {
                "type": "line",
                "data": {
                    "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
                    "datasets": [{
                        "label": "Tasks Completed",
                        "data": [12, 19, 3, 5, 2]
                    }]
                }
            }
        elif widget.widget_type == ChartType.PIE:
            return {
                "type": "pie",
                "data": {
                    "labels": ["Completed", "In Progress", "Todo"],
                    "datasets": [{
                        "data": [10, 5, 3]
                    }]
                }
            }
        
        return {"message": "Widget data generated"}


class AnalyticsService:
    """Main analytics service orchestrating all analytics operations."""
    
    def __init__(self):
        self.calculator_service = AnalyticsCalculatorService()
        self.report_service = ReportGenerationService()
        self.dashboard_service = DashboardService()
    
    async def get_analytics_summary(
        self, user: UserRead, db: Session
    ) -> Dict[str, Any]:
        """Get analytics summary for the organization."""
        
        # Get recent reports
        recent_reports = db.query(Report).filter(
            Report.organization_id == user.organization_id,
            Report.generated_at >= datetime.utcnow() - timedelta(days=30)
        ).order_by(desc(Report.generated_at)).limit(5).all()
        
        # Get dashboard count
        dashboard_count = db.query(Dashboard).filter(
            Dashboard.organization_id == user.organization_id,
            Dashboard.is_archived == False
        ).count()
        
        # Get active alerts count
        active_alerts = db.query(ReportAlert).filter(
            ReportAlert.organization_id == user.organization_id,
            ReportAlert.is_active == True
        ).count()
        
        return {
            "total_reports_generated": len(recent_reports),
            "total_dashboards": dashboard_count,
            "total_active_alerts": active_alerts,
            "total_scheduled_reports": 0,  # Would need to implement
            "recent_reports": [
                {
                    "id": r.id,
                    "name": r.name,
                    "type": r.template.report_type if r.template else "unknown",
                    "generated_at": r.generated_at.isoformat()
                }
                for r in recent_reports
            ],
            "recent_alerts": [],
            "popular_templates": [],
            "popular_dashboards": [],
            "avg_report_generation_time": 0.0,
            "cache_hit_rate": 0.0,
            "alert_response_rate": 0.0
        }