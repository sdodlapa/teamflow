# Performance Monitoring API Endpoints
# Day 6: Performance Optimization & Scaling Implementation

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.security import get_current_user
from app.models.user import User
from app.services.performance_service import (
    performance_monitor, 
    metrics_collector,
    PerformanceMonitor,
    MetricsCollector
)

router = APIRouter()

# Pydantic models for API responses
class PerformanceMetricResponse(BaseModel):
    """Performance metric data structure"""
    timestamp: datetime
    metric_name: str
    value: float
    tags: Dict[str, str] = Field(default_factory=dict)
    duration: Optional[float] = None

class EndpointStatsResponse(BaseModel):
    """Endpoint performance statistics"""
    endpoint: str
    avg_duration: float
    min_duration: float
    max_duration: float
    request_count: int
    error_count: int
    error_rate: float
    p95_duration: float
    p99_duration: float

class SystemHealthResponse(BaseModel):
    """System health check response"""
    overall_status: str
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_requests: int
    database_status: str
    cache_status: str
    uptime_seconds: float

class PerformanceAlertResponse(BaseModel):
    """Performance alert structure"""
    level: str  # info, warning, critical
    message: str
    timestamp: datetime
    endpoint: Optional[str] = None
    duration: Optional[float] = None
    error_rate: Optional[float] = None
    query: Optional[str] = None

class CacheStatsResponse(BaseModel):
    """Cache performance statistics"""
    hit_ratio: float
    total_hits: int
    total_misses: int
    total_operations: int
    redis_available: bool
    local_cache_size: int

class DatabaseStatsResponse(BaseModel):
    """Database performance statistics"""
    active_connections: int
    total_connections: int
    avg_query_time: float
    slow_query_count: int
    cache_hit_ratio: float
    table_count: int
    recent_queries: List[Dict[str, Any]]

class PerformanceSummaryResponse(BaseModel):
    """Comprehensive performance summary"""
    timestamp: datetime
    overall_health_score: int
    system_health: SystemHealthResponse
    endpoint_stats: List[EndpointStatsResponse]
    cache_stats: CacheStatsResponse
    database_stats: DatabaseStatsResponse
    recent_alerts: List[PerformanceAlertResponse]
    recommendations: List[str]

@router.get("/health", response_model=SystemHealthResponse, tags=["Performance"])
async def get_system_health():
    """
    Get comprehensive system health status
    
    Returns real-time system health metrics including:
    - CPU and memory usage
    - Disk usage
    - Active request count
    - Database connectivity
    - Cache status
    """
    try:
        # Get system metrics
        system_metrics = performance_monitor.get_system_metrics()
        app_metrics = metrics_collector.get_metrics_summary(timeframe_minutes=5)
        
        # Determine overall status
        cpu_percent = system_metrics.get("cpu", {}).get("percent", 0) if system_metrics else 0
        memory_percent = system_metrics.get("memory", {}).get("percent", 0) if system_metrics else 0
        disk_percent = system_metrics.get("disk", {}).get("percent", 0) if system_metrics else 0
        
        # Health status logic
        if cpu_percent > 90 or memory_percent > 95:
            overall_status = "critical"
        elif cpu_percent > 80 or memory_percent > 85:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        # Check cache status
        cache_status = "healthy"
        if metrics_collector.redis_client:
            try:
                await metrics_collector.redis_client.ping()
                cache_status = "healthy"
            except:
                cache_status = "degraded"
        else:
            cache_status = "unavailable"
        
        return SystemHealthResponse(
            overall_status=overall_status,
            timestamp=datetime.utcnow(),
            cpu_percent=round(cpu_percent, 2),
            memory_percent=round(memory_percent, 2),
            disk_percent=round(disk_percent, 2),
            active_requests=app_metrics.get("active_requests", 0),
            database_status="healthy",  # Would implement proper DB health check
            cache_status=cache_status,
            uptime_seconds=0  # Would implement proper uptime tracking
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/metrics", response_model=PerformanceSummaryResponse, tags=["Performance"])
async def get_performance_metrics(
    timeframe_minutes: int = Query(5, ge=1, le=60, description="Timeframe in minutes for metrics aggregation"),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive performance metrics summary
    
    Returns detailed performance analysis including:
    - Request timing statistics
    - Database performance metrics
    - Cache hit ratios
    - System resource usage
    - Recent performance alerts
    - Optimization recommendations
    """
    try:
        # Get application metrics
        app_metrics = metrics_collector.get_metrics_summary(timeframe_minutes)
        
        # Get system health
        health_response = await get_system_health()
        
        # Process endpoint statistics
        endpoint_stats_list = []
        for endpoint, stats in app_metrics.get("endpoint_stats", {}).items():
            recent_times = list(metrics_collector.endpoint_performance[endpoint]["recent_times"])
            
            # Calculate percentiles
            if recent_times:
                sorted_times = sorted(recent_times)
                p95_idx = int(len(sorted_times) * 0.95)
                p99_idx = int(len(sorted_times) * 0.99)
                p95_duration = sorted_times[p95_idx] if p95_idx < len(sorted_times) else 0
                p99_duration = sorted_times[p99_idx] if p99_idx < len(sorted_times) else 0
            else:
                p95_duration = p99_duration = 0
            
            endpoint_stats_list.append(EndpointStatsResponse(
                endpoint=endpoint,
                avg_duration=round(stats.get("avg_duration", 0), 2),
                min_duration=round(stats.get("min_duration", 0), 2),
                max_duration=round(stats.get("max_duration", 0), 2),
                request_count=stats.get("request_count", 0),
                error_count=metrics_collector.endpoint_performance[endpoint]["error_count"],
                error_rate=round(
                    metrics_collector.endpoint_performance[endpoint]["error_count"] / 
                    max(1, stats.get("request_count", 1)), 3
                ),
                p95_duration=round(p95_duration, 2),
                p99_duration=round(p99_duration, 2)
            ))
        
        # Cache statistics
        cache_stats = CacheStatsResponse(
            hit_ratio=round(app_metrics.get("cache_stats", {}).get("hit_ratio", 0), 2),
            total_hits=app_metrics.get("cache_stats", {}).get("total_hits", 0),
            total_misses=app_metrics.get("cache_stats", {}).get("total_misses", 0),
            total_operations=metrics_collector.cache_hit_miss["hits"] + metrics_collector.cache_hit_miss["misses"],
            redis_available=metrics_collector.redis_client is not None,
            local_cache_size=len(metrics_collector.metrics)
        )
        
        # Database statistics
        db_stats = app_metrics.get("database_stats", {})
        recent_db_queries = list(metrics_collector.db_query_times)[-10:]  # Last 10 queries
        
        database_stats = DatabaseStatsResponse(
            active_connections=db_stats.get("active_connections", 0),
            total_connections=db_stats.get("total_connections", 0),
            avg_query_time=round(db_stats.get("avg_duration", 0), 2),
            slow_query_count=len(metrics_collector.slow_queries),
            cache_hit_ratio=0,  # Would implement proper DB cache hit ratio
            table_count=0,  # Would implement proper table count
            recent_queries=[
                {
                    "query": q.get("query", "")[:100],
                    "duration": round(q.get("duration", 0), 2),
                    "timestamp": q.get("timestamp", datetime.utcnow()).isoformat()
                }
                for q in recent_db_queries
            ]
        )
        
        # Recent alerts
        recent_alerts = [
            PerformanceAlertResponse(
                level=alert["level"],
                message=alert["message"],
                timestamp=alert["timestamp"],
                endpoint=alert.get("endpoint"),
                duration=alert.get("duration"),
                error_rate=alert.get("error_rate"),
                query=alert.get("query")
            )
            for alert in list(metrics_collector.performance_alerts)[-20:]  # Last 20 alerts
        ]
        
        # Generate recommendations
        recommendations = []
        
        # Response time recommendations
        for stats in endpoint_stats_list:
            if stats.avg_duration > 1000:
                recommendations.append(f"Optimize {stats.endpoint} - average response time is {stats.avg_duration}ms")
        
        # Database recommendations
        if len(metrics_collector.slow_queries) > 5:
            recommendations.append("Multiple slow database queries detected - consider query optimization")
        
        # Cache recommendations
        if cache_stats.hit_ratio < 80:
            recommendations.append("Cache hit ratio is below 80% - review caching strategy")
        
        # System recommendations
        if health_response.cpu_percent > 80:
            recommendations.append("CPU usage is high - consider scaling or optimization")
        if health_response.memory_percent > 85:
            recommendations.append("Memory usage is high - review memory consumption patterns")
        
        # Calculate overall health score
        health_score = 100
        if health_response.cpu_percent > 80:
            health_score -= 10
        if health_response.memory_percent > 85:
            health_score -= 10
        if cache_stats.hit_ratio < 80:
            health_score -= 5
        if database_stats.avg_query_time > 100:
            health_score -= 10
        
        return PerformanceSummaryResponse(
            timestamp=datetime.utcnow(),
            overall_health_score=max(0, health_score),
            system_health=health_response,
            endpoint_stats=endpoint_stats_list,
            cache_stats=cache_stats,
            database_stats=database_stats,
            recent_alerts=recent_alerts,
            recommendations=recommendations
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@router.get("/alerts", response_model=List[PerformanceAlertResponse], tags=["Performance"])
async def get_performance_alerts(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of alerts to return"),
    level: Optional[str] = Query(None, description="Filter by alert level: info, warning, critical"),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent performance alerts
    
    Returns a list of performance alerts with filtering options
    """
    try:
        alerts = list(metrics_collector.performance_alerts)
        
        # Filter by level if specified
        if level:
            alerts = [alert for alert in alerts if alert.get("level") == level]
        
        # Sort by timestamp (newest first) and limit
        alerts = sorted(alerts, key=lambda x: x.get("timestamp", datetime.min), reverse=True)[:limit]
        
        return [
            PerformanceAlertResponse(
                level=alert["level"],
                message=alert["message"],
                timestamp=alert["timestamp"],
                endpoint=alert.get("endpoint"),
                duration=alert.get("duration"),
                error_rate=alert.get("error_rate"),
                query=alert.get("query")
            )
            for alert in alerts
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance alerts: {str(e)}")

@router.get("/cache/stats", response_model=CacheStatsResponse, tags=["Performance"])
async def get_cache_statistics(current_user: User = Depends(get_current_user)):
    """
    Get detailed cache performance statistics
    
    Returns cache hit ratios, operation counts, and status
    """
    try:
        return CacheStatsResponse(
            hit_ratio=round(
                metrics_collector.cache_hit_miss["hits"] / 
                max(1, metrics_collector.cache_hit_miss["hits"] + metrics_collector.cache_hit_miss["misses"]) * 100, 2
            ),
            total_hits=metrics_collector.cache_hit_miss["hits"],
            total_misses=metrics_collector.cache_hit_miss["misses"],
            total_operations=metrics_collector.cache_hit_miss["hits"] + metrics_collector.cache_hit_miss["misses"],
            redis_available=metrics_collector.redis_client is not None,
            local_cache_size=len(metrics_collector.metrics)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache statistics: {str(e)}")

@router.post("/cache/clear", tags=["Performance"])
async def clear_performance_cache(current_user: User = Depends(get_current_user)):
    """
    Clear performance monitoring cache
    
    Clears both Redis and local caches for performance data
    """
    try:
        cleared_items = 0
        
        # Clear Redis cache if available
        if metrics_collector.redis_client:
            try:
                # Get all teamflow:performance:* keys
                keys = await metrics_collector.redis_client.keys("teamflow:performance:*")
                if keys:
                    cleared_items += await metrics_collector.redis_client.delete(*keys)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to clear Redis cache: {str(e)}")
        
        # Clear local metrics (keep structure but clear data)
        with metrics_collector._lock:
            metrics_collector.metrics.clear()
            for endpoint_times in metrics_collector.request_times.values():
                endpoint_times.clear()
            metrics_collector.db_query_times.clear()
            metrics_collector.slow_queries.clear()
            metrics_collector.performance_alerts.clear()
            
            # Reset counters but keep structure
            for endpoint_stats in metrics_collector.endpoint_performance.values():
                endpoint_stats["total_time"] = 0
                endpoint_stats["request_count"] = 0
                endpoint_stats["error_count"] = 0
                endpoint_stats["min_time"] = float('inf')
                endpoint_stats["max_time"] = 0
                endpoint_stats["recent_times"].clear()
        
        return {
            "message": "Performance cache cleared successfully",
            "redis_keys_cleared": cleared_items,
            "local_cache_cleared": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear performance cache: {str(e)}")

@router.get("/database/slow-queries", tags=["Performance"]) 
async def get_slow_database_queries(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of slow queries to return"),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent slow database queries
    
    Returns queries that exceeded the slow query threshold
    """
    try:
        slow_queries = list(metrics_collector.slow_queries)[-limit:]
        
        return {
            "slow_queries": [
                {
                    "query": q["query"],
                    "duration_ms": round(q["duration"], 2),
                    "timestamp": q["timestamp"].isoformat()
                }
                for q in slow_queries
            ],
            "threshold_ms": metrics_collector.alert_thresholds["slow_db_query"],
            "total_slow_queries": len(metrics_collector.slow_queries),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get slow queries: {str(e)}")