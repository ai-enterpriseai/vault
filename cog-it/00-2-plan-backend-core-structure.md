# 00-2: Backend Core Structure and API Foundation

## Objective
Establish the FastAPI backend architecture, create core API structure, and migrate essential utilities from the existing Streamlit application.

## Prerequisites
- Project setup completed (00-1)
- Basic FastAPI app running

## Implementation Steps

### 1. API Router Structure
- Create modular router system in `api/` directory
- Set up base router with health check endpoints
- Implement proper error handling middleware
- Add CORS configuration for frontend integration

### 2. Core Business Logic Migration
- Move existing utilities from `../utils/` to `backend/utils/`
- Adapt configuration management for FastAPI
- Create service layer for business logic separation
- Implement dependency injection pattern

### 3. Database and Storage Setup
- Configure Qdrant vector database connection
- Set up document storage handling
- Create database initialization scripts
- Implement connection pooling and health checks

### 4. Authentication Foundation
- Create basic authentication middleware
- Set up JWT token handling (preparation for future auth)
- Implement request logging and monitoring
- Add rate limiting middleware

### 5. Configuration Management
- Migrate existing YAML configuration system
- Create Pydantic settings models
- Set up environment-specific configurations
- Implement secrets management

## Files to Create

### API Structure
1. `backend/api/__init__.py`
2. `backend/api/base.py` - Base router with health checks
3. `backend/api/chat.py` - Chat endpoints (placeholder)
4. `backend/api/documents.py` - Document endpoints (placeholder)
5. `backend/api/sequences.py` - Sequence endpoints (placeholder)
6. `backend/api/websockets.py` - WebSocket handlers (placeholder)

### Core Services
7. `backend/core/__init__.py`
8. `backend/core/config.py` - Configuration management
9. `backend/core/database.py` - Database connections
10. `backend/core/exceptions.py` - Custom exception classes
11. `backend/core/middleware.py` - Custom middleware
12. `backend/core/dependencies.py` - Dependency injection

### Utilities Migration
13. `backend/utils/__init__.py`
14. `backend/utils/logging.py` - Migrated from existing
15. `backend/utils/configs.py` - Adapted configuration utilities
16. `backend/utils/loader.py` - Document loader (adapted)
17. `backend/utils/retriever.py` - Context retriever (adapted)

### Models Foundation
18. `backend/models/__init__.py`
19. `backend/models/base.py` - Base Pydantic models
20. `backend/models/config.py` - Configuration models

## Key Adaptations Required

### Configuration System
```python
# OLD: Streamlit secrets
st.secrets['API_KEY']

# NEW: Pydantic settings
from core.config import settings
settings.api_key
```

### Error Handling
```python
# OLD: Streamlit error display
st.error("Error message")

# NEW: FastAPI HTTPException
raise HTTPException(status_code=400, detail="Error message")
```

### Async Pattern Consistency
```python
# Ensure all functions are properly async
async def process_document(file: UploadFile) -> ProcessedDocument:
    # Implementation
```

## Success Criteria
- [ ] FastAPI app starts with all routers registered
- [ ] Health check endpoint returns system status
- [ ] Configuration loads from environment and YAML
- [ ] Database connection establishes successfully
- [ ] All utilities are successfully migrated and functional
- [ ] Error handling middleware catches and formats exceptions
- [ ] Logging works across all modules

## Testing Strategy
- Create basic unit tests for core utilities
- Test configuration loading with different environments
- Verify database connection and health checks
- Test error handling middleware

## Dependencies
```python
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.4.0
pydantic-settings>=2.0.0
python-multipart>=0.0.6
aiofiles>=23.2.0
```

## Estimated Time
4-5 hours

## Next Steps
After completion, proceed to `00-3-plan-frontend-foundation.md`