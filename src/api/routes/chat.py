"""Chat routes for Jarvis text conversations."""

from __future__ import annotations

import json
from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from src.api.auth import require_api_key
from src.api.logger import get_logger, log_request
from src.api.session import get_session, save_session
from src.llm.infer import infer


MAX_HISTORY_MESSAGES = 12

router = APIRouter(dependencies=[Depends(require_api_key)])


class ChatRequest(BaseModel):
    """Incoming chat request."""

    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Outgoing chat response."""

    response: str
    session_id: str


def build_history_prompt(history: list[dict[str, str]]) -> str:
    """Format recent session history for the local LLM."""
    recent_history = history[-MAX_HISTORY_MESSAGES:]
    lines = [
        "Use the following conversation history to answer the latest user message.",
        "Keep the reply concise and useful.",
        "",
        "Conversation:",
    ]

    for message in recent_history:
        role = message["role"].title()
        content = message["content"].strip()
        if content:
            lines.append(f"{role}: {content}")

    lines.append("")
    lines.append("Assistant:")
    return "\n".join(lines)


def _sse(payload: dict[str, str | bool]) -> str:
    """Format one Server-Sent Events message."""
    return f"data: {json.dumps(payload)}\n\n"


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse | JSONResponse:
    """Generate a local Jarvis response for a text message."""
    log_request("/chat", request.session_id)
    try:
        message = request.message.strip()
        if not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="message must not be empty",
            )

        session_id, history = get_session(request.session_id)
        log_request("/chat", session_id)
        history.append({"role": "user", "content": message})

        response = infer(build_history_prompt(history))
        history.append({"role": "assistant", "content": response})
        save_session(session_id, history)

        return ChatResponse(response=response, session_id=session_id)
    except HTTPException:
        raise
    except Exception as exc:
        get_logger().exception("error endpoint=/chat session_id=%s", request.session_id)
        return JSONResponse(status_code=500, content={"error": str(exc)})


@router.post("/chat/stream")
def chat_stream(request: ChatRequest) -> StreamingResponse | JSONResponse:
    """Stream a local Jarvis response as Server-Sent Events."""
    log_request("/chat/stream", request.session_id)
    try:
        message = request.message.strip()
        if not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="message must not be empty",
            )

        session_id, history = get_session(request.session_id)
        log_request("/chat/stream", session_id)
        history.append({"role": "user", "content": message})
        prompt = build_history_prompt(history)

        def token_events() -> Iterator[str]:
            response_parts: list[str] = []
            try:
                for token in infer(prompt, stream=True):
                    response_parts.append(token)
                    yield _sse({"token": token})

                response = "".join(response_parts).strip()
                history.append({"role": "assistant", "content": response})
                save_session(session_id, history)
                yield _sse({"done": True, "session_id": session_id})
            except Exception as exc:
                get_logger().exception("error endpoint=/chat/stream session_id=%s", session_id)
                yield _sse({"error": str(exc)})

        return StreamingResponse(token_events(), media_type="text/event-stream")
    except HTTPException:
        raise
    except Exception as exc:
        get_logger().exception("error endpoint=/chat/stream session_id=%s", request.session_id)
        return JSONResponse(status_code=500, content={"error": str(exc)})
