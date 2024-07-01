from fastapi import WebSocket, WebSocketDisconnect
import whisper
import asyncio
import torch
import json

from app.routers.audio_WS import ConnectionManager

# Load the Whisper model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("small", device=device)


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


async def accumulate_audio_data(websocket: WebSocket, manager: ConnectionManager, audio_file_path: str):
    try:
        while True:
            data = await websocket.receive_bytes()
            append_audio_to_file(data, audio_file_path)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def transcribe_periodically(websocket: WebSocket, manager: ConnectionManager, audio_file_path: str):
    try:
        while True:
            await asyncio.sleep(1)
            transcript = await transcribe_audio_file(audio_file_path)
            if transcript and websocket:
                await manager.send(json.dumps({"message": transcript}), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
