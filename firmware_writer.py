from pathlib import Path
from typing import Dict, Optional


PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
MAIN_CPP = SRC_DIR / "main.cpp"
PIN_FILE = PROJECT_ROOT / "pin_connections.txt"


def write_firmware(code: str, pin_map: Optional[Dict[str, str]] = None) -> bool:
    """
    Writes validated firmware code to src/main.cpp.
    Optionally writes pin connections to pin_connections.txt.

    Returns True on success, False on failure.
    """

    if not code or not code.strip():
        print("[WRITER ERROR] Empty code. Nothing written.")
        return False

    try:
        # Ensure src/ directory exists
        SRC_DIR.mkdir(parents=True, exist_ok=True)

        # Write firmware
        MAIN_CPP.write_text(code.strip(), encoding="utf-8")
        print(f"[WRITER] Firmware written to {MAIN_CPP}")

        # Write pin connections if provided
        if pin_map:
            with open(PIN_FILE, "w", encoding="utf-8") as f:
                f.write("=== PIN CONNECTIONS ===\n")
                for component, gpio in pin_map.items():
                    f.write(f"{component} → {gpio}\n")

            print(f"[WRITER] Pin connections written to {PIN_FILE}")

        return True

    except Exception as e:
        print(f"[WRITER ERROR] Failed to write files: {e}")
        return False
