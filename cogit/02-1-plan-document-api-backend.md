# 02-1: Document API Backend - File Management & Processing

## Objective
Implement comprehensive document management API in FastAPI, migrating and enhancing the document processing functionality from Streamlit's `sections/data.py` with improved file handling, batch processing, and progress tracking.

## Prerequisites
- Backend core structure completed (00-2)
- Chat API backend completed (01-1)
- Original data.py functionality understood

## Implementation Steps

### 1. Document Models and Schemas
- Create document metadata models
- Define file upload schemas and validation
- Implement processing status tracking models
- Create batch operation models
- Design document collection schemas

### 2. File Upload and Storage
- Implement secure file upload endpoints
- Create file validation and sanitization
- Set up temporary and permanent storage
- Add file deduplication logic
- Implement chunked upload for large files

### 3. Document Processing Pipeline
- Migrate document loading logic from `utils/loader.py`
- Enhance processing with progress tracking
- Implement background task processing
- Add document format detection and conversion
- Create processing queue management

### 4. Vector Database Integration
- Enhance Qdrant integration for document indexing
- Implement collection management
- Add document versioning support
- Create index optimization routines
- Implement search and retrieval enhancements

### 5. Document Management API
- Create CRUD endpoints for documents
- Implement batch processing endpoints
- Add document search and filtering
- Create processing status endpoints
- Implement document preview and download

## Files to Create

### Document Models
1. `backend/models/documents.py` - Document metadata and file models
2. `backend/models/processing.py` - Processing status and job models
3. `backend/schemas/documents.py` - Request/response schemas for documents
4. `backend/schemas/upload.py` - File upload and processing schemas

### Core Document Services
5. `backend/core/document_service.py` - Main document management logic
6. `backend/core/file_processor.py` - File processing and conversion
7. `backend/core/indexing_service.py` - Document indexing and vector operations
8. `backend/core/storage_service.py` - File storage management

### Background Processing
9. `backend/core/task_manager.py` - Background task coordination
10. `backend/core/processing_queue.py` - Document processing queue
11. `backend/workers/document_worker.py` - Background processing worker

### API Implementation
12. `backend/api/documents.py` - Document CRUD endpoints
13. `backend/api/upload.py` - File upload endpoints
14. `backend/api/processing.py` - Processing status and management
15. `backend/api/collections.py` - Document collection management

### Storage and Database
16. `backend/storage/file_manager.py` - File system operations
17. `backend/storage/document_store.py` - Document metadata persistence
18. `backend/db/document_repository.py` - Database operations for documents

### Utilities
19. `backend/utils/file_utils.py` - File handling utilities
20. `backend/utils/document_parser.py` - Document parsing and extraction
21. `backend/utils/validation.py` - File validation and security

## Key Features Implementation

### 1. Enhanced Document Models
```python
# backend/models/documents.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"
    DELETED = "deleted"

class DocumentType(str, Enum):
    PDF = "pdf"
    TEXT = "text"
    WORD = "word"
    MARKDOWN = "markdown"
    HTML = "html"
    IMAGE = "image"

class DocumentMetadata(BaseModel):
    id: str = Field(..., description="Unique document identifier")
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    document_type: DocumentType
    status: DocumentStatus = DocumentStatus.UPLOADED
    checksum: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
class ProcessedDocument(BaseModel):
    metadata: DocumentMetadata
    content: str
    chunks: List[str] = Field(default_factory=list)
    embeddings_generated: bool = False
    vector_ids: List[str] = Field(default_factory=list)
    processing_metrics: Dict[str, Any] = Field(default_factory=dict)

class DocumentCollection(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    document_count: int = 0
    total_size: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. File Upload Service with Validation
```python
# backend/core/storage_service.py
import aiofiles
import hashlib
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException

class StorageService:
    def __init__(self, upload_dir: Path, max_file_size: int = 100 * 1024 * 1024):
        self.upload_dir = upload_dir
        self.max_file_size = max_file_size
        self.allowed_types = {
            'application/pdf',
            'text/plain',
            'text/markdown',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/html',
            'image/png',
            'image/jpeg'
        }
    
    async def validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file for security and constraints."""
        if file.content_type not in self.allowed_types:
            raise HTTPException(400, f"File type {file.content_type} not allowed")
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset position
        
        if size > self.max_file_size:
            raise HTTPException(400, f"File too large: {size} bytes")
    
    async def save_file(self, file: UploadFile, document_id: str) -> Path:
        """Save uploaded file with security measures."""
        await self.validate_file(file)
        
        # Generate secure filename
        file_extension = Path(file.filename).suffix.lower()
        secure_filename = f"{document_id}{file_extension}"
        file_path = self.upload_dir / secure_filename
        
        # Save file with streaming to handle large files
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return file_path
    
    async def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum for file integrity."""
        sha256_hash = hashlib.sha256()
        async with aiofiles.open(file_path, "rb") as f:
            async for chunk in self._read_chunks(f):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    async def _read_chunks(self, file, chunk_size: int = 8192):
        """Read file in chunks for memory efficiency."""
        while chunk := await file.read(chunk_size):
            yield chunk
```

### 3. Enhanced Document Processing Service
```python
# backend/core/document_service.py
import uuid
from typing import List, Optional
from fastapi import UploadFile, BackgroundTasks
from backend.models.documents import DocumentMetadata, ProcessedDocument, DocumentStatus

class DocumentService:
    def __init__(self, storage_service, file_processor, indexing_service):
        self.storage = storage_service
        self.processor = file_processor
        self.indexer = indexing_service
        self.document_store = DocumentStore()
    
    async def upload_document(
        self, 
        file: UploadFile, 
        collection_id: Optional[str] = None,
        background_tasks: BackgroundTasks = None
    ) -> DocumentMetadata:
        """Upload and queue document for processing."""
        
        # Generate document ID and save file
        document_id = str(uuid.uuid4())
        file_path = await self.storage.save_file(file, document_id)
        checksum = await self.storage.calculate_checksum(file_path)
        
        # Check for duplicates
        existing_doc = await self.document_store.find_by_checksum(checksum)
        if existing_doc:
            # Return existing document instead of duplicating
            return existing_doc.metadata
        
        # Create document metadata
        metadata = DocumentMetadata(
            id=document_id,
            filename=file_path.name,
            original_filename=file.filename,
            content_type=file.content_type,
            file_size=file_path.stat().st_size,
            document_type=self._detect_document_type(file.content_type),
            checksum=checksum,
            status=DocumentStatus.UPLOADED
        )
        
        # Save metadata
        await self.document_store.save_metadata(metadata)
        
        # Queue for background processing
        if background_tasks:
            background_tasks.add_task(self.process_document, document_id)
        
        return metadata
    
    async def process_document(self, document_id: str) -> ProcessedDocument:
        """Process document: extract text, chunk, and index."""
        
        # Update status to processing
        await self.document_store.update_status(document_id, DocumentStatus.PROCESSING)
        
        try:
            # Load document metadata
            metadata = await self.document_store.get_metadata(document_id)
            file_path = self.storage.upload_dir / metadata.filename
            
            # Extract text content
            content = await self.processor.extract_text(file_path, metadata.document_type)
            
            # Chunk document for vector storage
            chunks = await self.processor.chunk_document(content)
            
            # Generate embeddings and index
            vector_ids = await self.indexer.index_document_chunks(
                document_id, chunks, metadata
            )
            
            # Create processed document
            processed_doc = ProcessedDocument(
                metadata=metadata,
                content=content,
                chunks=chunks,
                embeddings_generated=True,
                vector_ids=vector_ids,
                processing_metrics={
                    "chunk_count": len(chunks),
                    "content_length": len(content),
                    "processing_time": time.time() - start_time
                }
            )
            
            # Update status and save processed document
            metadata.status = DocumentStatus.INDEXED
            metadata.processed_at = datetime.utcnow()
            await self.document_store.save_processed_document(processed_doc)
            
            return processed_doc
            
        except Exception as e:
            # Update status to failed
            await self.document_store.update_status(document_id, DocumentStatus.FAILED)
            raise ProcessingError(f"Failed to process document {document_id}: {str(e)}")
    
    async def batch_upload(
        self, 
        files: List[UploadFile],
        collection_id: Optional[str] = None
    ) -> List[DocumentMetadata]:
        """Upload multiple documents and process in batch."""
        uploaded_docs = []
        
        for file in files:
            try:
                metadata = await self.upload_document(file, collection_id)
                uploaded_docs.append(metadata)
            except Exception as e:
                # Log error but continue with other files
                logger.error(f"Failed to upload {file.filename}: {str(e)}")
        
        # Start batch processing
        await self.start_batch_processing([doc.id for doc in uploaded_docs])
        
        return uploaded_docs
```

### 4. Background Processing with Progress Tracking
```python
# backend/core/processing_queue.py
import asyncio
from typing import Dict, List
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessingQueue:
    def __init__(self, max_concurrent_tasks: int = 3):
        self.max_concurrent = max_concurrent_tasks
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_status: Dict[str, TaskStatus] = {}
        self.task_progress: Dict[str, float] = {}
        self.pending_queue: List[str] = []
    
    async def add_task(self, task_id: str, coro) -> None:
        """Add task to processing queue."""
        if len(self.active_tasks) < self.max_concurrent:
            await self._start_task(task_id, coro)
        else:
            self.pending_queue.append(task_id)
            self.task_status[task_id] = TaskStatus.PENDING
    
    async def _start_task(self, task_id: str, coro) -> None:
        """Start processing task."""
        self.task_status[task_id] = TaskStatus.RUNNING
        self.task_progress[task_id] = 0.0
        
        task = asyncio.create_task(self._run_task(task_id, coro))
        self.active_tasks[task_id] = task
    
    async def _run_task(self, task_id: str, coro) -> None:
        """Run task with error handling and cleanup."""
        try:
            await coro
            self.task_status[task_id] = TaskStatus.COMPLETED
            self.task_progress[task_id] = 1.0
        except Exception as e:
            self.task_status[task_id] = TaskStatus.FAILED
            logger.error(f"Task {task_id} failed: {str(e)}")
        finally:
            # Cleanup and start next pending task
            self.active_tasks.pop(task_id, None)
            await self._start_next_pending_task()
    
    async def _start_next_pending_task(self) -> None:
        """Start next task from pending queue."""
        if self.pending_queue and len(self.active_tasks) < self.max_concurrent:
            next_task_id = self.pending_queue.pop(0)
            # Get the coroutine for this task and start it
            # This would need to be implemented based on your task storage
    
    def get_task_status(self, task_id: str) -> Dict:
        """Get current status and progress of a task."""
        return {
            "status": self.task_status.get(task_id, "unknown"),
            "progress": self.task_progress.get(task_id, 0.0)
        }
```

## API Endpoints Implementation

### Document Management Endpoints
```python
# backend/api/documents.py
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Query
from typing import List, Optional

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentMetadata)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    collection_id: Optional[str] = None
):
    """Upload a single document for processing."""
    return await document_service.upload_document(file, collection_id, background_tasks)

@router.post("/batch-upload", response_model=List[DocumentMetadata])
async def batch_upload_documents(
    files: List[UploadFile] = File(...),
    collection_id: Optional[str] = None
):
    """Upload multiple documents for batch processing."""
    return await document_service.batch_upload(files, collection_id)

@router.get("/", response_model=List[DocumentMetadata])
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[DocumentStatus] = None,
    collection_id: Optional[str] = None
):
    """List documents with filtering and pagination."""
    return await document_service.list_documents(skip, limit, status, collection_id)

@router.get("/{document_id}", response_model=ProcessedDocument)
async def get_document(document_id: str):
    """Get detailed document information."""
    return await document_service.get_document(document_id)

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete document and all associated data."""
    return await document_service.delete_document(document_id)

@router.get("/{document_id}/status")
async def get_processing_status(document_id: str):
    """Get current processing status and progress."""
    return await document_service.get_processing_status(document_id)

@router.post("/{document_id}/reprocess")
async def reprocess_document(document_id: str, background_tasks: BackgroundTasks):
    """Reprocess an existing document."""
    background_tasks.add_task(document_service.process_document, document_id)
    return {"message": "Document queued for reprocessing"}
```

## Migration Strategy from Streamlit

### 1. DataLoader Class Migration
```python
# OLD: sections/data.py
class DataLoader:
    async def load_file(self):
        uploaded_file = st.file_uploader("Choose a file to upload")
        if st.button("load file") and uploaded_file is not None:
            # ... processing logic

# NEW: Enhanced API-based approach
# Multiple endpoints for different upload scenarios
# Background processing with progress tracking
# Better error handling and validation
```

### 2. Enhanced Error Handling
```python
# OLD: Basic Streamlit error display
except Exception as e:
    st.error("Failed to load file")

# NEW: Structured error responses
except ValidationError as e:
    raise HTTPException(400, detail=f"Validation error: {str(e)}")
except ProcessingError as e:
    raise HTTPException(500, detail=f"Processing failed: {str(e)}")
```

## Success Criteria
- [ ] File upload endpoints accept and validate files correctly
- [ ] Document processing works in background with progress tracking
- [ ] Batch upload handles multiple files efficiently
- [ ] Document indexing integrates properly with vector database
- [ ] File deduplication prevents duplicate storage
- [ ] Processing status endpoints provide real-time updates
- [ ] Document search and filtering work correctly
- [ ] All original Streamlit data loading functionality is preserved
- [ ] Large file uploads work without timeout issues
- [ ] Error handling is comprehensive and informative

## Performance Optimizations
- Implement chunked file uploads for large files
- Use background processing to avoid blocking requests
- Add file compression for storage efficiency
- Implement caching for frequently accessed documents
- Use connection pooling for database operations

## Security Considerations
- Validate file types and sizes to prevent attacks
- Implement virus scanning for uploaded files
- Use secure file naming to prevent directory traversal
- Implement rate limiting for upload endpoints
- Add authentication and authorization checks

## Estimated Time
8-10 hours

## Next Steps
After completion, proceed to `02-2-plan-document-frontend-ui.md`