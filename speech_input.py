"""
speech_input.py

Handles microphone audio capture for Machine Intelligence.
Records a short voice command and saves it as a WAV file.
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
from datetime import datetime

# -------- Configuration --------
SAMPLE_RATE = 16000        # Whisper-friendly
CHANNELS = 1               # Mono
RECORD_SECONDS = 5         # Max command length
AUDIO_DIR = Path("audio")  # Folder to store recordings


def record_audio():
    """
    Records audio from the default microphone.
    Returns path to recorded WAV file or None on failure.
    """

    try:
        # Ensure audio directory exists
        AUDIO_DIR.mkdir(exist_ok=True)

        print(f"[AUDIO] Recording for {RECORD_SECONDS} seconds...")

        recording = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32"
        )

        sd.wait()  # Block until recording is finished

        # Basic silence check
        if np.max(np.abs(recording)) < 0.01:
            print("[AUDIO] Recording too quiet or silent.")
            return None

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = AUDIO_DIR / f"command_{timestamp}.wav"

        # Save WAV file
        sf.write(audio_path, recording, SAMPLE_RATE)

        print(f"[AUDIO] Saved recording: {audio_path}")
        return audio_path

    except Exception as e:
        print(f"[AUDIO ERROR] {e}")
        return None
