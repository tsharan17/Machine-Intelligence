from components.base import BaseComponent


class SerialOutput(BaseComponent):

    name = "SERIAL"
    interfaces = []  # No GPIO — uses hardware UART

    def generate_setup(self, pin_assignments: dict, action: dict) -> str:
        baud = action.get("baud_rate", 115200)
        return f"    Serial.begin({baud});\n"

    def generate_loop(self, pin_assignments: dict, action: dict) -> str:
        message  = action.get("message", "Hello from Machine Intelligence!")
        interval = action.get("interval_ms", 1000)
        lines = [
            f"    Serial.println(\"{message}\");",
            f"    delay({interval});",
        ]
        return "\n".join(lines) + "\n"