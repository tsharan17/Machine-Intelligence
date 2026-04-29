from llm_client import query_llm_json

VALID_SIGNAL_TYPES = {
    "digital_output",
    "digital_input",
    "analog_input",
    "pwm_output",
}


def resolve_interfaces(component_name: str) -> dict | None:
    """
    Uses LLM to resolve the GPIO interfaces for a given component.

    Returns:
        {
            "name": "ULTRASONIC",
            "interfaces": [
                {"label": "TRIG", "signal_type": "digital_output"},
                {"label": "ECHO", "signal_type": "digital_input"}
            ]
        }
    """

    prompt = f"""
Return STRICT JSON only.
No explanation. No markdown.

Describe the GPIO interfaces for this hardware component: {component_name}

FORMAT:
{{
  "name": "{component_name}",
  "interfaces": [
    {{
      "label": "INTERFACE_LABEL",
      "signal_type": "digital_output|digital_input|analog_input|pwm_output"
    }}
  ]
}}

Rules:
- Labels must be UPPERCASE (e.g. TRIG, ECHO, SIGNAL)
- Only use these signal types: digital_output, digital_input, analog_input, pwm_output
- Ultrasonic sensor: TRIG (digital_output) and ECHO (digital_input)
- LED: SIGNAL (digital_output)
- Buzzer: SIGNAL (digital_output)
- Servo: SIGNAL (pwm_output)
- Serial/UART components: return empty interfaces list
"""

    result = query_llm_json(prompt)

    if not result:
        print(f"[HARDWARE RESOLVER] No result for: {component_name}")
        return None

    if "interfaces" not in result:
        print(f"[HARDWARE RESOLVER] Missing 'interfaces' for: {component_name}")
        return None

    validated = []
    for iface in result["interfaces"]:
        label       = iface.get("label", "").upper().strip()
        signal_type = iface.get("signal_type", "").lower().strip()

        if not label:
            print(f"[HARDWARE RESOLVER] Empty label skipped.")
            continue
        if signal_type not in VALID_SIGNAL_TYPES:
            print(f"[HARDWARE RESOLVER] Invalid signal type '{signal_type}' for {label}, skipped.")
            continue

        validated.append({"label": label, "signal_type": signal_type})

    return {
        "name": component_name.upper().strip(),
        "interfaces": validated
    }