from components.base import BaseComponent


class RGBLED(BaseComponent):
    """
    RGB LED (Common Cathode)

    Interfaces:
        R (pwm_output) — Red channel
        G (pwm_output) — Green channel
        B (pwm_output) — Blue channel

    Wiring:
        R pin   → 330Ω resistor → GPIO (PWM)
        G pin   → 330Ω resistor → GPIO (PWM)
        B pin   → 330Ω resistor → GPIO (PWM)
        GND pin → GND

    Note: For Common Anode RGB LED, invert values (255 - value)
    """

    name = "RGB"
    interfaces = [
        {"label": "R", "signal_type": "pwm_output"},
        {"label": "G", "signal_type": "pwm_output"},
        {"label": "B", "signal_type": "pwm_output"},
    ]

    def generate_setup(self, pin_assignments: dict, action: dict) -> str:
        r = pin_assignments["R"]
        g = pin_assignments["G"]
        b = pin_assignments["B"]
        lines = [
            f"    pinMode({r}, OUTPUT);",
            f"    pinMode({g}, OUTPUT);",
            f"    pinMode({b}, OUTPUT);",
            f"    // Turn off RGB at startup",
            f"    analogWrite({r}, 0);",
            f"    analogWrite({g}, 0);",
            f"    analogWrite({b}, 0);",
            f"    Serial.begin(115200);",
        ]
        return "\n".join(lines) + "\n"

    def generate_loop(self, pin_assignments: dict, action: dict) -> str:
        r           = pin_assignments["R"]
        g           = pin_assignments["G"]
        b           = pin_assignments["B"]
        action_type = action.get("type", "blink")
        interval    = action.get("interval_ms", 500)

        # Get color values (0-255), default to white
        red_val   = action.get("red",   255)
        green_val = action.get("green", 255)
        blue_val  = action.get("blue",  255)

        if action_type == "blink":
            times = action.get("times", 0)
            if times > 0:
                lines = [
                    f"    for (int i = 0; i < {times}; i++) {{",
                    f"        analogWrite({r}, {red_val});",
                    f"        analogWrite({g}, {green_val});",
                    f"        analogWrite({b}, {blue_val});",
                    f"        delay({interval});",
                    f"        analogWrite({r}, 0);",
                    f"        analogWrite({g}, 0);",
                    f"        analogWrite({b}, 0);",
                    f"        delay({interval});",
                    f"    }}",
                    f"    while(true);",
                ]
            else:
                lines = [
                    f"    analogWrite({r}, {red_val});",
                    f"    analogWrite({g}, {green_val});",
                    f"    analogWrite({b}, {blue_val});",
                    f"    delay({interval});",
                    f"    analogWrite({r}, 0);",
                    f"    analogWrite({g}, 0);",
                    f"    analogWrite({b}, 0);",
                    f"    delay({interval});",
                ]

        elif action_type == "color_cycle":
            # Cycle through Red → Green → Blue
            lines = [
                f"    // Red",
                f"    analogWrite({r}, 255); analogWrite({g}, 0);   analogWrite({b}, 0);",
                f"    delay({interval});",
                f"    // Green",
                f"    analogWrite({r}, 0);   analogWrite({g}, 255); analogWrite({b}, 0);",
                f"    delay({interval});",
                f"    // Blue",
                f"    analogWrite({r}, 0);   analogWrite({g}, 0);   analogWrite({b}, 255);",
                f"    delay({interval});",
            ]

        elif action_type == "simple_on_off":
            on = action.get("on", True)
            if on:
                lines = [
                    f"    analogWrite({r}, {red_val});",
                    f"    analogWrite({g}, {green_val});",
                    f"    analogWrite({b}, {blue_val});",
                    f"    while(true);",
                ]
            else:
                lines = [
                    f"    analogWrite({r}, 0);",
                    f"    analogWrite({g}, 0);",
                    f"    analogWrite({b}, 0);",
                    f"    while(true);",
                ]
        else:
            lines = [
                f"    analogWrite({r}, {red_val});",
                f"    analogWrite({g}, {green_val});",
                f"    analogWrite({b}, {blue_val});",
                f"    delay({interval});",
            ]

        return "\n".join(lines) + "\n"
