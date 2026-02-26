def build_firmware(actions, pin_map):

    code = "#include <Arduino.h>\n\n"
    code += "void setup() {\n"

    # Configure all pins
    used_pins = set(pin_map.values())
    for pin in used_pins:
        code += f"    pinMode({pin}, OUTPUT);\n"

    code += "}\n\n"
    code += "void loop() {\n"

    for action in actions:

        if action["type"] == "blink":

            comp = action["component"].upper()
            pin = pin_map[f"{comp}_GPIO"]

            times = action.get("times", 1)
            interval = action.get("interval_ms", 1000)

            buzzer_pin = None
            if action.get("with"):
                buzzer_pin = pin_map.get("BUZZER_GPIO")

            code += f"    for(int i=0;i<{times};i++){{\n"
            code += f"        digitalWrite({pin}, HIGH);\n"

            if buzzer_pin:
                code += f"        digitalWrite({buzzer_pin}, HIGH);\n"

            code += f"        delay({interval});\n"
            code += f"        digitalWrite({pin}, LOW);\n"

            if buzzer_pin:
                code += f"        digitalWrite({buzzer_pin}, LOW);\n"

            code += f"        delay({interval});\n"
            code += "    }\n"

    code += "    while(true);\n"
    code += "}\n"

    return code