"""
Performance monitoring and optimization API endpoints
"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.services.performance_service import performance_monitor, metrics_collector
from app.core.database_optimizer import db_optimizer, query_tracker, db_maintenance
from app.core.cache import cache


router = APIRouter()


@router.get("/performance/dashboard")
async def get_performance_dashboard(
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get comprehensive performance dashboard data"""
    try:
        # Get performance summary
        performance_summary = await performance_monitor.get_performance_summary()
        
        # Get query statistics
        query_stats = query_tracker.get_query_stats()
        slow_queries = query_tracker.get_slow_queries()
        
        # Get cache statistics
        cache_stats = cache.get_stats()
        
        # Get database optimization stats
        db_stats = await db_optimizer.get_database_size_stats()
        
        return {
            "performance_summary": performance_summary,
            "query_statistics": {
                "overview": query_stats,
                "slow_queries": slow_queries[:10]  # Top 10 slow queries
            },
            "cache_statistics": cache_stats,
            "database_statistics": db_stats,
            "timestamp": performance_summary.get("timestamp")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance dashboard: {str(e)}")


@router.get("/performance/metrics")
async def get_performance_metrics(
    timeframe_minutes: int = Query(5, description="Timeframe in minutes for metrics"),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get performance metrics for specified timeframe"""
    try:
        metrics_summary = metrics_collector.get_metrics_summary(timeframe_minutes)
        system_metrics = performance_monitor.get_system_metrics()
        
        return {
            "metrics_summary": metrics_summary,
            "system_metrics": system_metrics,
            "timeframe_minutes": timeframe_minutes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance metrics: {str(e)}")


@router.get("/performance/database/analysis")
async def get_database_analysis(
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get comprehensive database performance analysis"""
    try:
        # Get slow queries analysis
        slow_queries = await db_optimizer.analyze_slow_queries()
        
        # Get index recommendations
        index_recommendations = await db_optimizer.get_index_recommendations()
        
        # Get table statistics
        table_stats = await db_optimizer.get_table_statistics()
        
        # Get connection pool stats
        connection_stats = await db_optimizer.optimize_connection_pool()
        
        # Get database size stats
        size_stats = await db_optimizer.get_database_size_stats()
        
        return {
            "slow_queries": slow_queries,
            "index_recommendations": index_recommendations,
            "table_statistics": table_stats[:10],  # Top 10 most active tables
            "connection_pool": connection_stats,
            "database_size": size_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting database analysis: {str(e)}")


@router.get("/performance/database/slow-queries")
async def get_slow_queries(
    min_duration_ms: float = Query(100, description="Minimum duration in milliseconds"),
    current_user: User = Depends(get_current_admin_user)
) -> List[Dict[str, Any]]:
    """Get slow queries analysis"""
    try:
        slow_queries = await db_optimizer.analyze_slow_queries(min_duration_ms)
        return slow_queries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting slow queries: {str(e)}")


@router.get("/performance/database/indexes")
async def get_index_recommendations(
    current_user: User = Depends(get_current_admin_user)
) -> List[Dict[str, Any]]:
    """Get index recommendations for performance optimization"""
    try:
        recommendations = await db_optimizer.get_index_recommendations()
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting index recommendations: {str(e)}")


@router.post("/performance/database/analyze")
async def analyze_database_statistics(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, str]:
    """Run ANALYZE on database to update statistics"""
    try:
        # Run analysis in background
        background_tasks.add_task(db_maintenance.analyze_all_tables)
        
        return {
            "status": "success",
            "message": "Database analysis started in background"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting database analysis: {str(e)}")


@router.post("/performance/database/vacuum")
async def vacuum_database_tables(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, str]:
    """Run VACUUM ANALYZE on tables that need maintenance"""
    try:
        # Run vacuum in background
        background_tasks.add_task(db_maintenance.vacuum_analyze_tables)
        
        return {
            "status": "success",
            "message": "Database vacuum started in background"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting database vacuum: {str(e)}")


@router.get("/performance/cache/statistics")
async def get_cache_statistics(
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get detailed cache statistics"""
    try:
        cache_stats = cache.get_stats()
        
        # Get additional cache performance metrics
        cache_metrics = metrics_collector.get_metrics_summary()
        
        return {
            "cache_stats": cache_stats,
            "performance_metrics": cache_metrics.get("cache_stats", {}),
            "recommendations": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache statistics: {str(e)}")


@router.post("/performance/cache/clear")
async def clear_cache(
    pattern: Optional[str] = Query(None, description="Pattern to match for selective clearing"),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Clear cache entries"""
    try:
        if pattern:
            deleted_count = cache.invalidate_pattern(pattern)
            return {
                "status": "success",
                "message": f"Cleared {deleted_count} cache entries matching pattern '{pattern}'"
            }
        else:
            # Clear all cache (not implemented for safety)
            return {
                "status": "error",
                "message": "Pattern required for cache clearing"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")


@router.get("/performance/system/resources")
async def get_system_resources(
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get current system resource usage"""
    try:
        system_metrics = performance_monitor.get_system_metrics()
        return system_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system resources: {str(e)}")


@router.get("/performance/api/endpoints")
async def get_api_performance(
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get API endpoint performance statistics"""
    try:
        metrics_summary = metrics_collector.get_metrics_summary(timeframe_minutes=30)
        endpoint_stats = metrics_summary.get("endpoint_stats", {})
        
        # Sort endpoints by average response time
        sorted_endpoints = sorted(
            endpoint_stats.items(),
            key=lambda x: x[1]["avg_duration"],
            reverse=True
        )
        
        return {
            "endpoint_performance": dict(sorted_endpoints),
            "summary": {
                "total_endpoints": len(endpoint_stats),
                "slowest_endpoint": sorted_endpoints[0] if sorted_endpoints else None,
                "average_response_time": sum(
                    stats["avg_duration"] for stats in endpoint_stats.values()
                ) / len(endpoint_stats) if endpoint_stats else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting API performance: {str(e)}")


@router.get("/performance/alerts")
async def get_performance_alerts(
    current_user: User = Depends(get_current_admin_user)
) -> List[Dict[str, Any]]:
    """Get performance alerts and recommendations"""
    try:
        performance_summary = await performance_monitor.get_performance_summary()
        recommendations = performance_summary.get("recommendations", [])
        health_scores = performance_summary.get("health_scores", {})
        
        alerts = []
        
        # Generate alerts based on health scores
        for component, score in health_scores.items():
            if score < 70:
                severity = "critical" if score < 50 else "warning"
                alerts.append({
                    "component": component,
                    "severity": severity,
                    "score": score,
                    "message": f"{component.replace('_', ' ').title()} performance is below threshold ({score}/100)"
                })
        
        # Add recommendations as alerts
        for recommendation in recommendations:
            alerts.append({
                "component": "optimization",
                "severity": "info",
                "score": None,
                "message": recommendation
            })
        
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance alerts: {str(e)}")


@router.get("/performance/health")
async def get_performance_health(
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Get overall performance health status"""
    try:
        performance_summary = await performance_monitor.get_performance_summary()
        health_scores = performance_summary.get("health_scores", {})
        
        overall_score = health_scores.get("overall", 0)
        
        # Determine health status
        if overall_score >= 90:
            status = "excellent"
        elif overall_score >= 75:
            status = "good"
        elif overall_score >= 60:
            status = "fair"
        elif overall_score >= 40:
            status = "poor"
        else:
            status = "critical"
        
        return {
            "overall_score": overall_score,
            "status": status,
            "component_scores": health_scores,
            "timestamp": performance_summary.get("timestamp"),
            "recommendations_count": len(performance_summary.get("recommendations", []))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance health: {str(e)}")


@router.post("/performance/optimize")
async def run_performance_optimization(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, str]:
    """Run automated performance optimization tasks"""
    try:
        # Schedule optimization tasks in background
        background_tasks.add_task(db_maintenance.analyze_all_tables)
        background_tasks.add_task(db_maintenance.vacuum_analyze_tables)
        
        return {
            "status": "success",
            "message": "Performance optimization tasks started in background"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting performance optimization: {str(e)}")


@router.get("/performance/report")
async def generate_performance_report(
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Generate comprehensive performance report"""
    try:
        # Get all performance data
        performance_summary = await performance_monitor.get_performance_summary()
        database_analysis = await get_database_analysis(current_user)
        cache_stats = cache.get_stats()
        query_stats = query_tracker.get_query_stats()
        
        # Generate report
        report = {
            "report_timestamp": performance_summary.get("timestamp"),
            "executive_summary": {
                "overall_health_score": performance_summary.get("health_scores", {}).get("overall", 0),
                "total_requests": metrics_collector.total_requests,
                "error_count": metrics_collector.error_count,
                "cache_hit_ratio": cache_stats.get("redis_hit_ratio", 0)
            },
            "performance_metrics": performance_summary.get("application_metrics", {}),
            "system_health": performance_summary.get("system_metrics", {}),
            "database_analysis": {
                "slow_queries_count": len(database_analysis["slow_queries"]),
                "index_recommendations_count": len(database_analysis["index_recommendations"]),
                "connection_pool_health": database_analysis["connection_pool"]
            },
            "cache_performance": cache_stats,
            "recommendations": performance_summary.get("recommendations", []),
            "health_scores": performance_summary.get("health_scores", {})
        }
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating performance report: {str(e)}")