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
model = whisper.load_model("base", device=device)


manager = ConnectionManager()


def save_audio_to_wav(audio_data: bytes, file_path: str, sample_rate: int = 16000):
    audio_segment = AudioSegment(
        data=audio_data,
        sample_width=2,
        frame_rate=sample_rate,
        channels=1
    )
    audio_segment.export(file_path, format="wav")


async def transcribe_audio(audio_data: bytes) -> str:
    audio_path = "temp_audio.wav"
    save_audio_to_wav(audio_data, audio_path)

    audio = whisper.load_audio(audio_path)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    options = whisper.DecodingOptions(language="en", fp16=torch.cuda.is_available())
    result = whisper.decode(model, mel, options)

    os.remove(audio_path)  # Clean up the temporary file
    return result.text


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    audio_data = bytearray()
    data_chunk = 16000 * 2
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            audio_data.extend(data)
            while len(audio_data) >= data_chunk:  # Process every 1 second of audio (16-bit mono)
                chunk = audio_data[:data_chunk]
                transcript = await transcribe_audio(chunk)
                await manager.send(json.dumps({"message": transcript}), websocket)
                audio_data = audio_data[data_chunk:]  # Keep unprocessed data in buffer
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Unexpected error: {e}")
        await websocket.close()



