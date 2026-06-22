"""
WebSocket endpoint for real-time demo output streaming
Broadcasts JMeter console output, SIP messages, and traffic statistics
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
import time

router = APIRouter()

# Active WebSocket connections per execution
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """Manages WebSocket connections for demo executions"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, execution_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        if execution_id not in self.active_connections:
            self.active_connections[execution_id] = set()
        self.active_connections[execution_id].add(websocket)
        print(f"Client connected to execution {execution_id}. Total: {len(self.active_connections[execution_id])}")
    
    def disconnect(self, websocket: WebSocket, execution_id: str):
        """Remove WebSocket connection"""
        if execution_id in self.active_connections:
            self.active_connections[execution_id].discard(websocket)
            if not self.active_connections[execution_id]:
                del self.active_connections[execution_id]
        print(f"Client disconnected from execution {execution_id}")
    
    async def broadcast(self, execution_id: str, message: dict):
        """Broadcast message to all clients watching this execution"""
        if execution_id not in self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = set()
        
        for connection in self.active_connections[execution_id]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                print(f"Error sending to client: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn, execution_id)
    
    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to specific client"""
        await websocket.send_json(message)


manager = ConnectionManager()


@router.websocket("/demo-output/{execution_id}")
async def websocket_demo_output(websocket: WebSocket, execution_id: str):
    """
    WebSocket endpoint for real-time demo output
    
    Message types:
    - output: Console output line
    - sip_message: SIP call flow message
    - traffic_stats: Real-time statistics update
    - status: Execution status change
    - error: Error message
    - complete: Execution completed
    """
    await manager.connect(websocket, execution_id)
    
    try:
        # Send initial connection confirmation
        await manager.send_personal(websocket, {
            "type": "connected",
            "execution_id": execution_id,
            "message": "Connected to demo output stream"
        })
        
        # Keep connection alive and listen for client messages (e.g., pause, stop)
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle client commands
            if message.get("type") == "ping":
                await manager.send_personal(websocket, {"type": "pong"})
            elif message.get("type") == "cancel":
                # TODO: Signal cancellation to execution service
                await manager.broadcast(execution_id, {
                    "type": "status",
                    "status": "cancelling"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, execution_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, execution_id)


async def broadcast_output(execution_id: str, message_type: str, payload):
    """
    Helper function to broadcast messages to all connected clients
    
    Args:
        execution_id: Execution ID
        message_type: Type of message (output, sip_message, traffic_stats, status, error, complete)
        payload: Message payload (string or dict)
    """
    message = {
        "type": message_type,
        "timestamp": time.time()
    }
    
    if isinstance(payload, str):
        message["data"] = payload
    elif isinstance(payload, dict):
        message.update(payload)
    else:
        message["data"] = str(payload)
    
    await manager.broadcast(execution_id, message)
