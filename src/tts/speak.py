"""Speak text locally with Piper TTS and sounddevice."""

from __future__ import annotations

import argparse
import os
import tempfile
import wave
from pathlib import Path

import sounddevice as sd
from dotenv import load_dotenv
from piper.voice import PiperVoice
from scipy.io import wavfile


DEFAULT_VOICE = "en_US-lessac-medium"
DEFAULT_VOICE_PATH = Path("voices") / f"{DEFAULT_VOICE}.onnx"


def resolve_voice_path(voice: str | None = None) -> Path:
    """Choose a Piper voice model path from CLI, .env, or the default voice."""
    load_dotenv()

    selected_voice = (
        voice
        or os.getenv("JARVIS_PIPER_VOICE")
        or os.getenv("JARVIS_PIPER_MODEL_PATH")
        or str(DEFAULT_VOICE_PATH)
    )

    voice_path = Path(selected_voice)
    if voice_path.suffix:
        return voice_path

    # Allow shorthand names like "en_US-lessac-medium".
    return Path("voices") / f"{selected_voice}.onnx"


def synthesize_to_wav(text: str, voice_path: Path, output_path: Path) -> Path:
    """Generate a WAV file with Piper."""
    if not text.strip():
        raise ValueError("text must not be empty")
    if not voice_path.exists():
        raise FileNotFoundError(f"Piper voice model not found: {voice_path}")

    voice = PiperVoice.load(str(voice_path))
    with wave.open(str(output_path), "wb") as wav_file:
        voice.synthesize(text, wav_file)

    return output_path


def play_wav(wav_path: Path) -> None:
    """Play a WAV file through the default speaker."""
    sample_rate, audio = wavfile.read(wav_path)
    sd.play(audio, samplerate=sample_rate)
    sd.wait()


def speak(text: str, voice: str | None = None) -> str:
    """Generate speech locally and play it through the speaker."""
    voice_path = resolve_voice_path(voice)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        wav_path = Path(tmp_file.name)

    try:
        synthesize_to_wav(text, voice_path, wav_path)
        play_wav(wav_path)
    finally:
        wav_path.unlink(missing_ok=True)

    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Speak text with local Piper TTS.")
    parser.add_argument("--text", required=True, help="Text for Jarvis to speak.")
    parser.add_argument(
        "--voice",
        help=f"Piper voice model path or voice name. Default: {DEFAULT_VOICE}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    speak(args.text, args.voice)


if __name__ == "__main__":
    main()
