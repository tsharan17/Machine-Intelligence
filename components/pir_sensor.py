from components.base import BaseComponent


class PIRSensor(BaseComponent):
    """
    PIR Motion Sensor (HC-SR501 or similar)

    Interfaces:
        OUT (digital_input) — HIGH when motion detected, LOW when clear

    Wiring:
        VCC → 5V (most PIR modules require 5V)
        GND → GND
        OUT → GPIO (digital input)

    Notes:
        - Has onboard sensitivity and time-delay potentiometers
        - Warm-up time: ~30-60 seconds after power on
        - Detection range: up to 7 meters (adjustable)
        - Output stays HIGH for ~3 seconds after motion detected
    """

    name = "PIR"
    interfaces = [
        {"label": "OUT", "signal_type": "digital_input"}
    ]

    def generate_setup(self, pin_assignments: dict, action: dict) -> str:
        pin = pin_assignments["OUT"]
        lines = [
            f"    pinMode({pin}, INPUT);",
            f"    Serial.begin(115200);",
            f"    Serial.println(\"PIR Sensor warming up...\");",
            f"    delay(2000);  // brief startup delay (full warmup is 30-60s on hardware)",
            f"    Serial.println(\"PIR Sensor Ready on GPIO {pin}\");",
        ]
        return "\n".join(lines) + "\n"

    def generate_loop(self, pin_assignments: dict, action: dict) -> str:
        pin        = pin_assignments["OUT"]
        buzzer_pin = action.get("buzzer_pin", None)
        led_pin    = action.get("led_pin", None)

        lines = [
            f"    int motionState = digitalRead({pin});",
            f"    if (motionState == HIGH) {{",
            f"        Serial.println(\"PIR: MOTION DETECTED!\");",
        ]

        if led_pin:
            lines.append(f"        digitalWrite({led_pin}, HIGH);")
        if buzzer_pin:
            lines += [
                f"        digitalWrite({buzzer_pin}, HIGH);",
                f"        delay(500);",
                f"        digitalWrite({buzzer_pin}, LOW);",
            ]

        lines += [
            f"        delay(1000);  // hold detection state",
            f"    }} else {{",
            f"        Serial.println(\"PIR: No motion\");",
        ]

        if led_pin:
            lines.append(f"        digitalWrite({led_pin}, LOW);")

        lines += [
            f"    }}",
            f"    delay(200);",
        ]

        return "\n".join(lines) + "\n"
