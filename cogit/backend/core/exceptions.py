"""
Custom exception classes for VAULT_APP v2.0
Provides structured error handling throughout the FastAPI application
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException


class VaultBaseException(Exception):
    """Base exception class for all VAULT_APP exceptions."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(VaultBaseException):
    """Raised when there are configuration-related errors."""
    pass


class DatabaseConnectionError(VaultBaseException):
    """Raised when database connection fails."""
    pass


class DatabaseInitializationError(VaultBaseException):
    """Raised when database initialization fails."""
    pass


class DocumentProcessingError(VaultBaseException):
    """Raised when document processing fails."""
    pass


class EmbeddingError(VaultBaseException):
    """Raised when embedding generation fails."""
    pass


class RetrievalError(VaultBaseException):
    """Raised when context retrieval fails."""
    pass


class AIModelError(VaultBaseException):
    """Raised when AI model operations fail."""
    pass


class ConversationError(VaultBaseException):
    """Raised when conversation operations fail."""
    pass


class AuthenticationError(VaultBaseException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(VaultBaseException):
    """Raised when authorization fails."""
    pass


class ValidationError(VaultBaseException):
    """Raised when input validation fails."""
    pass


class RateLimitError(VaultBaseException):
    """Raised when rate limits are exceeded."""
    pass


class ExternalServiceError(VaultBaseException):
    """Raised when external service calls fail."""
    pass


# HTTP Exception mappers for FastAPI

def create_http_exception(
    exc: VaultBaseException,
    status_code: int = 500,
    headers: Optional[Dict[str, str]] = None
) -> HTTPException:
    """Convert VaultBaseException to FastAPI HTTPException."""
    
    detail = {
        "error": {
            "type": type(exc).__name__,
            "message": exc.message,
            "details": exc.details
        }
    }
    
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers=headers
    )


def map_exception_to_http(exc: VaultBaseException) -> HTTPException:
    """Map specific exceptions to appropriate HTTP status codes."""
    
    exception_mappings = {
        ConfigurationError: 500,  # Internal Server Error
        DatabaseConnectionError: 503,  # Service Unavailable
        DatabaseInitializationError: 503,  # Service Unavailable
        DocumentProcessingError: 422,  # Unprocessable Entity
        EmbeddingError: 502,  # Bad Gateway
        RetrievalError: 502,  # Bad Gateway
        AIModelError: 502,  # Bad Gateway
        ConversationError: 400,  # Bad Request
        AuthenticationError: 401,  # Unauthorized
        AuthorizationError: 403,  # Forbidden
        ValidationError: 422,  # Unprocessable Entity
        RateLimitError: 429,  # Too Many Requests
        ExternalServiceError: 502,  # Bad Gateway
    }
    
    status_code = exception_mappings.get(type(exc), 500)
    return create_http_exception(exc, status_code)


# Exception handler decorators

def handle_database_errors(func):
    """Decorator to handle database-related errors."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (DatabaseConnectionError, DatabaseInitializationError) as e:
            raise map_exception_to_http(e)
        except Exception as e:
            raise DatabaseConnectionError(f"Unexpected database error: {e}")
    return wrapper


def handle_ai_errors(func):
    """Decorator to handle AI model-related errors."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (AIModelError, EmbeddingError, RetrievalError) as e:
            raise map_exception_to_http(e)
        except Exception as e:
            raise AIModelError(f"Unexpected AI service error: {e}")
    return wrapper


def handle_document_errors(func):
    """Decorator to handle document processing errors."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except DocumentProcessingError as e:
            raise map_exception_to_http(e)
        except Exception as e:
            raise DocumentProcessingError(f"Unexpected document processing error: {e}")
    return wrapper