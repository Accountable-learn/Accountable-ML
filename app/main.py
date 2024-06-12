from fastapi import FastAPI
from .routers import webSocket
from fastapi.middleware.cors import CORSMiddleware


"""
TODO: Here are a couple of things to be done
1. WebSocket for real time communication
    - Socket set up - Done
    - Try to stream the audio via the socket
    - Connect to FE
2. Verify JWT for controlled access 
    - Add authentication to verify JWT
3. Add Whisper model
    - 
"""

app = FastAPI()


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webSocket.router)