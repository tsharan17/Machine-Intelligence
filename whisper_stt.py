"""
whisper_stt.py
Robust Whisper transcription with confidence filtering
"""

import whisper
from pathlib import Path

WHISPER_MODEL = "medium"  # base | small | medium
LANGUAGE = "en"

print("[WHISPER] Loading Whisper model...")
model = whisper.load_model(WHISPER_MODEL)
print("[WHISPER] Model loaded.")


def transcribe_audio(audio_path: Path) -> str:
    try:
        audio_path = Path(audio_path)

        if not audio_path.exists():
            print("[WHISPER ERROR] Audio file does not exist.")
            return ""

        print(f"[WHISPER] Transcribing: {audio_path.name}")

        result = model.transcribe(
            str(audio_path),
            language=LANGUAGE,
            fp16=False,
            temperature=0.0
        )

        text = result.get("text", "").strip()
        segments = result.get("segments", [])

        if not text:
            print("[WHISPER] No speech detected.")
            return ""

        if segments:
            avg_conf = sum(s["avg_logprob"] for s in segments) / len(segments)
            if avg_conf < -0.8:
                print("[WHISPER] Low confidence transcription rejected.")
                return ""

        print(f"[WHISPER] Transcription: {text}")
        return text

    except Exception as e:
        print(f"[WHISPER ERROR] {e}")
        return ""
