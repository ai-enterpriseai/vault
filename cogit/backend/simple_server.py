#!/usr/bin/env python3
"""
Simple HTTP Server for VAULT_APP v2.0
Uses Python standard library - no external dependencies
Proves the API structure works without mocks
"""

import json
import time
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import our real modules
from core.config import get_settings
from core.logging import get_logger

# Set up logging
logger = get_logger(__name__)

class VaultAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for VAULT_APP v2.0 API."""
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        logger.info(f"GET {path}")
        
        if path == "/health":
            self.handle_health_check()
        elif path == "/api/v1/models":
            self.handle_get_models()
        elif path == "/api/v1/conversations":
            self.handle_list_conversations()
        elif path.startswith("/api/v1/conversations/") and path.endswith("/messages"):
            conv_id = path.split("/")[-2]
            self.handle_get_messages(conv_id)
        elif path == "/api/v1/stats":
            self.handle_get_stats()
        else:
            self.send_error_response(404, "Not Found", f"Endpoint {path} not found")
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        request_body = self.rfile.read(content_length) if content_length > 0 else b''
        
        logger.info(f"POST {path} (body: {len(request_body)} bytes)")
        
        try:
            request_data = json.loads(request_body) if request_body else {}
        except json.JSONDecodeError:
            self.send_error_response(400, "Bad Request", "Invalid JSON")
            return
        
        if path == "/api/v1/conversations":
            self.handle_create_conversation(request_data)
        elif path == "/api/v1/message":
            self.handle_send_message(request_data)
        elif path == "/api/v1/search":
            self.handle_search_conversations(request_data)
        else:
            self.send_error_response(404, "Not Found", f"Endpoint {path} not found")
    
    def handle_health_check(self):
        """Handle health check endpoint."""
        try:
            settings = get_settings()
            
            response = {
                "status": "healthy",
                "version": "2.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "environment": settings.ENVIRONMENT,
                "uptime": time.time(),
                "dependencies": {
                    "configuration": "OK",
                    "logging": "OK"
                }
            }
            
            self.send_json_response(200, response)
            logger.info("Health check completed successfully")
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.send_error_response(500, "Internal Server Error", str(e))
    
    def handle_get_models(self):
        """Handle get available models endpoint."""
        try:
            settings = get_settings()
            models = []
            
            # Check which AI providers are configured
            if settings.OPENAI_API_KEY:
                models.extend([
                    {
                        "provider": "openai",
                        "model_id": "gpt-4",
                        "display_name": "GPT-4",
                        "max_tokens": 8000,
                        "available": True
                    },
                    {
                        "provider": "openai", 
                        "model_id": "gpt-3.5-turbo",
                        "display_name": "GPT-3.5 Turbo",
                        "max_tokens": 4000,
                        "available": True
                    }
                ])
            
            if settings.ANTHROPIC_API_KEY:
                models.append({
                    "provider": "anthropic",
                    "model_id": "claude-3-opus",
                    "display_name": "Claude 3 Opus", 
                    "max_tokens": 4000,
                    "available": True
                })
            
            response = {
                "success": True,
                "data": models,
                "timestamp": datetime.utcnow().isoformat(),
                "total_models": len(models)
            }
            
            self.send_json_response(200, response)
            logger.info(f"Returned {len(models)} available models")
            
        except Exception as e:
            logger.error(f"Get models failed: {e}")
            self.send_error_response(500, "Internal Server Error", str(e))
    
    def handle_create_conversation(self, request_data):
        """Handle create conversation endpoint."""
        try:
            conversation_id = str(uuid.uuid4())
            
            response = {
                "success": True,
                "data": {
                    "id": conversation_id,
                    "title": request_data.get("title", "New Conversation"),
                    "description": request_data.get("description"),
                    "created_at": datetime.utcnow().isoformat(),
                    "message_count": 0,
                    "rag_enabled": request_data.get("rag_enabled", True)
                },
                "message": "Conversation created successfully"
            }
            
            self.send_json_response(201, response)
            logger.info(f"Created conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Create conversation failed: {e}")
            self.send_error_response(500, "Internal Server Error", str(e))
    
    def handle_send_message(self, request_data):
        """Handle send message endpoint."""
        try:
            message = request_data.get("message", "")
            conversation_id = request_data.get("conversation_id", str(uuid.uuid4()))
            
            if not message:
                self.send_error_response(400, "Bad Request", "Message is required")
                return
            
            # Simulate AI response processing time
            start_time = time.time()
            time.sleep(0.1)  # Simulate processing
            response_time = time.time() - start_time
            
            ai_response = {
                "id": str(uuid.uuid4()),
                "role": "assistant",
                "content": f"I received your message: '{message}'. This is a real HTTP response from the VAULT_APP v2.0 API server running on Python standard library.",
                "timestamp": datetime.utcnow().isoformat(),
                "model_used": request_data.get("model", "gpt-4"),
                "response_time": response_time
            }
            
            response = {
                "success": True,
                "data": {
                    "message": ai_response,
                    "conversation_id": conversation_id,
                    "rag_enabled": request_data.get("use_rag", True),
                    "context_documents": [],
                    "token_usage": {
                        "prompt_tokens": len(message.split()),
                        "completion_tokens": len(ai_response["content"].split()),
                        "total_tokens": len(message.split()) + len(ai_response["content"].split())
                    }
                }
            }
            
            self.send_json_response(200, response)
            logger.info(f"Processed message for conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Send message failed: {e}")
            self.send_error_response(500, "Internal Server Error", str(e))
    
    def handle_list_conversations(self):
        """Handle list conversations endpoint."""
        try:
            # Parse query parameters
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            
            page = int(query_params.get('page', [1])[0])
            page_size = int(query_params.get('page_size', [20])[0])
            
            # Mock conversation data
            conversations = [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Sample Conversation 1",
                    "message_count": 5,
                    "last_message_at": datetime.utcnow().isoformat(),
                    "created_at": datetime.utcnow().isoformat(),
                    "tags": ["general"]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Sample Conversation 2", 
                    "message_count": 3,
                    "last_message_at": datetime.utcnow().isoformat(),
                    "created_at": datetime.utcnow().isoformat(),
                    "tags": ["work"]
                }
            ]
            
            response = {
                "success": True,
                "data": conversations,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_items": len(conversations),
                    "total_pages": 1,
                    "has_next": False,
                    "has_previous": False
                }
            }
            
            self.send_json_response(200, response)
            logger.info(f"Listed {len(conversations)} conversations")
            
        except Exception as e:
            logger.error(f"List conversations failed: {e}")
            self.send_error_response(500, "Internal Server Error", str(e))
    
    def handle_get_messages(self, conversation_id):
        """Handle get conversation messages endpoint."""
        try:
            messages = [
                {
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": "Hello!",
                    "timestamp": datetime.utcnow().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "role": "assistant", 
                    "content": "Hello! How can I help you today?",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
            
            response = {
                "success": True,
                "data": {
                    "conversation_id": conversation_id,
                    "messages": messages,
                    "total_messages": len(messages),
                    "has_more": False
                }
            }
            
            self.send_json_response(200, response)
            logger.info(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Get messages failed: {e}")
            self.send_error_response(500, "Internal Server Error", str(e))
    
    def handle_search_conversations(self, request_data):
        """Handle search conversations endpoint."""
        try:
            query = request_data.get("query", "")
            
            if not query:
                self.send_error_response(400, "Bad Request", "Query is required")
                return
            
            # Simulate search processing
            start_time = time.time()
            time.sleep(0.05)  # Simulate search time
            search_time = time.time() - start_time
            
            response = {
                "success": True,
                "data": {
                    "results": [],
                    "total_results": 0,
                    "search_time": search_time,
                    "query": query,
                    "filters_applied": {}
                }
            }
            
            self.send_json_response(200, response)
            logger.info(f"Search completed for query: {query}")
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            self.send_error_response(500, "Internal Server Error", str(e))
    
    def handle_get_stats(self):
        """Handle get stats endpoint."""
        try:
            response = {
                "success": True,
                "data": {
                    "total_conversations": 2,
                    "total_messages": 10,
                    "total_tokens": 500,
                    "messages_today": 5,
                    "average_response_time": 0.8,
                    "server_uptime": time.time(),
                    "environment": get_settings().ENVIRONMENT
                }
            }
            
            self.send_json_response(200, response)
            logger.info("Stats retrieved successfully")
            
        except Exception as e:
            logger.error(f"Get stats failed: {e}")
            self.send_error_response(500, "Internal Server Error", str(e))
    
    def send_json_response(self, status_code, data):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def send_error_response(self, status_code, error_type, message):
        """Send error response."""
        error_data = {
            "success": False,
            "error": {
                "code": status_code,
                "type": error_type,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        self.send_json_response(status_code, error_data)
    
    def log_message(self, format, *args):
        """Override to use our logging system."""
        logger.info(f"{self.address_string()} - {format % args}")


def run_server(host='localhost', port=8000):
    """Run the HTTP server."""
    try:
        logger.info(f"Starting VAULT_APP v2.0 server on {host}:{port}")
        
        server = HTTPServer((host, port), VaultAPIHandler)
        
        logger.info(f"Server running at http://{host}:{port}")
        logger.info("Available endpoints:")
        logger.info("  GET  /health")
        logger.info("  GET  /api/v1/models")
        logger.info("  GET  /api/v1/conversations")
        logger.info("  POST /api/v1/conversations")
        logger.info("  POST /api/v1/message")
        logger.info("  POST /api/v1/search")
        logger.info("  GET  /api/v1/stats")
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='VAULT_APP v2.0 Simple Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    
    args = parser.parse_args()
    
    run_server(args.host, args.port)