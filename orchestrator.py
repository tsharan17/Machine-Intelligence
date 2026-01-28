"""
Machine Intelligence
Main Orchestrator

This is the ONLY file the user runs.
All system logic flows through here.
"""

import sys
import time
from pathlib import Path

# ---- Internal modules (to be implemented next) ----
try:
    from speech_input import record_audio
    from whisper_stt import transcribe_audio
    from prompt_manager import build_prompt
    from llm_client import generate_firmware_code
    from code_validator import validate_code
    from firmware_writer import write_firmware
    from platformio_runner import build_and_upload
    from device_detector import detect_device
    from error_handler import handle_error
except ImportError as e:
    print(f"[FATAL] Missing module: {e}")
    sys.exit(1)


# ---- Constants ----
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
MAIN_CPP = SRC_DIR / "main.cpp"


# ---- Helper ----
def banner():
    print("\n" + "=" * 60)
    print(" MACHINE INTELLIGENCE :: Voice-to-Firmware System ")
    print("=" * 60 + "\n")


# ---- Main Run Loop ----
def main():
    banner()

    print("[INIT] Starting system initialization...")

    # 1. Detect connected hardware
    device_info = detect_device()
    if not device_info:
        handle_error("NO_DEVICE", "No supported board detected.")
        return

    print(f"[INIT] Detected device: {device_info}")

    print("[INIT] System ready. Listening for commands...\n")

    # Continuous run loop
    while True:
        try:
            # 2. Capture voice input
            print("[LISTEN] Speak your command...")
            audio_path = record_audio()

            if not audio_path:
                print("[WARN] No audio captured. Retrying...\n")
                continue

            # 3. Speech-to-text
            print("[STT] Transcribing audio...")
            command_text = transcribe_audio(audio_path)

            if not command_text or len(command_text.strip()) < 4:
                print("[WARN] Could not understand command. Try again.\n")
                continue

            print(f"[USER] \"{command_text}\"")

            # 4. Build LLM prompt
            prompt = build_prompt(command_text)

            # 5. Generate firmware using LLM
            print("[LLM] Generating firmware code...")
            firmware_code = generate_firmware_code(prompt)

            if not firmware_code:
                handle_error("LLM_EMPTY", "LLM returned no code.")
                continue

            # 6. Validate generated code
            print("[VALIDATE] Checking firmware safety...")
            valid, reason = validate_code(firmware_code)

            if not valid:
                handle_error("VALIDATION_FAILED", reason)
                continue

            # 7. Write firmware to main.cpp
            print("[WRITE] Writing firmware to src/main.cpp...")
            write_firmware(firmware_code, MAIN_CPP)

            # 8. Build and upload using PlatformIO
            print("[UPLOAD] Compiling and flashing firmware...")
            success, log = build_and_upload()

            if not success:
                handle_error("UPLOAD_FAILED", log)
                continue

            print("[SUCCESS] Firmware uploaded and running.\n")

            # Small pause before next command
            time.sleep(1)

        except KeyboardInterrupt:
            print("\n[EXIT] User interrupted execution.")
            break

        except Exception as e:
            handle_error("RUNTIME_EXCEPTION", str(e))
            continue


# ---- Entry Point ----
if __name__ == "__main__":
    main()
