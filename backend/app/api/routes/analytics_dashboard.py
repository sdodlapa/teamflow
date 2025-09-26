"""
Analytics Dashboard API Routes
Day 25: Analytics Dashboard Implementation
"""

from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.analytics_service import analytics_service
from app.services.performance_service import performance_monitor

router = APIRouter(prefix="/analytics", tags=["analytics", "dashboard"])

# Response Models
class DashboardStatsResponse(BaseModel):
    """Main dashboard statistics"""
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    overdue_tasks: int = 0
    active_projects: int = 0
    active_users: int = 0
    total_time_logged_hours: float = 0
    completion_rate: float = 0
    avg_completion_time_hours: float = 0
    productivity_score: float = 0
    
    # Trend data (vs previous period)
    tasks_trend: float = 0
    completion_trend: float = 0
    productivity_trend: float = 0
    time_trend: float = 0

class RecentActivityItem(BaseModel):
    """Recent activity item"""
    id: str
    type: str  # 'task_completed', 'project_created', 'user_joined', etc.
    description: str
    user_name: Optional[str] = None
    timestamp: datetime
    metadata: Dict[str, Any] = {}

class KeyInsight(BaseModel):
    """Key business insight"""
    id: str
    title: str
    description: str
    impact: str  # 'positive', 'negative', 'neutral'
    category: str  # 'productivity', 'performance', 'resources', 'deadlines'
    confidence: float  # 0.0 - 1.0
    action_required: bool = False
    recommendations: List[str] = []

class AnalyticsDashboardResponse(BaseModel):
    """Complete analytics dashboard response"""
    dashboard_stats: DashboardStatsResponse
    recent_activity: List[RecentActivityItem]
    key_insights: List[KeyInsight]
    performance_summary: Dict[str, Any]
    period_days: int
    last_updated: datetime

class TaskAnalyticsResponse(BaseModel):
    """Task-specific analytics"""
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    avg_completion_time_hours: float
    overdue_count: int
    by_priority: Dict[str, int]
    by_status: Dict[str, int]
    by_assignee: List[Dict[str, Any]]
    completion_trend: List[Dict[str, Any]]  # Daily/weekly data points

class ProjectAnalyticsResponse(BaseModel):
    """Project-specific analytics"""
    total_projects: int
    active_projects: int
    completed_projects: int
    project_health: Dict[str, Any]
    resource_utilization: Dict[str, Any]
    milestone_tracking: Dict[str, Any]
    project_performance: List[Dict[str, Any]]

class TeamAnalyticsResponse(BaseModel):
    """Team performance analytics"""
    team_size: int
    active_members: int
    productivity_metrics: Dict[str, Any]
    workload_distribution: List[Dict[str, Any]]
    collaboration_metrics: Dict[str, Any]
    skill_analysis: Dict[str, Any]

@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
async def get_analytics_dashboard(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive analytics dashboard data
    
    This is the main endpoint for the Day 25 Analytics Dashboard implementation.
    Provides real-time business intelligence and insights.
    """
    try:
        # Get current period
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get dashboard statistics (mock data for now - integrate with real services)
        dashboard_stats = DashboardStatsResponse(
            total_tasks=156,
            completed_tasks=89,
            in_progress_tasks=45,
            overdue_tasks=12,
            active_projects=12,
            active_users=24,
            total_time_logged_hours=1248.5,
            completion_rate=57.1,
            avg_completion_time_hours=4.2,
            productivity_score=85.0,
            tasks_trend=12.0,
            completion_trend=8.0,
            productivity_trend=7.0,
            time_trend=-15.0
        )
        
        # Get recent activity
        recent_activity = [
            RecentActivityItem(
                id="act-001",
                type="task_completed",
                description="Sarah completed 'Homepage Design' task",
                user_name="Sarah Johnson",
                timestamp=datetime.utcnow() - timedelta(minutes=2)
            ),
            RecentActivityItem(
                id="act-002",
                type="project_created",
                description="New project 'Mobile App' created by John",
                user_name="John Smith",
                timestamp=datetime.utcnow() - timedelta(minutes=15)
            ),
            RecentActivityItem(
                id="act-003",
                type="task_overdue",
                description="Task 'API Integration' is overdue",
                timestamp=datetime.utcnow() - timedelta(hours=1)
            )
        ]
        
        # Generate key insights
        key_insights = [
            KeyInsight(
                id="insight-001",
                title="Productivity Increased",
                description="Team velocity has improved by 12% this month",
                impact="positive",
                category="productivity",
                confidence=0.85,
                action_required=False,
                recommendations=["Continue current practices", "Consider scaling successful strategies"]
            ),
            KeyInsight(
                id="insight-002",
                title="Faster Task Completion",
                description="Average task completion time improved by 15%",
                impact="positive",
                category="performance",
                confidence=0.92,
                action_required=False
            ),
            KeyInsight(
                id="insight-003",
                title="Upcoming Deadlines",
                description="3 high-priority tasks approaching deadlines",
                impact="neutral",
                category="deadlines",
                confidence=1.0,
                action_required=True,
                recommendations=["Review task priorities", "Allocate additional resources", "Consider deadline extensions"]
            )
        ]
        
        # Get performance summary
        performance_summary = await performance_monitor.get_performance_summary()
        
        return AnalyticsDashboardResponse(
            dashboard_stats=dashboard_stats,
            recent_activity=recent_activity,
            key_insights=key_insights,
            performance_summary=performance_summary,
            period_days=days,
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch analytics dashboard: {str(e)}"
        )

@router.get("/tasks", response_model=TaskAnalyticsResponse)
async def get_task_analytics(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed task analytics"""
    try:
        # Mock task analytics data (integrate with real task service)
        task_analytics = TaskAnalyticsResponse(
            total_tasks=156,
            completed_tasks=89,
            completion_rate=57.1,
            avg_completion_time_hours=4.2,
            overdue_count=12,
            by_priority={
                "high": 35,
                "medium": 78,
                "low": 43
            },
            by_status={
                "todo": 22,
                "in_progress": 45,
                "in_review": 10,
                "done": 89
            },
            by_assignee=[
                {"name": "Sarah Johnson", "assigned": 25, "completed": 18, "completion_rate": 72.0},
                {"name": "John Smith", "assigned": 32, "completed": 20, "completion_rate": 62.5},
                {"name": "Mike Davis", "assigned": 28, "completed": 22, "completion_rate": 78.6}
            ],
            completion_trend=[
                {"date": "2024-09-19", "completed": 8, "total": 12},
                {"date": "2024-09-20", "completed": 12, "total": 15},
                {"date": "2024-09-21", "completed": 10, "total": 14},
                {"date": "2024-09-22", "completed": 15, "total": 18},
                {"date": "2024-09-23", "completed": 11, "total": 16}
            ]
        )
        
        return task_analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch task analytics: {str(e)}"
        )

@router.get("/projects", response_model=ProjectAnalyticsResponse)
async def get_project_analytics(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed project analytics"""
    try:
        # Mock project analytics data
        project_analytics = ProjectAnalyticsResponse(
            total_projects=12,
            active_projects=8,
            completed_projects=4,
            project_health={
                "healthy": 6,
                "at_risk": 2,
                "critical": 0
            },
            resource_utilization={
                "optimal": 5,
                "over_allocated": 2,
                "under_allocated": 1
            },
            milestone_tracking={
                "on_track": 18,
                "behind": 4,
                "ahead": 2
            },
            project_performance=[
                {
                    "id": 1,
                    "name": "Website Redesign",
                    "completion": 85,
                    "health": "healthy",
                    "team_size": 6,
                    "tasks_completed": 45,
                    "tasks_total": 53
                },
                {
                    "id": 2,
                    "name": "Mobile App",
                    "completion": 32,
                    "health": "healthy",
                    "team_size": 4,
                    "tasks_completed": 12,
                    "tasks_total": 37
                }
            ]
        )
        
        return project_analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch project analytics: {str(e)}"
        )

@router.get("/team", response_model=TeamAnalyticsResponse)
async def get_team_analytics(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed team analytics"""
    try:
        # Mock team analytics data
        team_analytics = TeamAnalyticsResponse(
            team_size=24,
            active_members=22,
            productivity_metrics={
                "avg_tasks_per_member": 6.5,
                "avg_completion_time": 4.2,
                "team_velocity": 85.0,
                "collaboration_score": 78.0
            },
            workload_distribution=[
                {"user": "Sarah Johnson", "workload": 85, "capacity": 100, "efficiency": 92},
                {"user": "John Smith", "workload": 78, "capacity": 100, "efficiency": 88},
                {"user": "Mike Davis", "workload": 92, "capacity": 100, "efficiency": 95}
            ],
            collaboration_metrics={
                "shared_tasks": 34,
                "cross_team_projects": 3,
                "communication_frequency": 4.2,
                "knowledge_sharing": 67
            },
            skill_analysis={
                "frontend": {"members": 8, "proficiency": 85},
                "backend": {"members": 6, "proficiency": 92},
                "design": {"members": 4, "proficiency": 88},
                "devops": {"members": 2, "proficiency": 78}
            }
        )
        
        return team_analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch team analytics: {str(e)}"
        )

@router.get("/export")
async def export_analytics_data(
    format: str = Query("csv", description="Export format (csv, excel, pdf)"),
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    include_charts: bool = Query(False, description="Include charts in export"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Export analytics data in various formats"""
    try:
        # This would generate and return exported analytics data
        # For now, return a simple response
        return {
            "message": f"Analytics export in {format} format initiated",
            "format": format,
            "days": days,
            "include_charts": include_charts,
            "status": "processing",
            "estimated_completion": "2-3 minutes"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export analytics data: {str(e)}"
        )

@router.post("/refresh")
async def refresh_analytics_cache(
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """Manually refresh analytics cache"""
    try:
        # Add background task to refresh analytics cache
        if background_tasks:
            background_tasks.add_task(analytics_service.refresh_cache)
        
        return {
            "message": "Analytics cache refresh initiated",
            "status": "processing",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh analytics cache: {str(e)}"
        )