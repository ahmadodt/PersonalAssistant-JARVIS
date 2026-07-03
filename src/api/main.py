"""FastAPI entry point for the Jarvis local API."""

from __future__ import annotations

import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse

from src.api.logger import get_logger, log_request
from src.api.routes.chat import router as chat_router
from src.api.routes.sessions import router as sessions_router
from src.api.routes.voice import router as voice_router


load_dotenv()

CLIENT_INDEX = Path(__file__).resolve().parents[1] / "client" / "index.html"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000

app = FastAPI(title="Jarvis API")
app.include_router(chat_router)
app.include_router(voice_router)
app.include_router(sessions_router)


def get_api_host() -> str:
    """Read the API bind host from the environment."""
    return os.getenv("JARVIS_HOST") or DEFAULT_HOST


def get_api_port() -> int:
    """Read the API bind port from the environment."""
    value = os.getenv("JARVIS_PORT") or str(DEFAULT_PORT)
    return int(value)


@app.on_event("startup")
def startup() -> None:
    """Log that the API has started."""
    get_logger().info("Jarvis API started on %s:%s", get_api_host(), get_api_port())


@app.middleware("http")
async def request_logger(request: Request, call_next):
    """Log every HTTP request before it reaches a route."""
    session_id = request.headers.get("X-Session-ID") or request.query_params.get("session_id")
    log_request(request.url.path, session_id)
    return await call_next(request)


@app.get("/")
def client() -> FileResponse:
    """Serve the simple mobile web client."""
    return FileResponse(CLIENT_INDEX)


@app.get("/health")
def health() -> dict[str, str]:
    """Return a simple health response for local checks."""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host=get_api_host(), port=get_api_port())
