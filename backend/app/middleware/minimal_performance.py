"""
Minimal performance middleware - FAST & LIGHTWEIGHT
Removes all heavy performance tracking that causes hanging
"""
import time
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware


class BasicAPIMiddleware(BaseHTTPMiddleware):
    """Lightweight API middleware with minimal overhead"""
    
    def __init__(self, app, max_request_size: int = 10 * 1024 * 1024):  # 10MB
        super().__init__(app)
        self.max_request_size = max_request_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Quick request size check only
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > self.max_request_size:
            return JSONResponse(
                status_code=413,
                content={"error": "Request too large"}
            )
        
        # Basic timing without heavy metrics
        start_time = time.time()
        response = await call_next(request)
        
        # Minimal headers only
        processing_time = (time.time() - start_time) * 1000
        response.headers["X-Process-Time"] = f"{processing_time:.2f}ms"
        
        return response


class MinimalPerformanceConfig:
    """Minimal middleware configuration - NO HANGING"""
    
    @staticmethod
    def get_middleware_stack() -> list:
        """Get ultra-minimal middleware stack"""
        return [
            # Only essential middleware
            (GZipMiddleware, {"minimum_size": 1000}),
            (BasicAPIMiddleware, {"max_request_size": 10 * 1024 * 1024}),
        ]
    
    @staticmethod
    def configure_app_middleware(app):
        """Configure FastAPI app with minimal middleware"""
        middleware_stack = MinimalPerformanceConfig.get_middleware_stack()
        
        for middleware_class, kwargs in reversed(middleware_stack):
            app.add_middleware(middleware_class, **kwargs)
        
        print("✅ Minimal performance middleware configured (no hanging)")
        return app