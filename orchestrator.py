from speech_input import get_voice_command
from component_extractor import extract_components_and_logic
from hardware_resolver import resolve_interfaces
from pin_allocator import allocate_pins
from board_mapper import load_board
from code_validator import validate_and_clean_code
from firmware_writer import write_firmware
from platformio_runner import build_and_upload
from circuit_printer import print_circuit_diagram

from logic_planner import plan_logic
from firmware_builder import build_firmware


def run_pipeline(board="esp32"):

    print("[SYSTEM] Speak your command")
    command = get_voice_command()

    if not command:
        print("[SYSTEM] No voice command detected")
        return

    print(f"[SYSTEM] Command: {command}")

    # 1️⃣ Extract components
    extracted = extract_components_and_logic(command)
    if not extracted or not extracted.get("components"):
        print("[SYSTEM] Could not extract components")
        return

    # 2️⃣ Resolve hardware interfaces
    resolved_components = []
    for comp_name in extracted["components"]:
        resolved = resolve_interfaces(comp_name)
        if resolved:
            resolved_components.append(resolved)

    if not resolved_components:
        print("[SYSTEM] No resolvable components found")
        return

    # 3️⃣ Load board profile
    board_profile = load_board(board)

    # 4️⃣ Allocate pins deterministically
    pin_map = allocate_pins(resolved_components, board_profile)

    # 5️⃣ Ask AI only for structured logic plan (NOT code)
    logic_plan = plan_logic(command)

    if not logic_plan or "actions" not in logic_plan:
        print("[SYSTEM] Failed to generate logic plan")
        return

    # 6️⃣ Build firmware deterministically
    firmware_code = build_firmware(
        logic_plan["actions"],
        pin_map
    )

    if not firmware_code:
        print("[SYSTEM] Firmware generation failed")
        return

    # 7️⃣ Validate code
    clean_code = validate_and_clean_code(firmware_code)
    if not clean_code:
        print("[SYSTEM] Code validation failed")
        return

    # 8️⃣ Write firmware to src/main.cpp
    write_firmware(clean_code, pin_map)

    # 9️⃣ Print circuit diagram in terminal
    print_circuit_diagram(board, resolved_components, pin_map)

    # 🔟 Build & Upload
    build_and_upload()


if __name__ == "__main__":
    run_pipeline("esp32")