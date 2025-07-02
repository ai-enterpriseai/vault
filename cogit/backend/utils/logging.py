"""
Logging configuration and utilities for VAULT_APP v2.0 backend
Migrated from Streamlit application and adapted for FastAPI
"""

import logging
import sys
from typing import Any, Callable, TypeVar, Optional
from pathlib import Path

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    structlog = None
    STRUCTLOG_AVAILABLE = False

# Type variables for generic function decoration
F = TypeVar('F', bound=Callable[..., Any])


def setup_backend_logger(name: str, level: str = "INFO", log_file: Optional[str] = None) -> Any:
    """
    Set up structured logging for FastAPI backend with consistent configuration.
    
    Args:
        name: Logger name, typically __name__ of module
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path for file output
        
    Returns:
        Configured structured logger or standard logger
    """
    if STRUCTLOG_AVAILABLE:
        return _setup_structlog(name, level, log_file)
    else:
        return _setup_standard_logger(name, level, log_file)


def _setup_structlog(name: str, level: str, log_file: Optional[str]) -> structlog.BoundLogger:
    """Set up structlog configuration for structured logging."""
    
    # Configure processors for structured logging
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.ExceptionPrettyPrinter(),
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
        structlog.stdlib.add_log_level,
    ]
    
    # Add JSON renderer for production or console for development
    if log_file:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    # Set up logging level
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True
    )
    
    # Set up file logging if specified
    if log_file:
        _setup_file_logging(log_file, log_level)
    
    return structlog.get_logger(name)


def _setup_standard_logger(name: str, level: str, log_file: Optional[str]) -> logging.Logger:
    """Set up standard Python logging as fallback."""
    
    logger = logging.getLogger(name)
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def _setup_file_logging(log_file: str, log_level: int):
    """Set up file logging for structured logs."""
    
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Set up file handler for the root logger
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    
    # JSON formatter for file logs
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    
    # Add to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.setLevel(log_level)


def get_backend_logger(name: str = "vault_app") -> Any:
    """
    Get a logger instance for the backend.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance (structlog or standard)
    """
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)


def configure_uvicorn_logging(log_level: str = "INFO"):
    """
    Configure uvicorn logging to work with our logging setup.
    
    Args:
        log_level: Logging level for uvicorn
    """
    log_level_int = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure uvicorn loggers
    uvicorn_loggers = [
        "uvicorn",
        "uvicorn.error", 
        "uvicorn.access"
    ]
    
    for logger_name in uvicorn_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level_int)
        
        # Remove default handlers
        logger.handlers = []
        
        # Add our handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level_int)
        
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)


def log_function_call(func: F) -> F:
    """
    Decorator to log function calls with arguments and results.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    def wrapper(*args, **kwargs):
        logger = get_backend_logger(func.__module__)
        
        # Log function entry
        if STRUCTLOG_AVAILABLE:
            logger.debug("Function called", 
                        function=func.__name__, 
                        args=str(args)[:100], 
                        kwargs=str(kwargs)[:100])
        else:
            logger.debug(f"Function called: {func.__name__} with args: {str(args)[:100]}")
        
        try:
            result = func(*args, **kwargs)
            
            # Log successful completion
            if STRUCTLOG_AVAILABLE:
                logger.debug("Function completed", function=func.__name__)
            else:
                logger.debug(f"Function completed: {func.__name__}")
            
            return result
            
        except Exception as e:
            # Log exception
            if STRUCTLOG_AVAILABLE:
                logger.error("Function failed", 
                           function=func.__name__, 
                           error=str(e),
                           exc_info=True)
            else:
                logger.error(f"Function failed: {func.__name__} - {str(e)}", exc_info=True)
            raise
    
    return wrapper


def setup_request_logging():
    """Set up request-specific logging context."""
    if STRUCTLOG_AVAILABLE:
        # This would be called in middleware to set up request context
        structlog.contextvars.clear_contextvars()


def add_request_context(request_id: str, method: str, path: str):
    """
    Add request context to logging.
    
    Args:
        request_id: Unique request identifier
        method: HTTP method
        path: Request path
    """
    if STRUCTLOG_AVAILABLE:
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=method, 
            path=path
        )


# Alias for backward compatibility
setup_logger = setup_backend_logger