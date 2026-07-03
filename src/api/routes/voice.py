"""Voice route for Jarvis audio conversations."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from src.api.auth import require_api_key
from src.api.logger import get_logger, log_request
from src.api.routes.chat import build_history_prompt
from src.api.session import get_session, save_session
from src.llm.infer import infer
from src.stt.transcribe import transcribe_audio


SUPPORTED_AUDIO_SUFFIXES = {".wav", ".mp3"}

router = APIRouter(dependencies=[Depends(require_api_key)])


@router.post("/voice")
def voice(
    audio: UploadFile = File(...),
    session_id: str | None = Form(default=None),
) -> dict[str, str] | JSONResponse:
    """Transcribe uploaded audio and return a Jarvis response."""
    resolved_session_id: str | None = session_id
    temp_path: Path | None = None
    log_request("/voice", resolved_session_id)

    try:
        suffix = Path(audio.filename or "").suffix.lower()
        if suffix not in SUPPORTED_AUDIO_SUFFIXES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="audio must be a WAV or MP3 file",
            )

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            shutil.copyfileobj(audio.file, temp_file)

        resolved_session_id, history = get_session(session_id)
        log_request("/voice", resolved_session_id)

        transcription = transcribe_audio(temp_path)
        if not transcription:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="audio did not contain transcribable speech",
            )

        history.append({"role": "user", "content": transcription})
        response = infer(build_history_prompt(history))
        history.append({"role": "assistant", "content": response})
        save_session(resolved_session_id, history)

        return {
            "transcription": transcription,
            "response": response,
            "session_id": resolved_session_id,
        }
    except HTTPException:
        raise
    except Exception as exc:
        get_logger().exception("error endpoint=/voice session_id=%s", resolved_session_id)
        return JSONResponse(status_code=500, content={"error": str(exc)})
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
