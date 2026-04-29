from components.base import BaseComponent


class Button(BaseComponent):
    """
    Tactile Push Button / Momentary Switch

    Interfaces:
        OUT (digital_input) — button state

    Wiring (with internal pull-up):
        One pin  → GPIO (configured INPUT_PULLUP)
        Other pin → GND

    Notes:
        - Uses INPUT_PULLUP: reads HIGH when not pressed, LOW when pressed
        - No external resistor needed with INPUT_PULLUP
        - Debounce logic included (50ms)
    """

    name = "BUTTON"
    interfaces = [
        {"label": "OUT", "signal_type": "digital_input"}
    ]

    def generate_setup(self, pin_assignments: dict, action: dict) -> str:
        pin = pin_assignments["OUT"]
        lines = [
            f"    pinMode({pin}, INPUT_PULLUP);  // HIGH = not pressed, LOW = pressed",
            f"    Serial.begin(115200);",
            f"    Serial.println(\"Button ready on GPIO {pin}\");",
        ]
        return "\n".join(lines) + "\n"

    def generate_loop(self, pin_assignments: dict, action: dict) -> str:
        pin        = pin_assignments["OUT"]
        led_pin    = action.get("led_pin", None)
        buzzer_pin = action.get("buzzer_pin", None)

        lines = [
            f"    int btnState = digitalRead({pin});",
            f"    if (btnState == LOW) {{  // Button pressed",
            f"        Serial.println(\"Button: PRESSED\");",
            f"        delay(50);  // debounce",
        ]

        if led_pin:
            lines.append(f"        digitalWrite({led_pin}, HIGH);")
        if buzzer_pin:
            lines.append(f"        digitalWrite({buzzer_pin}, HIGH);")

        lines += [
            f"        while(digitalRead({pin}) == LOW);  // wait for release",
            f"        Serial.println(\"Button: RELEASED\");",
        ]

        if led_pin:
            lines.append(f"        digitalWrite({led_pin}, LOW);")
        if buzzer_pin:
            lines.append(f"        digitalWrite({buzzer_pin}, LOW);")

        lines += [
            f"        delay(50);  // debounce after release",
            f"    }}",
        ]

        return "\n".join(lines) + "\n"
