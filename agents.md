# Jarvis Agent Context

Jarvis is a personal AI assistant designed to run locally with no paid APIs. The long-term goal is an always-available voice assistant accessible from iPhone and Android through a backend service.

## Current Phase

Phase 1: local foundation.

- Record audio from the microphone.
- Transcribe speech with faster-whisper.
- Generate responses with llama.cpp through llama-cpp-python.
- Speak responses with piper-tts.
- Play audio through local speakers.
- Store persistent memory across sessions.

## Stack

- Python
- sounddevice and scipy
- faster-whisper
- llama-cpp-python
- piper-tts
- LiteLLM
- FastAPI
- Docker
- LangGraph
- MCP

## Rules

- No paid APIs.
- No cloud-only dependencies for core assistant behavior.
- Prefer local-first, offline-capable components.
- Keep modules small and easy to replace.
- Do not hard-code secrets, paths, model files, or device-specific settings.
- Put configurable values in environment variables or config files.

## Folder Structure

```text
jarvis/
├── agents.md
├── README.md
├── PLAN.md
├── requirements.txt
├── .env.example
├── .gitignore
├── models/
│   └── .gitkeep
└── src/
    ├── audio/
    │   └── record.py
    ├── stt/
    │   └── transcribe.py
    └── llm/
        └── infer.py
```

