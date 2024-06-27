from fastapi import FastAPI, HTTPException, Request, status
from .custom_http_res import format_res
from .routers import audio_WS, questions
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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


@app.get('/helloworld', response_class=JSONResponse)
def hello():
    return format_res(200, "hello world!")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return format_res(exc.status_code, {"detail": exc.detail})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return format_res(status.HTTP_500_INTERNAL_SERVER_ERROR, {"detail": str(exc)})


# Register the endpoint
app.include_router(audio_WS.router)
app.include_router(questions.router)
