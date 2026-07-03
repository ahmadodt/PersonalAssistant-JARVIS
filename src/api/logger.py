"""Logging helpers for the Jarvis API."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path


LOG_PATH = Path("logs/jarvis.log")


def get_logger() -> logging.Logger:
    """Return the shared Jarvis API logger."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("jarvis.api")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def log_request(endpoint: str, session_id: str | None = None) -> None:
    """Log a request with endpoint, session, and UTC timestamp."""
    timestamp = datetime.now(timezone.utc).isoformat()
    get_logger().info("request endpoint=%s session_id=%s timestamp=%s", endpoint, session_id, timestamp)
