import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent


def build_and_upload() -> bool:
    """
    Builds and uploads firmware using PlatformIO.
    Returns True on success, False on failure.
    """

    try:
        print("[PIO] Building firmware...")
        build_cmd = ["pio", "run"]
        build_proc = subprocess.run(
            build_cmd,
            cwd=PROJECT_ROOT,
            stdout=sys.stdout,
            stderr=sys.stderr
        )

        if build_proc.returncode != 0:
            print("[PIO ERROR] Build failed")
            return False

        print("[PIO] Uploading firmware...")
        upload_cmd = ["pio", "run", "--target", "upload"]
        upload_proc = subprocess.run(
            upload_cmd,
            cwd=PROJECT_ROOT,
            stdout=sys.stdout,
            stderr=sys.stderr
        )

        if upload_proc.returncode != 0:
            print("[PIO ERROR] Upload failed")
            return False

        print("[PIO] Firmware uploaded successfully")
        return True

    except FileNotFoundError:
        print("[PIO ERROR] PlatformIO CLI not found. Is PlatformIO installed?")
        return False

    except Exception as e:
        print(f"[PIO ERROR] Unexpected error: {e}")
        return False

