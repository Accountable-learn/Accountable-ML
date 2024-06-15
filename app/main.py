from fastapi import FastAPI
from .routers import webSocket
from fastapi.middleware.cors import CORSMiddleware
import logging
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

"""
TODO: Here are a couple of things to be done
1. WebSocket for real time communication
    - Socket set up - Done
    - Try to stream the audio via the socket from FE
    - Configure NGINX to redirect websocket for production
    - Connect to FE
    
2. Verify JWT for controlled access
    - Add authentication to verify JWT
    - Given a JWT, send it to backend auth server to do the authentication
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

@app.get('/helloworld')
def hello():
    logger.debug('this is a debug message')
    return "hello world!"


# Register the endpoint
app.include_router(webSocket.router)
