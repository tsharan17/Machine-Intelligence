def allocate_pins(resolved_components: list, board_profile: dict) -> dict:
    """
    Deterministically assigns GPIO pins from the board profile to each
    component interface.
    """

    allocation = {}

    # Copy pools so original profile is untouched
    digital_pool = board_profile["digital_pins"].copy()
    analog_pool  = board_profile["analog_pins"].copy()
    pwm_pool     = board_profile["pwm_pins"].copy()

    # ⚠️ Remove unsafe / problematic ESP32 pins (basic sanity filter)
    RESERVED_PINS = {0, 1, 3, 6, 7, 8, 9, 10, 11}  # boot + flash pins
    digital_pool = [p for p in digital_pool if p not in RESERVED_PINS]

    for comp in resolved_components:

        comp_name = comp["name"].upper()
        allocation[comp_name] = {}

        # ✅ FIX 1: Force I2C pins for MPU (prevents random garbage allocation)
        if comp_name in ["MPU9250", "MPU6500"]:
            allocation[comp_name]["SDA"] = 21
            allocation[comp_name]["SCL"] = 22

            # Remove them from pool if present
            if 21 in digital_pool:
                digital_pool.remove(21)
            if 22 in digital_pool:
                digital_pool.remove(22)

            continue

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