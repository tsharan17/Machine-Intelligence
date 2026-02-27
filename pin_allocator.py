def allocate_pins(resolved_components: list, board_profile: dict) -> dict:
    """
    Deterministically assigns GPIO pins from the board profile to each
    component interface.

    Args:
        resolved_components: list of dicts, e.g.:
            [
                {"name": "LED",    "interfaces": [{"label": "SIGNAL", "signal_type": "digital_output"}]},
                {"name": "BUZZER", "interfaces": [{"label": "SIGNAL", "signal_type": "digital_output"}]},
            ]
        board_profile: dict loaded from pin_profiles/<board>.json

    Returns:
        Nested allocation dict, e.g.:
            {
                "LED":        {"SIGNAL": 2},
                "ULTRASONIC": {"TRIG": 4, "ECHO": 5},
                "BUZZER":     {"SIGNAL": 12},
            }
    """

    allocation    = {}
    digital_pool  = board_profile["digital_pins"].copy()
    analog_pool   = board_profile["analog_pins"].copy()
    pwm_pool      = board_profile["pwm_pins"].copy()

    for comp in resolved_components:

        comp_name = comp["name"].upper()
        allocation[comp_name] = {}

        for iface in comp["interfaces"]:

            label       = iface["label"].upper()
            signal_type = iface["signal_type"]

            if signal_type in ("digital_output", "digital_input"):
                if not digital_pool:
                    raise RuntimeError(
                        f"[PIN ALLOCATOR] Ran out of digital pins while allocating "
                        f"{comp_name}.{label}. Use a board with more GPIOs."
                    )
                pin = digital_pool.pop(0)

            elif signal_type == "analog_input":
                if not analog_pool:
                    raise RuntimeError(
                        f"[PIN ALLOCATOR] Ran out of analog pins while allocating "
                        f"{comp_name}.{label}."
                    )
                pin = analog_pool.pop(0)

            elif signal_type == "pwm_output":
                if not pwm_pool:
                    raise RuntimeError(
                        f"[PIN ALLOCATOR] Ran out of PWM pins while allocating "
                        f"{comp_name}.{label}."
                    )
                pin = pwm_pool.pop(0)

            else:
                raise ValueError(
                    f"[PIN ALLOCATOR] Unsupported signal type: '{signal_type}' "
                    f"for {comp_name}.{label}"
                )

            allocation[comp_name][label] = pin

    return allocation