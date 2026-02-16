from prompt_manager import build_prompt
from llm_client import generate_firmware_code
from code_validator import validate_and_clean_code
from firmware_writer import write_firmware
from platformio_runner import build_and_upload
from speech_input import get_voice_command


def run_pipeline(user_command: str, upload: bool = True) -> None:
    print("[ORCH] Starting Machine Intelligence pipeline")
    
    prompt = build_prompt(user_command)
    print("[ORCH] Prompt constructed")

    firmware_code, pin_map = generate_firmware_code(prompt)

    if not firmware_code:
        print("[ORCH ERROR] LLM failed")
        return

    print("[ORCH] Firmware + pin data received")

    clean_code = validate_and_clean_code(firmware_code)
    if not clean_code:
        print("[ORCH ERROR] Code validation failed")
        return

    print("[ORCH] Firmware validated")

    if not write_firmware(clean_code):
        print("[ORCH ERROR] Firmware writing failed")
        return

    print("[ORCH] Firmware written")

    # ---- Detailed Pin Connections ----
    if pin_map:
        print("\n========== DETAILED PIN CONNECTIONS ==========\n")

        for component, details in pin_map.items():
            gpio = details.get("gpio", "Unknown")
            connection = details.get("connection", "")

            print(f"{component}")
            print(f"  GPIO: {gpio}")
            print(f"  Wiring: {connection}\n")

        print("=============================================\n")

    success = build_and_upload(upload)

    if success:
        print("[ORCH] Pipeline completed successfully")
    else:
        print("[ORCH ERROR] PlatformIO step failed")


if __name__ == "__main__":
    print("[SYSTEM] Speak your command after the prompt")

    command = get_voice_command()

    if not command:
        print("[SYSTEM ERROR] No voice command detected.")
        exit(1)

    run_pipeline(command, upload=False)   # build-only safe mode
