"""
Health check endpoints for production monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import os
import asyncio

from app.core.database import get_db
from app.core.monitoring import HealthChecker, PerformanceMonitor, logger

router = APIRouter(tags=["health"])


@router.get("/health")
async def basic_health_check():
    """Basic health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "teamflow-api"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check with all system components"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "teamflow-api",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "checks": {}
    }
    
    overall_healthy = True
    
    try:
        # Database health check
        db_health = await HealthChecker.check_database_health(db)
        health_status["checks"]["database"] = db_health
        if db_health["status"] != "healthy":
            overall_healthy = False
            
        # Memory usage check
        memory_health = await HealthChecker.check_memory_usage()
        health_status["checks"]["memory"] = memory_health
        
        # System info
        system_info = HealthChecker.get_system_info()
        health_status["checks"]["system"] = system_info
        
        # Performance metrics
        performance_metrics = PerformanceMonitor.get_metrics_summary()
        if performance_metrics:
            health_status["checks"]["performance"] = {
                "status": "healthy",
                "metrics_available": len(performance_metrics),
                "operations": list(performance_metrics.keys())[:5]  # Show first 5
            }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        overall_healthy = False
        health_status["checks"]["error"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Set overall status
    if not overall_healthy:
        health_status["status"] = "unhealthy"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )
    
    return health_status


@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe endpoint"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Kubernetes readiness probe endpoint"""
    try:
        # Check if we can connect to database
        await HealthChecker.check_database_health(db)
        
        return {
            "status": "ready", 
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/health/metrics")
async def metrics_endpoint():
    """Prometheus-style metrics endpoint"""
    try:
        metrics = PerformanceMonitor.get_metrics_summary()
        memory_info = await HealthChecker.check_memory_usage()
        
        # Format as simple key-value pairs for now
        # In production, you'd use proper Prometheus format
        response_lines = [
            "# HELP http_requests_total Total HTTP requests",
            "# TYPE http_requests_total counter"
        ]
        
        for operation, stats in metrics.items():
            # Clean operation name for metrics
            metric_name = operation.replace(" ", "_").replace("/", "_").lower()
            response_lines.extend([
                f'http_request_duration_avg{{operation="{operation}"}} {stats["avg"]:.2f}',
                f'http_request_duration_max{{operation="{operation}"}} {stats["max"]:.2f}',
                f'http_requests_total{{operation="{operation}"}} {stats["count"]}'
            ])
        
        if memory_info.get("status") == "healthy":
            response_lines.extend([
                "# HELP memory_usage_mb Current memory usage in MB",
                "# TYPE memory_usage_mb gauge",
                f'memory_usage_mb {memory_info["memory_usage_mb"]}'
            ])
        
        return {
            "metrics": "\n".join(response_lines),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {str(e)}")
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/health/dependencies")
async def dependencies_check():
    """Check external dependencies"""
    dependencies = {
        "database": {"status": "unknown"},
        "external_apis": {"status": "not_implemented"},
        "file_storage": {"status": "not_implemented"}
    }
    
    overall_healthy = True
    
    try:
        # We would check external services here
        # For now, just return basic structure
        dependencies["timestamp"] = datetime.utcnow().isoformat()
        
    except Exception as e:
        overall_healthy = False
        dependencies["error"] = str(e)
    
    if not overall_healthy:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=dependencies
        )
    
    return dependencies


# Additional health check for specific services
@router.get("/api/v1/auth/health")
async def auth_service_health():
    """Health check specific to authentication service"""
    try:
        # In a real implementation, you might check:
        # - JWT secret is available
        # - External auth providers are reachable
        # - User session store is accessible
        
        auth_health = {
            "status": "healthy",
            "service": "authentication",
            "timestamp": datetime.utcnow().isoformat(),
            "jwt_configured": bool(os.getenv("SECRET_KEY")),
            "features": {
                "password_auth": True,
                "jwt_tokens": True,
                "refresh_tokens": True
            }
        }
        
        return auth_health
        
    except Exception as e:
        logger.error(f"Auth health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "service": "authentication", 
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )