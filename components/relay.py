from components.base import BaseComponent


class Relay(BaseComponent):
    """
    Single-channel Relay Module (5V relay, active LOW or HIGH)

    Interfaces:
        IN (digital_output) — control signal from microcontroller

    Wiring:
        VCC → 5V (most relay modules need 5V coil)
        GND → GND
        IN  → GPIO (digital output)

    Notes:
        - Active LOW relays: LOW = relay ON, HIGH = relay OFF
        - Active HIGH relays: HIGH = relay ON, LOW = relay OFF
        - Default here is ACTIVE LOW (most common modules)
        - Controls high-voltage devices (lamps, motors, pumps)
        - NEVER connect mains voltage without proper isolation
    """

    name = "RELAY"
    interfaces = [
        {"label": "IN", "signal_type": "digital_output"}
    ]

    def generate_setup(self, pin_assignments: dict, action: dict) -> str:
        pin         = pin_assignments["IN"]
        active_low  = action.get("active_low", True)
        init_state  = "HIGH" if active_low else "LOW"  # start with relay OFF
        lines = [
            f"    pinMode({pin}, OUTPUT);",
            f"    digitalWrite({pin}, {init_state});  // relay OFF at startup",
            f"    Serial.begin(115200);",
        ]
        return "\n".join(lines) + "\n"

    def generate_loop(self, pin_assignments: dict, action: dict) -> str:
        pin        = pin_assignments["IN"]
        active_low = action.get("active_low", True)
        on_state   = "LOW"  if active_low else "HIGH"
        off_state  = "HIGH" if active_low else "LOW"
        interval   = action.get("interval_ms", 1000)
        action_type = action.get("type", "blink")

        if action_type == "blink":
            times = action.get("times", 0)
            if times > 0:
                lines = [
                    f"    for (int i = 0; i < {times}; i++) {{",
                    f"        digitalWrite({pin}, {on_state});   // relay ON",
                    f"        Serial.println(\"Relay: ON\");",
                    f"        delay({interval});",
                    f"        digitalWrite({pin}, {off_state});  // relay OFF",
                    f"        Serial.println(\"Relay: OFF\");",
                    f"        delay({interval});",
                    f"    }}",
                    f"    while(true);",
                ]
            else:
                lines = [
                    f"    digitalWrite({pin}, {on_state});",
                    f"    Serial.println(\"Relay: ON\");",
                    f"    delay({interval});",
                    f"    digitalWrite({pin}, {off_state});",
                    f"    Serial.println(\"Relay: OFF\");",
                    f"    delay({interval});",
                ]
        elif action_type == "simple_on_off":
            on      = action.get("on", True)
            state   = on_state if on else off_state
            label   = "ON" if on else "OFF"
            lines   = [
                f"    digitalWrite({pin}, {state});",
                f"    Serial.println(\"Relay: {label}\");",
                f"    while(true);",
            ]
        else:
            lines = [
                f"    digitalWrite({pin}, {on_state});",
                f"    delay({interval});",
                f"    digitalWrite({pin}, {off_state});",
                f"    delay({interval});",
            ]

        return "\n".join(lines) + "\n"
