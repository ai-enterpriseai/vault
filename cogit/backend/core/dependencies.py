"""
Dependency injection for VAULT_APP v2.0 FastAPI application
Provides shared dependencies for database, configuration, logging, and services
"""

from typing import Optional, Dict, Any
from functools import lru_cache

try:
    from fastapi import Depends, HTTPException, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    FASTAPI_AVAILABLE = True
except ImportError:
    def Depends(func):
        return func
    HTTPException = Exception
    status = None
    HTTPBearer = object
    HTTPAuthorizationCredentials = None
    FASTAPI_AVAILABLE = False

from core.config import get_settings, Settings
from core.database import get_database, QdrantDatabase
from core.logging import get_logger
from core.exceptions import AuthenticationError, ConfigurationError


# Configuration Dependencies

@lru_cache()
def get_settings_dependency() -> Settings:
    """FastAPI dependency to get application settings."""
    return get_settings()


def get_logger_dependency(name: str = "vault_app"):
    """FastAPI dependency to get logger instance."""
    return get_logger(name)


# Database Dependencies

async def get_database_dependency() -> QdrantDatabase:
    """FastAPI dependency to get database instance."""
    try:
        database = get_database()
        if not database.is_connected:
            await database.initialize()
        return database
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Database dependency failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )


# Authentication Dependencies

security = HTTPBearer(auto_error=False) if FASTAPI_AVAILABLE else None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security) if FASTAPI_AVAILABLE else None
) -> Optional[Dict[str, Any]]:
    """
    Get current authenticated user from JWT token.
    Currently returns None (authentication not implemented).
    """
    if not credentials:
        return None
    
    # TODO: Implement JWT token validation
    # For now, just pass through
    return None


async def require_authentication(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user) if FASTAPI_AVAILABLE else None
) -> Dict[str, Any]:
    """
    Require user to be authenticated.
    Currently disabled until authentication is implemented.
    """
    # TODO: Enable when authentication is implemented
    # if not current_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Authentication required",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    
    # For now, return mock user
    return {"id": "anonymous", "role": "user"}


# Service Dependencies

class ServiceContainer:
    """Container for application services and their dependencies."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._initialized = False
    
    async def initialize(self):
        """Initialize all services."""
        if self._initialized:
            return
            
        try:
            # Initialize database
            database = get_database()
            await database.initialize()
            self._services["database"] = database
            
            # Initialize other services as needed
            self._services["settings"] = get_settings()
            self._services["logger"] = get_logger(__name__)
            
            self._initialized = True
            
        except Exception as e:
            logger = get_logger(__name__)
            logger.error(f"Service container initialization failed: {e}")
            raise ConfigurationError(f"Failed to initialize services: {e}")
    
    def get_service(self, service_name: str) -> Any:
        """Get service instance by name."""
        if not self._initialized:
            raise RuntimeError("Service container not initialized")
        return self._services.get(service_name)
    
    async def cleanup(self):
        """Cleanup all services."""
        if self._services.get("database"):
            await self._services["database"].close()
        self._services.clear()
        self._initialized = False


# Global service container
_service_container: Optional[ServiceContainer] = None


def get_service_container() -> ServiceContainer:
    """Get global service container."""
    global _service_container
    if _service_container is None:
        _service_container = ServiceContainer()
    return _service_container


async def get_service_container_dependency() -> ServiceContainer:
    """FastAPI dependency to get service container."""
    container = get_service_container()
    if not container._initialized:
        await container.initialize()
    return container


# Utility Dependencies

def get_request_id_dependency():
    """Get request ID from request state."""
    def _get_request_id(request) -> str:
        return getattr(request.state, 'request_id', 'unknown')
    return _get_request_id


# Validation Dependencies

def validate_pagination(
    page: int = 1, 
    page_size: int = 20, 
    max_page_size: int = 100
) -> Dict[str, int]:
    """Validate and normalize pagination parameters."""
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20
    if page_size > max_page_size:
        page_size = max_page_size
    
    return {
        "page": page,
        "page_size": page_size,
        "offset": (page - 1) * page_size
    }


def validate_search_params(
    query: Optional[str] = None,
    max_query_length: int = 1000
) -> Dict[str, Any]:
    """Validate search parameters."""
    if query and len(query) > max_query_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query too long (max {max_query_length} characters)"
        )
    
    return {
        "query": query.strip() if query else None,
        "has_query": bool(query and query.strip())
    }


# Configuration validation dependencies

def validate_api_keys() -> bool:
    """Validate that required API keys are configured."""
    settings = get_settings()
    
    required_keys = []
    if not settings.OPENAI_API_KEY:
        required_keys.append("OPENAI_API_KEY")
    if not settings.QDRANT_API_KEY:
        required_keys.append("QDRANT_API_KEY")
    
    if required_keys:
        logger = get_logger(__name__)
        logger.warning(f"Missing required API keys: {', '.join(required_keys)}")
        return False
    
    return True


def require_api_keys():
    """Dependency that requires API keys to be configured."""
    if not validate_api_keys():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Required API keys not configured"
        )
    return True


# Cleanup functions

async def cleanup_dependencies():
    """Cleanup all dependency resources."""
    global _service_container
    if _service_container:
        await _service_container.cleanup()
        _service_container = None