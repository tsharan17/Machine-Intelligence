def humanize_signal(signal_type: str) -> str:
    """Convert a signal_type string to a human-readable label."""
    mapping = {
        "digital_output": "Output Device",
        "digital_input":  "Input Sensor",
        "analog_input":   "Analog Sensor",
        "pwm_output":     "PWM Controlled Device",
    }
    return mapping.get(signal_type, "Device")


def generate_hardware_report(resolved_components: list, pin_map: dict) -> str:
    """
    Generate a human-readable wiring report.

    Args:
        resolved_components: list of resolved component dicts with interfaces
        pin_map: nested dict {"COMP": {"LABEL": pin_number}}
    """
    report = []
    report.append("\n========== CIRCUIT CONNECTIONS ==========\n")

    for comp in resolved_components:
        comp_name = comp["name"].upper()
        comp_pins = pin_map.get(comp_name, {})

        report.append(f"Component : {comp_name}")
        report.append(f"  GND → Board GND")
        report.append(f"  VCC → 3.3V or 5V (check datasheet)")

        for iface in comp.get("interfaces", []):
            label       = iface["label"].upper()
            signal_type = iface["signal_type"]
            pin         = comp_pins.get(label, "?")
            readable    = humanize_signal(signal_type)
            report.append(f"  {comp_name}.{label} ({readable}) → GPIO {pin}")

        report.append("")

    report.append("=========================================\n")
    return "\n".join(report)