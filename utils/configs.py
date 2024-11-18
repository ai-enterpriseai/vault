import yaml

import streamlit as st

from pathlib import Path
from typing import Optional, Literal, Union
from pydantic import BaseModel, Field, field_validator

from pipeline.utils.logging import setup_logger

logger = setup_logger(__name__)

def load_config(config_path: Union[str, Path] = None) -> dict:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path: Optional path to config file. If None, loads from parent directory
        
    Returns:
        dict: Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    try:
        # If no path provided, look in parent directory
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config.yaml'
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
    Replace API keys in the configuration with Streamlit secrets.

    Args:
        config (dict): The configuration dictionary.

    Returns:
        dict: The updated configuration dictionary with API keys replaced.
    """
    if not config.generator.together_api_key or config.indexer.qdrant_api_key == 'YOUR_API_KEY':
        config.indexer.qdrant_api_key = st.secrets['QDRANT_API_KEY']
    
    if not config.indexer.url or config.indexer.url == 'YOUR_URL':
        config.indexer.url = st.secrets['QDRANT_URL']

    if not config.indexer.collection_name or config.indexer.collection_name == 'YOUR_COLLECTION_NAME':
        config.indexer.collection_name = st.secrets['QDRANT_COLLECTION_NAME']

    if not config.generator.together_api_key or config.generator.together_api_key == 'YOUR_API_KEY':
        config.generator.together_api_key = st.secrets['TOGETHER_API_KEY']

    if not config.generator.anthropic_api_key or config.generator.anthropic_api_key == 'YOUR_API_KEY':
        config.generator.anthropic_api_key = st.secrets['ANTHROPIC_API_KEY']

    return config

class UIConfig(BaseModel):
    """Configuration for the Streamlit UI."""
    title: str = Field(
        default="InhouseGPT - LLM for Business",
        description="Application title"
    )
    icon: str = Field(
        default="💡",
        description="Application icon (emoji or path)"
    )
    layout: Literal["centered", "wide"] = Field(
        default="wide",
        description="Page layout"
    )
    sidebar_state: Literal["auto", "expanded", "collapsed"] = Field(
        default="auto",
        description="Initial sidebar state"
    )
    sidebar_title: str = Field(
        default="InhouseGPT-App",
        description="Sidebar title"
    )
    sidebar_description: Optional[str] = Field(
        default="Explore InhouseGPT knowledge base",
        description="Sidebar description"
    )
    logo_path: Optional[Path] = Field(
        default=None,
        description="Path to logo image"
    )
    logo_width: int = Field(
        default=300,
        description="Width of logo in pixels"
    )
    hide_streamlit_elements: bool = Field(
        default=True,
        description="Hide default Streamlit UI elements"
    )
    theme: dict = Field(
        default={
            "primaryColor": "#FF4B4B",
            "backgroundColor": "#FFFFFF",
            "secondaryBackgroundColor": "#F0F2F6",
            "textColor": "#262730",
            "font": "sans serif"
        },
        description="Streamlit theme configuration"
    )

class AppConfig(BaseModel):
    """Main application configuration."""
    app_name: str = Field(
        default="vault",
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
    ui: UIConfig = Field(
        default_factory=UIConfig,
        description="UI configuration"
    )

    @field_validator("*")
    def validate_paths(cls, v, field):
        """Validate and create directories for path fields."""
        if isinstance(v, Path) and field.name.endswith('_path'):
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
        frozen = True
        extra = "forbid"