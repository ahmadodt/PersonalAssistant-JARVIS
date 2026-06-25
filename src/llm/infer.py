"""Run local LLM inference with llama-cpp-python."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from llama_cpp import Llama


DEFAULT_MODEL_PATH = Path("models/phi-3-mini.gguf")
DEFAULT_SYSTEM_PROMPT = "You are Jarvis, a helpful personal assistant."


def gpu_available() -> bool:
    """Return True when a local NVIDIA GPU appears available."""
    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        return False
    try:
        result = subprocess.run(
            [nvidia_smi],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return False
    return result.returncode == 0


def resolve_model_path(model_path: str | None = None) -> Path:
    """Choose model path from CLI, .env, or the default path."""
    load_dotenv()
    return Path(model_path or os.getenv("JARVIS_LLAMACPP_MODEL_PATH") or DEFAULT_MODEL_PATH)


def build_prompt(prompt: str, system_prompt: str = DEFAULT_SYSTEM_PROMPT) -> str:
    """Format a simple instruction prompt for local chat-style models."""
    return f"System: {system_prompt}\nUser: {prompt.strip()}\nAssistant:"


def infer(
    prompt: str,
    model_path: str | None = None,
    max_tokens: int = 256,
    temperature: float = 0.7,
) -> str:
    """Run a prompt through a local GGUF model and return the response text."""
    resolved_model_path = resolve_model_path(model_path)
    if not resolved_model_path.exists():
        raise FileNotFoundError(f"Model file not found: {resolved_model_path}")

    llm = Llama(
        model_path=str(resolved_model_path),
        n_gpu_layers=-1 if gpu_available() else 0,
        n_ctx=4096,
        verbose=False,
    )
    result = llm(
        build_prompt(prompt),
        max_tokens=max_tokens,
        temperature=temperature,
        stop=["User:", "System:"],
    )
    return result["choices"][0]["text"].strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local LLM inference.")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--model")
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.7)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(infer(args.prompt, args.model, args.max_tokens, args.temperature))


if __name__ == "__main__":
    main()

