from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import numpy as np
import whisper
import torch
import os
import wave
import ffmpeg
import io
import json
from pydub import AudioSegment

# Disable ssl for now
import ssl

from pydub.exceptions import CouldntDecodeError

ssl._create_default_https_context = ssl._create_unverified_context

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


# Load the Whisper model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("small", device=device)


manager = ConnectionManager()


def append_audio_to_file(audio_data: bytes, file_path: str):
    with open(file_path, "ab") as f:
        f.write(audio_data)

async def transcribe_audio_file(file_path: str) -> str:
    # Load the audio file
    audio = whisper.load_audio(file_path)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    options = whisper.DecodingOptions(language="en", fp16=torch.cuda.is_available())
    result = whisper.decode(model, mel, options)
    return result.text

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    audio_file_path = "accumulated_audio.mp3"
    # Clear any existing file at the start
    if os.path.exists(audio_file_path):
        os.remove(audio_file_path)

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            append_audio_to_file(data, audio_file_path)

            # Periodically transcribe the accumulated audio file
            transcript = await transcribe_audio_file(audio_file_path)
            print(transcript)
            if transcript:
                await manager.send(json.dumps({"message": transcript}), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Unexpected error: {e}")
        await websocket.close()

