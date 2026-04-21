from backend.speech_input import get_voice_command
from backend.command_cleaner import clean_command
from backend.component_extractor import extract_components_and_logic
from backend.hardware_resolver import resolve_interfaces
from backend.pin_allocator import allocate_pins
from backend.board_mapper import load_board
from backend.code_validator import validate_and_clean_code
from backend.firmware_writer import write_firmware
from backend.firmware_builder import build_firmware
from backend.circuit_printer import print_circuit_diagram
from backend.logic_planner import plan_logic
from backend.platformio_runner import build_and_upload
from backend.error_handler import handle_pipeline_error


def run_pipeline(board: str = "esp32"):

    print("\n" + "=" * 55)
    print("   Machine Intelligence — Embedded AI Pipeline")
    print("=" * 55)

    # ── Step 1: Capture voice input ───────────────────────────
    print("\n[1/9] Listening for voice command...")
    raw_command = get_voice_command()

    if not raw_command:
        print("[SYSTEM] ✗ No voice command detected. Exiting.")
        return

    # ── Step 2: Clean command ─────────────────────────────────
    command = clean_command(raw_command)
    print(f"[2/9] Command : \"{command}\"")

    # ── Step 3: Extract components ────────────────────────────
    print("\n[3/9] Extracting hardware components...")
    extracted = extract_components_and_logic(command)

    if not extracted or not extracted.get("components"):
        print("[SYSTEM] ✗ Could not extract components. Exiting.")
        return

    print(f"      ✓ Components : {extracted['components']}")

    # ── Step 4: Resolve hardware interfaces ───────────────────
    print("\n[4/9] Resolving hardware interfaces...")
    resolved_components = []

    for comp_name in extracted["components"]:
        resolved = resolve_interfaces(comp_name)
        if resolved:
            labels = [i["label"] for i in resolved["interfaces"]]
            print(f"      ✓ {comp_name} : {labels}")
            resolved_components.append(resolved)
        else:
            print(f"      ✗ Could not resolve: {comp_name}")

    if not resolved_components:
        print("[SYSTEM] ✗ No resolvable components found. Exiting.")
        return

    # ── Step 5: Load board profile ────────────────────────────
    print(f"\n[5/9] Loading board profile: {board}...")
    try:
        board_profile = load_board(board)
        print(f"      ✓ Board: {board_profile.get('name', board)}")
    except FileNotFoundError as e:
        handle_pipeline_error("Board Loader", e)
        return

    # ── Step 6: Allocate GPIO pins ────────────────────────────
    print("\n[6/9] Allocating GPIO pins...")
    try:
        pin_map = allocate_pins(resolved_components, board_profile)
        for comp_name, pins in pin_map.items():
            for label, pin in pins.items():
                print(f"      ✓ {comp_name}.{label} → GPIO {pin}")
    except (RuntimeError, ValueError) as e:
        handle_pipeline_error("Pin Allocator", e)
        return

    # ── Step 7: Plan logic ────────────────────────────────────
    print("\n[7/9] Planning logic...")
    logic_plan = plan_logic(command)

    if not logic_plan or "actions" not in logic_plan:
        print("[SYSTEM] ✗ Failed to generate logic plan. Exiting.")
        return

    for action in logic_plan["actions"]:
        print(f"      ✓ {action.get('type')} → {action.get('component')}")

    # ── Step 8: Build firmware ────────────────────────────────
    print("\n[8/9] Building firmware...")
    try:
        firmware_code = build_firmware(logic_plan["actions"], pin_map)
    except Exception as e:
        handle_pipeline_error("Firmware Builder", e)
        return

    if not firmware_code:
        print("[SYSTEM] ✗ Firmware generation failed. Exiting.")
        return

    clean_code = validate_and_clean_code(firmware_code)
    if not clean_code:
        print("[SYSTEM] ✗ Code validation failed. Exiting.")
        return

    print("      ✓ Firmware valid")

    # ── Write firmware + pin map ──────────────────────────────
    write_firmware(clean_code, pin_map)

    # ── Print circuit diagram ─────────────────────────────────
    print_circuit_diagram(board, resolved_components, pin_map)

    # ── Step 9: Build and upload ──────────────────────────────
    print("[9/9] Building and uploading via PlatformIO...\n")
    success = build_and_upload()

    if success:
        print("\n[SYSTEM] ✅ Pipeline complete — firmware uploaded successfully.")
    else:
        print("\n[SYSTEM] ✗ Build or upload failed. Check PlatformIO output above.")


if __name__ == "__main__":
    run_pipeline("esp32")