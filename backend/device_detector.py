import subprocess


def detect_connected_device() -> str | None:
    """
    Detects a connected microcontroller via PlatformIO's device list.

    Returns the port string (e.g. '/dev/ttyUSB0' or 'COM3'), or None if not found.
    """
    try:
        result = subprocess.run(
            ["pio", "device", "list", "--serial"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            print("[DEVICE DETECTOR] PlatformIO device list command failed.")
            return None

        for line in result.stdout.strip().splitlines():
            if any(kw in line for kw in ["/dev/ttyUSB", "/dev/ttyACM", "COM"]):
                port = line.strip().split()[0]
                print(f"[DEVICE DETECTOR] Found device: {port}")
                return port

        print("[DEVICE DETECTOR] No serial device found. Is the board connected?")
        return None

    except FileNotFoundError:
        print("[DEVICE DETECTOR] PlatformIO (pio) not installed or not in PATH.")
        return None
    except subprocess.TimeoutExpired:
        print("[DEVICE DETECTOR] Device detection timed out.")
        return None
    except Exception as e:
        print(f"[DEVICE DETECTOR] Unexpected error: {e}")
        return None