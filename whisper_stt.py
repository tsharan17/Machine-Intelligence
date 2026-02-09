"""
whisper_stt.py

Handles speech-to-text using OpenAI Whisper (local).
Takes a WAV file path and returns transcribed text.
"""

import whisper
from pathlib import Path

# -------- Configuration --------
WHISPER_MODEL = "base"   # small | base | medium | large
LANGUAGE = "en"

# Load model once
print("[WHISPER] Loading Whisper model...")
model = whisper.load_model(WHISPER_MODEL)
print("[WHISPER] Model loaded.")


def transcribe_audio(audio_path: Path) -> str:
    """
    Transcribes the given audio file using Whisper.
    Returns transcribed text or empty string on failure.
    """
    try:
        audio_path = Path(audio_path)

        if not audio_path.exists():
            print("[WHISPER ERROR] Audio file does not exist.")
            return ""

        print(f"[WHISPER] Transcribing: {audio_path.name}")

        result = model.transcribe(
            str(audio_path),
            language=LANGUAGE,
            fp16=False  # REQUIRED for Windows CPU
        )

        text = result.get("text", "").strip()

        if not text:
            print("[WHISPER] No speech detected.")
            return ""

        print(f"[WHISPER] Transcription: {text}")
        return text

    except Exception as e:
        print(f"[WHISPER ERROR] {e}")
        return ""
