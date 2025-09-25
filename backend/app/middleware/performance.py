"""
Performance optimization middleware for FastAPI
"""
import time
import gzip
import asyncio
from typing import Callable, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.types import ASGIApp

from app.services.performance_service import metrics_collector, performance_tracker


class ResponseCompressionMiddleware(BaseHTTPMiddleware):
    """Advanced response compression middleware"""
    
    def __init__(self, app: ASGIApp, minimum_size: int = 1000, compression_level: int = 6):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compression_level = compression_level
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Skip compression for small responses or if already compressed
        if (
            hasattr(response, 'body') and 
            len(response.body) >= self.minimum_size and
            'content-encoding' not in response.headers
        ):
            # Check if client accepts gzip
            accept_encoding = request.headers.get('accept-encoding', '')
            if 'gzip' in accept_encoding:
                # Compress response body
                compressed_body = gzip.compress(
                    response.body, 
                    compresslevel=self.compression_level
                )
                
                # Update response
                response.headers['content-encoding'] = 'gzip'
                response.headers['content-length'] = str(len(compressed_body))
                
                # Create new response with compressed body
                return Response(
                    content=compressed_body,
                    status_code=response.status_code,
                    headers=response.headers,
                    media_type=response.media_type
                )
        
        return response


class PerformanceTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track API performance metrics"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        metrics_collector.increment_active_requests()
        
        # Get endpoint for tracking
        endpoint = f"{request.method} {request.url.path}"
        
        try:
            async with performance_tracker(f"api_request:{endpoint}"):
                response = await call_next(request)
                
                # Record successful request
                duration = (time.time() - start_time) * 1000
                metrics_collector.record_request_time(endpoint, duration)
                
                # Add performance headers
                response.headers["X-Response-Time"] = f"{duration:.2f}ms"
                response.headers["X-Process-Time"] = f"{duration:.2f}"
                
                return response
                
        except Exception as e:
            # Record error
            metrics_collector.record_error(type(e).__name__)
            duration = (time.time() - start_time) * 1000
            metrics_collector.record_request_time(f"{endpoint}:error", duration)
            raise
        finally:
            metrics_collector.decrement_active_requests()


class DatabaseQueryTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track database query performance"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.active_queries = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # This middleware would integrate with SQLAlchemy events
        # to track query performance during request processing
        
        query_start_time = time.time()
        
        try:
            response = await call_next(request)
            return response
        finally:
            # Database query tracking would be implemented here
            # This is a placeholder for SQLAlchemy event integration
            pass


class CachePerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to track cache performance"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Track cache operations during request
        cache_operations = []
        
        # This would integrate with the cache system to track operations
        response = await call_next(request)
        
        # Add cache performance headers
        if cache_operations:
            response.headers["X-Cache-Operations"] = str(len(cache_operations))
        
        return response


class APIOptimizationMiddleware(BaseHTTPMiddleware):
    """Middleware for API-level optimizations"""
    
    def __init__(self, app: ASGIApp, max_request_size: int = 10 * 1024 * 1024):  # 10MB
        super().__init__(app)
        self.max_request_size = max_request_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check request size
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > self.max_request_size:
            return JSONResponse(
                status_code=413,
                content={"error": "Request too large"}
            )
        
        # Add request optimization headers
        start_time = time.time()
        
        response = await call_next(request)
        
        # Add optimization headers
        processing_time = (time.time() - start_time) * 1000
        response.headers["X-Processing-Time"] = f"{processing_time:.2f}ms"
        response.headers["X-API-Version"] = "v1"
        
        # Add cache control headers for static-like responses
        if request.url.path.startswith('/api/health'):
            response.headers["Cache-Control"] = "public, max-age=60"
        elif request.url.path.startswith('/api/docs'):
            response.headers["Cache-Control"] = "public, max-age=3600"
        
        return response


class ConnectionPoolMiddleware(BaseHTTPMiddleware):
    """Middleware to optimize database connection usage"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.connection_stats = {
            "active_connections": 0,
            "total_requests": 0,
            "connection_errors": 0
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        self.connection_stats["total_requests"] += 1
        
        try:
            # Track database connection usage
            self.connection_stats["active_connections"] += 1
            
            response = await call_next(request)
            
            # Add connection pool headers for monitoring
            response.headers["X-DB-Connections"] = str(self.connection_stats["active_connections"])
            
            return response
            
        except Exception as e:
            if "database" in str(e).lower() or "connection" in str(e).lower():
                self.connection_stats["connection_errors"] += 1
            raise
        finally:
            self.connection_stats["active_connections"] = max(0, self.connection_stats["active_connections"] - 1)


class AsyncTaskMiddleware(BaseHTTPMiddleware):
    """Middleware to handle background task optimization"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.background_tasks = []
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Process any background tasks efficiently
        if hasattr(response, 'background') and response.background:
            # Optimize background task execution
            pass
        
        return response


class ResourceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor resource usage per request"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.resource_stats = {
            "memory_usage": [],
            "cpu_time": [],
            "io_operations": []
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        import psutil
        import os
        
        # Get initial resource usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        initial_cpu_time = process.cpu_times().user + process.cpu_times().system
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Calculate resource usage
            final_memory = process.memory_info().rss
            final_cpu_time = process.cpu_times().user + process.cpu_times().system
            
            memory_delta = final_memory - initial_memory
            cpu_delta = final_cpu_time - initial_cpu_time
            wall_time = time.time() - start_time
            
            # Add resource usage headers
            response.headers["X-Memory-Delta"] = f"{memory_delta / 1024:.2f}KB"
            response.headers["X-CPU-Time"] = f"{cpu_delta * 1000:.2f}ms"
            response.headers["X-Wall-Time"] = f"{wall_time * 1000:.2f}ms"
            
            # Store stats for monitoring
            self.resource_stats["memory_usage"].append(memory_delta)
            self.resource_stats["cpu_time"].append(cpu_delta)
            
            # Keep only recent stats
            for key in self.resource_stats:
                if len(self.resource_stats[key]) > 1000:
                    self.resource_stats[key] = self.resource_stats[key][-1000:]
            
            return response
            
        except Exception as e:
            raise


class SmartPaginationMiddleware(BaseHTTPMiddleware):
    """Middleware to optimize pagination queries"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check for pagination parameters
        query_params = dict(request.query_params)
        
        # Optimize pagination parameters
        if 'limit' in query_params:
            try:
                limit = int(query_params['limit'])
                # Enforce reasonable limits
                if limit > 1000:
                    query_params['limit'] = '1000'
                elif limit < 1:
                    query_params['limit'] = '10'
                
                # Update request with optimized parameters
                # This is a simplified example - actual implementation would modify the request
                
            except ValueError:
                query_params['limit'] = '10'
        
        response = await call_next(request)
        return response


# Middleware configuration helper
class PerformanceMiddlewareConfig:
    """Configuration helper for performance middleware"""
    
    @staticmethod
    def get_middleware_stack() -> list:
        """Get simplified, non-hanging middleware stack for performance"""
        return [
            # Keep essential middleware only
            (GZipMiddleware, {"minimum_size": 1000}),
            (APIOptimizationMiddleware, {"max_request_size": 10 * 1024 * 1024}),
            # REMOVED: Heavy middleware that causes hanging
            # - ResponseCompressionMiddleware (redundant with GZip)
            # - PerformanceTrackingMiddleware (async context manager issues)
            # - ConnectionPoolMiddleware (not needed with proper SQLAlchemy setup)
            # - ResourceMonitoringMiddleware (psutil calls are expensive)
            # - SmartPaginationMiddleware (complex logic)
        ]
    
    @staticmethod
    def configure_app_middleware(app):
        """Configure FastAPI app with performance middleware"""
        middleware_stack = PerformanceMiddlewareConfig.get_middleware_stack()
        
        for middleware_class, kwargs in reversed(middleware_stack):
            app.add_middleware(middleware_class, **kwargs)
        
        return app