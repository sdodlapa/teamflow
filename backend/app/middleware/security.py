"""
Security middleware for TeamFlow - Comprehensive security headers and protection.
Provides CSRF protection, rate limiting, security headers, and threat detection.
"""
import time
import hashlib
import hmac
import ipaddress
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Callable, Tuple
import asyncio
import json
from collections import defaultdict, deque

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.security import SecurityAlert, LoginAttempt, AuditLog
from app.models.user import User
from app.services.security_service import SecurityService


class SecurityHeaders:
    """Comprehensive security headers for all responses."""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get comprehensive security headers."""
        return {
            # Content Security Policy
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https: blob:; "
                "connect-src 'self' ws: wss:; "
                "media-src 'self'; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "
                "upgrade-insecure-requests"
            ),
            
            # Strict Transport Security (HSTS)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # X-Frame-Options (clickjacking protection)
            "X-Frame-Options": "DENY",
            
            # X-Content-Type-Options (MIME sniffing protection)
            "X-Content-Type-Options": "nosniff",
            
            # X-XSS-Protection
            "X-XSS-Protection": "1; mode=block",
            
            # Referrer Policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Permissions Policy
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "accelerometer=(), "
                "gyroscope=(), "
                "magnetometer=()"
            ),
            
            # Cross-Origin policies
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin",
            
            # Cache Control for sensitive data
            "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            
            # Remove server information
            "Server": "TeamFlow"
        }


class RateLimiter:
    """Advanced rate limiting with sliding window and burst protection."""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(lambda: deque())
        self.blocked_ips: Dict[str, datetime] = {}
        self.suspicious_ips: Dict[str, int] = defaultdict(int)
        
        # Rate limits (requests per minute)
        self.limits = {
            "default": 100,
            "auth": 10,     # Authentication endpoints
            "api": 1000,    # API endpoints with API key
            "upload": 20,   # File upload endpoints
            "search": 50    # Search endpoints
        }
        
        # Burst limits (requests per second)
        self.burst_limits = {
            "default": 10,
            "auth": 2,
            "api": 50,
            "upload": 5,
            "search": 5
        }
    
    def _clean_old_requests(self, requests: deque, window_seconds: int = 60):
        """Remove old requests outside the time window."""
        now = time.time()
        while requests and requests[0] < now - window_seconds:
            requests.popleft()
    
    def _get_client_key(self, request: Request) -> str:
        """Get unique client identifier for rate limiting."""
        # Try to get user ID from token if available
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        client_ip = self._get_client_ip(request)
        return f"ip:{client_ip}"
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP with proxy support."""
        # Check for forwarded headers (reverse proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _get_endpoint_category(self, path: str) -> str:
        """Categorize endpoint for appropriate rate limiting."""
        if "/auth/" in path or "/login" in path or "/register" in path:
            return "auth"
        elif path.startswith("/api/v1/") and "api-key" in path:
            return "api"
        elif "/upload" in path or "/files/" in path:
            return "upload"
        elif "/search" in path:
            return "search"
        else:
            return "default"
    
    def is_blocked(self, request: Request) -> bool:
        """Check if IP is currently blocked."""
        client_ip = self._get_client_ip(request)
        
        if client_ip in self.blocked_ips:
            block_time = self.blocked_ips[client_ip]
            if datetime.utcnow() < block_time:
                return True
            else:
                # Remove expired block
                del self.blocked_ips[client_ip]
        
        return False
    
    def check_rate_limit(self, request: Request) -> Tuple[bool, Dict[str, Any]]:
        """Check if request should be rate limited."""
        if self.is_blocked(request):
            return False, {
                "error": "IP temporarily blocked",
                "retry_after": 300  # 5 minutes
            }
        
        client_key = self._get_client_key(request)
        client_ip = self._get_client_ip(request)
        now = time.time()
        
        # Get request history for this client
        client_requests = self.requests[client_key]
        self._clean_old_requests(client_requests)
        
        # Determine rate limits for this endpoint
        endpoint_category = self._get_endpoint_category(request.url.path)
        minute_limit = self.limits[endpoint_category]
        burst_limit = self.burst_limits[endpoint_category]
        
        # Check burst limit (requests in last second)
        recent_requests = [req for req in client_requests if req > now - 1]
        if len(recent_requests) >= burst_limit:
            self.suspicious_ips[client_ip] += 1
            return False, {
                "error": "Rate limit exceeded - too many requests per second",
                "limit": burst_limit,
                "window": "1 second",
                "retry_after": 1
            }
        
        # Check minute limit
        if len(client_requests) >= minute_limit:
            self.suspicious_ips[client_ip] += 1
            
            # Block IP if too many violations
            if self.suspicious_ips[client_ip] >= 5:
                self.blocked_ips[client_ip] = datetime.utcnow() + timedelta(minutes=5)
                return False, {
                    "error": "IP blocked due to repeated violations",
                    "retry_after": 300
                }
            
            return False, {
                "error": "Rate limit exceeded",
                "limit": minute_limit,
                "window": "1 minute",
                "retry_after": 60
            }
        
        # Record this request
        client_requests.append(now)
        
        return True, {
            "remaining": minute_limit - len(client_requests),
            "limit": minute_limit,
            "window": "1 minute"
        }


class ThreatDetector:
    """Advanced threat detection and suspicious activity monitoring."""
    
    def __init__(self):
        self.suspicious_patterns = {
            # SQL injection patterns
            "sql_injection": [
                r"(\bUNION\b.*\bSELECT\b)", r"(\bSELECT\b.*\bFROM\b.*\bWHERE\b)",
                r"(\bINSERT\b.*\bINTO\b)", r"(\bUPDATE\b.*\bSET\b)",
                r"(\bDELETE\b.*\bFROM\b)", r"(\bDROP\b.*\bTABLE\b)",
                r"(\';.*--)", r"(\bOR\b.*=.*)"
            ],
            
            # XSS patterns
            "xss": [
                r"<script[^>]*>.*?</script>", r"javascript:",
                r"on\w+\s*=", r"<iframe[^>]*>",
                r"<object[^>]*>", r"<embed[^>]*>"
            ],
            
            # Path traversal
            "path_traversal": [
                r"\.\.\/", r"\.\.\\", r"\/etc\/passwd",
                r"\/windows\/system32", r"\.\.\%2f"
            ],
            
            # Command injection
            "command_injection": [
                r";\s*rm\s+", r";\s*cat\s+", r";\s*ls\s+",
                r"&&\s*", r"\|\|\s*", r"`.*`"
            ]
        }
        
        self.failed_attempts: Dict[str, List[datetime]] = defaultdict(list)
    
    def detect_threats(self, request: Request) -> List[Dict[str, Any]]:
        """Detect potential security threats in request."""
        threats = []
        
        # Check URL for suspicious patterns
        url_threats = self._check_url_threats(request.url.path)
        threats.extend(url_threats)
        
        # Check query parameters
        if request.url.query:
            query_threats = self._check_query_threats(request.url.query)
            threats.extend(query_threats)
        
        # Check headers for suspicious patterns
        header_threats = self._check_header_threats(request.headers)
        threats.extend(header_threats)
        
        return threats
    
    def _check_url_threats(self, url_path: str) -> List[Dict[str, Any]]:
        """Check URL path for threats."""
        threats = []
        
        for threat_type, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                if self._pattern_matches(pattern, url_path):
                    threats.append({
                        "type": threat_type,
                        "location": "url_path",
                        "pattern": pattern,
                        "value": url_path[:100],  # Truncate for logging
                        "severity": "high"
                    })
        
        return threats
    
    def _check_query_threats(self, query_string: str) -> List[Dict[str, Any]]:
        """Check query string for threats."""
        threats = []
        
        for threat_type, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                if self._pattern_matches(pattern, query_string):
                    threats.append({
                        "type": threat_type,
                        "location": "query_string",
                        "pattern": pattern,
                        "value": query_string[:100],
                        "severity": "medium"
                    })
        
        return threats
    
    def _check_header_threats(self, headers) -> List[Dict[str, Any]]:
        """Check request headers for threats."""
        threats = []
        
        suspicious_headers = [
            "User-Agent", "Referer", "X-Forwarded-For",
            "X-Originating-IP", "X-Remote-IP"
        ]
        
        for header_name in suspicious_headers:
            header_value = headers.get(header_name, "")
            if header_value:
                for threat_type, patterns in self.suspicious_patterns.items():
                    for pattern in patterns:
                        if self._pattern_matches(pattern, header_value):
                            threats.append({
                                "type": threat_type,
                                "location": f"header_{header_name.lower()}",
                                "pattern": pattern,
                                "value": header_value[:100],
                                "severity": "medium"
                            })
        
        return threats
    
    def _pattern_matches(self, pattern: str, text: str) -> bool:
        """Check if pattern matches text (case-insensitive)."""
        import re
        try:
            return bool(re.search(pattern, text, re.IGNORECASE))
        except re.error:
            return pattern.lower() in text.lower()
    
    def record_failed_attempt(self, client_ip: str, attempt_type: str):
        """Record a failed attempt for monitoring."""
        now = datetime.utcnow()
        self.failed_attempts[f"{client_ip}:{attempt_type}"].append(now)
        
        # Clean old attempts (older than 1 hour)
        cutoff = now - timedelta(hours=1)
        self.failed_attempts[f"{client_ip}:{attempt_type}"] = [
            attempt for attempt in self.failed_attempts[f"{client_ip}:{attempt_type}"]
            if attempt > cutoff
        ]
    
    def is_suspicious_activity(self, client_ip: str, attempt_type: str) -> bool:
        """Check if there's suspicious activity from this IP."""
        attempts = self.failed_attempts.get(f"{client_ip}:{attempt_type}", [])
        
        # More than 10 failed attempts in 1 hour is suspicious
        if len(attempts) > 10:
            return True
        
        # More than 5 attempts in 10 minutes is suspicious
        recent_cutoff = datetime.utcnow() - timedelta(minutes=10)
        recent_attempts = [a for a in attempts if a > recent_cutoff]
        
        return len(recent_attempts) > 5


class CSRFProtection:
    """CSRF token generation and validation."""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
    
    def generate_token(self, session_id: str, timestamp: Optional[str] = None) -> str:
        """Generate CSRF token for session."""
        if timestamp is None:
            timestamp = str(int(time.time()))
        
        message = f"{session_id}:{timestamp}"
        signature = hmac.new(
            self.secret_key,
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}:{signature}"
    
    def validate_token(self, token: str, session_id: str, max_age: int = 3600) -> bool:
        """Validate CSRF token."""
        try:
            timestamp_str, signature = token.split(":", 1)
            timestamp = int(timestamp_str)
            
            # Check if token is not expired
            if time.time() - timestamp > max_age:
                return False
            
            # Generate expected signature
            expected_token = self.generate_token(session_id, timestamp_str)
            expected_signature = expected_token.split(":", 1)[1]
            
            # Compare signatures securely
            return hmac.compare_digest(signature, expected_signature)
        
        except (ValueError, IndexError):
            return False


# Global instances
rate_limiter = RateLimiter()
threat_detector = ThreatDetector()
csrf_protection = CSRFProtection("your-secret-key-here")  # Should be from config


async def security_middleware(request: Request, call_next: Callable) -> Response:
    """Comprehensive security middleware."""
    
    # Skip security checks for health checks and static files
    if request.url.path in ["/health", "/docs", "/openapi.json"] or \
       request.url.path.startswith("/static/"):
        response = await call_next(request)
        return response
    
    # 1. Rate limiting
    allowed, rate_info = rate_limiter.check_rate_limit(request)
    if not allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "details": rate_info
            },
            headers={"Retry-After": str(rate_info.get("retry_after", 60))}
        )
    
    # 2. Threat detection
    threats = threat_detector.detect_threats(request)
    if threats:
        # Log the threat
        client_ip = rate_limiter._get_client_ip(request)
        
        # Block high-severity threats
        high_severity_threats = [t for t in threats if t.get("severity") == "high"]
        if high_severity_threats:
            # Record security alert (would need database context)
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "Security threat detected",
                    "request_id": getattr(request.state, "request_id", "unknown")
                }
            )
        
        # Log medium severity threats but allow request
        request.state.security_threats = threats
    
    # 3. IP validation (basic)
    client_ip = rate_limiter._get_client_ip(request)
    if client_ip and client_ip != "unknown":
        try:
            # Validate IP format
            ipaddress.ip_address(client_ip)
            
            # Check against known bad IP ranges (would be configurable)
            # For now, block obviously invalid IPs
            if client_ip.startswith("0.") or client_ip == "127.0.0.1":
                pass  # Allow localhost for development
            
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Invalid client IP"}
            )
    
    # 4. Process request
    try:
        response = await call_next(request)
    except Exception as e:
        # Log security-related exceptions
        if hasattr(request.state, "security_threats"):
            # This was a request with detected threats that caused an error
            pass
        raise
    
    # 5. Add security headers to response
    security_headers = SecurityHeaders.get_security_headers()
    for header_name, header_value in security_headers.items():
        response.headers[header_name] = header_value
    
    # 6. Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(rate_info.get("limit", 100))
    response.headers["X-RateLimit-Remaining"] = str(rate_info.get("remaining", 0))
    response.headers["X-RateLimit-Window"] = rate_info.get("window", "1 minute")
    
    # 7. Add security context headers
    if hasattr(request.state, "security_threats"):
        response.headers["X-Security-Threats-Detected"] = str(len(request.state.security_threats))
    
    return response


async def audit_middleware(request: Request, call_next: Callable) -> Response:
    """Audit logging middleware for security compliance."""
    
    # Skip audit for certain endpoints
    if request.url.path in ["/health", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    start_time = time.time()
    client_ip = rate_limiter._get_client_ip(request)
    
    # Extract user context if available
    user_id = getattr(request.state, "user_id", None)
    organization_id = getattr(request.state, "organization_id", None)
    
    # Process request
    response = await call_next(request)
    
    # Calculate response time
    response_time = time.time() - start_time
    
    # Determine if this should be audited
    should_audit = (
        request.method in ["POST", "PUT", "PATCH", "DELETE"] or  # Modifying operations
        "auth" in request.url.path or  # Authentication operations
        hasattr(request.state, "security_threats") or  # Security threats detected
        response.status_code >= 400  # Error responses
    )
    
    if should_audit:
        # Create audit log (would need database context)
        audit_data = {
            "action_type": f"{request.method}_{request.url.path.replace('/', '_').strip('_')}",
            "resource_type": "api_endpoint",
            "resource_id": request.url.path,
            "description": f"{request.method} {request.url.path}",
            "ip_address": client_ip,
            "user_agent": request.headers.get("User-Agent"),
            "request_method": request.method,
            "request_path": request.url.path,
            "response_status": response.status_code,
            "response_time": response_time,
            "user_id": user_id,
            "organization_id": organization_id,
            "extra_data": {
                "query_params": dict(request.query_params),
                "response_time_ms": round(response_time * 1000, 2),
                "threats_detected": getattr(request.state, "security_threats", [])
            }
        }
        
        # Store audit data in request state for later processing
        request.state.audit_data = audit_data
    
    return response


class IPWhitelist:
    """IP whitelist/blacklist management."""
    
    def __init__(self):
        self.whitelist: Set[str] = set()
        self.blacklist: Set[str] = set()
        self.whitelist_networks: List[ipaddress.IPv4Network] = []
        self.blacklist_networks: List[ipaddress.IPv4Network] = []
    
    def add_to_whitelist(self, ip_or_network: str):
        """Add IP or network to whitelist."""
        try:
            if "/" in ip_or_network:
                network = ipaddress.ip_network(ip_or_network)
                self.whitelist_networks.append(network)
            else:
                self.whitelist.add(ip_or_network)
        except ValueError:
            raise ValueError(f"Invalid IP or network: {ip_or_network}")
    
    def add_to_blacklist(self, ip_or_network: str):
        """Add IP or network to blacklist."""
        try:
            if "/" in ip_or_network:
                network = ipaddress.ip_network(ip_or_network)
                self.blacklist_networks.append(network)
            else:
                self.blacklist.add(ip_or_network)
        except ValueError:
            raise ValueError(f"Invalid IP or network: {ip_or_network}")
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if IP is allowed."""
        try:
            ip = ipaddress.ip_address(client_ip)
            
            # Check blacklist first
            if client_ip in self.blacklist:
                return False
            
            for network in self.blacklist_networks:
                if ip in network:
                    return False
            
            # If whitelist is empty, allow by default
            if not self.whitelist and not self.whitelist_networks:
                return True
            
            # Check whitelist
            if client_ip in self.whitelist:
                return True
            
            for network in self.whitelist_networks:
                if ip in network:
                    return True
            
            return False
        
        except ValueError:
            # Invalid IP format
            return False


# Global IP whitelist instance
ip_whitelist = IPWhitelist()


def configure_security_middleware(app):
    """Configure security middleware for the application."""
    app.middleware("http")(security_middleware)
    app.middleware("http")(audit_middleware)