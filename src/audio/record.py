"""Record microphone audio to a WAV file."""

from __future__ import annotations

import argparse
from pathlib import Path

import sounddevice as sd
from scipy.io.wavfile import write


DEFAULT_DURATION_SECONDS = 5
DEFAULT_SAMPLE_RATE = 16_000
DEFAULT_CHANNELS = 1
DEFAULT_OUTPUT_PATH = Path("recordings/input.wav")


def record_audio(
    output_path: Path,
    duration_seconds: int = DEFAULT_DURATION_SECONDS,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    channels: int = DEFAULT_CHANNELS,
) -> Path:
    """Record audio from the default microphone and save it as a WAV file."""
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be greater than 0")
    if sample_rate <= 0:
        raise ValueError("sample_rate must be greater than 0")
    if channels <= 0:
        raise ValueError("channels must be greater than 0")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Recording {duration_seconds} seconds of audio...")
    audio = sd.rec(
        int(duration_seconds * sample_rate),
        samplerate=sample_rate,
        channels=channels,
        dtype="int16",
    )
    sd.wait()
    write(output_path, sample_rate, audio)
    print(f"Saved recording to {output_path}")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record microphone audio to WAV.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION_SECONDS)
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_SAMPLE_RATE)
    parser.add_argument("--channels", type=int, default=DEFAULT_CHANNELS)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    record_audio(args.output, args.duration, args.sample_rate, args.channels)


if __name__ == "__main__":
    main()

