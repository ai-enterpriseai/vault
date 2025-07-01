# 05-1: Integration Testing and System Validation

## Objective
Conduct comprehensive integration testing across all components of the migrated system, validate that all functionality from the original Streamlit application has been successfully preserved and enhanced, and ensure production readiness.

## Prerequisites
- All core implementation plans completed (00-1 through 04-1)
- Backend API fully functional
- Frontend components implemented
- Dashboard and analytics working

## Implementation Steps

### 1. Test Environment Setup
- Create isolated testing environments
- Set up test databases and vector stores
- Configure test API keys and services
- Implement test data fixtures and mocking
- Create automated testing pipelines

### 2. Backend Integration Testing
- Test API endpoint integration
- Validate database operations and migrations
- Test external service integrations (LLM APIs, Qdrant)
- Verify background task processing
- Test WebSocket connections and streaming

### 3. Frontend Integration Testing
- Test component integration and data flow
- Validate routing and navigation
- Test real-time features and WebSocket integration
- Verify responsive design across devices
- Test accessibility compliance

### 4. End-to-End Workflow Testing
- Test complete chat workflows
- Validate document upload and processing pipelines
- Test sequence execution from start to finish
- Verify analytics data collection and display
- Test error handling and recovery scenarios

### 5. Performance and Load Testing
- Conduct performance benchmarking
- Test concurrent user scenarios
- Validate system scalability
- Test memory and resource usage
- Verify database performance under load

### 6. Security and Compliance Testing
- Test authentication and authorization
- Validate input sanitization and security
- Test API rate limiting and protection
- Verify data privacy and encryption
- Conduct security vulnerability scanning

## Files to Create

### Test Infrastructure
1. `backend/tests/conftest.py` - Test configuration and fixtures
2. `backend/tests/test_fixtures.py` - Test data fixtures
3. `frontend/tests/setup.ts` - Frontend test setup
4. `frontend/tests/mocks/` - API mocks and test utilities
5. `docker-compose.test.yml` - Test environment configuration

### Backend Integration Tests
6. `backend/tests/integration/test_chat_flow.py` - Chat workflow tests
7. `backend/tests/integration/test_document_processing.py` - Document pipeline tests
8. `backend/tests/integration/test_sequence_execution.py` - Sequence workflow tests
9. `backend/tests/integration/test_websocket_connections.py` - Real-time feature tests
10. `backend/tests/integration/test_database_operations.py` - Database integration tests

### Frontend Integration Tests
11. `frontend/tests/integration/ChatInterface.test.tsx` - Chat UI integration tests
12. `frontend/tests/integration/DocumentManagement.test.tsx` - Document UI tests
13. `frontend/tests/integration/SequenceRunner.test.tsx` - Sequence UI tests
14. `frontend/tests/integration/Dashboard.test.tsx` - Dashboard integration tests
15. `frontend/tests/integration/Navigation.test.tsx` - Routing and navigation tests

### End-to-End Tests
16. `e2e/tests/complete_workflows.spec.ts` - Complete user workflows
17. `e2e/tests/cross_browser.spec.ts` - Cross-browser compatibility
18. `e2e/tests/mobile_responsive.spec.ts` - Mobile responsiveness tests
19. `e2e/tests/performance.spec.ts` - Performance testing
20. `e2e/tests/accessibility.spec.ts` - Accessibility compliance tests

### Load and Performance Tests
21. `tests/load/chat_load_test.py` - Chat system load testing
22. `tests/load/document_processing_load.py` - Document processing load tests
23. `tests/load/sequence_execution_load.py` - Sequence execution load tests
24. `tests/performance/benchmark_suite.py` - Performance benchmarking

## Key Testing Scenarios

### 1. Chat System Integration Tests
```python
# backend/tests/integration/test_chat_flow.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from websockets import connect

class TestChatIntegration:
    """Integration tests for the complete chat system."""
    
    async def test_complete_chat_workflow(self, client: TestClient, test_db):
        """Test end-to-end chat workflow with RAG."""
        
        # 1. Upload and process a test document
        with open("test_document.pdf", "rb") as f:
            upload_response = client.post(
                "/api/documents/upload",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        assert upload_response.status_code == 200
        doc_id = upload_response.json()["id"]
        
        # 2. Wait for document processing
        await self.wait_for_document_processing(client, doc_id)
        
        # 3. Create new conversation
        conv_response = client.post("/api/chat/conversations")
        assert conv_response.status_code == 200
        conv_id = conv_response.json()["id"]
        
        # 4. Send message and verify RAG context retrieval
        message_response = client.post(
            f"/api/chat/conversations/{conv_id}/messages",
            json={
                "content": "What is mentioned about testing in the document?",
                "use_context": True
            }
        )
        assert message_response.status_code == 200
        
        # 5. Verify response contains context from uploaded document
        response_data = message_response.json()
        assert "context" in response_data
        assert len(response_data["context"]) > 0
    
    async def test_websocket_streaming(self, websocket_url):
        """Test real-time chat streaming via WebSocket."""
        
        async with connect(f"{websocket_url}/chat/test-conversation") as websocket:
            # Send message
            await websocket.send(json.dumps({
                "type": "message",
                "content": "Hello, can you help me?"
            }))
            
            # Receive streaming chunks
            chunks = []
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    if data["type"] == "chunk":
                        chunks.append(data["content"])
                    elif data["type"] == "complete":
                        break
                        
                except asyncio.TimeoutError:
                    break
            
            # Verify streaming worked
            assert len(chunks) > 0
            full_response = "".join(chunks)
            assert len(full_response) > 10
```

### 2. Document Processing Integration Tests
```python
# backend/tests/integration/test_document_processing.py
class TestDocumentProcessingIntegration:
    """Integration tests for document processing pipeline."""
    
    async def test_batch_document_upload(self, client: TestClient):
        """Test batch document upload and processing."""
        
        # Prepare multiple test files
        files = [
            ("files", ("doc1.txt", "Test document 1 content", "text/plain")),
            ("files", ("doc2.txt", "Test document 2 content", "text/plain")),
            ("files", ("doc3.pdf", b"PDF content", "application/pdf"))
        ]
        
        # Upload batch
        response = client.post("/api/documents/batch-upload", files=files)
        assert response.status_code == 200
        
        uploaded_docs = response.json()
        assert len(uploaded_docs) == 3
        
        # Wait for all documents to be processed
        for doc in uploaded_docs:
            await self.wait_for_document_processing(client, doc["id"])
            
            # Verify document is searchable
            search_response = client.get(
                f"/api/documents/{doc['id']}/search",
                params={"query": "test"}
            )
            assert search_response.status_code == 200
    
    async def test_document_indexing_and_retrieval(self, client: TestClient):
        """Test document indexing and vector search functionality."""
        
        # Upload document with known content
        test_content = "This document discusses artificial intelligence and machine learning applications."
        
        response = client.post(
            "/api/documents/upload",
            files={"file": ("ai_doc.txt", test_content, "text/plain")}
        )
        doc_id = response.json()["id"]
        
        # Wait for processing and indexing
        await self.wait_for_document_processing(client, doc_id)
        
        # Test vector search
        search_response = client.post(
            "/api/documents/search",
            json={
                "query": "machine learning",
                "limit": 10
            }
        )
        
        assert search_response.status_code == 200
        results = search_response.json()
        assert len(results) > 0
        assert any("machine learning" in result["content"].lower() for result in results)
```

### 3. Sequence Execution Integration Tests
```python
# backend/tests/integration/test_sequence_execution.py
class TestSequenceExecutionIntegration:
    """Integration tests for sequence execution system."""
    
    async def test_contract_analysis_sequence(self, client: TestClient):
        """Test complete contract analysis sequence execution."""
        
        # Prepare contract text
        contract_text = """
        Employment Contract
        
        The employee will work 40 hours per week.
        Compensation is $50,000 per year.
        Termination requires 30 days notice.
        """
        
        # Execute contract check sequence
        execution_response = client.post(
            "/api/sequences/execute",
            json={
                "blueprint_id": "contractcheck",
                "input_variables": {
                    "contract_text": contract_text
                },
                "models": ["gpt-4o-2024-08-06"],
                "num_runs": 1
            }
        )
        
        assert execution_response.status_code == 200
        execution = execution_response.json()
        execution_id = execution["id"]
        
        # Monitor execution progress
        await self.wait_for_sequence_completion(client, execution_id)
        
        # Verify results
        result_response = client.get(f"/api/sequences/executions/{execution_id}")
        assert result_response.status_code == 200
        
        result = result_response.json()
        assert result["status"] == "completed"
        assert len(result["results"]) > 0
        assert "analysis" in result["results"][0]["response"].lower()
    
    async def test_sequence_progress_websocket(self, websocket_url):
        """Test real-time sequence progress via WebSocket."""
        
        # Start sequence execution
        # ... (execution setup)
        
        # Connect to progress WebSocket
        async with connect(f"{websocket_url}/sequences/{execution_id}/progress") as ws:
            progress_updates = []
            
            while True:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=30.0)
                    data = json.loads(message)
                    progress_updates.append(data)
                    
                    if data.get("type") == "completed":
                        break
                        
                except asyncio.TimeoutError:
                    break
            
            # Verify progress tracking
            assert len(progress_updates) > 1
            assert any(update.get("progress", 0) > 0 for update in progress_updates)
```

### 4. Frontend Integration Tests
```tsx
// frontend/tests/integration/ChatInterface.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { MockWebSocketProvider } from '../mocks/websocket';

describe('Chat Interface Integration', () => {
  test('complete chat workflow with file attachment', async () => {
    // Mock WebSocket for real-time features
    const mockWS = new MockWebSocketProvider();
    
    render(
      <MockWebSocketProvider value={mockWS}>
        <ChatInterface />
      </MockWebSocketProvider>
    );
    
    // Test file attachment
    const fileInput = screen.getByLabelText(/attach file/i);
    const testFile = new File(['test content'], 'test.txt', { type: 'text/plain' });
    
    fireEvent.change(fileInput, { target: { files: [testFile] } });
    
    // Verify file is attached
    await waitFor(() => {
      expect(screen.getByText('test.txt')).toBeInTheDocument();
    });
    
    // Send message with attachment
    const messageInput = screen.getByPlaceholderText(/type your message/i);
    fireEvent.change(messageInput, { target: { value: 'Analyze this document' } });
    fireEvent.click(screen.getByRole('button', { name: /send/i }));
    
    // Verify message appears
    await waitFor(() => {
      expect(screen.getByText('Analyze this document')).toBeInTheDocument();
    });
    
    // Simulate streaming response
    mockWS.simulateMessage({
      type: 'chunk',
      content: 'Based on the document you uploaded...'
    });
    
    // Verify streaming response appears
    await waitFor(() => {
      expect(screen.getByText(/based on the document/i)).toBeInTheDocument();
    });
  });
  
  test('conversation management features', async () => {
    render(<ChatInterface />);
    
    // Test creating new conversation
    fireEvent.click(screen.getByRole('button', { name: /new conversation/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/new conversation/i)).toBeInTheDocument();
    });
    
    // Test conversation switching
    // Test conversation deletion
    // Test conversation export
    // ... additional conversation management tests
  });
});
```

### 5. End-to-End Testing with Playwright
```typescript
// e2e/tests/complete_workflows.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Complete User Workflows', () => {
  test('user can complete full document analysis workflow', async ({ page }) => {
    // Navigate to application
    await page.goto('/');
    
    // Upload document
    await page.goto('/documents');
    await page.setInputFiles('[data-testid="file-upload"]', 'test-files/sample.pdf');
    
    // Wait for processing
    await page.waitForSelector('[data-testid="processing-complete"]', { timeout: 60000 });
    
    // Navigate to chat
    await page.goto('/chat');
    
    // Ask question about uploaded document
    await page.fill('[data-testid="message-input"]', 'What are the main points in the uploaded document?');
    await page.click('[data-testid="send-button"]');
    
    // Wait for and verify AI response
    await page.waitForSelector('[data-testid="assistant-message"]', { timeout: 30000 });
    const response = await page.textContent('[data-testid="assistant-message"]');
    expect(response).toContain('document');
    
    // Verify dashboard shows activity
    await page.goto('/dashboard');
    const messageCount = await page.textContent('[data-testid="total-messages"]');
    expect(parseInt(messageCount)).toBeGreaterThan(0);
  });
  
  test('user can execute sequence workflow', async ({ page }) => {
    await page.goto('/sequences');
    
    // Select contract analysis sequence
    await page.click('[data-testid="contractcheck-sequence"]');
    
    // Fill in contract text
    await page.fill('[data-testid="contract-input"]', 'Sample employment contract...');
    
    // Execute sequence
    await page.click('[data-testid="execute-sequence"]');
    
    // Monitor progress
    await page.waitForSelector('[data-testid="execution-complete"]', { timeout: 120000 });
    
    // Verify results
    const results = await page.textContent('[data-testid="sequence-results"]');
    expect(results).toContain('analysis');
    expect(results.length).toBeGreaterThan(100);
  });
});
```

## Performance Testing Framework

### Load Testing Configuration
```python
# tests/load/chat_load_test.py
from locust import HttpUser, task, between
import json

class ChatLoadUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup user session."""
        # Create conversation
        response = self.client.post("/api/chat/conversations")
        self.conversation_id = response.json()["id"]
    
    @task(3)
    def send_chat_message(self):
        """Send chat message - most common operation."""
        self.client.post(
            f"/api/chat/conversations/{self.conversation_id}/messages",
            json={
                "content": "What is artificial intelligence?",
                "use_context": True
            }
        )
    
    @task(1)
    def upload_document(self):
        """Upload document - less frequent operation."""
        files = {"file": ("test.txt", "Test content", "text/plain")}
        self.client.post("/api/documents/upload", files=files)
    
    @task(1)
    def execute_sequence(self):
        """Execute sequence - least frequent operation."""
        self.client.post(
            "/api/sequences/execute",
            json={
                "blueprint_id": "solver",
                "input_variables": {"error": "TypeError: object is not callable"},
                "models": ["gpt-4o-2024-08-06"]
            }
        )
```

## Validation Checklist

### Functional Validation
- [ ] All original Streamlit features work in React version
- [ ] Chat conversations with streaming responses
- [ ] Document upload, processing, and indexing
- [ ] All 6 sequence types execute correctly
- [ ] Real-time progress tracking via WebSocket
- [ ] Dashboard displays accurate metrics
- [ ] File attachments and exports work
- [ ] Search and filtering functionality
- [ ] Error handling and recovery

### Performance Validation
- [ ] Response times < 2 seconds for 95th percentile
- [ ] WebSocket connections stable under load
- [ ] Document processing completes within reasonable time
- [ ] Dashboard loads quickly with large datasets
- [ ] Memory usage remains stable
- [ ] Database queries are optimized
- [ ] API rate limiting works correctly

### Security Validation
- [ ] Input validation prevents injection attacks
- [ ] File uploads are properly sanitized
- [ ] API endpoints require proper authentication
- [ ] Sensitive data is properly encrypted
- [ ] CORS is configured correctly
- [ ] Rate limiting prevents abuse
- [ ] Error messages don't leak sensitive information

### Usability Validation
- [ ] Interface is intuitive and responsive
- [ ] Mobile experience is fully functional
- [ ] Accessibility guidelines are met
- [ ] Error messages are helpful
- [ ] Loading states are clear
- [ ] Navigation is logical and consistent
- [ ] Dark/light themes work properly

## Success Criteria

### Technical Requirements
- [ ] 99.9% uptime during testing period
- [ ] Zero data loss or corruption
- [ ] All APIs return correct status codes
- [ ] WebSocket connections handle disconnections gracefully
- [ ] Database migrations complete successfully
- [ ] All external service integrations work
- [ ] Backup and recovery procedures validated

### User Experience Requirements
- [ ] Feature parity with original Streamlit application
- [ ] Improved performance over original system
- [ ] Enhanced user interface and navigation
- [ ] Mobile responsive design works flawlessly
- [ ] Real-time features provide immediate feedback
- [ ] Error recovery is seamless
- [ ] System scales to handle multiple concurrent users

### Quality Assurance
- [ ] 90%+ test coverage across all components
- [ ] No critical or high-severity bugs
- [ ] Performance meets or exceeds requirements
- [ ] Security scanning passes with no critical issues
- [ ] Code quality metrics meet standards
- [ ] Documentation is complete and accurate

## Estimated Time
15-20 hours

## Final Deployment Steps
After successful testing:
1. Production environment setup
2. Database migration and data validation
3. DNS and SSL certificate configuration
4. Monitoring and alerting setup
5. Backup and disaster recovery validation
6. User training and documentation
7. Go-live and post-deployment monitoring

This comprehensive testing plan ensures that the migrated React + FastAPI system not only preserves all original functionality but significantly enhances the user experience, performance, and maintainability of the VAULT_APP platform.