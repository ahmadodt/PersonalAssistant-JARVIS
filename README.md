# Jarvis

Jarvis is a personal, local-first AI assistant. The goal is a voice-driven assistant that runs without paid APIs and can later be reached from iPhone and Android through a local FastAPI backend.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Record Audio

```powershell
python src/audio/record.py --output recordings/test.wav --duration 5
```

## Transcribe Audio

```powershell
python src/stt/transcribe.py --input recordings/test.wav
```

## Run Local LLM Inference

```powershell
python src/llm/infer.py --prompt "hello" --model models/phi-3-mini.gguf
```

Jarvis should work without paid APIs. Models, voices, memory, and assistant behavior should be local by default.

