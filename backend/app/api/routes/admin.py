"""
Administrative dashboard and analytics API endpoints
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.models.organization import Organization
from app.models.project import Project
from app.models.task import Task
from app.schemas.analytics import *
from app.services.analytics_service import analytics_service
from app.services.performance_service import performance_monitor, metrics_collector
from app.core.cache import cache


router = APIRouter()


@router.get("/admin/dashboard")
async def get_admin_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get comprehensive admin dashboard data"""
    try:
        # Get system overview statistics
        system_stats = await get_system_statistics(db)
        
        # Get user activity metrics
        user_metrics = await analytics_service.get_user_activity_summary(days=30)
        
        # Get performance summary
        performance_summary = await performance_monitor.get_performance_summary()
        
        # Get organization metrics
        org_metrics = await get_organization_metrics(db)
        
        # Get recent activities
        recent_activities = await get_recent_system_activities(db, limit=10)
        
        # Get system health
        system_health = await get_system_health_overview()
        
        # Get growth metrics
        growth_metrics = await get_growth_metrics(db)
        
        return {
            "dashboard_timestamp": datetime.utcnow(),
            "system_statistics": system_stats,
            "user_metrics": user_metrics,
            "performance_summary": performance_summary,
            "organization_metrics": org_metrics,
            "recent_activities": recent_activities,
            "system_health": system_health,
            "growth_metrics": growth_metrics,
            "quick_actions": [
                {"title": "User Management", "url": "/admin/users", "icon": "users"},
                {"title": "System Performance", "url": "/admin/performance", "icon": "activity"},
                {"title": "Security Logs", "url": "/admin/security", "icon": "shield"},
                {"title": "Analytics Reports", "url": "/admin/analytics", "icon": "bar-chart"},
                {"title": "System Configuration", "url": "/admin/config", "icon": "settings"}
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading admin dashboard: {str(e)}")


@router.get("/admin/analytics/overview")
async def get_analytics_overview(
    timeframe_days: int = Query(30, description="Timeframe in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get comprehensive analytics overview"""
    try:
        # User analytics
        user_analytics = await analytics_service.get_user_analytics(days=timeframe_days)
        
        # Project analytics
        project_analytics = await get_project_analytics(db, days=timeframe_days)
        
        # Task analytics
        task_analytics = await get_task_analytics(db, days=timeframe_days)
        
        # Usage patterns
        usage_patterns = await analytics_service.get_usage_patterns(days=timeframe_days)
        
        # Performance analytics
        performance_analytics = await get_performance_analytics(days=timeframe_days)
        
        # Feature adoption
        feature_adoption = await get_feature_adoption_metrics(db, days=timeframe_days)
        
        return {
            "timeframe_days": timeframe_days,
            "generated_at": datetime.utcnow(),
            "user_analytics": user_analytics,
            "project_analytics": project_analytics,
            "task_analytics": task_analytics,
            "usage_patterns": usage_patterns,
            "performance_analytics": performance_analytics,
            "feature_adoption": feature_adoption
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics overview: {str(e)}")


@router.get("/admin/users/analytics")
async def get_user_analytics(
    timeframe_days: int = Query(30, description="Timeframe in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get detailed user analytics"""
    try:
        # User registration trends
        registration_trends = await get_user_registration_trends(db, days=timeframe_days)
        
        # User activity patterns
        activity_patterns = await analytics_service.get_user_activity_patterns(days=timeframe_days)
        
        # User engagement metrics
        engagement_metrics = await get_user_engagement_metrics(db, days=timeframe_days)
        
        # Top active users
        top_users = await get_top_active_users(db, days=timeframe_days, limit=20)
        
        # User demographics
        demographics = await get_user_demographics(db)
        
        # User retention analysis
        retention_analysis = await get_user_retention_analysis(db, days=timeframe_days)
        
        return {
            "timeframe_days": timeframe_days,
            "total_users": await get_total_user_count(db),
            "registration_trends": registration_trends,
            "activity_patterns": activity_patterns,
            "engagement_metrics": engagement_metrics,
            "top_active_users": top_users,
            "demographics": demographics,
            "retention_analysis": retention_analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user analytics: {str(e)}")


@router.get("/admin/organizations/analytics")
async def get_organization_analytics(
    timeframe_days: int = Query(30, description="Timeframe in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get detailed organization analytics"""
    try:
        # Organization growth trends
        growth_trends = await get_organization_growth_trends(db, days=timeframe_days)
        
        # Organization size distribution
        size_distribution = await get_organization_size_distribution(db)
        
        # Most active organizations
        active_orgs = await get_most_active_organizations(db, days=timeframe_days, limit=20)
        
        # Organization project metrics
        project_metrics = await get_organization_project_metrics(db, days=timeframe_days)
        
        # Organization user metrics
        user_metrics = await get_organization_user_metrics(db, days=timeframe_days)
        
        return {
            "timeframe_days": timeframe_days,
            "total_organizations": await get_total_organization_count(db),
            "growth_trends": growth_trends,
            "size_distribution": size_distribution,
            "most_active": active_orgs,
            "project_metrics": project_metrics,
            "user_metrics": user_metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting organization analytics: {str(e)}")


@router.get("/admin/projects/analytics")
async def get_project_analytics_detailed(
    timeframe_days: int = Query(30, description="Timeframe in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get detailed project analytics"""
    try:
        # Project creation trends
        creation_trends = await get_project_creation_trends(db, days=timeframe_days)
        
        # Project completion rates
        completion_rates = await get_project_completion_rates(db, days=timeframe_days)
        
        # Project size analysis
        size_analysis = await get_project_size_analysis(db)
        
        # Most active projects
        active_projects = await get_most_active_projects(db, days=timeframe_days, limit=20)
        
        # Project collaboration metrics
        collaboration_metrics = await get_project_collaboration_metrics(db, days=timeframe_days)
        
        # Project performance metrics
        performance_metrics = await get_project_performance_metrics(db, days=timeframe_days)
        
        return {
            "timeframe_days": timeframe_days,
            "total_projects": await get_total_project_count(db),
            "creation_trends": creation_trends,
            "completion_rates": completion_rates,
            "size_analysis": size_analysis,
            "most_active": active_projects,
            "collaboration_metrics": collaboration_metrics,
            "performance_metrics": performance_metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting project analytics: {str(e)}")


@router.get("/admin/tasks/analytics")
async def get_task_analytics_detailed(
    timeframe_days: int = Query(30, description="Timeframe in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get detailed task analytics"""
    try:
        # Task creation and completion trends
        task_trends = await get_task_trends(db, days=timeframe_days)
        
        # Task status distribution
        status_distribution = await get_task_status_distribution(db)
        
        # Task priority analysis
        priority_analysis = await get_task_priority_analysis(db, days=timeframe_days)
        
        # Task completion time analysis
        completion_time_analysis = await get_task_completion_time_analysis(db, days=timeframe_days)
        
        # Task assignment patterns
        assignment_patterns = await get_task_assignment_patterns(db, days=timeframe_days)
        
        # Task productivity metrics
        productivity_metrics = await get_task_productivity_metrics(db, days=timeframe_days)
        
        return {
            "timeframe_days": timeframe_days,
            "total_tasks": await get_total_task_count(db),
            "task_trends": task_trends,
            "status_distribution": status_distribution,
            "priority_analysis": priority_analysis,
            "completion_time_analysis": completion_time_analysis,
            "assignment_patterns": assignment_patterns,
            "productivity_metrics": productivity_metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting task analytics: {str(e)}")


@router.get("/admin/system/health")
async def get_system_health_detailed(
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get detailed system health information"""
    try:
        # Performance health
        performance_health = await performance_monitor.get_performance_summary()
        
        # Database health
        database_health = await get_database_health_metrics()
        
        # Cache health
        cache_health = await get_cache_health_metrics()
        
        # API health
        api_health = await get_api_health_metrics()
        
        # Storage health
        storage_health = await get_storage_health_metrics()
        
        # Security health
        security_health = await get_security_health_metrics()
        
        # Overall health score calculation
        health_components = [
            performance_health.get("health_scores", {}).get("overall", 100),
            database_health.get("health_score", 100),
            cache_health.get("health_score", 100),
            api_health.get("health_score", 100),
            storage_health.get("health_score", 100),
            security_health.get("health_score", 100)
        ]
        
        overall_health_score = sum(health_components) / len(health_components)
        
        return {
            "timestamp": datetime.utcnow(),
            "overall_health_score": round(overall_health_score, 2),
            "health_status": get_health_status_from_score(overall_health_score),
            "components": {
                "performance": performance_health,
                "database": database_health,
                "cache": cache_health,
                "api": api_health,
                "storage": storage_health,
                "security": security_health
            },
            "recommendations": await get_system_health_recommendations(health_components)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system health: {str(e)}")


@router.get("/admin/reports/usage")
async def generate_usage_report(
    start_date: datetime = Query(..., description="Start date for report"),
    end_date: datetime = Query(..., description="End date for report"),
    format: str = Query("json", description="Report format (json, csv, pdf)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Generate comprehensive usage report"""
    try:
        days_diff = (end_date - start_date).days
        
        # User usage metrics
        user_usage = await get_user_usage_report(db, start_date, end_date)
        
        # Organization usage metrics
        org_usage = await get_organization_usage_report(db, start_date, end_date)
        
        # Feature usage metrics
        feature_usage = await get_feature_usage_report(db, start_date, end_date)
        
        # API usage metrics
        api_usage = await get_api_usage_report(start_date, end_date)
        
        # Storage usage metrics
        storage_usage = await get_storage_usage_report(db, start_date, end_date)
        
        # Performance metrics during period
        performance_metrics = await get_performance_report(start_date, end_date)
        
        report_data = {
            "report_metadata": {
                "generated_at": datetime.utcnow(),
                "generated_by": current_user.email,
                "period_start": start_date,
                "period_end": end_date,
                "period_days": days_diff,
                "report_format": format
            },
            "executive_summary": {
                "total_active_users": user_usage.get("active_users", 0),
                "total_organizations": org_usage.get("total_organizations", 0),
                "total_api_requests": api_usage.get("total_requests", 0),
                "average_response_time": performance_metrics.get("avg_response_time", 0),
                "system_uptime_percent": performance_metrics.get("uptime_percent", 100)
            },
            "detailed_metrics": {
                "user_usage": user_usage,
                "organization_usage": org_usage,
                "feature_usage": feature_usage,
                "api_usage": api_usage,
                "storage_usage": storage_usage,
                "performance_metrics": performance_metrics
            }
        }
        
        if format == "csv":
            # Convert to CSV format (implementation would be added)
            return {"message": "CSV format not yet implemented", "data": report_data}
        elif format == "pdf":
            # Convert to PDF format (implementation would be added)
            return {"message": "PDF format not yet implemented", "data": report_data}
        else:
            return report_data
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating usage report: {str(e)}")


@router.post("/admin/reports/schedule")
async def schedule_report(
    report_config: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, str]:
    """Schedule automated report generation"""
    try:
        # Validate report configuration
        required_fields = ["report_type", "schedule", "recipients"]
        for field in required_fields:
            if field not in report_config:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Schedule the report generation
        background_tasks.add_task(
            schedule_automated_report,
            report_config,
            current_user.id
        )
        
        return {
            "status": "success",
            "message": f"Report scheduled successfully: {report_config['report_type']}",
            "schedule": report_config["schedule"],
            "report_id": f"report_{int(datetime.utcnow().timestamp())}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scheduling report: {str(e)}")


# Helper functions for analytics calculations

async def get_system_statistics(db: AsyncSession) -> Dict[str, Any]:
    """Get basic system statistics"""
    # Total counts
    total_users = await db.scalar(select(func.count(User.id)).where(User.is_active == True))
    total_orgs = await db.scalar(select(func.count(Organization.id)).where(Organization.is_active == True))
    total_projects = await db.scalar(select(func.count(Project.id)).where(Project.is_active == True))
    total_tasks = await db.scalar(select(func.count(Task.id)).where(Task.is_active == True))
    
    return {
        "total_users": total_users or 0,
        "total_organizations": total_orgs or 0,
        "total_projects": total_projects or 0,
        "total_tasks": total_tasks or 0,
        "last_updated": datetime.utcnow()
    }


async def get_organization_metrics(db: AsyncSession) -> Dict[str, Any]:
    """Get organization-level metrics"""
    # Most active organizations by task count
    result = await db.execute(
        select(Organization.name, func.count(Task.id).label('task_count'))
        .join(Project, Organization.id == Project.organization_id)
        .join(Task, Project.id == Task.project_id)
        .where(and_(Organization.is_active == True, Task.is_active == True))
        .group_by(Organization.id, Organization.name)
        .order_by(desc('task_count'))
        .limit(10)
    )
    
    top_orgs = [{"name": row[0], "task_count": row[1]} for row in result]
    
    return {
        "top_organizations_by_activity": top_orgs,
        "average_projects_per_org": await get_average_projects_per_org(db),
        "average_users_per_org": await get_average_users_per_org(db)
    }


async def get_recent_system_activities(db: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent system activities"""
    # This would typically come from an audit log table
    # For now, return recent task creations as proxy for activity
    result = await db.execute(
        select(Task.title, Task.created_at, User.username, Project.name.label('project_name'))
        .join(User, Task.assignee_id == User.id)
        .join(Project, Task.project_id == Project.id)
        .where(Task.is_active == True)
        .order_by(desc(Task.created_at))
        .limit(limit)
    )
    
    activities = []
    for row in result:
        activities.append({
            "type": "task_created",
            "description": f"Task '{row[0]}' created in project '{row[3]}'",
            "user": row[2],
            "timestamp": row[1],
            "icon": "plus-circle"
        })
    
    return activities


async def get_system_health_overview() -> Dict[str, Any]:
    """Get basic system health overview"""
    # This would integrate with various health check systems
    return {
        "overall_status": "healthy",
        "api_status": "operational",
        "database_status": "healthy",
        "cache_status": "operational",
        "storage_status": "healthy",
        "last_check": datetime.utcnow()
    }


async def get_growth_metrics(db: AsyncSession) -> Dict[str, Any]:
    """Get growth metrics for the past 30 days"""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # User growth
    users_30_days = await db.scalar(
        select(func.count(User.id))
        .where(and_(User.created_at >= thirty_days_ago, User.is_active == True))
    )
    
    # Organization growth
    orgs_30_days = await db.scalar(
        select(func.count(Organization.id))
        .where(and_(Organization.created_at >= thirty_days_ago, Organization.is_active == True))
    )
    
    # Project growth
    projects_30_days = await db.scalar(
        select(func.count(Project.id))
        .where(and_(Project.created_at >= thirty_days_ago, Project.is_active == True))
    )
    
    return {
        "new_users_30_days": users_30_days or 0,
        "new_organizations_30_days": orgs_30_days or 0,
        "new_projects_30_days": projects_30_days or 0,
        "growth_period": "30 days"
    }


# Additional helper functions would be implemented here...
async def get_average_projects_per_org(db: AsyncSession) -> float:
    """Calculate average projects per organization"""
    result = await db.execute(
        select(func.avg(func.count(Project.id)))
        .select_from(Organization)
        .join(Project, Organization.id == Project.organization_id, isouter=True)
        .where(Organization.is_active == True)
        .group_by(Organization.id)
    )
    avg_projects = result.scalar()
    return round(avg_projects or 0, 2)


async def get_average_users_per_org(db: AsyncSession) -> float:
    """Calculate average users per organization"""
    # This would require a user-organization membership table
    # For now, return a placeholder
    return 5.2


def get_health_status_from_score(score: float) -> str:
    """Convert health score to status string"""
    if score >= 90:
        return "excellent"
    elif score >= 75:
        return "good"
    elif score >= 60:
        return "fair"
    elif score >= 40:
        return "poor"
    else:
        return "critical"


async def schedule_automated_report(report_config: Dict[str, Any], user_id: str):
    """Background task to schedule automated reports"""
    # This would integrate with a job scheduler like Celery
    print(f"Scheduling automated report: {report_config['report_type']} for user {user_id}")
    # Implementation would be added here


# Placeholder functions for various analytics calculations
async def get_project_analytics(db: AsyncSession, days: int) -> Dict[str, Any]:
    """Get project analytics (placeholder)"""
    return {"message": "Project analytics implementation pending"}


async def get_task_analytics(db: AsyncSession, days: int) -> Dict[str, Any]:
    """Get task analytics (placeholder)"""
    return {"message": "Task analytics implementation pending"}


async def get_performance_analytics(days: int) -> Dict[str, Any]:
    """Get performance analytics (placeholder)"""
    return {"message": "Performance analytics implementation pending"}


async def get_feature_adoption_metrics(db: AsyncSession, days: int) -> Dict[str, Any]:
    """Get feature adoption metrics (placeholder)"""
    return {"message": "Feature adoption metrics implementation pending"}


# Additional analytics functions would be implemented here...