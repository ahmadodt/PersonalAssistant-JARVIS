# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Jarvis is a local-first, voice-driven personal AI assistant. All core features must run offline with no paid APIs. The planned long-term path is: local voice loop → FastAPI backend → iPhone/Android access.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

`llama-cpp-python` needs a separate GPU build for CUDA — replace `cu130` with the installed CUDA version:

```powershell
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu130
```

Without it, `src/llm/infer.py` falls back to CPU automatically.

## Running Modules

Each `src/` module is a standalone CLI script:

```powershell
# Record microphone audio
python src/audio/record.py --output recordings/test.wav --duration 5

# Transcribe audio
python src/stt/transcribe.py --input recordings/test.wav

# Run local LLM
python src/llm/infer.py --prompt "hello" --model models/phi-3-mini.gguf

# Speak text
python src/tts/speak.py --text "Hello, I am Jarvis."
```

## Architecture

The intended voice loop pipeline is: **audio/record → stt/transcribe → llm/infer → tts/speak**.

Each stage is a self-contained Python module under `src/` with a public function and a `main()` CLI entry point. Modules are designed to be imported by an orchestrator (not yet built) or run standalone.

- `src/audio/record.py` — captures mic input via `sounddevice`, writes 16 kHz mono WAV to `recordings/`
- `src/stt/transcribe.py` — loads a faster-whisper model and returns a transcript string
- `src/llm/infer.py` — loads a GGUF model via `llama-cpp-python`; auto-detects GPU via `nvidia-smi` and sets `n_gpu_layers=-1` if available, else CPU only
- `src/tts/speak.py` — synthesizes speech with Piper, writes a temp WAV, plays it via `sounddevice`, then deletes the temp file

**Model files** go in `models/` (GGUF format). **Piper voice models** go in `voices/` (`.onnx` + `.onnx.json` pairs).

## Configuration

All tuneable values come from `.env` (loaded via `python-dotenv`). Never hard-code paths, model filenames, or device-specific values. The env vars follow a `JARVIS_` prefix convention:

| Variable | Used by |
|---|---|
| `JARVIS_LLAMACPP_MODEL_PATH` | `src/llm/infer.py` |
| `JARVIS_PIPER_VOICE` / `JARVIS_PIPER_MODEL_PATH` | `src/tts/speak.py` |
| `JARVIS_WHISPER_MODEL` | `src/stt/transcribe.py` (consumed by orchestrator, not yet wired) |
| `JARVIS_RECORD_SECONDS`, `JARVIS_SAMPLE_RATE`, `JARVIS_AUDIO_CHANNELS` | audio recording defaults |
| `JARVIS_API_HOST`, `JARVIS_API_PORT`, `JARVIS_API_TOKEN` | future FastAPI layer |

## Design Rules

- No paid APIs. No cloud-only dependencies for core assistant behavior.
- Modules must stay small and swappable.
- All configurable values go in `.env` / environment variables.
- Planned stack additions (not yet implemented): FastAPI, LangGraph, LiteLLM, MCP, Docker.
