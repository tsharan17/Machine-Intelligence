"""
speech_input.py

Continuous microphone listening with silence-based recording.
Starts recording when speech is detected.
Stops recording after sustained silence.
Returns transcribed voice command.
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
from datetime import datetime
import queue
import time

from whisper_stt import transcribe_audio

# -------- Configuration --------
SAMPLE_RATE = 16000
CHANNELS = 1
AUDIO_DIR = Path("audio")

# Voice activity detection parameters
SPEECH_THRESHOLD = 0.02     # amplitude threshold to detect speech
SILENCE_DURATION = 2      # seconds of silence to stop recording
MAX_RECORD_SECONDS = 15     # hard safety cap (important)

# Internal queue for audio frames
_audio_queue = queue.Queue()


def _audio_callback(indata, frames, time_info, status):
    if status:
        print(f"[AUDIO WARNING] {status}")
    _audio_queue.put(indata.copy())


def record_audio_until_silence() -> Path | None:
    """
    Records audio when speech is detected and stops after silence.
    Returns path to WAV file or None.
    """
    AUDIO_DIR.mkdir(exist_ok=True)

    print("[AUDIO] Listening... speak now")

    recorded_frames = []
    recording = False
    silence_start = None
    start_time = None

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        callback=_audio_callback
    ):
        while True:
            try:
                frame = _audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            amplitude = np.max(np.abs(frame))

            # Detect speech start
            if amplitude > SPEECH_THRESHOLD and not recording:
                print("[AUDIO] Speech detected, recording...")
                recording = True
                start_time = time.time()

            if recording:
                recorded_frames.append(frame)

                # Detect silence
                if amplitude < SPEECH_THRESHOLD:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start >= SILENCE_DURATION:
                        print("[AUDIO] Silence detected, stopping recording")
                        break
                else:
                    silence_start = None

                # Hard safety cap
                if time.time() - start_time > MAX_RECORD_SECONDS:
                    print("[AUDIO WARNING] Max recording time reached")
                    break

    if not recorded_frames:
        print("[AUDIO ERROR] No audio recorded")
        return None

    audio_data = np.concatenate(recorded_frames, axis=0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_path = AUDIO_DIR / f"command_{timestamp}.wav"

    sf.write(audio_path, audio_data, SAMPLE_RATE)
    print(f"[AUDIO] Saved recording: {audio_path}")

    return audio_path


def get_voice_command() -> str:
    """
    Captures voice command using silence-based recording
    and returns transcribed text.
    """
    audio_path = record_audio_until_silence()
    if not audio_path:
        return ""

    return transcribe_audio(audio_path)
