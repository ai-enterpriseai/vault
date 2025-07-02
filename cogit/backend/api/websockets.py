"""
WebSocket handlers for VAULT_APP v2.0
Provides real-time communication for chat and system events
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from fastapi import WebSocket, WebSocketDisconnect, APIRouter
    from fastapi.websockets import WebSocketState
    FASTAPI_AVAILABLE = True
except ImportError:
    class WebSocket:
        pass
    class WebSocketDisconnect(Exception):
        pass
    class APIRouter:
        def __init__(self, *args, **kwargs):
            pass
        def websocket(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    class WebSocketState:
        CONNECTED = "connected"
        DISCONNECTED = "disconnected"
    FASTAPI_AVAILABLE = False

from core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time communication."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.chat_rooms: Dict[str, List[str]] = {}
        self.user_info: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str, room_id: str = "default"):
        """Accept a new WebSocket connection."""
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            
            # Add to chat room
            if room_id not in self.chat_rooms:
                self.chat_rooms[room_id] = []
            if client_id not in self.chat_rooms[room_id]:
                self.chat_rooms[room_id].append(client_id)
            
            # Store user info
            self.user_info[client_id] = {
                "connected_at": datetime.utcnow().isoformat(),
                "room_id": room_id,
                "status": "connected"
            }
            
            logger.info(f"WebSocket connected: {client_id} in room {room_id}")
            
            # Notify room about new connection
            await self.broadcast_to_room(room_id, {
                "type": "user_joined",
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_client=client_id)
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket {client_id}: {e}")
            raise
    
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        try:
            if client_id in self.active_connections:
                # Get room info before removing
                room_id = self.user_info.get(client_id, {}).get("room_id", "default")
                
                # Remove from connections
                del self.active_connections[client_id]
                
                # Remove from chat room
                if room_id in self.chat_rooms and client_id in self.chat_rooms[room_id]:
                    self.chat_rooms[room_id].remove(client_id)
                    
                    # Clean up empty rooms
                    if not self.chat_rooms[room_id]:
                        del self.chat_rooms[room_id]
                
                # Remove user info
                if client_id in self.user_info:
                    del self.user_info[client_id]
                
                logger.info(f"WebSocket disconnected: {client_id}")
                
                # Notify room about disconnection
                asyncio.create_task(self.broadcast_to_room(room_id, {
                    "type": "user_left",
                    "client_id": client_id,
                    "timestamp": datetime.utcnow().isoformat()
                }))
                
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket {client_id}: {e}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message))
                logger.debug(f"Sent message to {client_id}: {message.get('type', 'unknown')}")
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude_client: Optional[str] = None):
        """Broadcast a message to all clients in a room."""
        if room_id not in self.chat_rooms:
            return
        
        clients = self.chat_rooms[room_id].copy()
        if exclude_client and exclude_client in clients:
            clients.remove(exclude_client)
        
        disconnected_clients = []
        
        for client_id in clients:
            try:
                if client_id in self.active_connections:
                    websocket = self.active_connections[client_id]
                    await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
        
        if clients:
            logger.debug(f"Broadcasted to room {room_id}: {message.get('type', 'unknown')} ({len(clients)} clients)")
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all connected clients."""
        clients = list(self.active_connections.keys())
        disconnected_clients = []
        
        for client_id in clients:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
        
        logger.debug(f"Broadcasted to all: {message.get('type', 'unknown')} ({len(clients)} clients)")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            "total_connections": len(self.active_connections),
            "total_rooms": len(self.chat_rooms),
            "rooms": {room: len(clients) for room, clients in self.chat_rooms.items()},
            "connections": list(self.active_connections.keys())
        }


# Global connection manager
manager = ConnectionManager()


@router.websocket("/chat/{client_id}")
async def websocket_chat_endpoint(websocket: WebSocket, client_id: str, room_id: str = "general"):
    """
    WebSocket endpoint for real-time chat.
    
    Args:
        websocket: WebSocket connection
        client_id: Unique client identifier
        room_id: Chat room identifier (default: "general")
    """
    await manager.connect(websocket, client_id, room_id)
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "welcome",
            "message": f"Connected to room: {room_id}",
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat()
        }, client_id)
        
        # Listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Process different message types
                await handle_chat_message(client_id, room_id, message_data)
                
            except json.JSONDecodeError as e:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                }, client_id)
                logger.warning(f"Invalid JSON from {client_id}: {e}")
            
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"Error in chat WebSocket for {client_id}: {e}")
    finally:
        manager.disconnect(client_id)


@router.websocket("/system/{client_id}")
async def websocket_system_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for system events and notifications.
    
    Args:
        websocket: WebSocket connection
        client_id: Unique client identifier
    """
    await manager.connect(websocket, client_id, "system")
    
    try:
        # Send system status
        await manager.send_personal_message({
            "type": "system_status",
            "message": "Connected to system events",
            "timestamp": datetime.utcnow().isoformat()
        }, client_id)
        
        # Listen for system-level messages
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Process system message types
                await handle_system_message(client_id, message_data)
                
            except json.JSONDecodeError as e:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                }, client_id)
                
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"Error in system WebSocket for {client_id}: {e}")
    finally:
        manager.disconnect(client_id)


async def handle_chat_message(client_id: str, room_id: str, message_data: dict):
    """Handle incoming chat messages."""
    try:
        message_type = message_data.get("type", "message")
        
        if message_type == "chat_message":
            # Broadcast chat message to room
            await manager.broadcast_to_room(room_id, {
                "type": "chat_message",
                "client_id": client_id,
                "message": message_data.get("message", ""),
                "timestamp": datetime.utcnow().isoformat()
            })
            
        elif message_type == "typing":
            # Broadcast typing indicator
            await manager.broadcast_to_room(room_id, {
                "type": "typing",
                "client_id": client_id,
                "is_typing": message_data.get("is_typing", False),
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_client=client_id)
            
        elif message_type == "ping":
            # Respond to ping
            await manager.send_personal_message({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            }, client_id)
            
        else:
            logger.warning(f"Unknown chat message type from {client_id}: {message_type}")
            
    except Exception as e:
        logger.error(f"Error handling chat message from {client_id}: {e}")


async def handle_system_message(client_id: str, message_data: dict):
    """Handle incoming system messages."""
    try:
        message_type = message_data.get("type", "unknown")
        
        if message_type == "get_stats":
            # Send connection statistics
            stats = manager.get_connection_stats()
            await manager.send_personal_message({
                "type": "stats",
                "data": stats,
                "timestamp": datetime.utcnow().isoformat()
            }, client_id)
            
        elif message_type == "subscribe_events":
            # Subscribe to system events (placeholder)
            await manager.send_personal_message({
                "type": "subscribed",
                "events": message_data.get("events", []),
                "timestamp": datetime.utcnow().isoformat()
            }, client_id)
            
        else:
            logger.warning(f"Unknown system message type from {client_id}: {message_type}")
            
    except Exception as e:
        logger.error(f"Error handling system message from {client_id}: {e}")


# Utility functions for broadcasting

async def broadcast_system_event(event_type: str, data: dict):
    """Broadcast a system event to all system WebSocket connections."""
    await manager.broadcast_to_room("system", {
        "type": "system_event",
        "event_type": event_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    })


async def notify_processing_status(client_id: str, status: str, details: dict):
    """Send processing status update to a specific client."""
    await manager.send_personal_message({
        "type": "processing_status",
        "status": status,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }, client_id)