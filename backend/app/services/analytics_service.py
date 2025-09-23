"""
Advanced analytics service for comprehensive data analysis and insights
"""
import asyncio
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc, and_, or_, text
from collections import defaultdict, Counter
import json

from app.core.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app.models.project import Project
from app.models.task import Task
from app.services.performance_service import metrics_collector, performance_monitor
from app.core.cache import cache


class AnalyticsService:
    """Comprehensive analytics service for business intelligence"""
    
    def __init__(self):
        self.cache_prefix = "analytics"
        self.default_cache_ttl = 300  # 5 minutes
    
    async def get_user_activity_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive user activity summary"""
        cache_key = f"{self.cache_prefix}:user_activity:{days}"
        cached_result = await cache.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        async for db in get_db():
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Active users metrics
            active_users_result = await db.execute(
                select(func.count(func.distinct(User.id)))
                .where(and_(
                    User.is_active == True,
                    User.last_login >= start_date
                ))
            )
            active_users = active_users_result.scalar() or 0
            
            # New registrations
            new_users_result = await db.execute(
                select(func.count(User.id))
                .where(and_(
                    User.is_active == True,
                    User.created_at >= start_date
                ))
            )
            new_users = new_users_result.scalar() or 0
            
            # Daily activity breakdown
            daily_activity = await self._get_daily_user_activity(db, start_date, end_date)
            
            # User retention analysis
            retention_metrics = await self._calculate_user_retention(db, days)
            
            result = {
                "period_days": days,
                "active_users": active_users,
                "new_registrations": new_users,
                "daily_activity": daily_activity,
                "retention_metrics": retention_metrics,
                "growth_rate": self._calculate_growth_rate(new_users, active_users),
                "last_updated": datetime.utcnow().isoformat()
            }
            
            await cache.set(cache_key, json.dumps(result, default=str), ttl=self.default_cache_ttl)
            return result
    
    async def get_user_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get detailed user analytics"""
        cache_key = f"{self.cache_prefix}:detailed_user_analytics:{days}"
        cached_result = await cache.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        async for db in get_db():
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # User registration trends
            registration_trends = await self._get_user_registration_trends(db, start_date, end_date)
            
            # User engagement patterns
            engagement_patterns = await self._get_user_engagement_patterns(db, start_date, end_date)
            
            # Top active users
            top_users = await self._get_top_active_users(db, start_date, end_date)
            
            # User demographics
            demographics = await self._get_user_demographics(db)
            
            # Session analytics
            session_analytics = await self._get_session_analytics(db, start_date, end_date)
            
            result = {
                "timeframe_days": days,
                "registration_trends": registration_trends,
                "engagement_patterns": engagement_patterns,
                "top_active_users": top_users,
                "demographics": demographics,
                "session_analytics": session_analytics,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            await cache.set(cache_key, json.dumps(result, default=str), ttl=self.default_cache_ttl)
            return result
    
    async def get_usage_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Analyze usage patterns and behavior"""
        cache_key = f"{self.cache_prefix}:usage_patterns:{days}"
        cached_result = await cache.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        # Get API usage patterns from performance metrics
        metrics_summary = metrics_collector.get_metrics_summary(timeframe_minutes=days * 24 * 60)
        
        # Analyze peak usage times
        peak_hours = await self._analyze_peak_hours(days)
        
        # Feature usage frequency
        feature_usage = await self._analyze_feature_usage(days)
        
        # User journey patterns
        journey_patterns = await self._analyze_user_journeys(days)
        
        result = {
            "analysis_period_days": days,
            "peak_usage_hours": peak_hours,
            "feature_usage_frequency": feature_usage,
            "user_journey_patterns": journey_patterns,
            "api_usage_patterns": {
                "total_requests": metrics_summary.get("total_requests", 0),
                "requests_per_hour": metrics_summary.get("requests_per_hour", 0),
                "peak_concurrent_users": metrics_summary.get("peak_concurrent_users", 0)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        await cache.set(cache_key, json.dumps(result, default=str), ttl=self.default_cache_ttl)
        return result
    
    async def get_user_activity_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Get detailed user activity patterns"""
        cache_key = f"{self.cache_prefix}:activity_patterns:{days}"
        cached_result = await cache.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        async for db in get_db():
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Hourly activity distribution
            hourly_distribution = await self._get_hourly_activity_distribution(db, start_date, end_date)
            
            # Daily activity trends
            daily_trends = await self._get_daily_activity_trends(db, start_date, end_date)
            
            # User behavior clusters
            behavior_clusters = await self._analyze_user_behavior_clusters(db, start_date, end_date)
            
            # Activity intensity analysis
            intensity_analysis = await self._analyze_activity_intensity(db, start_date, end_date)
            
            result = {
                "timeframe_days": days,
                "hourly_distribution": hourly_distribution,
                "daily_trends": daily_trends,
                "behavior_clusters": behavior_clusters,
                "intensity_analysis": intensity_analysis,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            await cache.set(cache_key, json.dumps(result, default=str), ttl=self.default_cache_ttl)
            return result
    
    async def generate_executive_summary(self, days: int = 30) -> Dict[str, Any]:
        """Generate executive summary for leadership"""
        cache_key = f"{self.cache_prefix}:executive_summary:{days}"
        cached_result = await cache.get(cache_key)
        
        if cached_result:
            return json.loads(cached_result)
        
        # Gather key metrics
        user_summary = await self.get_user_activity_summary(days)
        usage_patterns = await self.get_usage_patterns(days)
        performance_summary = await performance_monitor.get_performance_summary()
        
        async for db in get_db():
            # Business metrics
            business_metrics = await self._get_business_metrics(db, days)
            
            # Growth indicators
            growth_indicators = await self._get_growth_indicators(db, days)
            
            # Key insights
            key_insights = await self._generate_key_insights(
                user_summary, usage_patterns, business_metrics
            )
            
            result = {
                "summary_period_days": days,
                "key_metrics": {
                    "total_active_users": user_summary.get("active_users", 0),
                    "new_user_growth": user_summary.get("new_registrations", 0),
                    "user_retention_rate": user_summary.get("retention_metrics", {}).get("retention_rate", 0),
                    "system_performance_score": performance_summary.get("health_scores", {}).get("overall", 100),
                    "api_requests_total": usage_patterns.get("api_usage_patterns", {}).get("total_requests", 0)
                },
                "business_metrics": business_metrics,
                "growth_indicators": growth_indicators,
                "key_insights": key_insights,
                "performance_health": performance_summary.get("health_scores", {}),
                "recommendations": await self._generate_executive_recommendations(
                    user_summary, business_metrics, performance_summary
                ),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            await cache.set(cache_key, json.dumps(result, default=str), ttl=self.default_cache_ttl * 2)
            return result
    
    # Private helper methods
    
    async def _get_daily_user_activity(self, db: AsyncSession, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get daily user activity breakdown"""
        result = await db.execute(
            select(
                func.date(User.last_login).label('activity_date'),
                func.count(func.distinct(User.id)).label('active_users')
            )
            .where(and_(
                User.is_active == True,
                User.last_login >= start_date,
                User.last_login <= end_date
            ))
            .group_by(func.date(User.last_login))
            .order_by(func.date(User.last_login))
        )
        
        daily_activity = []
        for row in result:
            daily_activity.append({
                "date": row[0].isoformat() if row[0] else None,
                "active_users": row[1]
            })
        
        return daily_activity
    
    async def _calculate_user_retention(self, db: AsyncSession, days: int) -> Dict[str, Any]:
        """Calculate user retention metrics"""
        # This is a simplified retention calculation
        # In a real implementation, you'd track user sessions and define retention criteria
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        retention_period = end_date - timedelta(days=7)
        
        # Users who registered in the period
        new_users_result = await db.execute(
            select(func.count(User.id))
            .where(and_(
                User.created_at >= start_date,
                User.created_at <= retention_period,
                User.is_active == True
            ))
        )
        new_users = new_users_result.scalar() or 0
        
        # Users who remained active after 7 days
        retained_users_result = await db.execute(
            select(func.count(User.id))
            .where(and_(
                User.created_at >= start_date,
                User.created_at <= retention_period,
                User.last_login >= retention_period,
                User.is_active == True
            ))
        )
        retained_users = retained_users_result.scalar() or 0
        
        retention_rate = (retained_users / new_users * 100) if new_users > 0 else 0
        
        return {
            "new_users": new_users,
            "retained_users": retained_users,
            "retention_rate": round(retention_rate, 2),
            "retention_period_days": 7
        }
    
    def _calculate_growth_rate(self, new_users: int, total_active: int) -> float:
        """Calculate user growth rate"""
        if total_active == 0:
            return 0.0
        return round((new_users / total_active) * 100, 2)
    
    async def _get_user_registration_trends(self, db: AsyncSession, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get user registration trends"""
        result = await db.execute(
            select(
                func.date(User.created_at).label('registration_date'),
                func.count(User.id).label('registrations')
            )
            .where(and_(
                User.created_at >= start_date,
                User.created_at <= end_date,
                User.is_active == True
            ))
            .group_by(func.date(User.created_at))
            .order_by(func.date(User.created_at))
        )
        
        trends = []
        for row in result:
            trends.append({
                "date": row[0].isoformat() if row[0] else None,
                "registrations": row[1]
            })
        
        return {
            "daily_registrations": trends,
            "total_registrations": sum(item["registrations"] for item in trends),
            "average_daily": round(sum(item["registrations"] for item in trends) / len(trends), 2) if trends else 0
        }
    
    async def _get_user_engagement_patterns(self, db: AsyncSession, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze user engagement patterns"""
        # This would typically involve more complex engagement tracking
        # For now, we'll use login frequency as a proxy
        
        # Users by login frequency
        frequent_users = await db.scalar(
            select(func.count(User.id))
            .where(and_(
                User.last_login >= start_date,
                User.is_active == True,
                # Assuming frequent users login more than once per week
                text("(EXTRACT(EPOCH FROM (NOW() - last_login)) / 86400) < 7")
            ))
        )
        
        occasional_users = await db.scalar(
            select(func.count(User.id))
            .where(and_(
                User.last_login >= start_date,
                User.is_active == True,
                text("(EXTRACT(EPOCH FROM (NOW() - last_login)) / 86400) BETWEEN 7 AND 30")
            ))
        )
        
        return {
            "frequent_users": frequent_users or 0,
            "occasional_users": occasional_users or 0,
            "engagement_score": self._calculate_engagement_score(frequent_users or 0, occasional_users or 0)
        }
    
    def _calculate_engagement_score(self, frequent: int, occasional: int) -> float:
        """Calculate overall engagement score"""
        total = frequent + occasional
        if total == 0:
            return 0.0
        
        # Weight frequent users more heavily
        score = ((frequent * 2) + (occasional * 1)) / (total * 2) * 100
        return round(score, 2)
    
    async def _get_top_active_users(self, db: AsyncSession, start_date: datetime, end_date: datetime, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top active users by various metrics"""
        # For this example, we'll rank by task creation/completion
        # In a real system, you'd have more comprehensive activity tracking
        
        result = await db.execute(
            select(
                User.username,
                User.email,
                func.count(Task.id).label('task_count')
            )
            .join(Task, User.id == Task.assignee_id, isouter=True)
            .where(and_(
                User.is_active == True,
                or_(
                    Task.created_at.is_(None),
                    and_(Task.created_at >= start_date, Task.created_at <= end_date)
                )
            ))
            .group_by(User.id, User.username, User.email)
            .order_by(desc('task_count'))
            .limit(limit)
        )
        
        top_users = []
        for row in result:
            top_users.append({
                "username": row[0],
                "email": row[1],
                "activity_score": row[2] or 0,
                "metric": "tasks_handled"
            })
        
        return top_users
    
    async def _get_user_demographics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get user demographic information"""
        # This would depend on what demographic data you collect
        # For now, we'll provide basic statistics
        
        total_users = await db.scalar(
            select(func.count(User.id)).where(User.is_active == True)
        )
        
        # Users by organization count (as a proxy for user type)
        org_distribution = await db.execute(
            select(
                Organization.name,
                func.count(User.id).label('user_count')
            )
            .join(User, Organization.id == User.id, isouter=True)  # This join would need proper membership table
            .where(Organization.is_active == True)
            .group_by(Organization.id, Organization.name)
            .order_by(desc('user_count'))
            .limit(10)
        )
        
        org_stats = []
        for row in org_distribution:
            org_stats.append({
                "organization": row[0],
                "user_count": row[1]
            })
        
        return {
            "total_users": total_users or 0,
            "organization_distribution": org_stats,
            "demographic_data": "Limited demographic tracking implemented"
        }
    
    async def _get_session_analytics(self, db: AsyncSession, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get session analytics (simplified)"""
        # This would require session tracking implementation
        # For now, return placeholder data
        
        return {
            "average_session_duration": 25.5,  # minutes
            "sessions_per_user": 3.2,
            "bounce_rate": 15.8,  # percentage
            "note": "Session tracking requires additional implementation"
        }
    
    async def _analyze_peak_hours(self, days: int) -> List[int]:
        """Analyze peak usage hours"""
        # This would analyze actual usage data
        # For now, return typical business hours
        return [9, 10, 11, 14, 15, 16]  # Peak hours (24-hour format)
    
    async def _analyze_feature_usage(self, days: int) -> Dict[str, int]:
        """Analyze feature usage frequency"""
        # This would track actual feature usage
        # For now, return sample data
        return {
            "task_management": 1250,
            "project_creation": 340,
            "file_uploads": 890,
            "team_collaboration": 720,
            "reporting": 180,
            "search": 560
        }
    
    async def _analyze_user_journeys(self, days: int) -> List[Dict[str, Any]]:
        """Analyze common user journey patterns"""
        # This would require detailed user interaction tracking
        # For now, return common patterns
        return [
            {
                "journey": "New User Onboarding",
                "steps": ["registration", "profile_setup", "first_project", "invite_team"],
                "completion_rate": 78.5,
                "average_time_minutes": 45
            },
            {
                "journey": "Task Management",
                "steps": ["task_creation", "assignment", "progress_update", "completion"],
                "completion_rate": 92.1,
                "average_time_minutes": 180
            }
        ]
    
    async def _get_hourly_activity_distribution(self, db: AsyncSession, start_date: datetime, end_date: datetime) -> Dict[int, int]:
        """Get hourly activity distribution"""
        # This would require timestamp analysis of user activities
        # For now, return sample distribution
        return {
            hour: max(0, 100 - abs(hour - 14) * 8) for hour in range(24)
        }
    
    async def _get_daily_activity_trends(self, db: AsyncSession, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get daily activity trends"""
        current_date = start_date
        trends = []
        
        while current_date <= end_date:
            # This would calculate actual daily activity
            # For now, simulate data
            activity_score = 75 + (hash(current_date.isoformat()) % 50)
            trends.append({
                "date": current_date.isoformat(),
                "activity_score": activity_score
            })
            current_date += timedelta(days=1)
        
        return {
            "daily_trends": trends,
            "average_activity": sum(item["activity_score"] for item in trends) / len(trends) if trends else 0
        }
    
    async def _analyze_user_behavior_clusters(self, db: AsyncSession, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze user behavior clusters"""
        # This would use machine learning for user segmentation
        # For now, return simplified clusters
        return {
            "power_users": {"count": 45, "characteristics": "High task completion, frequent logins"},
            "regular_users": {"count": 234, "characteristics": "Moderate usage, team collaboration"},
            "occasional_users": {"count": 89, "characteristics": "Infrequent usage, basic features"},
            "new_users": {"count": 67, "characteristics": "Recent registration, exploring features"}
        }
    
    async def _analyze_activity_intensity(self, db: AsyncSession, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze activity intensity patterns"""
        return {
            "high_intensity_hours": [10, 11, 14, 15],
            "medium_intensity_hours": [9, 12, 13, 16, 17],
            "low_intensity_hours": [8, 18, 19, 20],
            "intensity_score": 72.5
        }
    
    async def _get_business_metrics(self, db: AsyncSession, days: int) -> Dict[str, Any]:
        """Get key business metrics"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Project completion rate
        total_projects = await db.scalar(
            select(func.count(Project.id))
            .where(and_(Project.created_at >= start_date, Project.is_active == True))
        )
        
        completed_projects = await db.scalar(
            select(func.count(Project.id))
            .where(and_(
                Project.created_at >= start_date,
                Project.status == "completed",  # Assuming status field exists
                Project.is_active == True
            ))
        ) or 0
        
        completion_rate = (completed_projects / total_projects * 100) if total_projects else 0
        
        return {
            "project_completion_rate": round(completion_rate, 2),
            "total_projects_created": total_projects or 0,
            "completed_projects": completed_projects,
            "active_projects": (total_projects or 0) - completed_projects
        }
    
    async def _get_growth_indicators(self, db: AsyncSession, days: int) -> Dict[str, Any]:
        """Get growth indicators"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        previous_start = start_date - timedelta(days=days)
        
        # Current period metrics
        current_users = await db.scalar(
            select(func.count(User.id))
            .where(and_(User.created_at >= start_date, User.is_active == True))
        ) or 0
        
        current_orgs = await db.scalar(
            select(func.count(Organization.id))
            .where(and_(Organization.created_at >= start_date, Organization.is_active == True))
        ) or 0
        
        # Previous period metrics
        previous_users = await db.scalar(
            select(func.count(User.id))
            .where(and_(
                User.created_at >= previous_start,
                User.created_at < start_date,
                User.is_active == True
            ))
        ) or 0
        
        previous_orgs = await db.scalar(
            select(func.count(Organization.id))
            .where(and_(
                Organization.created_at >= previous_start,
                Organization.created_at < start_date,
                Organization.is_active == True
            ))
        ) or 0
        
        # Calculate growth rates
        user_growth = ((current_users - previous_users) / previous_users * 100) if previous_users else 0
        org_growth = ((current_orgs - previous_orgs) / previous_orgs * 100) if previous_orgs else 0
        
        return {
            "user_growth_rate": round(user_growth, 2),
            "organization_growth_rate": round(org_growth, 2),
            "current_period_users": current_users,
            "previous_period_users": previous_users,
            "current_period_organizations": current_orgs,
            "previous_period_organizations": previous_orgs
        }
    
    async def _generate_key_insights(self, user_summary: Dict, usage_patterns: Dict, business_metrics: Dict) -> List[str]:
        """Generate key insights from analytics data"""
        insights = []
        
        # User growth insights
        if user_summary.get("growth_rate", 0) > 10:
            insights.append("Strong user growth indicates successful user acquisition strategies")
        elif user_summary.get("growth_rate", 0) < 5:
            insights.append("User growth is slower than expected - consider marketing initiatives")
        
        # Retention insights
        retention_rate = user_summary.get("retention_metrics", {}).get("retention_rate", 0)
        if retention_rate > 80:
            insights.append("Excellent user retention indicates high product satisfaction")
        elif retention_rate < 60:
            insights.append("User retention needs improvement - focus on user experience")
        
        # Feature usage insights
        api_requests = usage_patterns.get("api_usage_patterns", {}).get("total_requests", 0)
        if api_requests > 10000:
            insights.append("High API usage indicates strong platform engagement")
        
        # Business metrics insights
        completion_rate = business_metrics.get("project_completion_rate", 0)
        if completion_rate > 80:
            insights.append("High project completion rate shows effective task management")
        elif completion_rate < 50:
            insights.append("Low project completion rate may indicate workflow issues")
        
        return insights
    
    async def _generate_executive_recommendations(self, user_summary: Dict, business_metrics: Dict, performance_summary: Dict) -> List[str]:
        """Generate recommendations for executives"""
        recommendations = []
        
        # Performance recommendations
        overall_performance = performance_summary.get("health_scores", {}).get("overall", 100)
        if overall_performance < 80:
            recommendations.append("Invest in performance optimization to improve user experience")
        
        # Growth recommendations
        growth_rate = user_summary.get("growth_rate", 0)
        if growth_rate < 10:
            recommendations.append("Consider expanding marketing efforts to accelerate user acquisition")
        
        # Retention recommendations
        retention_rate = user_summary.get("retention_metrics", {}).get("retention_rate", 0)
        if retention_rate < 70:
            recommendations.append("Implement user onboarding improvements and feature tutorials")
        
        # Business efficiency recommendations
        completion_rate = business_metrics.get("project_completion_rate", 0)
        if completion_rate < 70:
            recommendations.append("Review project management workflows and provide team training")
        
        return recommendations


# Global analytics service instance
analytics_service = AnalyticsService()


# Export the service
__all__ = ['analytics_service', 'AnalyticsService']