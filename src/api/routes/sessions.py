"""Session management routes for the Jarvis API."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from src.api.auth import require_api_key
from src.api.logger import get_logger, log_request
from src.api.session import delete_session, list_sessions


router = APIRouter(dependencies=[Depends(require_api_key)])


@router.get("/sessions")
def sessions() -> dict[str, list[str]] | JSONResponse:
    """Return active in-memory session IDs."""
    log_request("/sessions")
    try:
        return {"sessions": list_sessions()}
    except Exception as exc:
        get_logger().exception("error endpoint=/sessions")
        return JSONResponse(status_code=500, content={"error": str(exc)})


@router.delete("/sessions/{session_id}")
def remove_session(session_id: str) -> dict[str, str] | JSONResponse:
    """Delete a session from memory and disk."""
    log_request("/sessions/{session_id}", session_id)
    try:
        if not delete_session(session_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="session not found",
            )
        return {"deleted": session_id}
    except HTTPException:
        raise
    except Exception as exc:
        get_logger().exception("error endpoint=/sessions/%s", session_id)
        return JSONResponse(status_code=500, content={"error": str(exc)})
