"""
speech_input.py
Robust adaptive microphone handling for noisy and silent environments
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
AUDIO_DIR = Path("audio")
SILENCE_DURATION = 1.2
MAX_RECORD_SECONDS = 12
DEVICE_INDEX = 5  # Change if needed

_audio_queue = queue.Queue()


def _audio_callback(indata, frames, time_info, status):
    if status:
        print(f"[AUDIO WARNING] {status}")
    _audio_queue.put(indata.copy())


def measure_ambient_noise(sample_rate, channels):
    print("[AUDIO] Calibrating ambient noise...")
    samples = []

    with sd.InputStream(
        samplerate=sample_rate,
        channels=channels,
        dtype="float32"
    ):
        start = time.time()
        while time.time() - start < 1.0:
            frame = sd.rec(int(sample_rate * 0.05), samplerate=sample_rate, channels=channels)
            sd.wait()
            samples.append(frame)

    ambient = np.mean(np.abs(np.concatenate(samples)))
    print(f"[AUDIO] Ambient noise level: {ambient:.6f}")
    return ambient


def record_audio_until_silence() -> Path | None:
    AUDIO_DIR.mkdir(exist_ok=True)

    print("[AUDIO] Listening... speak now")

    try:
        sd.default.device = (DEVICE_INDEX, None)
        device_info = sd.query_devices(DEVICE_INDEX)

        sample_rate = int(device_info["default_samplerate"])
        channels = int(device_info["max_input_channels"])

        if channels < 1:
            print("[AUDIO ERROR] No input channels.")
            return None

        print(f"[AUDIO] Sample rate: {sample_rate}")
        print(f"[AUDIO] Channels: {channels}")

    except Exception as e:
        print(f"[AUDIO ERROR] Device setup failed: {e}")
        return None

    ambient_noise = measure_ambient_noise(sample_rate, channels)
    speech_threshold = ambient_noise * 3

    recorded_frames = []
    recording = False
    silence_start = None
    start_time = None

    try:
        with sd.InputStream(
            samplerate=sample_rate,
            channels=channels,
            dtype="float32",
            callback=_audio_callback
        ):
            while True:
                try:
                    frame = _audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                amplitude = np.max(np.abs(frame))

                if amplitude > speech_threshold and not recording:
                    print("[AUDIO] Speech detected, recording...")
                    recording = True
                    start_time = time.time()

                if recording:
                    recorded_frames.append(frame)

                    if amplitude < speech_threshold:
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start >= SILENCE_DURATION:
                            print("[AUDIO] Silence detected, stopping recording")
                            break
                    else:
                        silence_start = None

                    if time.time() - start_time > MAX_RECORD_SECONDS:
                        print("[AUDIO WARNING] Max recording time reached")
                        break

    except Exception as e:
        print(f"[AUDIO ERROR] Stream failure: {e}")
        return None

    if not recorded_frames:
        print("[AUDIO ERROR] No audio recorded")
        return None

    audio_data = np.concatenate(recorded_frames, axis=0)

    # Normalize audio
    max_val = np.max(np.abs(audio_data))
    if max_val > 0:
        audio_data = audio_data / max_val

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_path = AUDIO_DIR / f"command_{timestamp}.wav"

    sf.write(audio_path, audio_data, sample_rate)
    print(f"[AUDIO] Saved recording: {audio_path}")

    return audio_path


def get_voice_command() -> str:
    audio_path = record_audio_until_silence()
    if not audio_path:
        return ""

    return transcribe_audio(audio_path)
