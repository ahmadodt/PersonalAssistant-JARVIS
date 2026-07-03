"""API key authentication for Jarvis routes."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import Header, HTTPException, status


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Reject requests without the configured X-API-Key header."""
    load_dotenv()
    expected_key = os.getenv("JARVIS_API_KEY")

    if not expected_key or x_api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
