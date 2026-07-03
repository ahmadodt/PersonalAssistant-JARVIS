"""Run local LLM inference with llama-cpp-python."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from collections.abc import Iterator

from dotenv import load_dotenv
from llama_cpp import Llama


DEFAULT_HF_REPO = "microsoft/Phi-3-mini-4k-instruct-gguf"
DEFAULT_HF_FILENAME = "Phi-3-mini-4k-instruct-q4.gguf"
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


def load_model(repo_id: str, filename: str) -> Llama:
    """Download (if needed) and load a GGUF model from HuggingFace Hub."""
    return Llama.from_pretrained(
        repo_id=repo_id,
        filename=filename,
        n_gpu_layers=-1 if gpu_available() else 0,
        n_ctx=4096,
        verbose=False,
    )


def build_prompt(prompt: str, system_prompt: str = DEFAULT_SYSTEM_PROMPT) -> str:
    """Format a simple instruction prompt for local chat-style models."""
    return f"System: {system_prompt}\nUser: {prompt.strip()}\nAssistant:"


def _stream_tokens(chunks: Iterator[dict]) -> Iterator[str]:
    """Yield text tokens from llama.cpp streaming chunks."""
    for chunk in chunks:
        choices = chunk.get("choices") or []
        if not choices:
            continue
        token = choices[0].get("text", "")
        if token:
            yield token


def infer(
    prompt: str,
    repo_id: str | None = None,
    filename: str | None = None,
    max_tokens: int = 256,
    temperature: float = 0.7,
    stream: bool = False,
) -> str | Iterator[str]:
    """Run a prompt through a HuggingFace GGUF model."""
    load_dotenv()
    resolved_repo = repo_id or os.getenv("JARVIS_HF_REPO") or DEFAULT_HF_REPO
    resolved_filename = filename or os.getenv("JARVIS_HF_FILENAME") or DEFAULT_HF_FILENAME

    llm = load_model(resolved_repo, resolved_filename)
    result = llm(
        build_prompt(prompt),
        max_tokens=max_tokens,
        temperature=temperature,
        stop=["User:", "System:"],
        stream=stream,
    )

    if stream:
        return _stream_tokens(result)

    return result["choices"][0]["text"].strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local LLM inference.")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--repo", help=f"HuggingFace repo ID. Default: {DEFAULT_HF_REPO}")
    parser.add_argument("--filename", help=f"GGUF filename in the repo. Default: {DEFAULT_HF_FILENAME}")
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.7)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(infer(args.prompt, args.repo, args.filename, args.max_tokens, args.temperature))


if __name__ == "__main__":
    main()
