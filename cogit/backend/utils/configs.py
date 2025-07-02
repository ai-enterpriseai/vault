"""
Configuration utilities for VAULT_APP v2.0 backend
Migrated from Streamlit application and adapted for FastAPI
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Literal, Union, Dict, Any
from pydantic import BaseModel, Field, field_validator, SecretStr

from core.logging import get_logger
from core.config import get_settings

logger = get_logger(__name__)


def load_config(config_path: Union[str, Path] = None) -> dict:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path: Optional path to config file. If None, loads from project root
        
    Returns:
        dict: Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    try:
        # If no path provided, look in project root (two levels up)
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / 'config.yaml'
        else:
            config_path = Path(config_path)
            
        # Read and parse YAML
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            config_name = next(iter(data))
            config_data = data[config_name]

        logger.info(f"Loaded configuration from {config_path}")
        return config_data
        
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in config file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise 


def replace_api_keys(config: dict) -> dict:
    """
    Replace API keys in the configuration with environment variables.
    
    Args:
        config (dict): The configuration dictionary.
        
    Returns:
        dict: The updated configuration dictionary with API keys replaced.
    """
    settings = get_settings()
    
    # Replace indexer/database keys
    if not config.generator.together_api_key or config.indexer.qdrant_api_key == 'YOUR_API_KEY':
        config.indexer.qdrant_api_key = settings.QDRANT_API_KEY
    
    if not config.indexer.url or config.indexer.url == 'YOUR_URL':
        config.indexer.url = settings.QDRANT_URL

    if not config.indexer.collection_name or config.indexer.collection_name == 'YOUR_COLLECTION_NAME':
        config.indexer.collection_name = settings.QDRANT_COLLECTION_NAME

    # Replace AI model keys
    if not config.generator.together_api_key or config.generator.together_api_key == 'YOUR_API_KEY':
        config.generator.together_api_key = settings.TOGETHER_API_KEY

    if not config.generator.anthropic_api_key or config.generator.anthropic_api_key == 'YOUR_API_KEY':
        config.generator.anthropic_api_key = settings.ANTHROPIC_API_KEY

    # Replace reranker keys
    if not config.retriever.reranker.api_key or config.retriever.reranker.api_key == 'YOUR_API_KEY':
        config.retriever.reranker.api_key = settings.COHERE_API_KEY

    return config


def replace_runner_settings(runner) -> None:
    """
    Configure SequenceRunner settings with API keys from environment variables,
    but only if they're not already set or are empty.
    
    Args:
        runner: SequenceRunner instance to configure
    """
    settings = get_settings()
    
    # Map settings names to environment values
    settings_mapping = {
        'openai_api_key': settings.OPENAI_API_KEY,
        'anthropic_api_key': settings.ANTHROPIC_API_KEY,
        'together_api_key': settings.TOGETHER_API_KEY,
        'hf_api_key': getattr(settings, 'HF_API_KEY', None),
        'cerebras_api_key': getattr(settings, 'CEREBRAS_API_KEY', None),
        'sambanova_api_key': getattr(settings, 'SAMBANOVA_API_KEY', None)
    }
    
    for setting_name, env_value in settings_mapping.items():
        if not env_value:
            continue
            
        current_value = getattr(runner.settings, setting_name, None)
        
        # Check if setting is None, empty, or not set
        if (current_value is None or 
            not current_value or 
            (hasattr(current_value, 'get_secret_value') and current_value.get_secret_value() == "")):
            
            setattr(
                runner.settings,
                setting_name,
                SecretStr(env_value)
            )
            logger.debug(f"Updated {setting_name} from environment")


def get_config_value(key_path: str, default: Any = None) -> Any:
    """
    Get a configuration value using dot notation.
    
    Args:
        key_path: Dot-separated key path (e.g., 'generator.temperature')
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    try:
        config = load_config()
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            value = value[key]
        
        return value
        
    except (KeyError, TypeError):
        return default


def validate_configuration() -> Dict[str, Any]:
    """
    Validate current configuration and return status.
    
    Returns:
        Dict with validation status and any issues found
    """
    issues = []
    warnings = []
    
    try:
        # Check if config file loads
        config = load_config()
        
        # Check required sections
        required_sections = ['processor', 'embedder', 'indexer', 'retriever', 'manager', 'generator']
        for section in required_sections:
            if section not in config:
                issues.append(f"Missing required section: {section}")
        
        # Check API key configuration
        settings = get_settings()
        if not settings.QDRANT_API_KEY:
            warnings.append("QDRANT_API_KEY not configured")
        if not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
            warnings.append("No AI model API keys configured")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "config_loaded": True
        }
        
    except Exception as e:
        return {
            "valid": False,
            "issues": [f"Configuration load failed: {e}"],
            "warnings": [],
            "config_loaded": False
        }


class APIConfig(BaseModel):
    """Configuration for API settings."""
    title: str = Field(
        default="VAULT_APP v2.0 API",
        description="API title"
    )
    description: str = Field(
        default="Advanced AI-powered document processing and conversation platform",
        description="API description"
    )
    version: str = Field(
        default="2.0.0",
        description="API version"
    )
    prefix: str = Field(
        default="/api/v1",
        description="API URL prefix"
    )
    enable_docs: bool = Field(
        default=True,
        description="Enable API documentation"
    )


class AppConfig(BaseModel):
    """Main application configuration for FastAPI backend."""
    app_name: str = Field(
        default="vault_app_v2",
        description="Application name"
    )
    debug: bool = Field(
        default=False,
        description="Debug mode flag"
    )
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Deployment environment"
    )
    base_path: Path = Field(
        default=Path.cwd(),
        description="Base path for application resources"
    )
    data_path: Path = Field(
        default=Path.cwd() / "data",
        description="Path to data directory"
    )
    cache_path: Path = Field(
        default=Path.cwd() / "cache",
        description="Path to cache directory"
    )
    temp_path: Path = Field(
        default=Path.cwd() / "temp",
        description="Path to temporary files directory"
    )
    logs_path: Path = Field(
        default=Path.cwd() / "logs",
        description="Path to logs directory"
    )
    api: APIConfig = Field(
        default_factory=APIConfig,
        description="API configuration"
    )

    @field_validator("*")
    def validate_paths(cls, v, info):
        """Validate and create directories for path fields."""
        if isinstance(v, Path) and info.field_name.endswith('_path'):
            v.mkdir(parents=True, exist_ok=True)
        return v

    @classmethod
    def from_yaml(cls, path: str) -> "AppConfig":
        """Load configuration from YAML file."""
        try:
            with open(path, 'r') as f:
                config_dict = yaml.safe_load(f)
            return cls.model_validate(config_dict)
        except Exception as e:
            raise ValueError(f"Failed to load config from {path}: {e}")

    def to_yaml(self, path: str) -> None:
        """Save configuration to YAML file."""
        try:
            with open(path, 'w') as f:
                yaml.safe_dump(
                    self.model_dump(exclude_none=True),
                    f,
                    default_flow_style=False
                )
        except Exception as e:
            raise ValueError(f"Failed to save config to {path}: {e}")

    class Config:
        """Pydantic model configuration."""
        validate_assignment = True
        frozen = False  # Allow updates for backend flexibility
        extra = "allow"  # Allow extra fields for extensibility


def create_default_config() -> AppConfig:
    """Create default application configuration."""
    return AppConfig()


def get_environment_config() -> Dict[str, Any]:
    """Get configuration values from environment variables."""
    env_config = {}
    
    # API configuration from environment
    if os.getenv('API_TITLE'):
        env_config['api_title'] = os.getenv('API_TITLE')
    if os.getenv('API_VERSION'):
        env_config['api_version'] = os.getenv('API_VERSION')
    if os.getenv('DEBUG'):
        env_config['debug'] = os.getenv('DEBUG').lower() in ('true', '1', 'yes')
    
    return env_config