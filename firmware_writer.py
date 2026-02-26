from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
MAIN_CPP = SRC_DIR / "main.cpp"
PIN_FILE = PROJECT_ROOT / "pin_connections.txt"


def write_firmware(code: str, pin_map: dict):

    SRC_DIR.mkdir(parents=True, exist_ok=True)

    MAIN_CPP.write_text(code, encoding="utf-8")

    with open(PIN_FILE, "w", encoding="utf-8") as f:
        f.write("=== PIN CONNECTIONS ===\n\n")
        for name, pin in pin_map.items():
            f.write(f"{name} -> GPIO {pin}\n")

    print("[WRITER] Firmware and pin connections saved")