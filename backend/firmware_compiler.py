def generate_firmware(ir, allocation):

    setup_lines = []
    loop_lines = []

    for key, info in allocation.items():
        pin = info["pin"]
        signal_type = info["signal_type"]

        if signal_type == "digital_output":
            setup_lines.append(f"pinMode({pin}, OUTPUT);")

        elif signal_type == "digital_input":
            setup_lines.append(f"pinMode({pin}, INPUT);")

        elif signal_type == "analog_input":
            setup_lines.append(f"pinMode({pin}, INPUT);")

        elif signal_type == "pwm_output":
            setup_lines.append(f"pinMode({pin}, OUTPUT);")

    firmware = f"""
#include <Arduino.h>

void setup() {{
{chr(10).join("    " + l for l in setup_lines)}
}}

void loop() {{
    // Logic handling not yet implemented
}}
"""

    return firmware
