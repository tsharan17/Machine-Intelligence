from speech_input import get_voice_command
from prompt_manager import build_prompt
from llm_client import generate_firmware_code
from code_validator import validate_and_clean_code
from firmware_writer import write_firmware
from board_mapper import load_board
from pin_allocator import allocate_pins
from platformio_runner import build_and_upload


def replace_placeholders(code: str, pin_map: dict):

    for name, pin in pin_map.items():

        # Replace {{LED_PIN}}
        code = code.replace(
            "{{" + name.upper() + "_PIN}}",
            str(pin)
        )

        # Safety: if model used LED_PIN without braces
        code = code.replace(
            name.upper() + "_PIN",
            str(pin)
        )

    return code


def print_circuit_diagram(board: str, pin_map: dict):

    print("\n========== COMPLETE CIRCUIT DIAGRAM ==========\n")
    print(f"Board: {board.upper()}\n")

    print("Power Connections:")
    print("  • Connect external device GND to board GND")
    print("  • Use correct voltage (ESP32 = 3.3V logic)\n")

    for name, pin in pin_map.items():

        print(f"{name.upper()} CONNECTION:")

        print(f"  GPIO {pin}  --->  {name} signal pin")
        print(f"  GND        --->  {name} GND")

        if name.lower() == "led":
            print("  Use 220Ω resistor between GPIO and LED anode")
            print("  LED cathode ---> GND")

        print()

    print("==============================================\n")


def run_pipeline(board="esp32"):

    print("[SYSTEM] Speak your command")

    command = get_voice_command()

    if not command:
        print("[SYSTEM] No voice command detected")
        return

    prompt = build_prompt(command)

    parsed = generate_firmware_code(prompt)

    if not parsed:
        print("[SYSTEM] LLM failed")
        return

    if "components" not in parsed or "firmware_code" not in parsed:
        print("[SYSTEM ERROR] Invalid LLM JSON structure")
        print(parsed)
        return

    components = parsed["components"]
    firmware_code = parsed["firmware_code"]

    board_profile = load_board(board)

    pin_map = allocate_pins(components, board_profile)

    firmware_code = replace_placeholders(firmware_code, pin_map)

    clean_code = validate_and_clean_code(firmware_code)

    if not clean_code:
        print("[SYSTEM] Validation failed")
        return

    write_firmware(clean_code, pin_map)

    print_circuit_diagram(board, pin_map)

    build_and_upload()


if __name__ == "__main__":
    run_pipeline("esp32")  # change to "arduino" if needed