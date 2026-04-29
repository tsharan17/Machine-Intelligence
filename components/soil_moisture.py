from components.base import BaseComponent


class SoilMoisture(BaseComponent):
    """
    Capacitive or Resistive Soil Moisture Sensor

    Interfaces:
        OUT (analog_input) — analog voltage proportional to moisture

    Wiring:
        VCC → 3.3V or 5V
        GND → GND
        OUT → GPIO (analog input)

    Reading (ESP32, 12-bit ADC):
        ~4095 = Dry soil (air)
        ~1500 = Wet soil
        ~800  = In water

    Notes:
        Use capacitive sensor (not resistive) for longer lifespan.
        Resistive sensors corrode quickly in soil.
    """

    name = "SOIL"
    interfaces = [
        {"label": "OUT", "signal_type": "analog_input"}
    ]

    def generate_setup(self, pin_assignments: dict, action: dict) -> str:
        pin = pin_assignments["OUT"]
        lines = [
            f"    pinMode({pin}, INPUT);",
            f"    Serial.begin(115200);",
            f"    Serial.println(\"Soil Moisture Sensor Ready on GPIO {pin}\");",
        ]
        return "\n".join(lines) + "\n"

    def generate_loop(self, pin_assignments: dict, action: dict) -> str:
        pin        = pin_assignments["OUT"]
        threshold  = action.get("threshold", 2500)  # above = dry, below = moist
        buzzer_pin = action.get("buzzer_pin", None)
        led_pin    = action.get("led_pin", None)
        relay_pin  = action.get("relay_pin", None)
        interval   = action.get("interval_ms", 1000)

        lines = [
            f"    int soilValue = analogRead({pin});",
            f"    Serial.print(\"Soil Moisture: \");",
            f"    Serial.println(soilValue);",
            f"    if (soilValue > {threshold}) {{  // Dry",
            f"        Serial.println(\"Soil: DRY — needs water!\");",
        ]

        if led_pin:
            lines.append(f"        digitalWrite({led_pin}, HIGH);  // alert LED on")
        if buzzer_pin:
            lines += [
                f"        digitalWrite({buzzer_pin}, HIGH);",
                f"        delay(200);",
                f"        digitalWrite({buzzer_pin}, LOW);",
            ]
        if relay_pin:
            lines.append(f"        digitalWrite({relay_pin}, LOW);   // activate pump (active LOW relay)")

        lines += [
            f"    }} else {{",
            f"        Serial.println(\"Soil: MOIST — OK\");",
        ]

        if led_pin:
            lines.append(f"        digitalWrite({led_pin}, LOW);")
        if relay_pin:
            lines.append(f"        digitalWrite({relay_pin}, HIGH);  // deactivate pump")

        lines += [
            f"    }}",
            f"    delay({interval});",
        ]

        return "\n".join(lines) + "\n"
