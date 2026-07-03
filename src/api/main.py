"""FastAPI entry point for the Jarvis local API."""

from __future__ import annotations

from dotenv import load_dotenv
from fastapi import FastAPI, Request

from src.api.logger import get_logger, log_request
from src.api.routes.chat import router as chat_router
from src.api.routes.voice import router as voice_router


load_dotenv()

app = FastAPI(title="Jarvis API")
app.include_router(chat_router)
app.include_router(voice_router)


@app.on_event("startup")
def startup() -> None:
    """Log that the API has started."""
    get_logger().info("Jarvis API started")


@app.middleware("http")
async def request_logger(request: Request, call_next):
    """Log every HTTP request before it reaches a route."""
    session_id = request.headers.get("X-Session-ID") or request.query_params.get("session_id")
    log_request(request.url.path, session_id)
    return await call_next(request)


@app.get("/health")
def health() -> dict[str, str]:
    """Return a simple health response for local checks."""
    return {"status": "ok"}
