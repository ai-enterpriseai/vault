"""
Logging configuration for VAULT_APP backend
Advanced logging with structured output, rotation, filtering, and performance monitoring
"""

import logging
import logging.handlers
import sys
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional, Union
from pathlib import Path
import traceback
from functools import wraps

from .config import get_settings


class StructuredFormatter(logging.Formatter):
    """JSON structured logging formatter."""
    
    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Base log data
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if enabled
        if self.include_extra:
            for key, value in record.__dict__.items():
                if key not in {
                    'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                    'filename', 'module', 'lineno', 'funcName', 'created',
                    'msecs', 'relativeCreated', 'thread', 'threadName',
                    'processName', 'process', 'getMessage', 'exc_info',
                    'exc_text', 'stack_info'
                }:
                    log_data["extra"] = log_data.get("extra", {})
                    log_data["extra"][key] = value
        
        return json.dumps(log_data, default=str, ensure_ascii=False)


class PlainFormatter(logging.Formatter):
    """Human-readable plain text formatter."""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


class PerformanceFilter(logging.Filter):
    """Filter to add performance metrics to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add performance context to log records."""
        # Add memory usage if available
        try:
            import psutil
            process = psutil.Process()
            record.memory_mb = round(process.memory_info().rss / 1024 / 1024, 2)
            record.cpu_percent = round(process.cpu_percent(), 2)
        except ImportError:
            pass
        
        return True


class RequestContextFilter(logging.Filter):
    """Filter to add request context to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add request context if available."""
        # This will be populated by middleware in web requests
        record.request_id = getattr(record, 'request_id', None)
        record.user_id = getattr(record, 'user_id', None)
        record.endpoint = getattr(record, 'endpoint', None)
        
        return True


def setup_logging(name: str, level: Optional[str] = None) -> logging.Logger:
    """Setup comprehensive logging for the application."""
    settings = get_settings()
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = getattr(logging, (level or settings.LOG_LEVEL).upper())
    logger.setLevel(log_level)
    
    # Add filters
    logger.addFilter(PerformanceFilter())
    logger.addFilter(RequestContextFilter())
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Choose formatter based on configuration
    if settings.LOG_FORMAT.lower() == "json":
        console_formatter = StructuredFormatter()
    else:
        console_formatter = PlainFormatter()
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Setup file handler if configured
    if settings.LOG_FILE:
        try:
            log_file_path = Path(settings.LOG_FILE)
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                filename=settings.LOG_FILE,
                maxBytes=settings.LOG_MAX_SIZE,
                backupCount=settings.LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(StructuredFormatter())
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.error(f"Failed to setup file logging: {e}")
    
    # Disable propagation to avoid duplicate logs
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with standard configuration."""
    return setup_logging(name)


def log_function_call(logger: Optional[logging.Logger] = None):
    """Decorator to log function calls with timing and parameters."""
    def decorator(func):
        func_logger = logger or get_logger(func.__module__)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Log function entry
            func_logger.debug(
                f"Calling {func.__name__}",
                extra={
                    "function": func.__name__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                    "event": "function_entry"
                }
            )
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Log successful completion
                func_logger.debug(
                    f"Completed {func.__name__} in {duration:.3f}s",
                    extra={
                        "function": func.__name__,
                        "duration_seconds": round(duration, 3),
                        "event": "function_success"
                    }
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Log error
                func_logger.error(
                    f"Error in {func.__name__} after {duration:.3f}s: {e}",
                    extra={
                        "function": func.__name__,
                        "duration_seconds": round(duration, 3),
                        "error_type": type(e).__name__,
                        "event": "function_error"
                    },
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


def log_performance_metrics():
    """Log system performance metrics."""
    logger = get_logger("vault_app.performance")
    
    try:
        import psutil
        
        # CPU and memory metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        logger.info(
            "System performance metrics",
            extra={
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / 1024 / 1024 / 1024, 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                "event": "performance_metrics"
            }
        )
        
    except ImportError:
        logger.warning("psutil not available for performance monitoring")
    except Exception as e:
        logger.error(f"Error collecting performance metrics: {e}")


class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter for adding context to all log messages."""
    
    def __init__(self, logger: logging.Logger, extra: Dict[str, Any]):
        super().__init__(logger, extra)
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Add extra context to log message."""
        if 'extra' in kwargs:
            kwargs['extra'].update(self.extra)
        else:
            kwargs['extra'] = {**self.extra}
        
        return msg, kwargs


def create_context_logger(name: str, **context) -> LoggerAdapter:
    """Create a logger with additional context."""
    base_logger = get_logger(name)
    return LoggerAdapter(base_logger, context)


def setup_uvicorn_logging():
    """Configure uvicorn logging to use our structured format."""
    settings = get_settings()
    
    # Configure uvicorn loggers
    uvicorn_loggers = [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi"
    ]
    
    for logger_name in uvicorn_loggers:
        logger = logging.getLogger(logger_name)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Add our configured handler
        if settings.LOG_FORMAT.lower() == "json":
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(StructuredFormatter())
            logger.addHandler(handler)
        
        # Set appropriate level
        if logger_name == "uvicorn.access":
            logger.setLevel(logging.INFO if settings.DEBUG else logging.WARNING)
        else:
            logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
        
        logger.propagate = False


# Initialize application logging
def initialize_logging():
    """Initialize application-wide logging configuration."""
    settings = get_settings()
    
    # Setup main application logger
    app_logger = setup_logging("vault_app")
    
    # Configure uvicorn logging
    setup_uvicorn_logging()
    
    # Log initialization
    app_logger.info(
        "Logging system initialized",
        extra={
            "log_level": settings.LOG_LEVEL,
            "log_format": settings.LOG_FORMAT,
            "log_file": settings.LOG_FILE,
            "environment": settings.ENVIRONMENT,
            "event": "logging_initialized"
        }
    )
    
    return app_logger