from components.base import BaseComponent


class Potentiometer(BaseComponent):
    """
    Potentiometer / Rotary Variable Resistor

    Interfaces:
        OUT (analog_input) — wiper voltage (0 to VCC)

    Wiring:
        Left pin  → GND
        Right pin → 3.3V
        Middle (wiper) → GPIO (analog input)

    Reading:
        0    = fully counter-clockwise (0V)
        4095 = fully clockwise (3.3V) on ESP32 (12-bit ADC)
        1023 = fully clockwise on Arduino (10-bit ADC)
    """

    name = "POTENTIOMETER"
    interfaces = [
        {"label": "OUT", "signal_type": "analog_input"}
    ]

    def generate_setup(self, pin_assignments: dict, action: dict) -> str:
        pin = pin_assignments["OUT"]
        lines = [
            f"    pinMode({pin}, INPUT);",
            f"    Serial.begin(115200);",
            f"    Serial.println(\"Potentiometer ready on GPIO {pin}\");",
        ]
        return "\n".join(lines) + "\n"

    def generate_loop(self, pin_assignments: dict, action: dict) -> str:
        pin      = pin_assignments["OUT"]
        interval = action.get("interval_ms", 200)
        led_pin  = action.get("led_pin", None)

        lines = [
            f"    int potValue = analogRead({pin});",
            f"    Serial.print(\"Potentiometer: \");",
            f"    Serial.println(potValue);",
        ]

        if led_pin:
            lines += [
                f"    // Map pot value to PWM brightness (0-255)",
                f"    int brightness = map(potValue, 0, 4095, 0, 255);",
                f"    analogWrite({led_pin}, brightness);",
            ]

        lines.append(f"    delay({interval});")
        return "\n".join(lines) + "\n"
