# 01-1: Chat API Backend - Streaming & RAG Integration

## Objective
Implement the core chat functionality in FastAPI, migrating the conversational AI logic from Streamlit's `sections/vault.py` while adding streaming capabilities, WebSocket support, and improved RAG integration.

## Prerequisites
- Backend core structure completed (00-2)
- Frontend foundation setup (00-3)
- Original vault.py functionality understood

## Implementation Steps

### 1. Chat Models and Types
- Create Pydantic models for chat messages and conversations
- Define request/response schemas for chat endpoints
- Implement conversation state models
- Create streaming response types

### 2. Chat Service Layer
- Migrate core chat logic from `sections/vault.py`
- Implement conversation management
- Create context retrieval integration
- Add message history persistence
- Implement streaming response generation

### 3. Chat API Endpoints
- Create REST endpoints for chat operations
- Implement WebSocket endpoint for real-time streaming
- Add conversation CRUD operations
- Create context injection endpoints
- Implement message search and filtering

### 4. RAG Integration Enhancement
- Adapt existing retriever logic for FastAPI
- Implement context caching for performance
- Add relevance scoring and filtering
- Create context visualization endpoints
- Implement multi-document context assembly

### 5. Streaming and Real-time Features
- Implement Server-Sent Events (SSE) for streaming
- Create WebSocket handlers for real-time chat
- Add typing indicators and presence
- Implement message queuing for reliability
- Add connection state management

## Files to Create

### Chat Models
1. `backend/models/chat.py` - Chat message and conversation models
2. `backend/models/streaming.py` - Streaming response models
3. `backend/schemas/chat.py` - Request/response schemas

### Core Chat Service
4. `backend/core/chat_service.py` - Main chat business logic
5. `backend/core/conversation_manager.py` - Conversation state management
6. `backend/core/streaming_service.py` - Streaming response handling

### Enhanced RAG Components
7. `backend/core/rag_service.py` - Enhanced RAG implementation
8. `backend/core/context_manager.py` - Context assembly and caching
9. `backend/utils/vector_search.py` - Vector search optimizations

### API Implementation
10. `backend/api/chat.py` - Chat REST endpoints
11. `backend/api/streaming.py` - Streaming and WebSocket endpoints
12. `backend/api/conversations.py` - Conversation management endpoints

### Database Integration
13. `backend/db/conversation_store.py` - Conversation persistence
14. `backend/db/message_store.py` - Message storage and retrieval
15. `backend/db/context_cache.py` - Context caching layer

## Key Features to Implement

### 1. Enhanced Chat Models
```python
# backend/models/chat.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    id: str = Field(..., description="Unique message identifier")
    conversation_id: str
    role: MessageRole
    content: str
    context: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Conversation(BaseModel):
    id: str
    title: Optional[str] = None
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

### 2. Streaming Response System
```python
# backend/core/streaming_service.py
import asyncio
from typing import AsyncGenerator
from fastapi.responses import StreamingResponse

class StreamingChatService:
    async def stream_response(
        self, 
        message: str, 
        conversation_id: str
    ) -> AsyncGenerator[str, None]:
        # Implement streaming logic
        async for chunk in self.llm_client.generate_stream(message):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
    
    def create_sse_response(self, generator: AsyncGenerator) -> StreamingResponse:
        return StreamingResponse(
            generator,
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
```

### 3. Enhanced RAG Service
```python
# backend/core/rag_service.py
from typing import List, Optional
from backend.utils.retriever import ContextRetriever
from backend.models.chat import ChatMessage

class RAGService:
    def __init__(self, retriever: ContextRetriever):
        self.retriever = retriever
        self.context_cache = {}
    
    async def get_enhanced_context(
        self, 
        query: str,
        conversation_history: List[ChatMessage],
        max_context_length: int = 4000
    ) -> str:
        # Enhanced context retrieval with conversation awareness
        pass
    
    async def get_relevant_documents(
        self, 
        query: str, 
        filters: Optional[Dict] = None
    ) -> List[RetrievedDocument]:
        # Document retrieval with filtering
        pass
```

### 4. WebSocket Chat Handler
```python
# backend/api/websockets.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, conversation_id: str):
        await websocket.accept()
        self.active_connections[conversation_id] = websocket
    
    async def disconnect(self, conversation_id: str):
        self.active_connections.pop(conversation_id, None)
    
    async def send_message(self, conversation_id: str, message: dict):
        websocket = self.active_connections.get(conversation_id)
        if websocket:
            await websocket.send_json(message)

@router.websocket("/chat/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    await manager.connect(websocket, conversation_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Process message and stream response
    except WebSocketDisconnect:
        await manager.disconnect(conversation_id)
```

## API Endpoints to Implement

### REST Endpoints
```python
# POST /api/chat/send - Send message and get response
# GET /api/chat/conversations - List user conversations
# GET /api/chat/conversations/{id} - Get conversation details
# POST /api/chat/conversations - Create new conversation
# DELETE /api/chat/conversations/{id} - Delete conversation
# GET /api/chat/conversations/{id}/messages - Get conversation messages
# POST /api/chat/conversations/{id}/context - Add context to conversation
# GET /api/chat/search - Search messages across conversations
```

### Streaming Endpoints
```python
# GET /api/chat/stream/{conversation_id} - SSE streaming endpoint
# WebSocket /api/ws/chat/{conversation_id} - Real-time chat WebSocket
```

## Migration Strategy from Streamlit

### 1. Vault Class Migration
```python
# OLD: sections/vault.py
class Vault:
    def __init__(self, config: PipelineConfig):
        self.config = replace_api_keys(config)
        # ... initialization

# NEW: backend/core/chat_service.py
class ChatService:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.conversation_manager = ConversationManager()
        # ... enhanced initialization
```

### 2. Message Handling Migration
```python
# OLD: Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# NEW: Database-backed conversation management
async def get_conversation(conversation_id: str) -> Conversation:
    return await self.conversation_store.get(conversation_id)
```

### 3. Response Generation Migration
```python
# OLD: Streamlit streaming display
async for chunk in await self.llm.generate(messages, stream=True):
    response += chunk
    resp_container.markdown(response)

# NEW: FastAPI streaming response
async def stream_chat_response(message: str) -> AsyncGenerator[str, None]:
    async for chunk in await self.llm.generate(messages, stream=True):
        yield json.dumps({"type": "chunk", "content": chunk})
```

## Performance Optimizations

### 1. Context Caching
- Implement Redis-based context caching
- Cache vector search results
- Optimize context assembly for repeated queries

### 2. Connection Management
- Implement connection pooling for database
- Add WebSocket connection limits
- Implement graceful degradation for high load

### 3. Async Optimization
- Use async/await throughout the pipeline
- Implement concurrent context retrieval
- Add background task processing for heavy operations

## Success Criteria
- [ ] Chat API endpoints respond correctly
- [ ] Streaming responses work via SSE and WebSocket
- [ ] RAG context retrieval functions properly
- [ ] Conversation persistence works
- [ ] Message history is maintained
- [ ] Context caching improves performance
- [ ] WebSocket connections are stable
- [ ] All original Streamlit chat functionality is preserved
- [ ] Response streaming is smooth and responsive
- [ ] Error handling is robust

## Testing Strategy
- Unit tests for chat service logic
- Integration tests for API endpoints
- WebSocket connection testing
- Streaming response validation
- RAG context quality testing
- Performance testing for concurrent users

## Dependencies
```python
# Additional backend dependencies
websockets>=11.0.0
redis>=5.0.0
python-socketio>=5.9.0
sse-starlette>=1.6.0
```

## Estimated Time
6-8 hours

## Next Steps
After completion, proceed to `01-2-plan-chat-frontend-ui.md`