from speech_input import get_voice_command
from command_cleaner import clean_command
from intent_parser import extract_intent
from resource_ir import ResourceIR
from board_mapper import load_board
from resource_allocator import allocate_resources
from firmware_compiler import generate_firmware
from firmware_writer import write_firmware
from code_validator import validate_and_clean_code
from platformio_runner import build_and_upload


def print_beginner_hardware_report(allocation, board_name):

    print("\n========== CIRCUIT CONNECTION GUIDE ==========\n")
    print(f"You are using the {board_name.upper()} board.\n")

    print("Important:")
    print("• Do NOT connect 5V signals directly to 3.3V pins.")
    print("• Always connect GND of external devices to board GND.\n")

    grouped = {}

    for key, info in allocation.items():
        comp_name, label = key.split(".")
        grouped.setdefault(comp_name, []).append((label, info))

    for comp, interfaces in grouped.items():
        print(f"{comp.upper()}")

        for label, info in interfaces:
            print(f"  {label.upper()} → GPIO {info['pin']}")

        print("  Connect GND to board GND")

        if "ultrasonic" in comp.lower():
            print("  VCC → 5V")
            print("  ⚠ Use voltage divider on ECHO if board is 3.3V")

        if "led" in comp.lower():
            print("  Use 220Ω resistor in series")

        print()

    print("==============================================\n")


def run_pipeline(board="esp32", upload=False):

    print("[SYSTEM] Speak your command")

    command = get_voice_command()
    if not command:
        print("[SYSTEM] No speech detected.")
        return

    cleaned = clean_command(command)
    print("[CLEANED]", cleaned)

    intent_dict = extract_intent(cleaned)
    print("[INTENT]", intent_dict)

    ir = ResourceIR(intent_dict)

    board_profile = load_board(board)

    allocation = allocate_resources(ir, board_profile)

    print_beginner_hardware_report(allocation, board)

    firmware = generate_firmware(ir, allocation)

    clean_code = validate_and_clean_code(firmware)
    if not clean_code:
        print("[VALIDATION FAILED]")
        return

    write_firmware(clean_code)

    build_and_upload(upload)


if __name__ == "__main__":
    run_pipeline(upload=False)
