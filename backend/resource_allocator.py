def allocate_resources(ir, board_profile):

    allocation = {}

    digital_pool = board_profile["digital_pins"].copy()
    analog_pool = board_profile["analog_pins"].copy()
    pwm_pool = board_profile["pwm_pins"].copy()

    for comp in ir.components:
        comp_name = comp["name"]

        for interface in comp["interfaces"]:
            signal_type = interface["signal_type"]
            label = interface["label"]

            if signal_type == "digital_output":
                pin = digital_pool.pop(0)
            elif signal_type == "digital_input":
                pin = digital_pool.pop(0)
            elif signal_type == "analog_input":
                pin = analog_pool.pop(0)
            elif signal_type == "pwm_output":
                pin = pwm_pool.pop(0)
            else:
                raise Exception(f"Unsupported signal type: {signal_type}")

            allocation[f"{comp_name}.{label}"] = {
                "pin": pin,
                "signal_type": signal_type
            }

    return allocation
