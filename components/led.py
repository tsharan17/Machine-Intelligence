from components.base import BaseComponent


class LED(BaseComponent):

    name = "LED"
    interfaces = [
        {"label": "SIGNAL", "signal_type": "digital_output"}
    ]

    def generate_setup(self, pin_assignments: dict, action: dict) -> str:
        pin = pin_assignments["SIGNAL"]
        return f"    pinMode({pin}, OUTPUT);\n"

    def generate_loop(self, pin_assignments: dict, action: dict) -> str:
        pin          = pin_assignments["SIGNAL"]
        action_type  = action.get("type", "blink")
        times        = action.get("times", 0)
        interval     = action.get("interval_ms", 500)

        if action_type == "blink" and times > 0:
            lines = [
                f"    for (int i = 0; i < {times}; i++) {{",
                f"        digitalWrite({pin}, HIGH);",
                f"        delay({interval});",
                f"        digitalWrite({pin}, LOW);",
                f"        delay({interval});",
                f"    }}",
                f"    while(true);  // halt after {times} blinks",
            ]
            return "\n".join(lines) + "\n"

        elif action_type == "blink":
            # blink forever
            lines = [
                f"    digitalWrite({pin}, HIGH);",
                f"    delay({interval});",
                f"    digitalWrite({pin}, LOW);",
                f"    delay({interval});",
            ]
            return "\n".join(lines) + "\n"

        elif action_type == "simple_on_off":
            state = "HIGH" if action.get("on", True) else "LOW"
            return f"    digitalWrite({pin}, {state});\n    while(true);\n"

        # fallback
        return (
            f"    digitalWrite({pin}, HIGH);\n"
            f"    delay(500);\n"
            f"    digitalWrite({pin}, LOW);\n"
            f"    delay(500);\n"
        )