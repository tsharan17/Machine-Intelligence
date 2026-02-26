def print_circuit_diagram(board_name: str, resolved_components: list, pin_map: dict):

    print("\n" + "=" * 60)
    print("                    COMPLETE CIRCUIT DIAGRAM")
    print("=" * 60)

    print(f"\nBoard: {board_name.upper()}")
    print("\nGeneral Wiring Rules:")
    print("  • Connect all device GND to board GND")
    print("  • Ensure voltage compatibility (ESP32 = 3.3V logic)")
    print("  • Use resistors/level shifting if required\n")

    for comp in resolved_components:

        comp_name = comp["name"].upper()
        print(f"{comp_name}")
        print("-" * len(comp_name))

        for iface in comp["interfaces"]:

            label = iface["label"].upper()
            key = f"{comp_name}_{label}"

            if key in pin_map:
                pin = pin_map[key]
                print(f"  GPIO {pin:<3} ---> {comp_name} {label}")

        print("  GND       ---> GND\n")

    print("=" * 60 + "\n")