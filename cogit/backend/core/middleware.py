"""
Custom middleware for VAULT_APP v2.0 FastAPI application
Provides authentication, rate limiting, request logging, and CORS handling
"""

import time
import uuid
import json
from typing import Callable, Dict, Any, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta

try:
    from fastapi import Request, Response
    from fastapi.middleware.base import BaseHTTPMiddleware
    from starlette.middleware.base import BaseHTTPMiddleware as StarletteBaseMiddleware
    from starlette.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    Request = None
    Response = None
    BaseHTTPMiddleware = object
    StarletteBaseMiddleware = object
    JSONResponse = None
    FASTAPI_AVAILABLE = True

from core.logging import get_logger
from core.config import get_settings
from core.exceptions import RateLimitError, AuthenticationError

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request/response logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Log request details
        await self._log_request(request, request_id)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            
            # Log response details
            await self._log_response(request, response, process_time, request_id)
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "process_time": process_time,
                    "error": str(e),
                    "event": "request_error"
                },
                exc_info=True
            )
            raise
    
    async def _log_request(self, request: Request, request_id: str):
        """Log incoming request details."""
        # Read request body for logging (if small)
        body_log = ""
        if request.headers.get("content-length"):
            content_length = int(request.headers.get("content-length", 0))
            if content_length < 1024:  # Only log small bodies
                try:
                    body = await request.body()
                    if body:
                        body_log = body.decode('utf-8')[:500]  # Truncate large bodies
                except Exception:
                    body_log = "[Failed to read body]"
        
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "content_type": request.headers.get("content-type"),
                "content_length": request.headers.get("content-length"),
                "body_preview": body_log,
                "event": "request_start"
            }
        )
    
    async def _log_response(self, request: Request, response: Response, 
                           process_time: float, request_id: str):
        """Log response details."""
        logger.info(
            f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": round(process_time, 3),
                "response_size": response.headers.get("content-length"),
                "event": "request_complete"
            }
        )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with configurable limits per endpoint."""
    
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Store request timestamps per IP
        self.request_times: Dict[str, deque] = defaultdict(deque)
        
        # Cleanup old entries periodically
        self.last_cleanup = datetime.utcnow()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = self._get_client_ip(request)
        
        # Check rate limits
        if await self._is_rate_limited(client_ip):
            logger.warning(
                f"Rate limit exceeded for IP: {client_ip}",
                extra={
                    "client_ip": client_ip,
                    "path": request.url.path,
                    "event": "rate_limit_exceeded"
                }
            )
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": 429,
                        "message": "Rate limit exceeded",
                        "details": {
                            "limit_per_minute": self.requests_per_minute,
                            "limit_per_hour": self.requests_per_hour
                        }
                    }
                }
            )
        
        # Record request
        await self._record_request(client_ip)
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP, considering proxies."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client IP is rate limited."""
        now = datetime.utcnow()
        request_times = self.request_times[client_ip]
        
        # Clean old entries
        one_hour_ago = now - timedelta(hours=1)
        one_minute_ago = now - timedelta(minutes=1)
        
        # Remove entries older than 1 hour
        while request_times and request_times[0] < one_hour_ago:
            request_times.popleft()
        
        # Count requests in last minute and hour
        minute_requests = sum(1 for t in request_times if t > one_minute_ago)
        hour_requests = len(request_times)
        
        return (minute_requests >= self.requests_per_minute or 
                hour_requests >= self.requests_per_hour)
    
    async def _record_request(self, client_ip: str):
        """Record request timestamp."""
        self.request_times[client_ip].append(datetime.utcnow())
        
        # Periodic cleanup of old IPs
        now = datetime.utcnow()
        if now - self.last_cleanup > timedelta(hours=2):
            await self._cleanup_old_entries()
            self.last_cleanup = now
    
    async def _cleanup_old_entries(self):
        """Clean up old entries to prevent memory leaks."""
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        
        # Remove IPs with no recent requests
        empty_ips = []
        for ip, times in self.request_times.items():
            # Remove old timestamps
            while times and times[0] < one_hour_ago:
                times.popleft()
            
            # Mark empty IPs for removal
            if not times:
                empty_ips.append(ip)
        
        # Remove empty IPs
        for ip in empty_ips:
            del self.request_times[ip]


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Basic authentication middleware for future JWT token handling."""
    
    def __init__(self, app, excluded_paths: Optional[list] = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/health",
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/api/v1/health"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip authentication for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        # For now, just pass through - JWT auth will be implemented later
        # Extract and validate Authorization header when implemented
        auth_header = request.headers.get("Authorization")
        if auth_header:
            request.state.auth_token = auth_header
        
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY" 
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response


# Middleware factory functions

def create_request_logging_middleware():
    """Create request logging middleware instance."""
    return RequestLoggingMiddleware


def create_rate_limit_middleware(requests_per_minute: int = 60, requests_per_hour: int = 1000):
    """Create rate limiting middleware with custom limits."""
    def middleware_factory(app):
        return RateLimitMiddleware(app, requests_per_minute, requests_per_hour)
    return middleware_factory


def create_auth_middleware(excluded_paths: Optional[list] = None):
    """Create authentication middleware with custom excluded paths."""
    def middleware_factory(app):
        return AuthenticationMiddleware(app, excluded_paths)
    return middleware_factory


def create_security_headers_middleware():
    """Create security headers middleware instance."""
    return SecurityHeadersMiddleware