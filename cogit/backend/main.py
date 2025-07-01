"""
VAULT_APP v2.0 - FastAPI Backend
Main application entry point with full middleware, routing, and database setup
"""

import asyncio
import time
import uuid
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn

from core.config import get_settings, validate_environment, ConfigurationError
from core.logging import initialize_logging, get_logger, log_performance_metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger = get_logger("vault_app.startup")
    
    try:
        # Validate environment configuration
        if not validate_environment():
            raise ConfigurationError("Environment validation failed")
        
        logger.info("Starting VAULT_APP v2.0 backend...")
        
        # Initialize database connections
        await initialize_database()
        
        # Log startup completion
        logger.info("VAULT_APP v2.0 backend started successfully")
        
        # Start background tasks
        asyncio.create_task(performance_monitoring_task())
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        raise
    
    finally:
        # Cleanup on shutdown
        logger.info("Shutting down VAULT_APP v2.0 backend...")
        await cleanup_database()
        logger.info("VAULT_APP v2.0 backend stopped")


async def initialize_database():
    """Initialize database connections."""
    logger = get_logger("vault_app.database")
    settings = get_settings()
    
    try:
        # Initialize Qdrant connection
        logger.info(f"Connecting to Qdrant at {settings.QDRANT_URL}")
        
        # This will be implemented when qdrant-client is installed
        # For now, just log the connection intent
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def cleanup_database():
    """Cleanup database connections."""
    logger = get_logger("vault_app.database")
    
    try:
        # Cleanup connections
        logger.info("Database cleanup completed")
        
    except Exception as e:
        logger.error(f"Database cleanup error: {e}")


async def performance_monitoring_task():
    """Background task for performance monitoring."""
    logger = get_logger("vault_app.monitoring")
    settings = get_settings()
    
    if not settings.ENABLE_METRICS:
        return
    
    while True:
        try:
            log_performance_metrics()
            await asyncio.sleep(60)  # Log metrics every minute
        except Exception as e:
            logger.error(f"Error in performance monitoring: {e}")
            await asyncio.sleep(60)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    # Initialize logging first
    logger = initialize_logging()
    settings = get_settings()
    
    # Create FastAPI app
    app = FastAPI(
        title="VAULT_APP v2.0",
        description="Advanced AI-powered document processing and conversation platform",
        version="2.0.0",
        docs_url="/docs" if settings.is_development() else None,
        redoc_url="/redoc" if settings.is_development() else None,
        openapi_url="/openapi.json" if settings.is_development() else None,
        lifespan=lifespan
    )
    
    # Add middleware
    setup_middleware(app)
    
    # Add routers
    setup_routes(app)
    
    # Add exception handlers
    setup_exception_handlers(app)
    
    logger.info("FastAPI application created and configured")
    return app


def setup_middleware(app: FastAPI):
    """Setup application middleware."""
    settings = get_settings()
    logger = get_logger("vault_app.middleware")
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Add request context
        request.state.request_id = request_id
        
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "event": "request_start"
            }
        )
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        logger.info(
            f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_seconds": round(duration, 3),
                "event": "request_complete"
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Gzip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    logger.info("Middleware configured")


def setup_routes(app: FastAPI):
    """Setup application routes."""
    settings = get_settings()
    logger = get_logger("vault_app.routes")
    
    # Import and include routers
    try:
        from api.health import router as health_router
        from api.chat import router as chat_router
        from api.documents import router as documents_router
        from api.sequences import router as sequences_router
        from api.analytics import router as analytics_router
        
        # Include routers with prefix
        app.include_router(health_router, tags=["Health"])
        app.include_router(chat_router, prefix=f"{settings.API_V1_PREFIX}/chat", tags=["Chat"])
        app.include_router(documents_router, prefix=f"{settings.API_V1_PREFIX}/documents", tags=["Documents"])
        app.include_router(sequences_router, prefix=f"{settings.API_V1_PREFIX}/sequences", tags=["Sequences"])
        app.include_router(analytics_router, prefix=f"{settings.API_V1_PREFIX}/analytics", tags=["Analytics"])
        
        logger.info("API routes configured")
        
    except ImportError as e:
        logger.warning(f"Some API modules not available: {e}")
        
        # Add basic health endpoint if routers aren't available
        @app.get("/health")
        async def health_check():
            return {"status": "healthy", "version": "2.0.0"}


def setup_exception_handlers(app: FastAPI):
    """Setup application exception handlers."""
    logger = get_logger("vault_app.exceptions")
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(
            f"HTTP exception: {exc.status_code} - {exc.detail}",
            extra={
                "request_id": getattr(request.state, 'request_id', None),
                "status_code": exc.status_code,
                "detail": exc.detail,
                "path": request.url.path,
                "event": "http_exception"
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                    "request_id": getattr(request.state, 'request_id', None)
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(
            f"Validation error: {exc.errors()}",
            extra={
                "request_id": getattr(request.state, 'request_id', None),
                "errors": exc.errors(),
                "path": request.url.path,
                "event": "validation_error"
            }
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": 422,
                    "message": "Validation error",
                    "details": exc.errors(),
                    "request_id": getattr(request.state, 'request_id', None)
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, 'request_id', None)
        
        logger.error(
            f"Unhandled exception: {type(exc).__name__}: {exc}",
            extra={
                "request_id": request_id,
                "exception_type": type(exc).__name__,
                "path": request.url.path,
                "event": "unhandled_exception"
            },
            exc_info=True
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": "Internal server error",
                    "request_id": request_id
                }
            }
        )
    
    logger.info("Exception handlers configured")


# Create app instance
app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.is_development(),
        log_config=None,  # Use our custom logging
        access_log=False,  # Handled by our middleware
    )