from fastapi import APIRouter, Depends, status, HTTPException, WebSocket, WebSocketDisconnect

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
        await websocket.accept()
        self.active_connections.append(websocket)

    async def send(self, message: str, websocket: WebSocket):
        """Direct Message"""
        await websocket.send_text(message)

    def disconnect(self, websocket: WebSocket):
        """disconnect event"""
        self.active_connections.remove(websocket)


manager = ConnectionManager()



# WebSocket endpoint for real time speech to text recognition
# Swaggers doesn't support websocket for documentation....
# ws://localhost:8000/speech_to_text/ws
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send(f"Received:{data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.send("Bye!!!", websocket)

