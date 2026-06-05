"""Whisper transcription using whisper-cpp."""

from __future__ import annotations
import subprocess
import tempfile
import os
from pathlib import Path


# Default model path (whisper.cpp convention)
DEFAULT_MODEL = Path.home() / ".cache" / "whisper" / "ggml-base.en.bin"

# Alternative paths to check
MODEL_PATHS = [
    DEFAULT_MODEL,
    Path("/usr/local/share/whisper-cpp/models/ggml-base.en.bin"),
    Path("/opt/homebrew/share/whisper-cpp/models/ggml-base.en.bin"),
    Path.home() / "whisper.cpp" / "models" / "ggml-base.en.bin",
]


def find_model() -> Path | None:
    """Find the whisper model file."""
    for path in MODEL_PATHS:
        if path.exists():
            return path
    return None


def find_whisper_binary() -> str | None:
    """Find the whisper-cpp binary."""
    # Check common names (whisper-cli is the homebrew version)
    names = ["whisper-cli", "whisper-cpp", "whisper", "main"]

    for name in names:
        result = subprocess.run(
            ["which", name],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()

    # Check homebrew paths
    brew_paths = [
        "/opt/homebrew/bin/whisper-cli",
        "/opt/homebrew/bin/whisper-cpp",
        "/usr/local/bin/whisper-cli",
        "/usr/local/bin/whisper-cpp",
    ]
    for path in brew_paths:
        if os.path.exists(path):
            return path

    return None


def transcribe(audio_data: bytes, model_path: Path | None = None) -> str:
    """
    Transcribe audio data using whisper-cpp.

    Args:
        audio_data: Raw audio bytes (webm/opus format)
        model_path: Path to model file (auto-detected if None)

    Returns:
        Transcribed text
    """
    if model_path is None:
        model_path = find_model()
        if model_path is None:
            raise RuntimeError(
                "Whisper model not found. Run: "
                "whisper-cpp-download-ggml-model base.en"
            )

    whisper_bin = find_whisper_binary()
    if whisper_bin is None:
        raise RuntimeError(
            "whisper-cpp not found. Run: brew install whisper-cpp"
        )

    # Write audio to temp file
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
        f.write(audio_data)
        audio_path = f.name

    # Convert to WAV using ffmpeg (whisper-cpp needs WAV)
    wav_path = audio_path.replace(".webm", ".wav")

    try:
        # Convert with ffmpeg
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", audio_path,
                "-ar", "16000",  # 16kHz sample rate
                "-ac", "1",      # mono
                "-f", "wav",
                wav_path
            ],
            check=True,
            capture_output=True,
            timeout=10
        )

        # Run whisper
        result = subprocess.run(
            [
                whisper_bin,
                "-m", str(model_path),
                "-f", wav_path,
                "-nt",  # no timestamps in output
                "-np",  # no prints except results
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"Whisper stderr: {result.stderr}")
            return ""

        # Parse output - whisper-cpp outputs text directly
        text = result.stdout.strip()

        # Remove any leading/trailing whitespace and brackets
        text = text.strip()
        if text.startswith("[") and "]" in text:
            # Remove timestamp prefix if present
            text = text.split("]", 1)[-1].strip()

        return text

    finally:
        # Cleanup temp files
        for path in [audio_path, wav_path]:
            try:
                os.unlink(path)
            except OSError:
                pass


if __name__ == "__main__":
    # Test model detection
    model = find_model()
    print(f"Model found: {model}")

    binary = find_whisper_binary()
    print(f"Binary found: {binary}")
