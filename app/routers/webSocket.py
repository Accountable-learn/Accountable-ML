from fastapi import APIRouter, Depends, status, HTTPException, WebSocket, WebSocketDisconnect
import json
import numpy as np
import logging
import sys

router = APIRouter(
    prefix="/speech_to_text",
    tags=['WebSocket']
)

class ConnectionManager:
    """Class defining socket events"""

    def __init__(self):
        """init method, keeping track of connections"""
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        """connect event"""
        # Process JWT first
        await websocket.accept()
        await websocket.send_text(json.dumps("Hi from FASTAPI"))
        self.active_connections.append(websocket)

    async def send(self, message: str, websocket: WebSocket):
        """Direct Message"""
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            self.disconnect(websocket)

    def disconnect(self, websocket: WebSocket):
        """disconnect event"""
        self.active_connections.remove(websocket)


manager = ConnectionManager()
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)


# WebSocket endpoint for real time speech to text recognition
# Swaggers doesn't support websocket for documentation....
# ws://localhost:8000/speech_to_text/ws
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            logger.debug("Got data from websocket")
            audio_data = np.frombuffer(data, dtype=np.float32)
            # Process data here
            await manager.send(f"Received: {len(audio_data)} audio", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)