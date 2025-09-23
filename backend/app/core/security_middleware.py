"""Security middleware for headers, CORS, and advanced security features."""

import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.status import HTTP_429_TOO_MANY_REQUESTS, HTTP_403_FORBIDDEN
from fastapi import HTTPException
import uuid
import json

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    def __init__(self, app, csp_policy: Optional[str] = None):
        super().__init__(app)
        self.csp_policy = csp_policy or self._default_csp_policy()
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = self.csp_policy
        
        # HSTS (only over HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Cache control for sensitive endpoints
        if self._is_sensitive_endpoint(request.url.path):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response
    
    def _default_csp_policy(self) -> str:
        """Default Content Security Policy."""
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
    
    def _is_sensitive_endpoint(self, path: str) -> bool:
        """Check if endpoint is sensitive and should not be cached."""
        sensitive_patterns = [
            "/api/v1/auth/",
            "/api/v1/users/me",
            "/api/v1/admin/",
            "/api/v1/security/",
            "/api/v1/webhooks/"
        ]
        return any(pattern in path for pattern in sensitive_patterns)


class AdvancedCORSMiddleware(BaseHTTPMiddleware):
    """Advanced CORS middleware with detailed configuration."""
    
    def __init__(
        self,
        app,
        allowed_origins: List[str] = None,
        allowed_methods: List[str] = None,
        allowed_headers: List[str] = None,
        exposed_headers: List[str] = None,
        allow_credentials: bool = True,
        max_age: int = 86400,
        allow_origin_regex: Optional[str] = None
    ):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allowed_headers = allowed_headers or ["*"]
        self.exposed_headers = exposed_headers or []
        self.allow_credentials = allow_credentials
        self.max_age = max_age
        self.allow_origin_regex = allow_origin_regex
    
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        
        if request.method == "OPTIONS":
            # Preflight request
            response = Response()
            if self._is_origin_allowed(origin):
                response.headers["Access-Control-Allow-Origin"] = origin or "*"
                response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
                response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)
                response.headers["Access-Control-Max-Age"] = str(self.max_age)
                
                if self.allow_credentials and origin:
                    response.headers["Access-Control-Allow-Credentials"] = "true"
            
            return response
        
        response = await call_next(request)
        
        if self._is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
            
            if self.exposed_headers:
                response.headers["Access-Control-Expose-Headers"] = ", ".join(self.exposed_headers)
            
            if self.allow_credentials and origin:
                response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response
    
    def _is_origin_allowed(self, origin: Optional[str]) -> bool:
        """Check if origin is allowed."""
        if not origin:
            return True
        
        if "*" in self.allowed_origins:
            return True
        
        if origin in self.allowed_origins:
            return True
        
        if self.allow_origin_regex:
            import re
            return bool(re.match(self.allow_origin_regex, origin))
        
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Advanced rate limiting middleware."""
    
    def __init__(
        self,
        app,
        default_rate_limit: str = "100/hour",
        rate_limit_storage: Optional[Dict] = None,
        rate_limit_rules: Optional[Dict[str, str]] = None,
        exempt_paths: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.default_rate_limit = default_rate_limit
        self.storage = rate_limit_storage or {}
        self.rate_limit_rules = rate_limit_rules or {}
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/redoc"]
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Get rate limit for this endpoint
        rate_limit = self._get_rate_limit_for_path(request.url.path)
        
        # Check rate limit
        if self._is_rate_limited(client_id, rate_limit):
            return JSONResponse(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": self._get_retry_after(client_id, rate_limit)
                },
                headers={
                    "Retry-After": str(self._get_retry_after(client_id, rate_limit)),
                    "X-RateLimit-Limit": str(self._parse_rate_limit(rate_limit)[0]),
                    "X-RateLimit-Remaining": str(self._get_remaining_requests(client_id, rate_limit))
                }
            )
        
        # Record request
        self._record_request(client_id, rate_limit)
        
        response = await call_next(request)
        
        # Add rate limit headers
        limit, window = self._parse_rate_limit(rate_limit)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(self._get_remaining_requests(client_id, rate_limit))
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier."""
        # Try to get user ID from JWT token
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.id}"
        
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        
        return f"ip:{request.client.host}"
    
    def _get_rate_limit_for_path(self, path: str) -> str:
        """Get rate limit rule for specific path."""
        for pattern, limit in self.rate_limit_rules.items():
            if pattern in path:
                return limit
        return self.default_rate_limit
    
    def _parse_rate_limit(self, rate_limit: str) -> tuple[int, int]:
        """Parse rate limit string (e.g., '100/hour') into (limit, window_seconds)."""
        limit_str, period = rate_limit.split("/")
        limit = int(limit_str)
        
        period_map = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400
        }
        
        window = period_map.get(period, 3600)
        return limit, window
    
    def _is_rate_limited(self, client_id: str, rate_limit: str) -> bool:
        """Check if client is rate limited."""
        limit, window = self._parse_rate_limit(rate_limit)
        now = time.time()
        window_start = now - window
        
        # Get requests in current window
        if client_id not in self.storage:
            self.storage[client_id] = []
        
        # Clean old requests
        self.storage[client_id] = [
            req_time for req_time in self.storage[client_id]
            if req_time > window_start
        ]
        
        return len(self.storage[client_id]) >= limit
    
    def _record_request(self, client_id: str, rate_limit: str):
        """Record a request for rate limiting."""
        if client_id not in self.storage:
            self.storage[client_id] = []
        
        self.storage[client_id].append(time.time())
    
    def _get_remaining_requests(self, client_id: str, rate_limit: str) -> int:
        """Get remaining requests in current window."""
        limit, _ = self._parse_rate_limit(rate_limit)
        current_count = len(self.storage.get(client_id, []))
        return max(0, limit - current_count)
    
    def _get_retry_after(self, client_id: str, rate_limit: str) -> int:
        """Get retry after seconds."""
        _, window = self._parse_rate_limit(rate_limit)
        if client_id not in self.storage or not self.storage[client_id]:
            return 0
        
        oldest_request = min(self.storage[client_id])
        return max(0, int(window - (time.time() - oldest_request)))


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """Middleware to restrict access by IP address."""
    
    def __init__(
        self,
        app,
        allowed_ips: List[str] = None,
        whitelist_paths: List[str] = None,
        block_private_ips: bool = False
    ):
        super().__init__(app)
        self.allowed_ips = allowed_ips or []
        self.whitelist_paths = whitelist_paths or []
        self.block_private_ips = block_private_ips
    
    async def dispatch(self, request: Request, call_next):
        # Skip for non-restricted paths
        if not self.whitelist_paths or not any(
            request.url.path.startswith(path) for path in self.whitelist_paths
        ):
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        
        # Check if IP is allowed
        if not self._is_ip_allowed(client_ip):
            return JSONResponse(
                status_code=HTTP_403_FORBIDDEN,
                content={"detail": "Access forbidden from this IP address"}
            )
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host
    
    def _is_ip_allowed(self, ip: str) -> bool:
        """Check if IP address is allowed."""
        import ipaddress
        
        try:
            client_ip = ipaddress.ip_address(ip)
            
            # Check private IP restriction
            if self.block_private_ips and client_ip.is_private:
                return False
            
            # Check whitelist
            if not self.allowed_ips:
                return True
            
            for allowed in self.allowed_ips:
                if "/" in allowed:
                    # CIDR notation
                    if client_ip in ipaddress.ip_network(allowed, strict=False):
                        return True
                else:
                    # Single IP
                    if client_ip == ipaddress.ip_address(allowed):
                        return True
            
            return False
            
        except ValueError:
            # Invalid IP format
            return False


class SecurityAuditMiddleware(BaseHTTPMiddleware):
    """Middleware to audit security-relevant requests."""
    
    def __init__(self, app, audit_paths: List[str] = None):
        super().__init__(app)
        self.audit_paths = audit_paths or [
            "/api/v1/auth/",
            "/api/v1/admin/",
            "/api/v1/security/",
            "/api/v1/users/",
            "/api/v1/organizations/"
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Check if request should be audited
        should_audit = any(
            request.url.path.startswith(path) for path in self.audit_paths
        )
        
        if should_audit:
            # Add audit context to request
            request.state.audit_context = {
                "request_id": str(uuid.uuid4()),
                "ip_address": self._get_client_ip(request),
                "user_agent": request.headers.get("User-Agent"),
                "method": request.method,
                "path": request.url.path,
                "timestamp": datetime.utcnow()
            }
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests with security context."""
    
    def __init__(self, app, log_sensitive_data: bool = False):
        super().__init__(app)
        self.log_sensitive_data = log_sensitive_data
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Prepare request context
        request_context = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "ip_address": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent"),
            "content_type": request.headers.get("Content-Type"),
            "content_length": request.headers.get("Content-Length"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add user context if available
        if hasattr(request.state, "user") and request.state.user:
            request_context["user_id"] = str(request.state.user.id)
            request_context["user_email"] = request.state.user.email
        
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        
        # Log response context
        response_context = {
            "status_code": response.status_code,
            "response_time": process_time,
            "content_length": response.headers.get("Content-Length")
        }
        
        # Store in request state for potential audit logging
        request.state.request_log = {
            "request": request_context,
            "response": response_context
        }
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host


# Security middleware configuration helper
def configure_security_middleware(app):
    """Configure all security middleware for the application."""
    
    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add advanced CORS
    app.add_middleware(
        AdvancedCORSMiddleware,
        allowed_origins=getattr(settings, "CORS_ORIGINS", ["*"]),
        allow_credentials=True,
        exposed_headers=["X-Total-Count", "X-RateLimit-Limit", "X-RateLimit-Remaining"]
    )
    
    # Add rate limiting
    rate_limit_rules = {
        "/api/v1/auth/login": "5/minute",
        "/api/v1/auth/register": "3/minute",
        "/api/v1/auth/": "20/minute",
        "/api/v1/admin/": "50/hour",
        "/api/v1/webhooks/": "1000/hour"
    }
    
    app.add_middleware(
        RateLimitMiddleware,
        default_rate_limit="1000/hour",
        rate_limit_rules=rate_limit_rules
    )
    
    # Add IP whitelist for admin endpoints
    app.add_middleware(
        IPWhitelistMiddleware,
        whitelist_paths=["/api/v1/admin/"],
        allowed_ips=getattr(settings, "ADMIN_ALLOWED_IPS", [])
    )
    
    # Add security audit logging
    app.add_middleware(SecurityAuditMiddleware)
    
    # Add request logging
    app.add_middleware(RequestLoggingMiddleware)
    
    return app