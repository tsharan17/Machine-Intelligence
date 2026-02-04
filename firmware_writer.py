from pathlib import Path


PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
MAIN_CPP = SRC_DIR / "main.cpp"


def write_firmware(code: str) -> bool:
    """
    Writes validated firmware code to src/main.cpp.
    Returns True on success, False on failure.
    """

    if not code or not code.strip():
        print("[WRITER ERROR] Empty code. Nothing written.")
        return False

    try:
        # Ensure src/ directory exists
        SRC_DIR.mkdir(parents=True, exist_ok=True)

        # Write firmware
        MAIN_CPP.write_text(code, encoding="utf-8")

        print(f"[WRITER] Firmware written to {MAIN_CPP}")
        return True

    except Exception as e:
        print(f"[WRITER ERROR] Failed to write firmware: {e}")
        return False
