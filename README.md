# Jarvis

Jarvis is a personal, local-first AI assistant. The goal is a voice-driven assistant that runs without paid APIs and can later be reached from iPhone and Android through a local FastAPI backend.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

### GPU Support (CUDA)

`llama-cpp-python` requires a separate install to enable GPU inference. Replace `cu130` with your CUDA version (e.g. `cu118`, `cu121`, `cu124`, `cu126`, `cu128`):

```powershell
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu130
```

Without this, inference falls back to CPU automatically.

## Record Audio

```powershell
python src/audio/record.py --output recordings/test.wav --duration 5
```

## Transcribe Audio

```powershell
python src/stt/transcribe.py --input recordings/test.wav
```

## Run Local LLM Inference

The model is downloaded from HuggingFace Hub on first run and cached locally.

```powershell
python src/llm/infer.py --prompt "hello"
```

To use a different model, set `JARVIS_HF_REPO` and `JARVIS_HF_FILENAME` in `.env`, or pass `--repo` and `--filename` flags.

Jarvis should work without paid APIs. Models, voices, memory, and assistant behavior should be local by default.


## Running with Docker

Create a local `.env` file before starting the container and set an API key:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set:

```text
JARVIS_API_KEY=your-local-secret
```

Place local model files in `models/` and Piper voice files in `voices/`. These folders are mounted into the container so large local assets are not baked into the image.

Start the API service:

```powershell
docker-compose up --build
```

The API runs on `http://127.0.0.1:8000` and uses the same mounted `data/` and `logs/` folders across restarts.
