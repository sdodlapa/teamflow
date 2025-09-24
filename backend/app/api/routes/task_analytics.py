"""Advanced task analytics API routes for Day 3 implementation."""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.task_analytics import TaskAnalyticsService


router = APIRouter(prefix="/analytics", tags=["analytics"])


# Request/Response Models
class TaskComplexityRequest(BaseModel):
    title: str
    description: str
    skill_requirements: List[str] = []
    dependencies_count: int = 0
    priority: str = "medium"


class TaskComplexityResponse(BaseModel):
    complexity_score: int
    complexity_type: str
    confidence_level: float
    factors: Dict[str, float]


class SmartAssignmentRequest(BaseModel):
    task_id: int
    candidate_user_ids: List[int]


class SmartAssignmentResponse(BaseModel):
    recommended_user_id: int
    confidence: float
    scores: Dict[int, Dict[str, float]]


class TeamPerformanceResponse(BaseModel):
    team_identifier: str
    tasks_completed: int
    on_time_percentage: float
    avg_completion_time_hours: Optional[float]
    avg_complexity_score: Optional[float]
    avg_quality_score: Optional[float]
    efficiency_indicators: Dict[str, float]
    bottlenecks: List[Dict]


class ProjectHealthResponse(BaseModel):
    project_id: int
    project_name: str
    health_score: float
    health_level: str
    scores: Dict[str, float]
    risks: Dict[str, float]
    metrics: Dict[str, int]
    recommendations: List[Dict]
    trend: str


@router.post("/tasks/estimate-complexity", response_model=TaskComplexityResponse)
async def estimate_task_complexity(
    request: TaskComplexityRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    AI-powered task complexity estimation.
    
    Analyzes task details to predict complexity on a 1-10 scale.
    """
    try:
        analytics_service = TaskAnalyticsService(db)
        
        task_data = {
            "title": request.title,
            "description": request.description,
            "skill_requirements": request.skill_requirements,
            "dependencies_count": request.dependencies_count,
            "priority": request.priority
        }
        
        result = await analytics_service.calculate_task_complexity(task_data)
        
        return TaskComplexityResponse(
            complexity_score=result["complexity_score"],
            complexity_type=result["complexity_type"].value,
            confidence_level=result["confidence_level"],
            factors=result["factors"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/smart-assignment", response_model=SmartAssignmentResponse)
async def smart_task_assignment(
    request: SmartAssignmentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Intelligent task assignment based on skills, workload, and performance.
    """
    try:
        analytics_service = TaskAnalyticsService(db)
        
        # Get task
        from sqlalchemy import select
        from app.models.task import Task
        
        task_query = select(Task).where(Task.id == request.task_id)
        result = await db.execute(task_query)
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Get candidate users
        from app.models.user import User
        users_query = select(User).where(User.id.in_(request.candidate_user_ids))
        result = await db.execute(users_query)
        candidate_users = result.scalars().all()
        
        if not candidate_users:
            raise HTTPException(status_code=400, detail="No valid candidate users found")
        
        assignment_result = await analytics_service.smart_task_assignment(task, candidate_users)
        
        if "error" in assignment_result:
            raise HTTPException(status_code=400, detail=assignment_result["error"])
        
        return SmartAssignmentResponse(
            recommended_user_id=assignment_result["recommended_user_id"],
            confidence=assignment_result["confidence"],
            scores=assignment_result["scores"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/productivity", response_model=Dict)
async def get_task_productivity_metrics(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive productivity metrics for a specific task.
    """
    try:
        analytics_service = TaskAnalyticsService(db)
        
        result = await analytics_service.calculate_productivity_metrics(task_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teams/{team_identifier}/performance", response_model=TeamPerformanceResponse)
async def get_team_performance_metrics(
    team_identifier: str,
    period_days: int = Query(default=30, description="Analysis period in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive team performance analysis for a specified period.
    """
    try:
        analytics_service = TaskAnalyticsService(db)
        
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=period_days)
        
        result = await analytics_service.analyze_team_performance(
            team_identifier, period_start, period_end
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return TeamPerformanceResponse(
            team_identifier=result["team_identifier"],
            tasks_completed=result["tasks_completed"],
            on_time_percentage=result["on_time_percentage"],
            avg_completion_time_hours=result["avg_completion_time_hours"],
            avg_complexity_score=result["avg_complexity_score"],
            avg_quality_score=result["avg_quality_score"],
            efficiency_indicators=result["efficiency_indicators"],
            bottlenecks=result["bottlenecks"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/health", response_model=ProjectHealthResponse)
async def get_project_health_metrics(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive project health assessment and recommendations.
    """
    try:
        analytics_service = TaskAnalyticsService(db)
        
        result = await analytics_service.generate_project_health_report(project_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return ProjectHealthResponse(
            project_id=result["project_id"],
            project_name=result["project_name"],
            health_score=result["health_score"],
            health_level=result["health_level"],
            scores=result["scores"],
            risks=result["risks"],
            metrics=result["metrics"],
            recommendations=result["recommendations"],
            trend=result["trend"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bottlenecks")
async def analyze_bottlenecks(
    scope: str = Query(..., description="Analysis scope: 'organization', 'project_X', or 'team_X'"),
    period_days: int = Query(default=30, description="Analysis period in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze process bottlenecks for specified scope and time period.
    """
    try:
        analytics_service = TaskAnalyticsService(db)
        
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=period_days)
        
        bottlenecks = await analytics_service._detect_bottlenecks(scope, period_start, period_end)
        
        return {
            "scope": scope,
            "analysis_period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
                "days": period_days
            },
            "bottlenecks": bottlenecks,
            "summary": {
                "total_bottlenecks": len(bottlenecks),
                "critical_bottlenecks": len([b for b in bottlenecks if b.get("severity", 0) > 0.7]),
                "most_common_type": max([b["type"] for b in bottlenecks], key=[b["type"] for b in bottlenecks].count) if bottlenecks else None
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_analytics_trends(
    metric: str = Query(..., description="Metric to analyze: 'productivity', 'quality', 'velocity'"),
    scope: str = Query(default="organization", description="Scope: 'organization', 'project_X', 'team_X'"),
    period_days: int = Query(default=90, description="Analysis period in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get trend analysis for specified metrics over time.
    """
    try:
        # Mock trend data - in real implementation would calculate from historical data
        trend_data = {
            "metric": metric,
            "scope": scope,
            "period_days": period_days,
            "data_points": [
                {"date": (datetime.utcnow() - timedelta(days=i)).isoformat(), "value": 75 + (i % 20)}
                for i in range(0, period_days, 7)
            ],
            "trend_direction": "improving",
            "trend_percentage": 12.5,
            "insights": [
                f"{metric.title()} has improved by 12.5% over the last {period_days} days",
                "Consistent upward trend observed",
                "Peak performance achieved in recent weeks"
            ]
        }
        
        return trend_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_analytics_dashboard(
    scope: str = Query(default="organization", description="Dashboard scope"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive analytics dashboard with key metrics and insights.
    """
    try:
        # Mock dashboard data - in real implementation would aggregate from various analytics
        dashboard = {
            "scope": scope,
            "generated_at": datetime.utcnow().isoformat(),
            "key_metrics": {
                "total_tasks": 1247,
                "completed_this_month": 89,
                "average_completion_time": 4.2,
                "team_productivity_score": 87.3,
                "overall_health_score": 82.1
            },
            "charts": {
                "task_completion_trend": [
                    {"week": f"Week {i}", "completed": 20 + (i * 3)} 
                    for i in range(1, 13)
                ],
                "complexity_distribution": {
                    "trivial": 15,
                    "simple": 35, 
                    "moderate": 30,
                    "complex": 15,
                    "critical": 5
                },
                "team_performance": [
                    {"team": f"Team {chr(65+i)}", "score": 75 + (i * 5)}
                    for i in range(5)
                ]
            },
            "alerts": [
                {
                    "type": "warning",
                    "message": "Project Alpha deadline risk detected",
                    "action": "Review resource allocation"
                },
                {
                    "type": "info",
                    "message": "Team productivity increased 8% this month",
                    "action": "Continue current practices"
                }
            ],
            "recommendations": [
                "Consider additional resources for high-complexity tasks",
                "Implement code review automation to reduce bottlenecks",
                "Team Alpha shows strong performance - replicate practices"
            ]
        }
        
        return dashboard
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/complexity/validate")
async def validate_complexity_estimation(
    task_id: int,
    actual_complexity: int = Query(..., ge=1, le=10, description="Actual complexity (1-10)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validate and improve complexity estimation accuracy with actual complexity feedback.
    """
    try:
        from sqlalchemy import select
        from app.models.task_analytics import TaskComplexityEstimation
        
        # Find existing estimation
        estimation_query = select(TaskComplexityEstimation).where(
            TaskComplexityEstimation.task_id == task_id
        )
        result = await db.execute(estimation_query)
        estimation = result.scalar_one_or_none()
        
        if not estimation:
            raise HTTPException(status_code=404, detail="No complexity estimation found for this task")
        
        # Update with actual complexity
        estimation.actual_complexity = actual_complexity
        estimation.accuracy_score = 1.0 - abs(estimation.complexity_score - actual_complexity) / 10.0
        
        await db.commit()
        
        return {
            "task_id": task_id,
            "estimated_complexity": estimation.complexity_score,
            "actual_complexity": actual_complexity,
            "accuracy_score": estimation.accuracy_score,
            "feedback": "Thank you for the validation. This helps improve our AI estimation model."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights")
async def get_ai_insights(
    scope: str = Query(default="organization", description="Insights scope"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered insights and recommendations based on analytics data.
    """
    try:
        # Mock AI insights - in real implementation would use ML models
        insights = {
            "scope": scope,
            "generated_at": datetime.utcnow().isoformat(),
            "insights": [
                {
                    "type": "productivity",
                    "confidence": 0.87,
                    "insight": "Teams with regular stand-ups show 23% higher productivity",
                    "recommendation": "Implement daily stand-ups for underperforming teams",
                    "impact": "high"
                },
                {
                    "type": "quality",
                    "confidence": 0.92,
                    "insight": "Code review turnaround time strongly correlates with bug rates",
                    "recommendation": "Set target review response time of 4 hours",
                    "impact": "medium"
                },
                {
                    "type": "resource",
                    "confidence": 0.78,
                    "insight": "Task complexity estimation accuracy has improved 15% this quarter",
                    "recommendation": "Continue training the AI model with feedback",
                    "impact": "low"
                },
                {
                    "type": "process",
                    "confidence": 0.84,
                    "insight": "Tasks with clear acceptance criteria complete 30% faster",
                    "recommendation": "Enforce acceptance criteria template for all tasks",
                    "impact": "high"
                }
            ],
            "predictive_alerts": [
                {
                    "type": "deadline_risk",
                    "probability": 0.73,
                    "message": "Project Beta has 73% chance of missing deadline",
                    "suggested_action": "Reallocate 2 developers or extend timeline by 1 week"
                },
                {
                    "type": "burnout_risk",
                    "probability": 0.41,
                    "message": "Developer John Smith shows signs of potential burnout",
                    "suggested_action": "Reduce workload and schedule wellness check"
                }
            ]
        }
        
        return insights
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))