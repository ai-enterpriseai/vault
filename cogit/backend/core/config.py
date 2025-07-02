"""
Configuration management for VAULT_APP backend
Comprehensive settings with validation, caching, and environment management
"""

import os
import logging
from typing import List, Optional, Any, Dict
from pathlib import Path
from functools import lru_cache
import json


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class Settings:
    """Application settings with validation and environment management."""
    
    def __init__(self):
        """Initialize settings with environment variables and validation."""
        # Application
        self.DEBUG: bool = self._get_bool("DEBUG", False)
        self.ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        self.LOG_LEVEL: str = self._get_log_level("LOG_LEVEL", "INFO")
        self.HOST: str = os.getenv("HOST", "0.0.0.0")
        self.PORT: int = self._get_int("PORT", 8000)
        
        # Security
        self.SECRET_KEY: str = self._get_required("SECRET_KEY", generate_if_missing=True)
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = self._get_int("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
        
        # API Configuration
        self.ALLOWED_ORIGINS: List[str] = self._get_list("ALLOWED_ORIGINS", [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173"
        ])
        self.API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
        self.MAX_REQUEST_SIZE: int = self._get_int("MAX_REQUEST_SIZE", 104857600)  # 100MB
        
        # Database - Qdrant
        self.QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")
        self.QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "vault_documents")
        self.QDRANT_TIMEOUT: int = self._get_int("QDRANT_TIMEOUT", 30)
        self.VECTOR_DIMENSION: int = self._get_int("VECTOR_DIMENSION", 1536)
        
        # AI API Keys (with validation)
        self.OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        self.TOGETHER_API_KEY: Optional[str] = os.getenv("TOGETHER_API_KEY")
        self.COHERE_API_KEY: Optional[str] = os.getenv("COHERE_API_KEY")
        
        # AI Model Settings
        self.DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4")
        self.MAX_TOKENS: int = self._get_int("MAX_TOKENS", 4000)
        self.TEMPERATURE: float = self._get_float("TEMPERATURE", 0.7)
        
        # File handling
        self.MAX_FILE_SIZE: int = self._get_int("MAX_FILE_SIZE", 104857600)  # 100MB
        self.UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
        self.ALLOWED_FILE_TYPES: List[str] = self._get_list("ALLOWED_FILE_TYPES", [
            ".pdf", ".txt", ".md", ".doc", ".docx", ".csv", ".json"
        ])
        
        # Performance Settings
        self.WORKER_PROCESSES: int = self._get_int("WORKER_PROCESSES", 1)
        self.WORKER_CONNECTIONS: int = self._get_int("WORKER_CONNECTIONS", 1000)
        self.KEEPALIVE: int = self._get_int("KEEPALIVE", 2)
        
        # Cache Settings
        self.CACHE_TTL: int = self._get_int("CACHE_TTL", 3600)  # 1 hour
        self.REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
        
        # Logging
        self.LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
        self.LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
        self.LOG_MAX_SIZE: int = self._get_int("LOG_MAX_SIZE", 10485760)  # 10MB
        self.LOG_BACKUP_COUNT: int = self._get_int("LOG_BACKUP_COUNT", 5)
        
        # Monitoring
        self.ENABLE_METRICS: bool = self._get_bool("ENABLE_METRICS", True)
        self.METRICS_PORT: int = self._get_int("METRICS_PORT", 9090)
        
        # Validate configuration after initialization
        self._validate_configuration()
    
    def _get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")
    
    def _get_int(self, key: str, default: int = 0) -> int:
        """Get integer environment variable with validation."""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            raise ConfigurationError(f"Invalid integer value for {key}: {os.getenv(key)}")
    
    def _get_float(self, key: str, default: float = 0.0) -> float:
        """Get float environment variable with validation."""
        try:
            return float(os.getenv(key, str(default)))
        except ValueError:
            raise ConfigurationError(f"Invalid float value for {key}: {os.getenv(key)}")
    
    def _get_list(self, key: str, default: List[str]) -> List[str]:
        """Get list from environment variable (comma-separated)."""
        value = os.getenv(key)
        if not value:
            return default
        return [item.strip() for item in value.split(",") if item.strip()]
    
    def _get_log_level(self, key: str, default: str = "INFO") -> str:
        """Get log level with validation."""
        level = os.getenv(key, default).upper()
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level not in valid_levels:
            raise ConfigurationError(f"Invalid log level {level}. Must be one of: {valid_levels}")
        return level
    
    def _get_required(self, key: str, generate_if_missing: bool = False) -> str:
        """Get required environment variable."""
        value = os.getenv(key)
        if not value:
            if generate_if_missing and key == "SECRET_KEY":
                # Generate a secure secret key if missing
                import secrets
                value = secrets.token_urlsafe(32)
                logging.warning(f"Generated {key} - consider setting it explicitly")
            else:
                raise ConfigurationError(f"Required environment variable {key} is not set")
        return value
    
    def _validate_configuration(self) -> None:
        """Validate configuration settings."""
        errors = []
        
        # Validate paths
        upload_path = Path(self.UPLOAD_DIR)
        if not upload_path.exists():
            try:
                upload_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create upload directory {self.UPLOAD_DIR}: {e}")
        
        # Validate port ranges
        if not (1 <= self.PORT <= 65535):
            errors.append(f"Invalid port number: {self.PORT}")
        
        if not (1 <= self.METRICS_PORT <= 65535):
            errors.append(f"Invalid metrics port number: {self.METRICS_PORT}")
        
        # Validate file size limits
        if self.MAX_FILE_SIZE <= 0:
            errors.append(f"MAX_FILE_SIZE must be positive: {self.MAX_FILE_SIZE}")
        
        # Validate AI settings
        if self.TEMPERATURE < 0 or self.TEMPERATURE > 2:
            errors.append(f"TEMPERATURE must be between 0 and 2: {self.TEMPERATURE}")
        
        if self.MAX_TOKENS <= 0:
            errors.append(f"MAX_TOKENS must be positive: {self.MAX_TOKENS}")
        
        # Validate environment
        valid_environments = ["development", "staging", "production"]
        if self.ENVIRONMENT not in valid_environments:
            errors.append(f"Invalid ENVIRONMENT: {self.ENVIRONMENT}. Must be one of: {valid_environments}")
        
        # Check for at least one AI API key in production
        if self.ENVIRONMENT == "production":
            ai_keys = [self.OPENAI_API_KEY, self.ANTHROPIC_API_KEY, self.TOGETHER_API_KEY, self.COHERE_API_KEY]
            if not any(ai_keys):
                errors.append("At least one AI API key must be configured in production")
        
        if errors:
            raise ConfigurationError(f"Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors))
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"
    
    def get_database_url(self) -> str:
        """Get complete Qdrant database URL."""
        return self.QDRANT_URL
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration dictionary."""
        return {
            "openai_api_key": self.OPENAI_API_KEY,
            "anthropic_api_key": self.ANTHROPIC_API_KEY,
            "together_api_key": self.TOGETHER_API_KEY,
            "cohere_api_key": self.COHERE_API_KEY,
            "default_model": self.DEFAULT_MODEL,
            "max_tokens": self.MAX_TOKENS,
            "temperature": self.TEMPERATURE
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary (excluding sensitive data)."""
        sensitive_keys = {
            "SECRET_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", 
            "TOGETHER_API_KEY", "COHERE_API_KEY", "QDRANT_API_KEY"
        }
        
        result = {}
        for key, value in self.__dict__.items():
            if key.upper() not in sensitive_keys:
                result[key] = value
            else:
                result[key] = "***" if value else None
        
        return result


# Global settings instance with thread-safe caching
_settings = None

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get application settings (singleton with caching)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Force reload of settings (useful for testing)."""
    global _settings
    get_settings.cache_clear()
    _settings = None
    return get_settings()


def validate_environment() -> bool:
    """Validate that the environment is properly configured."""
    try:
        settings = get_settings()
        logging.info(f"Configuration validated successfully for environment: {settings.ENVIRONMENT}")
        return True
    except ConfigurationError as e:
        logging.error(f"Configuration validation failed: {e}")
        return False