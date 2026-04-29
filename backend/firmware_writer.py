from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
SRC_DIR      = PROJECT_ROOT / "src"
MAIN_CPP     = SRC_DIR / "main.cpp"
PIN_FILE     = PROJECT_ROOT / "pin_connections.txt"


def write_firmware(code: str, pin_map: dict):
    """
    Writes firmware to src/main.cpp and saves the pin map to pin_connections.txt.

    pin_map format (nested):
        {"LED": {"SIGNAL": 2}, "ULTRASONIC": {"TRIG": 4, "ECHO": 5}}
    """

    SRC_DIR.mkdir(parents=True, exist_ok=True)

    MAIN_CPP.write_text(code, encoding="utf-8")

    with open(PIN_FILE, "w", encoding="utf-8") as f:
        f.write("=== PIN CONNECTIONS ===\n\n")
        for comp_name, interfaces in pin_map.items():
            for label, pin in interfaces.items():
                f.write(f"{comp_name}.{label}  →  GPIO {pin}\n")

    print(f"[WRITER] Firmware  → {MAIN_CPP}")
    print(f"[WRITER] Pin map   → {PIN_FILE}")