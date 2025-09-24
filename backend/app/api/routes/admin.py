"""
Admin Dashboard & Analytics API
Day 7: Comprehensive admin dashboard endpoints
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field

from app.core.dependencies import get_current_user, get_current_admin_user
from app.models.user import User
from app.services.admin_analytics_service import (
    admin_analytics_service,
    AnalyticsTimeframe,
    DashboardSummary,
    UserAnalytics,
    ProjectAnalytics,
    TaskAnalytics,
    WorkflowAnalytics,
    AnalyticsMetric
)

# Create admin router
router = APIRouter(prefix="/admin", tags=["admin"])


# Pydantic response models
class DashboardSummaryResponse(BaseModel):
    """Dashboard summary response model"""
    total_users: int
    total_organizations: int
    total_projects: int
    total_tasks: int
    active_users_today: int
    tasks_completed_today: int
    system_health_score: float
    performance_score: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_users": 150,
                "total_organizations": 12,
                "total_projects": 45,
                "total_tasks": 320,
                "active_users_today": 28,
                "tasks_completed_today": 15,
                "system_health_score": 85.7,
                "performance_score": 92.3
            }
        }


class UserAnalyticsResponse(BaseModel):
    """User analytics response model"""
    total_users: int
    active_users: Dict[str, int]
    new_users: Dict[str, int]
    user_engagement: Dict[str, float]
    top_organizations: List[Dict[str, Any]]
    user_activity_trends: List[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_users": 150,
                "active_users": {"24h": 28, "7d": 95, "30d": 132},
                "new_users": {"24h": 3, "7d": 12, "30d": 25},
                "user_engagement": {
                    "daily_active_rate": 18.7,
                    "weekly_active_rate": 63.3,
                    "monthly_active_rate": 88.0
                },
                "top_organizations": [
                    {"name": "Acme Corp", "user_count": 25, "activity_score": 85.5}
                ],
                "user_activity_trends": [
                    {"date": "2025-09-24", "active_users": 32, "new_users": 4}
                ]
            }
        }


class ProjectAnalyticsResponse(BaseModel):
    """Project analytics response model"""
    total_projects: int
    active_projects: int
    completed_projects: int
    project_completion_rate: float
    average_project_duration: float
    projects_by_status: Dict[str, int]
    top_performing_projects: List[Dict[str, Any]]
    project_health_distribution: Dict[str, int]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_projects": 45,
                "active_projects": 32,
                "completed_projects": 13,
                "project_completion_rate": 28.9,
                "average_project_duration": 45.5,
                "projects_by_status": {
                    "active": 32,
                    "completed": 13,
                    "on_hold": 0,
                    "cancelled": 0
                },
                "top_performing_projects": [
                    {"name": "Project Alpha", "completion_rate": 95.5, "tasks_completed": 45, "team_size": 8}
                ],
                "project_health_distribution": {
                    "excellent": 14,
                    "good": 18,
                    "fair": 9,
                    "poor": 4
                }
            }
        }


class TaskAnalyticsResponse(BaseModel):
    """Task analytics response model"""
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int
    task_completion_rate: float
    average_completion_time: float
    tasks_by_priority: Dict[str, int]
    tasks_by_status: Dict[str, int]
    productivity_trends: List[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_tasks": 320,
                "completed_tasks": 185,
                "pending_tasks": 135,
                "overdue_tasks": 12,
                "task_completion_rate": 57.8,
                "average_completion_time": 3.5,
                "tasks_by_priority": {
                    "high": 45,
                    "medium": 180,
                    "low": 95
                },
                "tasks_by_status": {
                    "todo": 85,
                    "in_progress": 50,
                    "completed": 185
                },
                "productivity_trends": [
                    {"date": "2025-09-24", "completed": 25, "created": 18}
                ]
            }
        }


class WorkflowAnalyticsResponse(BaseModel):
    """Workflow analytics response model"""
    total_workflows: int
    active_workflows: int
    workflow_executions: int
    success_rate: float
    failed_executions: int
    average_execution_time: float
    most_used_workflows: List[Dict[str, Any]]
    workflow_performance: List[Dict[str, Any]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_workflows": 8,
                "active_workflows": 6,
                "workflow_executions": 150,
                "success_rate": 92.5,
                "failed_executions": 11,
                "average_execution_time": 4.2,
                "most_used_workflows": [
                    {"name": "Task Assignment", "executions": 45, "success_rate": 95.5}
                ],
                "workflow_performance": [
                    {"workflow": "Task Assignment", "avg_time": 2.1, "success_rate": 95.5}
                ]
            }
        }


class AnalyticsMetricResponse(BaseModel):
    """Analytics metric response model"""
    name: str
    value: float
    metric_type: str
    timeframe: str
    change_percent: Optional[float] = None
    trend: Optional[str] = None
    unit: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "User Growth Rate",
                "value": 12.5,
                "metric_type": "percentage",
                "timeframe": "30d",
                "change_percent": 2.3,
                "trend": "up",
                "unit": "%"
            }
        }


class AnalyticsReportResponse(BaseModel):
    """Complete analytics report response model"""
    report_metadata: Dict[str, Any]
    dashboard_summary: Dict[str, Any]
    user_analytics: Dict[str, Any]
    project_analytics: Dict[str, Any]
    task_analytics: Dict[str, Any]
    workflow_analytics: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_metadata": {
                    "generated_at": "2025-09-24T17:00:00Z",
                    "timeframe": "30d",
                    "organization_id": None,
                    "report_version": "1.0"
                },
                "dashboard_summary": {"total_users": 150},
                "user_analytics": {"total_users": 150},
                "project_analytics": {"total_projects": 45},
                "task_analytics": {"total_tasks": 320},
                "workflow_analytics": {"total_workflows": 8}
            }
        }


# Admin Dashboard Endpoints

@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    org_id: Optional[str] = Query(None, description="Organization ID to filter by"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get high-level dashboard summary with key metrics
    
    Requires admin privileges.
    """
    try:
        summary = await admin_analytics_service.get_dashboard_summary(org_id)
        return summary.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard summary: {str(e)}"
        )


@router.get("/analytics/users", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    timeframe: AnalyticsTimeframe = Query(
        AnalyticsTimeframe.LAST_30_DAYS,
        description="Analytics timeframe"
    ),
    org_id: Optional[str] = Query(None, description="Organization ID to filter by"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get comprehensive user analytics including activity, engagement, and trends
    
    Requires admin privileges.
    """
    try:
        analytics = await admin_analytics_service.get_user_analytics(timeframe, org_id)
        return analytics.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user analytics: {str(e)}"
        )


@router.get("/analytics/projects", response_model=ProjectAnalyticsResponse)
async def get_project_analytics(
    timeframe: AnalyticsTimeframe = Query(
        AnalyticsTimeframe.LAST_30_DAYS,
        description="Analytics timeframe"
    ),
    org_id: Optional[str] = Query(None, description="Organization ID to filter by"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get comprehensive project analytics including completion rates and performance
    
    Requires admin privileges.
    """
    try:
        analytics = await admin_analytics_service.get_project_analytics(timeframe, org_id)
        return analytics.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get project analytics: {str(e)}"
        )


@router.get("/analytics/tasks", response_model=TaskAnalyticsResponse)
async def get_task_analytics(
    timeframe: AnalyticsTimeframe = Query(
        AnalyticsTimeframe.LAST_30_DAYS,
        description="Analytics timeframe"
    ),
    org_id: Optional[str] = Query(None, description="Organization ID to filter by"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get comprehensive task analytics including completion rates and productivity trends
    
    Requires admin privileges.
    """
    try:
        analytics = await admin_analytics_service.get_task_analytics(timeframe, org_id)
        return analytics.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task analytics: {str(e)}"
        )


@router.get("/analytics/workflows", response_model=WorkflowAnalyticsResponse)
async def get_workflow_analytics(
    timeframe: AnalyticsTimeframe = Query(
        AnalyticsTimeframe.LAST_30_DAYS,
        description="Analytics timeframe"
    ),
    org_id: Optional[str] = Query(None, description="Organization ID to filter by"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get comprehensive workflow analytics including execution rates and performance
    
    Requires admin privileges.
    """
    try:
        analytics = await admin_analytics_service.get_workflow_analytics(timeframe, org_id)
        return analytics.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get workflow analytics: {str(e)}"
        )


@router.get("/analytics/metrics", response_model=List[AnalyticsMetricResponse])
async def get_custom_metrics(
    metric_names: List[str] = Query(
        ...,
        description="List of metric names to retrieve"
    ),
    timeframe: AnalyticsTimeframe = Query(
        AnalyticsTimeframe.LAST_30_DAYS,
        description="Analytics timeframe"
    ),
    org_id: Optional[str] = Query(None, description="Organization ID to filter by"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get custom analytics metrics by name
    
    Available metrics:
    - user_growth_rate: Rate of user growth
    - task_velocity: Average tasks completed per day
    - system_uptime: System uptime percentage
    
    Requires admin privileges.
    """
    try:
        metrics = await admin_analytics_service.get_custom_metrics(
            metric_names, timeframe, org_id
        )
        return [metric.to_dict() for metric in metrics]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get custom metrics: {str(e)}"
        )


@router.get("/analytics/report", response_model=AnalyticsReportResponse)
async def export_analytics_report(
    timeframe: AnalyticsTimeframe = Query(
        AnalyticsTimeframe.LAST_30_DAYS,
        description="Analytics timeframe"
    ),
    org_id: Optional[str] = Query(None, description="Organization ID to filter by"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Generate and export comprehensive analytics report
    
    This endpoint provides a complete analytics report including all metrics,
    suitable for executive reporting or detailed analysis.
    
    Requires admin privileges.
    """
    try:
        report = await admin_analytics_service.export_analytics_report(timeframe, org_id)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analytics report: {str(e)}"
        )


# Real-time Admin Dashboard Endpoints

@router.get("/dashboard/health")
async def get_system_health(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get real-time system health status
    
    Requires admin privileges.
    """
    try:
        # Get basic health metrics
        summary = await admin_analytics_service.get_dashboard_summary()
        
        health_status = {
            "status": "healthy" if summary.system_health_score > 70 else "warning",
            "health_score": summary.system_health_score,
            "performance_score": summary.performance_score,
            "active_users": summary.active_users_today,
            "system_load": {
                "cpu_usage": "Normal",  # Placeholder
                "memory_usage": "Normal",  # Placeholder
                "disk_usage": "Normal"  # Placeholder
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return health_status
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system health: {str(e)}"
        )


@router.get("/dashboard/alerts")
async def get_admin_alerts(
    limit: int = Query(10, description="Maximum number of alerts to return"),
    severity: Optional[str] = Query(None, description="Filter by alert severity"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get admin alerts and notifications
    
    Requires admin privileges.
    """
    try:
        # Placeholder implementation
        alerts = [
            {
                "id": "alert_001",
                "severity": "warning",
                "title": "High Task Overdue Rate",
                "message": "12 tasks are currently overdue across 3 projects",
                "created_at": "2025-09-24T16:30:00Z",
                "action_required": True
            },
            {
                "id": "alert_002", 
                "severity": "info",
                "title": "New User Registrations",
                "message": "4 new users registered in the last 24 hours",
                "created_at": "2025-09-24T15:45:00Z",
                "action_required": False
            }
        ]
        
        # Filter by severity if specified
        if severity:
            alerts = [alert for alert in alerts if alert["severity"] == severity]
        
        # Limit results
        alerts = alerts[:limit]
        
        return {
            "alerts": alerts,
            "total_count": len(alerts),
            "unread_count": sum(1 for alert in alerts if alert.get("action_required", False))
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get admin alerts: {str(e)}"
        )