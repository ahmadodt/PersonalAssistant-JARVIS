"""In-memory and file-backed session management for Jarvis API conversations."""

from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

from src.memory.memory import load_memory, save_memory


History = list[dict[str, str]]
SESSION_DIR = Path("data/sessions")
SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

_sessions: dict[str, History] = {}


def session_path(session_id: str) -> Path:
    """Return the JSON memory path for a session."""
    return SESSION_DIR / f"{session_id}.json"


def _clean_session_id(session_id: str | None = None) -> str:
    """Use a provided safe session ID or generate a new one."""
    if not session_id:
        return str(uuid4())
    if not SESSION_ID_PATTERN.fullmatch(session_id):
        raise ValueError("session_id may only contain letters, numbers, underscores, and hyphens")
    return session_id


def get_session(session_id: str | None = None) -> tuple[str, History]:
    """Return an existing session or load one from disk."""
    resolved_session_id = _clean_session_id(session_id)
    if resolved_session_id in _sessions:
        return resolved_session_id, _sessions[resolved_session_id]

    path = session_path(resolved_session_id)
    history = load_memory(path) if path.exists() else []
    _sessions[resolved_session_id] = history
    return resolved_session_id, history


def save_session(session_id: str, history: History) -> None:
    """Persist a session's conversation history."""
    save_memory(session_path(_clean_session_id(session_id)), history)
