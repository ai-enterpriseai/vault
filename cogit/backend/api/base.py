"""
Base API router for VAULT_APP v2.0
Provides health checks and basic system information endpoints
"""

from typing import Dict, Any
from datetime import datetime
import platform
import sys

try:
    from fastapi import APIRouter, Depends
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    class APIRouter:
        def __init__(self, *args, **kwargs):
            pass
        def get(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    def Depends(func):
        return func
    JSONResponse = dict
    FASTAPI_AVAILABLE = False

from core.config import get_settings
from core.database import get_database
from core.logging import get_logger
from core.dependencies import get_database_dependency

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns:
        Health status with system information and component status
    """
    try:
        settings = get_settings()
        
        # Basic system info
        health_info = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "environment": settings.ENVIRONMENT,
            "system": {
                "platform": platform.system(),
                "python_version": sys.version,
                "architecture": platform.architecture()[0]
            }
        }
        
        # Component health checks
        components = {}
        
        # Database health check
        try:
            database = get_database()
            db_health = await database.health_check()
            components["database"] = db_health
        except Exception as e:
            components["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_info["status"] = "degraded"
        
        # Configuration health check
        components["configuration"] = {
            "status": "healthy" if settings else "unhealthy",
            "loaded": settings is not None
        }
        
        # API keys validation
        api_keys_status = "healthy"
        missing_keys = []
        
        if not settings.QDRANT_API_KEY:
            missing_keys.append("QDRANT_API_KEY")
        if not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
            missing_keys.append("AI_MODEL_KEYS")
            
        if missing_keys:
            api_keys_status = "degraded"
            
        components["api_keys"] = {
            "status": api_keys_status,
            "missing": missing_keys
        }
        
        health_info["components"] = components
        
        # Overall status determination
        if any(comp.get("status") == "unhealthy" for comp in components.values()):
            health_info["status"] = "unhealthy"
        elif any(comp.get("status") == "degraded" for comp in components.values()):
            health_info["status"] = "degraded"
            
        logger.info(f"Health check completed - Status: {health_info['status']}")
        
        # Return appropriate HTTP status
        if health_info["status"] == "healthy":
            return health_info
        elif health_info["status"] == "degraded":
            return JSONResponse(status_code=200, content=health_info)
        else:
            return JSONResponse(status_code=503, content=health_info)
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        error_response = {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }
        return JSONResponse(status_code=503, content=error_response)


@router.get("/health/live")
async def liveness_check():
    """
    Simple liveness probe for container orchestration.
    
    Returns:
        Basic alive status
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/ready")
async def readiness_check(database: Any = Depends(get_database_dependency) if FASTAPI_AVAILABLE else None):
    """
    Readiness probe that checks if app can serve requests.
    
    Returns:
        Ready status based on critical dependencies
    """
    try:
        ready = True
        checks = {}
        
        # Check database connectivity
        if database:
            try:
                db_health = await database.health_check()
                checks["database"] = db_health["status"] == "healthy"
            except Exception:
                checks["database"] = False
                ready = False
        else:
            checks["database"] = False
            ready = False
        
        # Check configuration
        try:
            settings = get_settings()
            checks["configuration"] = settings is not None
        except Exception:
            checks["configuration"] = False
            ready = False
        
        response = {
            "status": "ready" if ready else "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks
        }
        
        if ready:
            return response
        else:
            return JSONResponse(status_code=503, content=response)
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )


@router.get("/info")
async def system_info():
    """
    Get detailed system information.
    
    Returns:
        System and application information
    """
    try:
        settings = get_settings()
        
        info = {
            "application": {
                "name": "VAULT_APP v2.0",
                "version": "2.0.0",
                "description": "Advanced AI-powered document processing and conversation platform",
                "environment": settings.ENVIRONMENT
            },
            "system": {
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": sys.version,
                "python_executable": sys.executable
            },
            "runtime": {
                "timestamp": datetime.utcnow().isoformat(),
                "uptime": "N/A",  # Would need startup tracking
                "process_id": None  # Could add os.getpid() if needed
            }
        }
        
        return info
        
    except Exception as e:
        logger.error(f"System info request failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to retrieve system information"}
        )