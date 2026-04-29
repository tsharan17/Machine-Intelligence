"""
whisper_stt.py
Robust Whisper transcription with confidence filtering.
Model loads lazily on first use — no blocking at import time.
Supports both bundled (PyInstaller) and development environments.
"""

import whisper
import os
import sys
from pathlib import Path

WHISPER_MODEL = "medium"  # base | small | medium
LANGUAGE = "en"

_model = None


def _get_model_download_root() -> str | None:
    """
    Return the directory where the bundled Whisper model lives.
    In a PyInstaller bundle, models are pre-extracted to _MEIPASS/whisper_models.
    In development, returns None so Whisper uses its default ~/.cache/whisper.
    """
    if getattr(sys, 'frozen', False):
        bundled = os.path.join(sys._MEIPASS, 'whisper_models')  # type: ignore[attr-defined]
        if os.path.isdir(bundled):
            return bundled
    return None


def get_model() -> whisper.Whisper:
    global _model
    if _model is None:
        model_dir = _get_model_download_root()
        print(f"[WHISPER] Loading '{WHISPER_MODEL}' model"
              + (f" from bundle: {model_dir}" if model_dir else " (downloading if needed)..."))
        _model = whisper.load_model(WHISPER_MODEL, download_root=model_dir)
        print("[WHISPER] Model ready.")
    return _model


def transcribe_audio(audio_path: Path) -> str:
    try:
        audio_path = Path(audio_path)

        if not audio_path.exists():
            print("[WHISPER ERROR] Audio file does not exist.")
            return ""

        print(f"[WHISPER] Transcribing: {audio_path.name}")

        result = get_model().transcribe(
            str(audio_path),
            language=LANGUAGE,
            fp16=False,
            temperature=0.0,
        )

        text = result.get("text", "").strip()
        segments = result.get("segments", [])

        if not text:
            print("[WHISPER] No speech detected.")
            return ""

        if segments:
            avg_conf = sum(s["avg_logprob"] for s in segments) / len(segments)
            if avg_conf < -0.8:
                print("[WHISPER] Low-confidence transcription rejected.")
                return ""

        print(f"[WHISPER] Transcription: {text}")
        return text

    except Exception as e:
        print(f"[WHISPER ERROR] {e}")
        return ""
