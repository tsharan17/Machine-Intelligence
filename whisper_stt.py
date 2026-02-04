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


# Load model once (IMPORTANT: do NOT load inside function repeatedly)
print("[WHISPER] Loading Whisper model...")
model = whisper.load_model(WHISPER_MODEL)
print("[WHISPER] Model loaded.")


def transcribe_audio(audio_path):
    """
    Transcribes the given audio file using Whisper.
    Returns transcribed text or None on failure.
    """

    try:
        audio_path = Path(audio_path)

        if not audio_path.exists():
            print("[WHISPER] Audio file does not exist.")
            return None

        print(f"[WHISPER] Transcribing: {audio_path.name}")

        result = model.transcribe(
            str(audio_path),
            language=LANGUAGE,
            fp16=False  # IMPORTANT for Windows CPUs
        )

        text = result.get("text", "").strip()

        if not text:
            print("[WHISPER] No speech detected.")
            return None

        print(f"[WHISPER] Transcription complete.")
        return text

    except Exception as e:
        print(f"[WHISPER ERROR] {e}")
        return None
