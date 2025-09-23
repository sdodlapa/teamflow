"""
Rate limiting middleware for API protection.
Provides configurable rate limiting for different API endpoints and users.
"""
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
import hashlib

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm."""
    
    def __init__(
        self,
        app,
        redis_url: str = "redis://localhost:6379",
        default_rate_limit: int = 100,  # requests per minute
        rate_limit_window: int = 60,    # window in seconds
        exempt_paths: Optional[list] = None
    ):
        super().__init__(app)
        self.redis_client = None
        self.redis_url = redis_url
        self.default_rate_limit = default_rate_limit
        self.rate_limit_window = rate_limit_window
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/openapi.json"]
        
        # In-memory fallback for when Redis is not available
        self.memory_store: Dict[str, Dict[str, Any]] = {}
        
        # Rate limit configurations for different endpoints
        self.endpoint_limits = {
            "POST:/api/v1/auth/login": 5,      # 5 login attempts per minute
            "POST:/api/v1/auth/register": 3,   # 3 registration attempts per minute
            "POST:/api/v1/webhooks/events": 300,  # 300 webhook events per minute
            "GET:/api/v1/search": 50,          # 50 search requests per minute
            "POST:/api/v1/files/upload": 20,   # 20 file uploads per minute
        }
        
        # User-based rate limits (premium users get higher limits)
        self.user_tier_limits = {
            "free": 100,        # 100 requests per minute
            "starter": 200,     # 200 requests per minute
            "professional": 500, # 500 requests per minute
            "enterprise": 1000  # 1000 requests per minute
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        
        # Skip rate limiting for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # Initialize Redis connection if needed
        if self.redis_client is None:
            try:
                self.redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
                await self.redis_client.ping()
            except Exception:
                # Redis not available, will use memory store
                pass
        
        # Get client identifier
        client_id = await self._get_client_identifier(request)
        
        # Get rate limit for this request
        rate_limit = await self._get_rate_limit(request)
        
        # Check rate limit
        is_allowed, remaining, reset_time = await self._check_rate_limit(
            client_id, rate_limit, request
        )
        
        if not is_allowed:
            # Rate limit exceeded
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "limit": rate_limit,
                    "remaining": remaining,
                    "reset": reset_time,
                    "retry_after": self.rate_limit_window
                },
                headers={
                    "X-RateLimit-Limit": str(rate_limit),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(self.rate_limit_window)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
    
    async def _get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for the client."""
        
        # Try to get user ID from request (if authenticated)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Try to get API key from headers
        api_key = request.headers.get("X-API-Key")
        if api_key:
            # Hash the API key for privacy
            hashed_key = hashlib.sha256(api_key.encode()).hexdigest()[:16]
            return f"api_key:{hashed_key}"
        
        # Fall back to IP address
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    async def _get_rate_limit(self, request: Request) -> int:
        """Get rate limit for the current request."""
        
        # Check endpoint-specific limits
        endpoint_key = f"{request.method}:{request.url.path}"
        if endpoint_key in self.endpoint_limits:
            return self.endpoint_limits[endpoint_key]
        
        # Check user tier limits
        user_tier = getattr(request.state, "user_tier", "free")
        if user_tier in self.user_tier_limits:
            return self.user_tier_limits[user_tier]
        
        return self.default_rate_limit
    
    async def _check_rate_limit(
        self, 
        client_id: str, 
        rate_limit: int, 
        request: Request
    ) -> tuple[bool, int, int]:
        """Check if request is within rate limit."""
        
        current_time = int(time.time())
        window_start = current_time - self.rate_limit_window
        key = f"rate_limit:{client_id}:{current_time // self.rate_limit_window}"
        
        if self.redis_client:
            return await self._check_rate_limit_redis(key, rate_limit, current_time)
        else:
            return await self._check_rate_limit_memory(client_id, rate_limit, current_time)
    
    async def _check_rate_limit_redis(
        self, 
        key: str, 
        rate_limit: int, 
        current_time: int
    ) -> tuple[bool, int, int]:
        """Check rate limit using Redis."""
        
        try:
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Increment counter for current window
            pipe.incr(key)
            pipe.expire(key, self.rate_limit_window)
            
            results = await pipe.execute()
            current_count = results[0]
            
            remaining = max(0, rate_limit - current_count)
            reset_time = current_time + self.rate_limit_window
            is_allowed = current_count <= rate_limit
            
            return is_allowed, remaining, reset_time
            
        except Exception:
            # Redis error, fall back to allowing the request
            return True, rate_limit - 1, current_time + self.rate_limit_window
    
    async def _check_rate_limit_memory(
        self, 
        client_id: str, 
        rate_limit: int, 
        current_time: int
    ) -> tuple[bool, int, int]:
        """Check rate limit using in-memory store."""
        
        window_start = current_time - self.rate_limit_window
        
        # Clean up old entries
        if client_id in self.memory_store:
            self.memory_store[client_id]["requests"] = [
                req_time for req_time in self.memory_store[client_id]["requests"]
                if req_time > window_start
            ]
        else:
            self.memory_store[client_id] = {"requests": []}
        
        # Add current request
        self.memory_store[client_id]["requests"].append(current_time)
        
        current_count = len(self.memory_store[client_id]["requests"])
        remaining = max(0, rate_limit - current_count)
        reset_time = current_time + self.rate_limit_window
        is_allowed = current_count <= rate_limit
        
        return is_allowed, remaining, reset_time


class APIKeyRateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware specifically for API keys."""
    
    def __init__(self, app, redis_url: str = "redis://localhost:6379"):
        super().__init__(app)
        self.redis_client = None
        self.redis_url = redis_url
        
        # API key rate limits (these would typically be stored in database)
        self.api_key_limits = {
            # Format: api_key_hash -> (requests_per_minute, requests_per_hour, requests_per_day)
            "default": (100, 1000, 10000),  # Default limits
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with API key rate limiting."""
        
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            # No API key, skip this middleware
            return await call_next(request)
        
        # Hash API key for lookup
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Get rate limits for this API key
        limits = self.api_key_limits.get(api_key_hash, self.api_key_limits["default"])
        per_minute, per_hour, per_day = limits
        
        # Check all rate limits
        current_time = int(time.time())
        
        checks = [
            ("minute", per_minute, 60),
            ("hour", per_hour, 3600),
            ("day", per_day, 86400)
        ]
        
        for period, limit, window in checks:
            is_allowed, remaining, reset_time = await self._check_api_key_limit(
                api_key_hash, period, limit, window, current_time
            )
            
            if not is_allowed:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": f"API key rate limit exceeded for {period}",
                        "limit": limit,
                        "remaining": remaining,
                        "reset": reset_time,
                        "period": period
                    },
                    headers={
                        f"X-RateLimit-{period.title()}-Limit": str(limit),
                        f"X-RateLimit-{period.title()}-Remaining": str(remaining),
                        f"X-RateLimit-{period.title()}-Reset": str(reset_time)
                    }
                )
        
        return await call_next(request)
    
    async def _check_api_key_limit(
        self,
        api_key_hash: str,
        period: str,
        limit: int,
        window: int,
        current_time: int
    ) -> tuple[bool, int, int]:
        """Check API key rate limit for specific period."""
        
        # Initialize Redis if needed
        if self.redis_client is None:
            try:
                self.redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
                await self.redis_client.ping()
            except Exception:
                # Redis not available, allow request
                return True, limit - 1, current_time + window
        
        window_start = current_time // window
        key = f"api_key_rate_limit:{api_key_hash}:{period}:{window_start}"
        
        try:
            # Increment counter and set expiration
            current_count = await self.redis_client.incr(key)
            if current_count == 1:
                await self.redis_client.expire(key, window)
            
            remaining = max(0, limit - current_count)
            reset_time = (window_start + 1) * window
            is_allowed = current_count <= limit
            
            return is_allowed, remaining, reset_time
            
        except Exception:
            # Redis error, allow request
            return True, limit - 1, current_time + window


def create_rate_limit_exception_handler():
    """Create exception handler for rate limit errors."""
    
    async def rate_limit_exception_handler(request: Request, exc: HTTPException):
        """Handle rate limit exceptions with proper response format."""
        
        if exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "status_code": 429
                },
                headers=exc.headers or {}
            )
        
        # Re-raise other exceptions
        raise exc
    
    return rate_limit_exception_handler