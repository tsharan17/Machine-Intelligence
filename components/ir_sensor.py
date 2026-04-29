from components.base import BaseComponent


class IRSensor(BaseComponent):
    """
    IR Obstacle / Object Detection Sensor (e.g. FC-51, TCRT5000)
    
    Interfaces:
        OUT (digital_input) — LOW when object detected, HIGH when clear
    
    Wiring:
        VCC → 3.3V or 5V
        GND → GND
        OUT → GPIO (digital input)
    """

    name = "IR"
    interfaces = [
        {"label": "OUT", "signal_type": "digital_input"}
    ]

    def generate_setup(self, pin_assignments: dict, action: dict) -> str:
        pin = pin_assignments["OUT"]
        lines = [
            f"    pinMode({pin}, INPUT);",
            f"    Serial.begin(115200);",
        ]
        return "\n".join(lines) + "\n"

    def generate_loop(self, pin_assignments: dict, action: dict) -> str:
        pin         = pin_assignments["OUT"]
        buzzer_pin  = action.get("buzzer_pin", None)
        led_pin     = action.get("led_pin", None)

        lines = [
            f"    int irState = digitalRead({pin});",
            f"    if (irState == LOW) {{",
            f"        Serial.println(\"IR: Object Detected!\");",
        ]

        if led_pin:
            lines.append(f"        digitalWrite({led_pin}, HIGH);")
        if buzzer_pin:
            lines.append(f"        digitalWrite({buzzer_pin}, HIGH);")
            lines.append(f"        delay(100);")
            lines.append(f"        digitalWrite({buzzer_pin}, LOW);")

        lines += [
            f"    }} else {{",
            f"        Serial.println(\"IR: Clear\");",
        ]

        if led_pin:
            lines.append(f"        digitalWrite({led_pin}, LOW);")

        lines += [
            f"    }}",
            f"    delay(200);",
        ]

        return "\n".join(lines) + "\n"
