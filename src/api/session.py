"""In-memory session management for Jarvis API conversations."""

from __future__ import annotations

from uuid import uuid4

from src.memory.memory import load_memory


History = list[dict[str, str]]

_sessions: dict[str, History] = {}


def get_session(session_id: str | None = None) -> tuple[str, History]:
    """Return an existing session or create a new one."""
    if session_id and session_id in _sessions:
        return session_id, _sessions[session_id]

    new_session_id = session_id or str(uuid4())
    history = load_memory()
    _sessions[new_session_id] = history
    return new_session_id, history
