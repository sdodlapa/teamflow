"""
Production monitoring utilities for TeamFlow Backend
Provides error tracking, performance monitoring, and health checks
"""

import os
import time
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import Request, Response
import asyncio

# Setup structured logging
class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add custom fields if available
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
            
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
            
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)


def setup_logging() -> logging.Logger:
    """Setup production logging configuration"""
    logger = logging.getLogger("teamflow")
    
    # Don't add handlers multiple times
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Console handler with JSON formatting
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    # Suppress verbose library logs in production
    if os.getenv("ENVIRONMENT") == "production":
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    return logger


# Global logger instance
logger = setup_logging()


class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    _instance = None
    _metrics: Dict[str, list] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def start_timer(cls, operation: str) -> float:
        """Start timing an operation"""
        return time.time()
    
    @classmethod  
    def end_timer(cls, operation: str, start_time: float, 
                 context: Optional[Dict[str, Any]] = None) -> float:
        """End timing and log slow operations"""
        duration = time.time() - start_time
        duration_ms = duration * 1000
        
        # Log slow operations (>2 seconds)
        if duration > 2.0:
            logger.warning(
                f"Slow operation: {operation}",
                extra={
                    'operation': operation,
                    'duration': duration_ms,
                    'context': context or {}
                }
            )
        
        # Store metric for aggregation
        if operation not in cls._metrics:
            cls._metrics[operation] = []
        cls._metrics[operation].append(duration_ms)
        
        # Keep only last 100 measurements per operation
        if len(cls._metrics[operation]) > 100:
            cls._metrics[operation] = cls._metrics[operation][-100:]
            
        return duration
    
    @classmethod
    def get_metrics_summary(cls) -> Dict[str, Dict[str, float]]:
        """Get performance metrics summary"""
        summary = {}
        
        for operation, durations in cls._metrics.items():
            if durations:
                summary[operation] = {
                    'count': len(durations),
                    'avg': sum(durations) / len(durations),
                    'min': min(durations),
                    'max': max(durations),
                    'p95': sorted(durations)[int(len(durations) * 0.95)] if len(durations) >= 20 else max(durations)
                }
        
        return summary
    
    @classmethod
    @asynccontextmanager
    async def track_async_operation(cls, operation: str, context: Optional[Dict[str, Any]] = None):
        """Async context manager for tracking operations"""
        start_time = cls.start_timer(operation)
        try:
            yield
        finally:
            cls.end_timer(operation, start_time, context)


class HealthChecker:
    """System health monitoring"""
    
    @staticmethod
    async def check_database_health(db_session) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            # Simple query to test connectivity
            await db_session.execute("SELECT 1")
            duration = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": round(duration, 2)
            }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy", 
                "error": str(e)
            }
    
    @staticmethod
    async def check_memory_usage() -> Dict[str, Any]:
        """Check memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "status": "healthy",
                "memory_usage_mb": round(memory_info.rss / 1024 / 1024, 2),
                "memory_percent": round(process.memory_percent(), 2)
            }
        except ImportError:
            return {"status": "unavailable", "reason": "psutil not installed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get basic system information"""
        return {
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": time.time() - getattr(HealthChecker, '_start_time', time.time())
        }

# Track application start time
HealthChecker._start_time = time.time()


class ErrorTracker:
    """Error tracking and reporting"""
    
    @staticmethod
    def report_error(error: Exception, context: Optional[Dict[str, Any]] = None, 
                    request: Optional[Request] = None):
        """Report an error with context"""
        error_data = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {},
        }
        
        if request:
            error_data['request'] = {
                'method': request.method,
                'url': str(request.url),
                'headers': dict(request.headers),
                'client_ip': request.client.host if request.client else None
            }
        
        logger.error(
            f"Application error: {type(error).__name__}",
            extra=error_data,
            exc_info=True
        )
    
    @staticmethod
    def report_api_error(endpoint: str, method: str, status_code: int, 
                        duration: float, error: Optional[str] = None):
        """Report API-specific errors"""
        logger.error(
            f"API error: {method} {endpoint}",
            extra={
                'endpoint': endpoint,
                'method': method, 
                'status_code': status_code,
                'duration': duration,
                'error': error
            }
        )


# Middleware for request monitoring
async def monitoring_middleware(request: Request, call_next):
    """Middleware to monitor all requests"""
    start_time = time.time()
    request_id = f"req_{int(time.time() * 1000)}"
    
    # Add request ID to context
    request.state.request_id = request_id
    
    try:
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000
        
        # Log request
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                'method': request.method,
                'path': request.url.path,
                'status_code': response.status_code,
                'duration': round(duration, 2),
                'request_id': request_id,
                'client_ip': request.client.host if request.client else None
            }
        )
        
        # Track performance
        PerformanceMonitor.end_timer(
            f"{request.method} {request.url.path}",
            start_time,
            {'status_code': response.status_code}
        )
        
        # Add monitoring headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration:.2f}ms"
        
        return response
        
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        
        # Log error
        ErrorTracker.report_error(e, {
            'request_id': request_id,
            'duration': duration
        }, request)
        
        raise


# Utility functions for common monitoring tasks
def log_user_activity(user_id: str, action: str, resource: str, 
                     details: Optional[Dict[str, Any]] = None):
    """Log user activity for auditing"""
    logger.info(
        f"User activity: {action}",
        extra={
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'details': details or {}
        }
    )


def log_security_event(event_type: str, details: Dict[str, Any], 
                      severity: str = "info"):
    """Log security-related events"""
    log_level = getattr(logging, severity.upper(), logging.INFO)
    logger.log(
        log_level,
        f"Security event: {event_type}",
        extra={
            'event_type': event_type,
            'severity': severity,
            'details': details
        }
    )


# Background task for metrics collection
async def collect_metrics_task():
    """Background task to collect and report metrics periodically"""
    while True:
        try:
            # Collect metrics every 5 minutes
            await asyncio.sleep(300)
            
            metrics = PerformanceMonitor.get_metrics_summary()
            if metrics:
                logger.info("Performance metrics", extra={'metrics': metrics})
                
        except Exception as e:
            logger.error(f"Metrics collection failed: {str(e)}")


# Export main classes and functions
__all__ = [
    'PerformanceMonitor',
    'HealthChecker', 
    'ErrorTracker',
    'monitoring_middleware',
    'log_user_activity',
    'log_security_event',
    'collect_metrics_task',
    'logger'
]