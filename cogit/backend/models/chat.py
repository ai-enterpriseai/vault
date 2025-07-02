"""
Chat models for VAULT_APP v2.0
Pydantic models for chat conversations, messages, and streaming
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Literal
from uuid import UUID
from enum import Enum

try:
    from pydantic import BaseModel, Field
except ImportError:
    # Fallback for when pydantic is not installed
    class BaseModel:
        pass
    
    def Field(*args, **kwargs):
        return None

from .base import BaseResponse, TimestampedModel, PaginationParams


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant" 
    SYSTEM = "system"


class ModelProvider(str, Enum):
    """AI model provider enumeration."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    TOGETHER = "together"
    COHERE = "cohere"


class ChatMessage(BaseModel):
    """Individual chat message model."""
    
    id: Optional[str] = None
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # RAG context information
    context_used: Optional[bool] = False
    source_documents: Optional[List[Dict[str, Any]]] = None
    
    # Model information
    model_used: Optional[str] = None
    provider: Optional[ModelProvider] = None
    
    # Performance metrics
    response_time: Optional[float] = None
    token_count: Optional[Dict[str, int]] = None


class ChatRequest(BaseModel):
    """Chat request model for sending messages."""
    
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    conversation_id: Optional[str] = None
    
    # Model configuration
    model: Optional[str] = None
    provider: Optional[ModelProvider] = None
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=8000)
    
    # RAG configuration
    use_rag: bool = Field(default=True, description="Enable RAG for this request")
    max_context_documents: int = Field(default=5, ge=0, le=20)
    context_similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    
    # Streaming
    stream: bool = Field(default=False, description="Enable streaming response")
    
    # Additional context
    system_prompt: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseResponse):
    """Chat response model."""
    
    message: ChatMessage
    conversation_id: str
    
    # RAG information
    context_documents: Optional[List[Dict[str, Any]]] = None
    rag_enabled: bool = False
    
    # Model information
    model_used: str
    provider_used: ModelProvider
    
    # Performance metrics
    response_time: float
    token_usage: Dict[str, int]
    
    # Cost information (if available)
    estimated_cost: Optional[float] = None


class StreamingChatResponse(BaseModel):
    """Streaming chat response chunk."""
    
    chunk_id: str
    conversation_id: str
    content_delta: str
    is_final: bool = False
    
    # Metadata for final chunk
    final_message: Optional[ChatMessage] = None
    token_usage: Optional[Dict[str, int]] = None
    response_time: Optional[float] = None


class ConversationCreate(BaseModel):
    """Request to create a new conversation."""
    
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    system_prompt: Optional[str] = Field(default=None, max_length=5000)
    
    # Default model settings for this conversation
    default_model: Optional[str] = None
    default_provider: Optional[ModelProvider] = None
    default_temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    
    # RAG settings
    rag_enabled: bool = Field(default=True)
    rag_collection: Optional[str] = None
    
    # Metadata
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(TimestampedModel):
    """Conversation response model."""
    
    title: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    
    # Settings
    default_model: Optional[str] = None
    default_provider: Optional[ModelProvider] = None
    default_temperature: float = 0.7
    rag_enabled: bool = True
    rag_collection: Optional[str] = None
    
    # Statistics
    message_count: int = 0
    last_message_at: Optional[datetime] = None
    
    # Metadata
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    
    # User information
    user_id: Optional[str] = None


class ConversationUpdate(BaseModel):
    """Request to update a conversation."""
    
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    system_prompt: Optional[str] = Field(default=None, max_length=5000)
    
    # Model settings
    default_model: Optional[str] = None
    default_provider: Optional[ModelProvider] = None
    default_temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    
    # RAG settings
    rag_enabled: Optional[bool] = None
    rag_collection: Optional[str] = None
    
    # Metadata
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class MessageHistory(BaseModel):
    """Message history with pagination support."""
    
    conversation_id: str
    messages: List[ChatMessage]
    total_messages: int
    has_more: bool = False
    
    # Conversation context
    conversation_title: Optional[str] = None
    system_prompt: Optional[str] = None


class ChatSearchRequest(BaseModel):
    """Request for searching chat history."""
    
    query: str = Field(..., min_length=1, max_length=500)
    conversation_ids: Optional[List[str]] = None
    
    # Search filters
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    message_roles: Optional[List[MessageRole]] = None
    
    # Search configuration
    limit: int = Field(default=20, ge=1, le=100)
    include_context: bool = Field(default=True)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class ChatSearchResult(BaseModel):
    """Individual search result."""
    
    conversation_id: str
    message: ChatMessage
    similarity_score: float
    
    # Context
    conversation_title: Optional[str] = None
    surrounding_messages: Optional[List[ChatMessage]] = None


class ChatSearchResponse(BaseResponse):
    """Chat search response."""
    
    results: List[ChatSearchResult]
    total_results: int
    search_time: float
    
    # Search metadata
    query: str
    filters_applied: Dict[str, Any]


class ConversationSummary(BaseModel):
    """Conversation summary for list views."""
    
    id: str
    title: str
    message_count: int
    last_message_at: Optional[datetime] = None
    last_message_preview: Optional[str] = None
    
    # Quick stats
    total_tokens: Optional[int] = None
    estimated_cost: Optional[float] = None
    
    # Metadata
    tags: List[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None


class ModelInfo(BaseModel):
    """Information about available AI models."""
    
    provider: ModelProvider
    model_id: str
    display_name: str
    description: Optional[str] = None
    
    # Capabilities
    max_tokens: int
    supports_streaming: bool = True
    supports_function_calling: bool = False
    
    # Pricing (per 1K tokens)
    input_cost: Optional[float] = None
    output_cost: Optional[float] = None
    
    # Status
    available: bool = True
    rate_limit: Optional[Dict[str, Any]] = None


class ChatStats(BaseModel):
    """Chat statistics and analytics."""
    
    total_conversations: int
    total_messages: int
    total_tokens: int
    
    # Provider usage
    provider_usage: Dict[ModelProvider, int]
    model_usage: Dict[str, int]
    
    # Time-based stats
    messages_today: int
    messages_this_week: int
    messages_this_month: int
    
    # Performance
    average_response_time: float
    rag_usage_rate: float
    
    # Costs
    estimated_total_cost: Optional[float] = None
    cost_by_provider: Optional[Dict[ModelProvider, float]] = None