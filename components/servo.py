from components.base import BaseComponent


class Servo(BaseComponent):

    name = "SERVO"
    interfaces = [
        {"label": "SIGNAL", "signal_type": "pwm_output"}
    ]

    def generate_setup(self, pin_assignments: dict, action: dict) -> str:
        pin = pin_assignments["SIGNAL"]
        lines = [
            f"    // Servo on GPIO {pin}",
            f"    // Include <ESP32Servo.h> for ESP32 or <Servo.h> for Arduino Uno",
            f"    myServo.attach({pin});",
        ]
        return "\n".join(lines) + "\n"

    def generate_loop(self, pin_assignments: dict, action: dict) -> str:
        angle    = action.get("angle", 90)
        interval = action.get("interval_ms", 1000)
        lines = [
            f"    myServo.write({angle});",
            f"    delay({interval});",
        ]
        return "\n".join(lines) + "\n"