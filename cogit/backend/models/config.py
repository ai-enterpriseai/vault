"""
Configuration models for VAULT_APP v2.0 backend
Pydantic models for configuration validation and type safety
"""

from typing import Optional, List, Dict, Any, Literal
from pathlib import Path

try:
    from pydantic import BaseModel, Field, validator, SecretStr
    PYDANTIC_AVAILABLE = True
except ImportError:
    # Fallback for when pydantic isn't available
    class BaseModel:
        pass
    def Field(*args, **kwargs):
        return None
    def validator(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    class SecretStr:
        def __init__(self, value):
            self.value = value
        def get_secret_value(self):
            return self.value
    PYDANTIC_AVAILABLE = False


class DatabaseConfig(BaseModel):
    """Database configuration model."""
    
    url: str = Field(..., description="Database connection URL")
    api_key: SecretStr = Field(..., description="Database API key")
    collection_name: str = Field(default="vault_documents", description="Collection name")
    timeout: float = Field(default=30.0, description="Connection timeout in seconds")
    max_connections: int = Field(default=10, description="Maximum number of connections")
    
    @validator('url')
    def validate_url(cls, v):
        """Validate database URL format."""
        if not v or v == "YOUR_URL":
            raise ValueError("Database URL must be configured")
        return v


class EmbedderConfig(BaseModel):
    """Embedder configuration model."""
    
    embedder_type: Literal["openai", "sentence_transformer"] = Field(
        default="sentence_transformer",
        description="Type of embedder to use"
    )
    dense_model_name: str = Field(
        default="all-mpnet-base-v2",
        description="Dense embedding model name"
    )
    dense_model_dimension: int = Field(
        default=768,
        description="Dense embedding dimension"
    )
    
    @validator('dense_model_dimension')
    def validate_dimension(cls, v):
        """Validate embedding dimension."""
        if v <= 0:
            raise ValueError("Embedding dimension must be positive")
        return v


class RerankerConfig(BaseModel):
    """Reranker configuration model."""
    
    reranker_type: Literal["reranker", "cohere"] = Field(
        default="cohere",
        description="Type of reranker to use"
    )
    reranker_model_name: str = Field(
        default="rerank-multilingual-v3.0",
        description="Reranker model name"
    )
    top_k: int = Field(default=5, description="Number of top results after reranking")
    api_key: SecretStr = Field(..., description="Reranker API key")


class RetrieverConfig(BaseModel):
    """Retriever configuration model."""
    
    top_k: int = Field(default=25, description="Number of initial results to retrieve")
    reranker: RerankerConfig = Field(..., description="Reranker configuration")


class GeneratorConfig(BaseModel):
    """AI model generator configuration."""
    
    primary_model: Dict[str, Any] = Field(
        default={
            "name": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            "max_tokens": 4096,
            "temperature": 0.2,
            "timeout": 30.0
        },
        description="Primary AI model configuration"
    )
    fallback_model: Dict[str, Any] = Field(
        default={
            "name": "claude-3-5-sonnet-20241022",
            "max_tokens": 4096,
            "temperature": 0.2,
            "timeout": 30.0
        },
        description="Fallback AI model configuration"
    )
    together_api_key: SecretStr = Field(..., description="Together AI API key")
    anthropic_api_key: SecretStr = Field(..., description="Anthropic API key")
    openai_api_key: Optional[SecretStr] = Field(None, description="OpenAI API key")


class ProcessorConfig(BaseModel):
    """Document processor configuration."""
    
    chunk_size: int = Field(default=512, description="Text chunk size for processing")
    chunk_overlap: int = Field(default=128, description="Overlap between chunks")
    min_chunk_size: int = Field(default=128, description="Minimum chunk size")
    
    @validator('chunk_size')
    def validate_chunk_size(cls, v):
        """Validate chunk size."""
        if v <= 0:
            raise ValueError("Chunk size must be positive")
        return v
    
    @validator('chunk_overlap')
    def validate_overlap(cls, v, values):
        """Validate chunk overlap."""
        if v < 0:
            raise ValueError("Chunk overlap cannot be negative")
        if 'chunk_size' in values and v >= values['chunk_size']:
            raise ValueError("Chunk overlap must be less than chunk size")
        return v


class ManagerConfig(BaseModel):
    """Prompt manager configuration."""
    
    templates_dir: str = Field(default="./prompts", description="Directory containing prompt templates")
    version: str = Field(default="v0.1", description="Prompt version")
    prompt: str = Field(
        default="system_workshop_assistant_de",
        description="Default prompt template name"
    )
    description: str = Field(
        default="German language workshop assistant for AI implementation guidance",
        description="Prompt description"
    )


class PipelineConfig(BaseModel):
    """Complete pipeline configuration model."""
    
    processor: ProcessorConfig = Field(default_factory=ProcessorConfig)
    embedder: EmbedderConfig = Field(default_factory=EmbedderConfig)
    indexer: DatabaseConfig = Field(..., description="Database/indexer configuration")
    retriever: RetrieverConfig = Field(..., description="Retriever configuration")
    manager: ManagerConfig = Field(default_factory=ManagerConfig)
    generator: GeneratorConfig = Field(..., description="AI generator configuration")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"


class APIConfig(BaseModel):
    """API-specific configuration."""
    
    title: str = Field(default="VAULT_APP v2.0 API", description="API title")
    description: str = Field(
        default="Advanced AI-powered document processing and conversation platform",
        description="API description"
    )
    version: str = Field(default="2.0.0", description="API version")
    prefix: str = Field(default="/api/v1", description="API URL prefix")
    docs_url: Optional[str] = Field(default="/docs", description="Documentation URL")
    redoc_url: Optional[str] = Field(default="/redoc", description="ReDoc URL")
    openapi_url: Optional[str] = Field(default="/openapi.json", description="OpenAPI schema URL")


class ServerConfig(BaseModel):
    """Server configuration."""
    
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Enable auto-reload")
    workers: int = Field(default=1, description="Number of worker processes")
    log_level: str = Field(default="INFO", description="Logging level")
    
    @validator('port')
    def validate_port(cls, v):
        """Validate port number."""
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v


class AppConfig(BaseModel):
    """Main application configuration."""
    
    app_name: str = Field(default="vault_app_v2", description="Application name")
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Environment name"
    )
    debug: bool = Field(default=False, description="Debug mode")
    secret_key: SecretStr = Field(..., description="Application secret key")
    
    # Component configurations
    api: APIConfig = Field(default_factory=APIConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    pipeline: PipelineConfig = Field(..., description="Pipeline configuration")
    
    # Paths
    base_path: Path = Field(default=Path.cwd(), description="Base application path")
    data_path: Path = Field(default=Path.cwd() / "data", description="Data directory")
    logs_path: Path = Field(default=Path.cwd() / "logs", description="Logs directory")
    temp_path: Path = Field(default=Path.cwd() / "temp", description="Temporary files directory")
    
    # Security and CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    allowed_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE"],
        description="Allowed HTTP methods"
    )
    
    @validator('*')
    def create_directories(cls, v, field):
        """Create directories for path fields."""
        if isinstance(v, Path) and field.name.endswith('_path'):
            v.mkdir(parents=True, exist_ok=True)
        return v
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "allow"  # Allow extra fields for flexibility


# Factory functions for creating default configurations

def create_default_pipeline_config() -> PipelineConfig:
    """Create default pipeline configuration."""
    return PipelineConfig(
        indexer=DatabaseConfig(
            url="http://localhost:6333",
            api_key=SecretStr("default_key"),
            collection_name="vault_documents"
        ),
        retriever=RetrieverConfig(
            reranker=RerankerConfig(
                api_key=SecretStr("default_key")
            )
        ),
        generator=GeneratorConfig(
            together_api_key=SecretStr("default_key"),
            anthropic_api_key=SecretStr("default_key")
        )
    )


def create_default_app_config() -> AppConfig:
    """Create default application configuration."""
    return AppConfig(
        secret_key=SecretStr("default_secret_key_change_in_production"),
        pipeline=create_default_pipeline_config()
    )