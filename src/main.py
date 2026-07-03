"""Run Jarvis as a local voice assistant loop."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from audio.record import (
    DEFAULT_CHANNELS,
    DEFAULT_DURATION_SECONDS,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_SAMPLE_RATE,
    record_audio,
)
from llm.infer import infer
from memory.memory import DEFAULT_MEMORY_PATH, load_memory, save_memory
from stt.transcribe import DEFAULT_COMPUTE_TYPE, DEFAULT_DEVICE, DEFAULT_MODEL_SIZE, transcribe_audio
from tts.speak import speak


EXIT_COMMANDS = {"exit", "quit"}
MAX_HISTORY_MESSAGES = 12


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if parsed <= 0:
        raise ValueError(f"{name} must be greater than 0")
    return parsed


def build_history_prompt(history: list[dict[str, str]]) -> str:
    """Format recent conversation history for the local LLM."""
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


def is_exit_command(text: str) -> bool:
    """Return True when the transcribed text asks Jarvis to stop."""
    normalized = text.strip().lower().strip(".!?")
    return normalized in EXIT_COMMANDS


def run_voice_loop() -> None:
    """Run mic -> STT -> LLM -> TTS until the user says exit or quit."""
    load_dotenv()

    record_seconds = _env_int("JARVIS_RECORD_SECONDS", DEFAULT_DURATION_SECONDS)
    sample_rate = _env_int("JARVIS_SAMPLE_RATE", DEFAULT_SAMPLE_RATE)
    channels = _env_int("JARVIS_AUDIO_CHANNELS", DEFAULT_CHANNELS)
    whisper_model = os.getenv("JARVIS_WHISPER_MODEL") or DEFAULT_MODEL_SIZE
    memory_path = Path(os.getenv("JARVIS_MEMORY_PATH") or DEFAULT_MEMORY_PATH)

    print("Loading memory...")
    history = load_memory(memory_path)
    print(f"Loaded {len(history)} memory messages from {memory_path}")
    print("Say 'exit' or 'quit' to stop Jarvis.")

    while True:
        print("\nRecording...")
        audio_path = record_audio(
            DEFAULT_OUTPUT_PATH,
            duration_seconds=record_seconds,
            sample_rate=sample_rate,
            channels=channels,
        )

        print("Transcribing...")
        user_text = transcribe_audio(
            audio_path,
            model_size=whisper_model,
            device=DEFAULT_DEVICE,
            compute_type=DEFAULT_COMPUTE_TYPE,
        )
        print(f"You: {user_text or '[no speech detected]'}")

        if not user_text:
            print("No speech detected. Listening again.")
            continue

        if is_exit_command(user_text):
            print("Exit command detected. Goodbye.")
            break

        history.append({"role": "user", "content": user_text})

        print("Generating response...")
        assistant_text = infer(build_history_prompt(history))
        print(f"Jarvis: {assistant_text}")

        history.append({"role": "assistant", "content": assistant_text})

        print("Saving memory...")
        save_memory(memory_path, history)

        print("Speaking...")
        speak(assistant_text)


def main() -> None:
    run_voice_loop()


if __name__ == "__main__":
    main()
