"""FastAPI entry point for the Jarvis local API."""

from __future__ import annotations

from dotenv import load_dotenv
from fastapi import FastAPI

from src.api.routes.chat import router as chat_router


load_dotenv()

app = FastAPI(title="Jarvis API")
app.include_router(chat_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Return a simple health response for local checks."""
    return {"status": "ok"}
