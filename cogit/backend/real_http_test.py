#!/usr/bin/env python3
"""
REAL HTTP Test for VAULT_APP v2.0
Makes actual HTTP requests to test the server
No mocks - real network calls
"""

import json
import time
import threading
import subprocess
import sys
import os
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

SERVER_HOST = "localhost"
SERVER_PORT = 8001
BASE_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

def start_test_server():
    """Start the test server in background."""
    print("Starting test server...")
    try:
        # Start server as subprocess
        server_process = subprocess.Popen([
            sys.executable, 'simple_server.py', 
            '--host', SERVER_HOST, 
            '--port', str(SERVER_PORT)
        ], cwd=os.path.dirname(__file__))
        
        # Wait for server to start
        time.sleep(2)
        
        return server_process
        
    except Exception as e:
        print(f"Failed to start server: {e}")
        return None

def make_request(method, endpoint, data=None):
    """Make HTTP request and return response."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = urlopen(url, timeout=10)
        elif method == "POST":
            request_data = json.dumps(data or {}).encode('utf-8')
            req = Request(url, data=request_data, headers={
                'Content-Type': 'application/json'
            })
            response = urlopen(req, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        status_code = response.getcode()
        response_data = json.loads(response.read().decode('utf-8'))
        
        return status_code, response_data
        
    except HTTPError as e:
        error_data = json.loads(e.read().decode('utf-8'))
        return e.code, error_data
    except URLError as e:
        return None, {"error": f"Connection failed: {e}"}
    except Exception as e:
        return None, {"error": f"Request failed: {e}"}

def test_health_endpoint():
    """Test the health check endpoint."""
    print("Testing /health endpoint...")
    
    status, data = make_request("GET", "/health")
    
    if status == 200:
        assert data.get("status") == "healthy", "Health status should be 'healthy'"
        assert data.get("version") == "2.0.0", "Version should be '2.0.0'"
        assert "timestamp" in data, "Should include timestamp"
        assert "environment" in data, "Should include environment"
        print("✓ Health endpoint working correctly")
        return True
    else:
        print(f"✗ Health endpoint failed: {status} - {data}")
        return False

def test_models_endpoint():
    """Test the models endpoint."""
    print("Testing /api/v1/models endpoint...")
    
    status, data = make_request("GET", "/api/v1/models")
    
    if status == 200:
        assert data.get("success") is True, "Response should be successful"
        assert "data" in data, "Should include data field"
        assert isinstance(data["data"], list), "Data should be a list"
        assert "total_models" in data, "Should include total_models"
        print(f"✓ Models endpoint returned {data['total_models']} models")
        return True
    else:
        print(f"✗ Models endpoint failed: {status} - {data}")
        return False

def test_create_conversation():
    """Test creating a conversation."""
    print("Testing POST /api/v1/conversations...")
    
    request_data = {
        "title": "Test Conversation",
        "description": "A conversation created by the real HTTP test",
        "rag_enabled": True
    }
    
    status, data = make_request("POST", "/api/v1/conversations", request_data)
    
    if status == 201:
        assert data.get("success") is True, "Response should be successful"
        assert "data" in data, "Should include data field"
        assert data["data"]["title"] == "Test Conversation", "Title should match"
        assert "id" in data["data"], "Should include conversation ID"
        print(f"✓ Created conversation: {data['data']['id']}")
        return True, data["data"]["id"]
    else:
        print(f"✗ Create conversation failed: {status} - {data}")
        return False, None

def test_send_message(conversation_id):
    """Test sending a message."""
    print("Testing POST /api/v1/message...")
    
    request_data = {
        "message": "Hello from the real HTTP test!",
        "conversation_id": conversation_id,
        "use_rag": True
    }
    
    status, data = make_request("POST", "/api/v1/message", request_data)
    
    if status == 200:
        assert data.get("success") is True, "Response should be successful"
        assert "data" in data, "Should include data field"
        assert "message" in data["data"], "Should include message"
        assert data["data"]["conversation_id"] == conversation_id, "Conversation ID should match"
        
        message_content = data["data"]["message"]["content"]
        assert "Hello from the real HTTP test!" in message_content, "Should echo user message"
        print("✓ Message sent and response received")
        return True
    else:
        print(f"✗ Send message failed: {status} - {data}")
        return False

def test_list_conversations():
    """Test listing conversations."""
    print("Testing GET /api/v1/conversations...")
    
    status, data = make_request("GET", "/api/v1/conversations?page=1&page_size=10")
    
    if status == 200:
        assert data.get("success") is True, "Response should be successful"
        assert "data" in data, "Should include data field"
        assert "pagination" in data, "Should include pagination"
        assert isinstance(data["data"], list), "Data should be a list"
        print(f"✓ Listed {len(data['data'])} conversations")
        return True
    else:
        print(f"✗ List conversations failed: {status} - {data}")
        return False

def test_search_conversations():
    """Test searching conversations."""
    print("Testing POST /api/v1/search...")
    
    request_data = {
        "query": "test search query",
        "limit": 10
    }
    
    status, data = make_request("POST", "/api/v1/search", request_data)
    
    if status == 200:
        assert data.get("success") is True, "Response should be successful"
        assert "data" in data, "Should include data field"
        assert "search_time" in data["data"], "Should include search time"
        assert data["data"]["query"] == "test search query", "Query should match"
        print(f"✓ Search completed in {data['data']['search_time']:.3f}s")
        return True
    else:
        print(f"✗ Search failed: {status} - {data}")
        return False

def test_stats_endpoint():
    """Test the stats endpoint."""
    print("Testing GET /api/v1/stats...")
    
    status, data = make_request("GET", "/api/v1/stats")
    
    if status == 200:
        assert data.get("success") is True, "Response should be successful"
        assert "data" in data, "Should include data field"
        stats = data["data"]
        assert "total_conversations" in stats, "Should include total_conversations"
        assert "server_uptime" in stats, "Should include server_uptime"
        assert "environment" in stats, "Should include environment"
        print("✓ Stats endpoint working correctly")
        return True
    else:
        print(f"✗ Stats endpoint failed: {status} - {data}")
        return False

def test_error_handling():
    """Test error handling."""
    print("Testing error handling...")
    
    # Test 404 error
    status, data = make_request("GET", "/nonexistent")
    if status == 404:
        assert data.get("success") is False, "Should be unsuccessful"
        assert "error" in data, "Should include error field"
        print("✓ 404 error handling works")
    else:
        print(f"✗ 404 error handling failed: {status}")
        return False
    
    # Test bad JSON
    status, data = make_request("POST", "/api/v1/message", None)
    if status == 400:
        print("✓ Bad request handling works")
    else:
        print(f"✗ Bad request handling unexpected: {status}")
        return False
    
    return True

def run_real_http_test():
    """Run comprehensive HTTP tests."""
    print("=" * 70)
    print("VAULT_APP v2.0 - REAL HTTP API TEST")
    print("Making actual network requests to real server")
    print("=" * 70)
    
    # Start server
    server_process = start_test_server()
    if not server_process:
        print("❌ Failed to start test server")
        return False
    
    try:
        # Wait for server to be ready
        print("Waiting for server to be ready...")
        for i in range(10):
            try:
                status, _ = make_request("GET", "/health")
                if status == 200:
                    print("✓ Server is ready")
                    break
            except:
                pass
            time.sleep(1)
        else:
            print("❌ Server not responding after 10 seconds")
            return False
        
        # Run tests
        tests = [
            ("Health Check", test_health_endpoint),
            ("Models Endpoint", test_models_endpoint),
            ("List Conversations", test_list_conversations),
            ("Stats Endpoint", test_stats_endpoint),
            ("Search Conversations", test_search_conversations),
            ("Error Handling", test_error_handling)
        ]
        
        # Test conversation workflow
        conversation_tests = [
            ("Create Conversation", test_create_conversation),
        ]
        
        results = []
        conversation_id = None
        
        # Run basic tests
        for test_name, test_func in tests:
            print(f"\n[{test_name}]")
            result = test_func()
            results.append(result)
        
        # Run conversation tests
        for test_name, test_func in conversation_tests:
            print(f"\n[{test_name}]")
            if test_func == test_create_conversation:
                result, conv_id = test_func()
                conversation_id = conv_id
            else:
                result = test_func()
            results.append(result)
        
        # Test messaging if we have a conversation
        if conversation_id:
            print("\n[Send Message]")
            result = test_send_message(conversation_id)
            results.append(result)
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print("\n" + "=" * 70)
        print("REAL HTTP TEST RESULTS")
        print("=" * 70)
        print(f"Tests passed: {passed}/{total}")
        print(f"Success rate: {(passed/total)*100:.0f}%")
        
        if passed == total:
            print("\n🎉 ALL HTTP TESTS PASSED!")
            print("✅ Real HTTP server working")
            print("✅ All API endpoints functional")
            print("✅ Real JSON request/response handling")
            print("✅ Error handling working")
            print("✅ No mocks - actual network communication")
            print(f"\n🌐 Server running at: {BASE_URL}")
            return True
        else:
            print(f"\n❌ {total - passed} HTTP TESTS FAILED!")
            return False
    
    finally:
        # Stop server
        if server_process:
            print(f"\nStopping test server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    success = run_real_http_test()
    sys.exit(0 if success else 1)