def allocate_pins(resolved_components, board_profile):

    allocation = {}

    digital_pool = board_profile["digital_pins"].copy()
    analog_pool = board_profile["analog_pins"].copy()
    pwm_pool = board_profile["pwm_pins"].copy()

    for comp in resolved_components:

        comp_name = comp["name"].upper()

        for iface in comp["interfaces"]:

            label = iface["label"].upper()
            signal_type = iface["signal_type"]

            if signal_type == "digital_output":
                pin = digital_pool.pop(0)
            elif signal_type == "digital_input":
                pin = digital_pool.pop(0)
            elif signal_type == "analog_input":
                pin = analog_pool.pop(0)
            elif signal_type == "pwm_output":
                pin = pwm_pool.pop(0)
            else:
                raise Exception("Unsupported signal type")

            allocation[f"{comp_name}_{label}"] = pin

    return allocation