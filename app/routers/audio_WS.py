from fastapi import WebSocket, APIRouter

import tempfile
from app.routers.connection_manager import ConnectionManager
from app.services import speech_to_text
import os
import asyncio
# TODO: Disable ssl for now
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

router = APIRouter(
    prefix="/speech_to_text",
    tags=['WebSocket']
)

manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio_file:
        audio_file_path = temp_audio_file.name

    try:
        await asyncio.gather(
            speech_to_text.accumulate_audio_data(websocket, manager, audio_file_path),
            speech_to_text.transcribe_periodically(websocket, manager, audio_file_path)
        )
    finally:
        # Clean up
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)
