from components.base import BaseComponent


class SoundSensor(BaseComponent):
    """
    Sound / Microphone Sensor Module (KY-038, LM393-based)

    Interfaces:
        DO (digital_input) — HIGH when sound exceeds threshold (set by onboard trimmer)
        AO (analog_input)  — raw analog sound level

    Wiring:
        VCC → 3.3V or 5V
        GND → GND
        DO  → GPIO (digital input)   ← threshold-based
        AO  → GPIO (analog input)    ← raw level (optional)

    Notes:
        Sensitivity adjusted via onboard potentiometer.
        DO goes HIGH when sound detected above threshold.
    """

    name = "SOUND"
    interfaces = [
        {"label": "DO", "signal_type": "digital_input"},
        {"label": "AO", "signal_type": "analog_input"},
    ]

    def generate_setup(self, pin_assignments: dict, action: dict) -> str:
        do_pin = pin_assignments.get("DO")
        ao_pin = pin_assignments.get("AO")
        lines = [
            f"    pinMode({do_pin}, INPUT);",
            f"    pinMode({ao_pin}, INPUT);",
            f"    Serial.begin(115200);",
            f"    Serial.println(\"Sound Sensor Ready — DO: GPIO {do_pin}, AO: GPIO {ao_pin}\");",
        ]
        return "\n".join(lines) + "\n"

    def generate_loop(self, pin_assignments: dict, action: dict) -> str:
        do_pin     = pin_assignments.get("DO")
        ao_pin     = pin_assignments.get("AO")
        led_pin    = action.get("led_pin", None)
        buzzer_pin = action.get("buzzer_pin", None)
        interval   = action.get("interval_ms", 100)

        lines = [
            f"    int digitalSound = digitalRead({do_pin});",
            f"    int analogSound  = analogRead({ao_pin});",
            f"    Serial.print(\"Sound Level (analog): \");",
            f"    Serial.print(analogSound);",
            f"    Serial.print(\"  |  Threshold triggered: \");",
            f"    Serial.println(digitalSound == HIGH ? \"YES\" : \"NO\");",
            f"    if (digitalSound == HIGH) {{",
            f"        Serial.println(\"Sound: LOUD — threshold exceeded!\");",
        ]

        if led_pin:
            lines.append(f"        digitalWrite({led_pin}, HIGH);")
        if buzzer_pin:
            lines += [
                f"        digitalWrite({buzzer_pin}, HIGH);",
                f"        delay(100);",
                f"        digitalWrite({buzzer_pin}, LOW);",
            ]

        lines += [
            f"    }} else {{",
        ]

        if led_pin:
            lines.append(f"        digitalWrite({led_pin}, LOW);")

        lines += [
            f"    }}",
            f"    delay({interval});",
        ]

        return "\n".join(lines) + "\n"
