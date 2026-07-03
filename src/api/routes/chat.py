"""Chat route for Jarvis text conversations."""

from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.auth import require_api_key
from src.api.session import get_session
from src.llm.infer import infer
from src.memory.memory import save_memory


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


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Generate a local Jarvis response for a text message."""
    message = request.message.strip()
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="message must not be empty",
        )

    session_id, history = get_session(request.session_id)
    history.append({"role": "user", "content": message})

    response = infer(build_history_prompt(history))
    history.append({"role": "assistant", "content": response})
    save_memory(history=history)

    return ChatResponse(response=response, session_id=session_id)
