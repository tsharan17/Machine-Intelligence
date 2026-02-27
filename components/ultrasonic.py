from components.base import BaseComponent


class Ultrasonic(BaseComponent):

    name = "ULTRASONIC"
    interfaces = [
        {"label": "TRIG", "signal_type": "digital_output"},
        {"label": "ECHO", "signal_type": "digital_input"},
    ]

    def generate_setup(self, pin_assignments: dict, action: dict) -> str:
        trig = pin_assignments["TRIG"]
        echo = pin_assignments["ECHO"]
        lines = [
            f"    pinMode({trig}, OUTPUT);",
            f"    pinMode({echo}, INPUT);",
            f"    Serial.begin(115200);",
        ]
        return "\n".join(lines) + "\n"

    def generate_loop(self, pin_assignments: dict, action: dict) -> str:
        trig          = pin_assignments["TRIG"]
        echo          = pin_assignments["ECHO"]
        threshold     = action.get("threshold_cm", 20)
        buzzer_pin    = action.get("buzzer_pin", None)  # injected by firmware_builder

        lines = [
            f"    // Ultrasonic HC-SR04 measurement",
            f"    digitalWrite({trig}, LOW);",
            f"    delayMicroseconds(2);",
            f"    digitalWrite({trig}, HIGH);",
            f"    delayMicroseconds(10);",
            f"    digitalWrite({trig}, LOW);",
            f"    long duration = pulseIn({echo}, HIGH);",
            f"    float distance_cm = duration * 0.034 / 2.0;",
            f"    Serial.print(\"Distance: \");",
            f"    Serial.print(distance_cm);",
            f"    Serial.println(\" cm\");",
        ]

        if buzzer_pin:
            lines += [
                f"    if (distance_cm < {threshold}) {{",
                f"        digitalWrite({buzzer_pin}, HIGH);",
                f"        delay(200);",
                f"        digitalWrite({buzzer_pin}, LOW);",
                f"    }}",
            ]
        else:
            lines += [
                f"    if (distance_cm < {threshold}) {{",
                f"        Serial.println(\"OBJECT DETECTED!\");",
                f"    }}",
            ]

        lines.append(f"    delay(200);")
        return "\n".join(lines) + "\n"