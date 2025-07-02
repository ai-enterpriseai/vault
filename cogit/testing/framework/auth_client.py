"""
Authenticated HTTP client for real API testing
Provides HTTP client with authentication, session management, and real request monitoring
"""

import time
import json
import asyncio
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from datetime import datetime

try:
    import requests
    import aiohttp
    import websockets
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False


class AuthenticatedClient:
    """
    HTTP client for authentic API testing with real authentication and monitoring.
    
    Supports both sync and async operations for comprehensive testing
    of the VAULT_APP FastAPI backend.
    """
    
    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        """
        Initialize authenticated client.
        
        Args:
            base_url: Base URL of the FastAPI backend (e.g., http://localhost:8000)
            auth_token: Authentication token for protected endpoints
        """
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session = requests.Session()
        self.request_log: List[Dict[str, Any]] = []
        
        # Configure session with real headers
        self.session.headers.update({
            'User-Agent': 'VAULT_APP_Tester/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        if auth_token:
            self.session.headers['Authorization'] = f'Bearer {auth_token}'
    
    def _log_request(self, method: str, url: str, response: requests.Response, 
                    request_data: Any = None, execution_time: float = 0) -> None:
        """Log request details for analysis."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": method,
            "url": url,
            "status_code": response.status_code,
            "execution_time": execution_time,
            "request_size": len(json.dumps(request_data).encode()) if request_data else 0,
            "response_size": len(response.content) if response.content else 0,
            "headers": dict(response.headers),
            "success": 200 <= response.status_code < 300
        }
        self.request_log.append(log_entry)
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """
        Perform authenticated GET request to real API.
        
        Args:
            endpoint: API endpoint (e.g., '/api/v1/health')
            params: Query parameters
            
        Returns:
            Real HTTP response
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        response = self.session.get(url, params=params)
        execution_time = time.time() - start_time
        
        self._log_request('GET', url, response, params, execution_time)
        return response
    
    def post(self, endpoint: str, data: Optional[Dict] = None, 
             files: Optional[Dict] = None) -> requests.Response:
        """
        Perform authenticated POST request to real API.
        
        Args:
            endpoint: API endpoint
            data: JSON data to send
            files: File uploads for multipart requests
            
        Returns:
            Real HTTP response
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        if files:
            # Remove Content-Type for file uploads (let requests set it)
            headers = {k: v for k, v in self.session.headers.items() 
                      if k.lower() != 'content-type'}
            response = self.session.post(url, data=data, files=files, headers=headers)
        else:
            response = self.session.post(url, json=data)
        
        execution_time = time.time() - start_time
        self._log_request('POST', url, response, data, execution_time)
        return response
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """Perform authenticated PUT request to real API."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        response = self.session.put(url, json=data)
        execution_time = time.time() - start_time
        
        self._log_request('PUT', url, response, data, execution_time)
        return response
    
    def delete(self, endpoint: str) -> requests.Response:
        """Perform authenticated DELETE request to real API."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        response = self.session.delete(url)
        execution_time = time.time() - start_time
        
        self._log_request('DELETE', url, response, None, execution_time)
        return response
    
    async def websocket_connect(self, endpoint: str, client_id: str) -> 'WebSocketTester':
        """
        Create WebSocket connection for real-time testing.
        
        Args:
            endpoint: WebSocket endpoint (e.g., '/ws/chat')
            client_id: Unique client identifier
            
        Returns:
            WebSocket tester instance
        """
        ws_url = self.base_url.replace('http', 'ws') + endpoint
        if '?' in ws_url:
            ws_url += f'&client_id={client_id}'
        else:
            ws_url += f'?client_id={client_id}'
        
        return WebSocketTester(ws_url, client_id, self.auth_token)
    
    def upload_real_file(self, endpoint: str, file_path: Path, 
                        additional_data: Optional[Dict] = None) -> requests.Response:
        """
        Upload a real file to the API.
        
        Args:
            endpoint: Upload endpoint
            file_path: Path to real file to upload
            additional_data: Additional form data
            
        Returns:
            Real HTTP response
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Test file not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, self._get_content_type(file_path))}
            return self.post(endpoint, data=additional_data, files=files)
    
    def _get_content_type(self, file_path: Path) -> str:
        """Get content type for file upload."""
        suffix = file_path.suffix.lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.json': 'application/json',
            '.md': 'text/markdown'
        }
        return content_types.get(suffix, 'application/octet-stream')
    
    def test_health_endpoints(self) -> Dict[str, Any]:
        """Test all health check endpoints and return results."""
        health_tests = {}
        
        endpoints = [
            '/health',
            '/health/live', 
            '/health/ready',
            '/info'
        ]
        
        for endpoint in endpoints:
            try:
                response = self.get(endpoint)
                health_tests[endpoint] = {
                    "status_code": response.status_code,
                    "response_time": self.request_log[-1]["execution_time"],
                    "success": response.status_code == 200,
                    "data": response.json() if response.content else None
                }
            except Exception as e:
                health_tests[endpoint] = {
                    "status_code": None,
                    "success": False,
                    "error": str(e)
                }
        
        return health_tests
    
    def test_api_performance(self, endpoint: str, iterations: int = 10) -> Dict[str, Any]:
        """
        Test API endpoint performance with multiple requests.
        
        Args:
            endpoint: Endpoint to test
            iterations: Number of requests to make
            
        Returns:
            Performance statistics
        """
        response_times = []
        status_codes = []
        
        for _ in range(iterations):
            response = self.get(endpoint)
            response_times.append(self.request_log[-1]["execution_time"])
            status_codes.append(response.status_code)
        
        return {
            "endpoint": endpoint,
            "iterations": iterations,
            "avg_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "success_rate": status_codes.count(200) / len(status_codes),
            "status_codes": status_codes,
            "total_time": sum(response_times)
        }
    
    def get_request_statistics(self) -> Dict[str, Any]:
        """Get comprehensive request statistics."""
        if not self.request_log:
            return {"total_requests": 0}
        
        successful_requests = [req for req in self.request_log if req["success"]]
        failed_requests = [req for req in self.request_log if not req["success"]]
        
        response_times = [req["execution_time"] for req in self.request_log]
        
        return {
            "total_requests": len(self.request_log),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": len(successful_requests) / len(self.request_log),
            "avg_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "total_request_size": sum(req["request_size"] for req in self.request_log),
            "total_response_size": sum(req["response_size"] for req in self.request_log),
            "methods_used": list(set(req["method"] for req in self.request_log))
        }


class WebSocketTester:
    """WebSocket client for real-time testing."""
    
    def __init__(self, url: str, client_id: str, auth_token: Optional[str] = None):
        """Initialize WebSocket tester."""
        self.url = url
        self.client_id = client_id
        self.auth_token = auth_token
        self.websocket = None
        self.messages_received: List[Dict[str, Any]] = []
        self.connection_start = None
        self.is_connected = False
    
    async def connect(self):
        """Establish WebSocket connection."""
        headers = {}
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        try:
            self.websocket = await websockets.connect(self.url, extra_headers=headers)
            self.connection_start = datetime.utcnow()
            self.is_connected = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to WebSocket: {e}")
    
    async def send_message(self, message: Dict[str, Any]):
        """Send message through WebSocket."""
        if not self.is_connected:
            raise RuntimeError("WebSocket not connected")
        
        await self.websocket.send(json.dumps(message))
    
    async def receive_message(self, timeout: float = 5.0) -> Dict[str, Any]:
        """Receive message from WebSocket with timeout."""
        if not self.is_connected:
            raise RuntimeError("WebSocket not connected")
        
        try:
            message = await asyncio.wait_for(self.websocket.recv(), timeout=timeout)
            parsed_message = json.loads(message)
            
            # Log received message
            self.messages_received.append({
                "timestamp": datetime.utcnow().isoformat(),
                "message": parsed_message
            })
            
            return parsed_message
        except asyncio.TimeoutError:
            raise TimeoutError(f"No message received within {timeout} seconds")
    
    async def test_chat_flow(self, messages: List[str]) -> List[Dict[str, Any]]:
        """
        Test complete chat conversation flow.
        
        Args:
            messages: List of messages to send
            
        Returns:
            List of responses received
        """
        responses = []
        
        for message in messages:
            # Send chat message
            await self.send_message({
                "type": "chat_message",
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Wait for response
            try:
                response = await self.receive_message(timeout=10.0)
                responses.append(response)
            except TimeoutError:
                responses.append({"error": "timeout", "original_message": message})
        
        return responses
    
    async def close(self):
        """Close WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics."""
        connection_duration = None
        if self.connection_start:
            connection_duration = (datetime.utcnow() - self.connection_start).total_seconds()
        
        return {
            "client_id": self.client_id,
            "connected": self.is_connected,
            "connection_duration": connection_duration,
            "messages_received": len(self.messages_received),
            "url": self.url
        }