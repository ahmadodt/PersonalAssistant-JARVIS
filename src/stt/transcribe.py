"""Transcribe a WAV file with faster-whisper."""

from __future__ import annotations

import argparse
from pathlib import Path

from faster_whisper import WhisperModel


DEFAULT_MODEL_SIZE = "base"
DEFAULT_DEVICE = "cpu"
DEFAULT_COMPUTE_TYPE = "int8"


def transcribe_audio(
    input_path: Path,
    model_size: str = DEFAULT_MODEL_SIZE,
    device: str = DEFAULT_DEVICE,
    compute_type: str = DEFAULT_COMPUTE_TYPE,
) -> str:
    """Transcribe an audio file and return the combined text."""
    if not input_path.exists():
        raise FileNotFoundError(f"Audio file not found: {input_path}")
    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: {input_path}")

    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, _info = model.transcribe(str(input_path))
    return " ".join(segment.text.strip() for segment in segments).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transcribe audio with faster-whisper.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--model", default=DEFAULT_MODEL_SIZE)
    parser.add_argument("--device", default=DEFAULT_DEVICE)
    parser.add_argument("--compute-type", default=DEFAULT_COMPUTE_TYPE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    text = transcribe_audio(args.input, args.model, args.device, args.compute_type)
    print(text)


if __name__ == "__main__":
    main()

