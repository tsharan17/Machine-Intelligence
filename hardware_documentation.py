def humanize_signal(signal_key):
    if "digital_output" in signal_key:
        return "Output Device"
    elif "digital_input" in signal_key:
        return "Input Device"
    elif "analog_input" in signal_key:
        return "Analog Sensor"
    elif "pwm_output" in signal_key:
        return "PWM Controlled Device"
    else:
        return "Device"


def generate_hardware_report(allocation):
    report = []
    report.append("\n========== CIRCUIT CONNECTIONS ==========\n")

    for index, (key, pin) in enumerate(allocation.items(), start=1):
        readable = humanize_signal(key)

        report.append(f"{readable} #{index}")
        report.append(f"  → Connect signal wire to GPIO {pin}")
        report.append(f"  → Connect device GND to board GND")
        report.append(f"  → Connect device VCC to appropriate voltage (3.3V or 5V)\n")

    report.append("=========================================\n")

    return "\n".join(report)
