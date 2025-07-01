# 03-1: Sequences API Backend - Workflow Automation & Blueprints

## Objective
Implement the workflow automation API in FastAPI, migrating and enhancing the sequence execution functionality from Streamlit's `sections/sequences.py` with improved blueprint management, real-time progress tracking, and advanced workflow features.

## Prerequisites
- Backend core structure completed (00-2)
- Chat and Document APIs implemented (01-1, 02-1)
- Original sequences.py functionality understood
- Blueprint files analyzed (`blueprints/` directory)

## Implementation Steps

### 1. Sequence Models and Blueprint System
- Create sequence execution models and schemas
- Implement blueprint template management
- Design workflow state tracking models
- Create result storage and comparison models
- Define sequence scheduling and automation models

### 2. Blueprint Management Service
- Migrate blueprint loading from `blueprints/` directory
- Create dynamic blueprint parsing system
- Implement template variable substitution
- Add blueprint validation and schema checking
- Create blueprint versioning and updates

### 3. Sequence Execution Engine
- Migrate SequenceRunner logic to FastAPI
- Implement async sequence execution
- Create progress tracking and real-time updates
- Add execution context management
- Implement error handling and recovery

### 4. Enhanced Workflow Features
- Add sequence chaining and dependencies
- Implement conditional logic and branching
- Create batch execution capabilities
- Add scheduled execution support
- Implement result comparison and analysis

### 5. Real-time Progress and WebSocket Integration
- Create WebSocket endpoints for real-time progress
- Implement execution monitoring and logging
- Add cancellation and pause/resume functionality
- Create execution queue management
- Add resource usage tracking

## Files to Create

### Sequence Models
1. `backend/models/sequences.py` - Sequence execution and blueprint models
2. `backend/models/workflows.py` - Advanced workflow models
3. `backend/schemas/sequences.py` - Request/response schemas
4. `backend/schemas/blueprints.py` - Blueprint template schemas

### Core Sequence Services
5. `backend/core/sequence_service.py` - Main sequence execution logic
6. `backend/core/blueprint_manager.py` - Blueprint loading and management
7. `backend/core/workflow_engine.py` - Advanced workflow execution
8. `backend/core/execution_tracker.py` - Progress tracking and monitoring

### Blueprint System
9. `backend/blueprints/blueprint_loader.py` - Dynamic blueprint loading
10. `backend/blueprints/template_processor.py` - Template variable processing
11. `backend/blueprints/validator.py` - Blueprint validation
12. `backend/blueprints/registry.py` - Blueprint registry and versioning

### API Implementation
13. `backend/api/sequences.py` - Sequence execution endpoints
14. `backend/api/blueprints.py` - Blueprint management endpoints
15. `backend/api/workflows.py` - Advanced workflow endpoints
16. `backend/api/sequence_websockets.py` - Real-time progress WebSockets

### Execution and Storage
17. `backend/execution/sequence_executor.py` - Core execution engine
18. `backend/execution/result_processor.py` - Result processing and storage
19. `backend/storage/sequence_store.py` - Sequence result persistence
20. `backend/workers/sequence_worker.py` - Background sequence processing

## Key Features Implementation

### 1. Enhanced Sequence Models
```python
# backend/models/sequences.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class SequenceStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class BlueprintType(str, Enum):
    CONTRACT_CHECK = "contractcheck"
    SOLVER = "solver"
    TESTER = "tester"
    GENERATOR = "generator"
    ADWORDS = "adwordscampaign"
    CALENDAR = "contentcalendar"

class SequenceExecution(BaseModel):
    id: str = Field(..., description="Unique execution identifier")
    blueprint_id: str
    blueprint_version: str = "latest"
    status: SequenceStatus = SequenceStatus.PENDING
    input_variables: Dict[str, Any] = Field(default_factory=dict)
    results: List[Dict[str, Any]] = Field(default_factory=list)
    progress: float = Field(0.0, ge=0.0, le=1.0)
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    execution_metrics: Dict[str, Any] = Field(default_factory=dict)

class BlueprintTemplate(BaseModel):
    id: str
    name: str
    description: str
    blueprint_type: BlueprintType
    template_content: str
    input_schema: Dict[str, Any]
    version: str = "1.0.0"
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WorkflowDefinition(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    sequences: List[str]  # Sequence IDs in execution order
    dependencies: Dict[str, List[str]] = Field(default_factory=dict)
    conditional_logic: Dict[str, Any] = Field(default_factory=dict)
    schedule: Optional[str] = None  # Cron expression
    is_active: bool = True
```

### 2. Blueprint Manager Service
```python
# backend/core/blueprint_manager.py
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from backend.models.sequences import BlueprintTemplate, BlueprintType

class BlueprintManager:
    def __init__(self, blueprints_dir: Path):
        self.blueprints_dir = blueprints_dir
        self.templates: Dict[str, BlueprintTemplate] = {}
        self.loaded_blueprints = set()
    
    async def load_all_blueprints(self) -> None:
        """Load all blueprint templates from filesystem."""
        for blueprint_file in self.blueprints_dir.glob("*.md"):
            await self.load_blueprint(blueprint_file)
    
    async def load_blueprint(self, file_path: Path) -> BlueprintTemplate:
        """Load a single blueprint template."""
        content = file_path.read_text(encoding='utf-8')
        
        # Parse blueprint content (Markdown with YAML frontmatter)
        template = await self._parse_blueprint_content(content, file_path.stem)
        
        self.templates[template.id] = template
        self.loaded_blueprints.add(template.id)
        
        return template
    
    async def _parse_blueprint_content(self, content: str, filename: str) -> BlueprintTemplate:
        """Parse blueprint Markdown content and extract metadata."""
        
        # Extract blueprint type from filename
        blueprint_type = self._get_blueprint_type(filename)
        
        # Parse input schema from content
        input_schema = self._extract_input_schema(content)
        
        return BlueprintTemplate(
            id=filename,
            name=filename.replace('_', ' ').title(),
            description=f"Generated from {filename}.md",
            blueprint_type=blueprint_type,
            template_content=content,
            input_schema=input_schema,
            version="1.0.0"
        )
    
    def _get_blueprint_type(self, filename: str) -> BlueprintType:
        """Map filename to blueprint type."""
        type_mapping = {
            'contractcheck': BlueprintType.CONTRACT_CHECK,
            'solver': BlueprintType.SOLVER,
            'tester': BlueprintType.TESTER,
            'generator': BlueprintType.GENERATOR,
            'adwordscampaign': BlueprintType.ADWORDS,
            'contentcalendar': BlueprintType.CALENDAR
        }
        return type_mapping.get(filename, BlueprintType.GENERATOR)
    
    def _extract_input_schema(self, content: str) -> Dict[str, Any]:
        """Extract input variable schema from blueprint content."""
        # Look for placeholder variables like {variable_name}
        import re
        variables = re.findall(r'\{(\w+)\}', content)
        
        schema = {
            "type": "object",
            "properties": {},
            "required": list(set(variables))
        }
        
        for var in set(variables):
            schema["properties"][var] = {
                "type": "string",
                "description": f"Input variable: {var}"
            }
        
        return schema
    
    async def get_blueprint(self, blueprint_id: str) -> Optional[BlueprintTemplate]:
        """Get blueprint template by ID."""
        return self.templates.get(blueprint_id)
    
    async def list_blueprints(self, blueprint_type: Optional[BlueprintType] = None) -> List[BlueprintTemplate]:
        """List all available blueprints, optionally filtered by type."""
        blueprints = list(self.templates.values())
        
        if blueprint_type:
            blueprints = [bp for bp in blueprints if bp.blueprint_type == blueprint_type]
        
        return blueprints
    
    async def validate_blueprint(self, blueprint_id: str, input_variables: Dict[str, Any]) -> bool:
        """Validate input variables against blueprint schema."""
        blueprint = await self.get_blueprint(blueprint_id)
        if not blueprint:
            raise ValueError(f"Blueprint {blueprint_id} not found")
        
        # Validate against input schema
        # This would use jsonschema or similar for proper validation
        required_vars = blueprint.input_schema.get("required", [])
        provided_vars = set(input_variables.keys())
        missing_vars = set(required_vars) - provided_vars
        
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        return True
```

### 3. Enhanced Sequence Execution Service
```python
# backend/core/sequence_service.py
import uuid
import asyncio
from typing import List, Dict, Any, Optional
from backend.models.sequences import SequenceExecution, SequenceStatus
from backend.core.blueprint_manager import BlueprintManager

class SequenceService:
    def __init__(self, blueprint_manager: BlueprintManager, sequencer_runner):
        self.blueprint_manager = blueprint_manager
        self.sequencer_runner = sequencer_runner
        self.active_executions: Dict[str, SequenceExecution] = {}
        self.execution_store = SequenceExecutionStore()
    
    async def execute_sequence(
        self,
        blueprint_id: str,
        input_variables: Dict[str, Any],
        models: List[str] = ["gpt-4o-2024-08-06"],
        num_runs: int = 1
    ) -> SequenceExecution:
        """Execute a sequence with the given parameters."""
        
        # Validate blueprint and inputs
        await self.blueprint_manager.validate_blueprint(blueprint_id, input_variables)
        blueprint = await self.blueprint_manager.get_blueprint(blueprint_id)
        
        # Create execution record
        execution = SequenceExecution(
            id=str(uuid.uuid4()),
            blueprint_id=blueprint_id,
            blueprint_version=blueprint.version,
            input_variables=input_variables,
            status=SequenceStatus.PENDING
        )
        
        # Store execution
        await self.execution_store.save_execution(execution)
        self.active_executions[execution.id] = execution
        
        # Start background execution
        asyncio.create_task(self._run_sequence_background(execution, models, num_runs))
        
        return execution
    
    async def _run_sequence_background(
        self,
        execution: SequenceExecution,
        models: List[str],
        num_runs: int
    ) -> None:
        """Run sequence in background with progress tracking."""
        
        try:
            # Update status to running
            execution.status = SequenceStatus.RUNNING
            execution.started_at = datetime.utcnow()
            await self.execution_store.update_execution(execution)
            
            # Get blueprint template
            blueprint = await self.blueprint_manager.get_blueprint(execution.blueprint_id)
            sequence_file = self.blueprint_manager.blueprints_dir / f"{blueprint.id}.md"
            
            # Execute sequence with progress tracking
            results = []
            total_steps = num_runs * len(models)
            completed_steps = 0
            
            # Run sequence using existing sequencer
            async for batch_results in self.sequencer_runner.run_sequence(
                sequence_file=sequence_file,
                models=models,
                num_runs=num_runs,
                **execution.input_variables
            ):
                # Process results and update progress
                for result in batch_results:
                    results.append({
                        "model": result.model if hasattr(result, 'model') else 'unknown',
                        "response": result.response,
                        "metadata": getattr(result, 'metadata', {}),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                completed_steps += len(batch_results)
                execution.progress = completed_steps / total_steps
                
                # Update execution with results and progress
                execution.results = results
                await self.execution_store.update_execution(execution)
                
                # Notify progress via WebSocket
                await self._notify_progress(execution.id, execution.progress, batch_results)
            
            # Mark as completed
            execution.status = SequenceStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.progress = 1.0
            execution.execution_metrics = {
                "total_results": len(results),
                "execution_time": (execution.completed_at - execution.started_at).total_seconds(),
                "models_used": models,
                "num_runs": num_runs
            }
            
        except Exception as e:
            # Mark as failed
            execution.status = SequenceStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            
        finally:
            # Update final state and cleanup
            await self.execution_store.update_execution(execution)
            self.active_executions.pop(execution.id, None)
    
    async def _notify_progress(self, execution_id: str, progress: float, results: List) -> None:
        """Notify clients of execution progress via WebSocket."""
        # This would integrate with WebSocket manager
        message = {
            "type": "progress",
            "execution_id": execution_id,
            "progress": progress,
            "latest_results": [r.response for r in results[-3:]]  # Last 3 results
        }
        await self.websocket_manager.broadcast_to_execution(execution_id, message)
    
    async def get_execution(self, execution_id: str) -> Optional[SequenceExecution]:
        """Get execution details by ID."""
        # Try active executions first
        if execution_id in self.active_executions:
            return self.active_executions[execution_id]
        
        # Fall back to storage
        return await self.execution_store.get_execution(execution_id)
    
    async def list_executions(
        self,
        status: Optional[SequenceStatus] = None,
        blueprint_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[SequenceExecution]:
        """List executions with filtering."""
        return await self.execution_store.list_executions(
            status=status,
            blueprint_id=blueprint_id,
            limit=limit,
            offset=offset
        )
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution."""
        execution = await self.get_execution(execution_id)
        if not execution or execution.status not in [SequenceStatus.PENDING, SequenceStatus.RUNNING]:
            return False
        
        execution.status = SequenceStatus.CANCELLED
        execution.completed_at = datetime.utcnow()
        await self.execution_store.update_execution(execution)
        
        # Remove from active executions
        self.active_executions.pop(execution_id, None)
        
        return True
```

### 4. WebSocket Progress Tracking
```python
# backend/api/sequence_websockets.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set

class SequenceWebSocketManager:
    def __init__(self):
        self.execution_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, execution_id: str):
        """Connect to sequence execution updates."""
        await websocket.accept()
        
        if execution_id not in self.execution_connections:
            self.execution_connections[execution_id] = set()
        
        self.execution_connections[execution_id].add(websocket)
    
    async def disconnect(self, websocket: WebSocket, execution_id: str):
        """Disconnect from sequence execution updates."""
        if execution_id in self.execution_connections:
            self.execution_connections[execution_id].discard(websocket)
            
            # Clean up empty connection sets
            if not self.execution_connections[execution_id]:
                del self.execution_connections[execution_id]
    
    async def broadcast_to_execution(self, execution_id: str, message: dict):
        """Broadcast message to all connections for an execution."""
        if execution_id not in self.execution_connections:
            return
        
        disconnected = set()
        for websocket in self.execution_connections[execution_id]:
            try:
                await websocket.send_json(message)
            except:
                disconnected.add(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            self.execution_connections[execution_id].discard(ws)

@router.websocket("/sequences/{execution_id}/progress")
async def sequence_progress_websocket(websocket: WebSocket, execution_id: str):
    """WebSocket endpoint for real-time sequence progress."""
    await manager.connect(websocket, execution_id)
    
    try:
        while True:
            # Keep connection alive and handle any client messages
            data = await websocket.receive_text()
            # Could handle pause/resume commands here
    except WebSocketDisconnect:
        await manager.disconnect(websocket, execution_id)
```

## API Endpoints Implementation

### Sequence Execution Endpoints
```python
# backend/api/sequences.py
from fastapi import APIRouter, BackgroundTasks, Query
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/api/sequences", tags=["sequences"])

@router.post("/execute", response_model=SequenceExecution)
async def execute_sequence(
    blueprint_id: str,
    input_variables: Dict[str, Any],
    models: List[str] = ["gpt-4o-2024-08-06"],
    num_runs: int = 1
):
    """Execute a sequence with given parameters."""
    return await sequence_service.execute_sequence(
        blueprint_id, input_variables, models, num_runs
    )

@router.get("/executions", response_model=List[SequenceExecution])
async def list_executions(
    status: Optional[SequenceStatus] = None,
    blueprint_id: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0)
):
    """List sequence executions with filtering."""
    return await sequence_service.list_executions(status, blueprint_id, limit, offset)

@router.get("/executions/{execution_id}", response_model=SequenceExecution)
async def get_execution(execution_id: str):
    """Get detailed execution information."""
    execution = await sequence_service.get_execution(execution_id)
    if not execution:
        raise HTTPException(404, "Execution not found")
    return execution

@router.post("/executions/{execution_id}/cancel")
async def cancel_execution(execution_id: str):
    """Cancel a running execution."""
    success = await sequence_service.cancel_execution(execution_id)
    if not success:
        raise HTTPException(400, "Cannot cancel execution")
    return {"message": "Execution cancelled"}

@router.get("/blueprints", response_model=List[BlueprintTemplate])
async def list_blueprints(blueprint_type: Optional[BlueprintType] = None):
    """List available blueprint templates."""
    return await blueprint_manager.list_blueprints(blueprint_type)

@router.get("/blueprints/{blueprint_id}", response_model=BlueprintTemplate)
async def get_blueprint(blueprint_id: str):
    """Get blueprint template details."""
    blueprint = await blueprint_manager.get_blueprint(blueprint_id)
    if not blueprint:
        raise HTTPException(404, "Blueprint not found")
    return blueprint
```

## Migration Strategy from Streamlit

### 1. Sequences Class Migration
```python
# OLD: sections/sequences.py
class Sequences:
    async def run_sequence_and_display(self, runner, sequence_file, models, placeholders):
        # UI-coupled execution logic

# NEW: Decoupled service architecture
# Separate execution logic from UI
# Real-time progress via WebSocket
# Better state management and persistence
```

### 2. Blueprint Management Enhancement
```python
# OLD: Static blueprint files
BLUEPRINT_DIR = Path(__file__).parent.parent / "blueprints"

# NEW: Dynamic blueprint management system
# Runtime loading and validation
# Version control and updates
# Schema validation and type checking
```

## Success Criteria
- [ ] All existing blueprint types execute correctly
- [ ] Real-time progress tracking works via WebSocket
- [ ] Sequence execution state is properly persisted
- [ ] Background processing handles multiple concurrent executions
- [ ] Blueprint validation prevents invalid inputs
- [ ] Execution cancellation works reliably
- [ ] All original Streamlit sequence functionality is preserved
- [ ] Error handling provides clear feedback
- [ ] Performance is acceptable for concurrent users
- [ ] WebSocket connections are stable during long executions

## Performance Considerations
- Implement execution queue to limit concurrent sequences
- Add resource usage monitoring and limits
- Use background workers for heavy processing
- Implement result caching for repeated executions
- Optimize WebSocket message frequency

## Security and Validation
- Validate blueprint content for security
- Sanitize user inputs in template variables
- Implement execution time limits
- Add resource usage quotas
- Validate model access permissions

## Estimated Time
10-12 hours

## Next Steps
After completion, proceed to `03-2-plan-sequences-frontend-ui.md`