from backend.component_registry import get_component


def build_firmware(actions: list, pin_map: dict) -> str:
    """
    Deterministically builds Arduino C++ firmware from a logic plan and pin map.
    No LLM involved — pure code generation.

    Args:
        actions: list of action dicts from logic_planner, e.g.:
            [{"type": "blink", "component": "LED", "times": 5, "interval_ms": 500}]
        pin_map: nested dict from pin_allocator, e.g.:
            {"LED": {"SIGNAL": 2}, "BUZZER": {"SIGNAL": 4}}

    Returns:
        Full Arduino C++ source string.
    """

    setup_lines = []
    loop_lines  = []
    setup_done  = set()  # prevent duplicate setup blocks for same component

    # Inject cross-component context before generating code
    _enrich_actions(actions, pin_map)

    for action in actions:

        comp_name = action.get("component", "").upper().strip()

        if not comp_name:
            print(f"[FIRMWARE BUILDER] Action missing 'component' field: {action}")
            continue

        comp = get_component(comp_name)
        if comp is None:
            print(f"[FIRMWARE BUILDER] Unknown component: '{comp_name}' — skipping.")
            continue

        comp_pins = pin_map.get(comp_name, {})

        # Setup block — generated only once per component
        if comp_name not in setup_done:
            setup_block = comp.generate_setup(comp_pins, action)
            if setup_block:
                setup_lines.append(setup_block.rstrip())
            setup_done.add(comp_name)

        # Loop block
        loop_block = comp.generate_loop(comp_pins, action)
        if loop_block:
            loop_lines.append(loop_block.rstrip())

    setup_body = "\n".join(setup_lines)
    loop_body  = "\n".join(loop_lines)

    return f"""#include <Arduino.h>

void setup() {{
{setup_body}
}}

void loop() {{
{loop_body}
}}
"""


def _enrich_actions(actions: list, pin_map: dict):
    """
    Inject cross-component pin references into actions before code generation.

    Example: ultrasonic detect_distance action gets the buzzer's GPIO pin
    injected so the ultrasonic loop can directly drive the buzzer.
    """
    buzzer_pin = None
    if "BUZZER" in pin_map:
        buzzer_pin = pin_map["BUZZER"].get("SIGNAL")

    for action in actions:
        if action.get("type") == "detect_distance" and buzzer_pin:
            action["buzzer_pin"] = buzzer_pin