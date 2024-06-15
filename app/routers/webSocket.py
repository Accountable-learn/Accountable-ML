from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import numpy as np
import whisper
import torch
import json
import os

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
        await websocket.send_text(json.dumps({"message": "Hi from FASTAPI"}))
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

# Load the Whisper model
model_path = os.path.join(os.path.dirname(__file__), '../models/base.en.pt')
model = whisper.load_model(model_path)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        audio_chunks = []
        accumulated_transcription = ''
        while True:
            data = await websocket.receive_bytes()
            audio_data = np.frombuffer(data, dtype=np.float32)
            audio_chunks.append(audio_data)
            # Process data here
            if len(audio_chunks) > 10:  # Arbitrary condition to process chunks
                audio_input = np.concatenate(audio_chunks)
                audio_chunks = []  # Reset chunks after processing

                # Convert the NumPy array to a PyTorch tensor and move to GPU if available
                audio_tensor = torch.tensor(audio_input, dtype=torch.float32).to(device)

                # Perform the transcription
                transcription_result = model.transcribe(audio_tensor)
                transcription_text = transcription_result['text']
                accumulated_transcription += transcription_text + " "

                # Send the transcribed text back to the client
                # logger.debug(accumulated_transcription)
                await manager.send(json.dumps({"text": accumulated_transcription}), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
