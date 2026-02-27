def print_circuit_diagram(board_name: str, resolved_components: list, pin_map: dict):
    """
    Prints a human-readable wiring diagram to the terminal.

    pin_map format (nested):
        {"LED": {"SIGNAL": 2}, "ULTRASONIC": {"TRIG": 4, "ECHO": 5}}
    """

    print("\n" + "=" * 60)
    print("              COMPLETE CIRCUIT DIAGRAM")
    print("=" * 60)

    print(f"\n  Board : {board_name.upper()}")
    print(  "  Logic : 3.3V (ESP32) — use level shifter for 5V devices\n")
    print(  "  General Rules:")
    print(  "    • Connect ALL component GND → board GND")
    print(  "    • Connect ALL component VCC → 3.3V or 5V (check datasheet)")
    print(  "    • Use 330Ω resistors in series with LEDs\n")
    print("-" * 60)

    for comp in resolved_components:

        comp_name = comp["name"].upper()
        comp_pins = pin_map.get(comp_name, {})

        print(f"\n  [{comp_name}]")

        if not comp_pins:
            print("    (No GPIO pins — uses built-in hardware interface)")
        else:
            for label, pin in comp_pins.items():
                print(f"    GPIO {pin:<3}  ←→  {comp_name} {label}")

        print(f"    GND      ←→  {comp_name} GND")

    print("\n" + "=" * 60 + "\n")