import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def build_and_upload():

    build = subprocess.run(
        ["pio", "run"],
        cwd=PROJECT_ROOT,
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    if build.returncode != 0:
        print("[PIO] Build failed")
        return False

    upload = subprocess.run(
        ["pio", "run", "--target", "upload"],
        cwd=PROJECT_ROOT,
        stdout=sys.stdout,
        stderr=sys.stderr
    )

    if upload.returncode != 0:
        print("[PIO] Upload failed")
        return False

    print("[PIO] Upload successful")
    return True