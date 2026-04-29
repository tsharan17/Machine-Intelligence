from components.base import BaseComponent


class LDR(BaseComponent):
    """
    LDR (Light Dependent Resistor) / Photoresistor

    Interfaces:
        OUT (analog_input) — analog voltage proportional to light level

    Wiring:
        One end of LDR → 3.3V
        Other end of LDR → GPIO (analog input)
        10kΩ resistor from that junction → GND
        (forms a voltage divider)

    Reading:
        High value (~4095) = Dark
        Low value  (~0)    = Bright light
    """

    name = "LDR"
    interfaces = [
        {"label": "OUT", "signal_type": "analog_input"}
    ]

    def generate_setup(self, pin_assignments: dict, action: dict) -> str:
        pin = pin_assignments["OUT"]
        lines = [
            f"    pinMode({pin}, INPUT);",
            f"    Serial.begin(115200);",
            f"    Serial.println(\"LDR Sensor Ready on GPIO {pin}\");",
        ]
        return "\n".join(lines) + "\n"

    def generate_loop(self, pin_assignments: dict, action: dict) -> str:
        pin           = pin_assignments["OUT"]
        threshold     = action.get("threshold", 2000)   # below = bright, above = dark
        buzzer_pin    = action.get("buzzer_pin", None)
        led_pin       = action.get("led_pin", None)
        interval      = action.get("interval_ms", 500)

        lines = [
            f"    int lightValue = analogRead({pin});",
            f"    Serial.print(\"Light Level: \");",
            f"    Serial.println(lightValue);",
            f"    if (lightValue > {threshold}) {{",
            f"        Serial.println(\"LDR: DARK detected\");",
        ]

        if led_pin:
            lines.append(f"        digitalWrite({led_pin}, HIGH);  // turn on LED in dark")
        if buzzer_pin:
            lines.append(f"        digitalWrite({buzzer_pin}, HIGH);")
            lines.append(f"        delay(100);")
            lines.append(f"        digitalWrite({buzzer_pin}, LOW);")

        lines += [
            f"    }} else {{",
            f"        Serial.println(\"LDR: BRIGHT\");",
        ]

        if led_pin:
            lines.append(f"        digitalWrite({led_pin}, LOW);")

        lines += [
            f"    }}",
            f"    delay({interval});",
        ]

        return "\n".join(lines) + "\n"
