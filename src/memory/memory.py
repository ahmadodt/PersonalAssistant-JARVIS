"""Persist Jarvis conversation history as local JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_MEMORY_PATH = Path("data/memory.json")


def _normalize_history(history: Any) -> list[dict[str, str]]:
    """Validate and normalize conversation history loaded from JSON."""
    if not isinstance(history, list):
        raise ValueError("memory history must be a list")

    normalized: list[dict[str, str]] = []
    for index, item in enumerate(history):
        if not isinstance(item, dict):
            raise ValueError(f"memory item {index} must be an object")

        role = item.get("role")
        content = item.get("content")
        if not isinstance(role, str) or not isinstance(content, str):
            raise ValueError(f"memory item {index} must contain string role and content")

        normalized.append({"role": role, "content": content})

    return normalized


def load_memory(path: Path | str = DEFAULT_MEMORY_PATH) -> list[dict[str, str]]:
    """Load conversation history from a JSON file."""
    memory_path = Path(path)
    if not memory_path.exists():
        return []
    if not memory_path.is_file():
        raise ValueError(f"Memory path is not a file: {memory_path}")

    with memory_path.open("r", encoding="utf-8") as file:
        return _normalize_history(json.load(file))


def save_memory(
    path: Path | str = DEFAULT_MEMORY_PATH,
    history: list[dict[str, str]] | None = None,
) -> None:
    """Save conversation history to a JSON file."""
    memory_path = Path(path)
    memory_path.parent.mkdir(parents=True, exist_ok=True)

    normalized = _normalize_history(history or [])
    with memory_path.open("w", encoding="utf-8") as file:
        json.dump(normalized, file, indent=2)
        file.write("\n")
