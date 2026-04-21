import re


def validate_and_clean_code(raw_code: str) -> str | None:
    """
    Validates and cleans Arduino firmware code.

    - Strips markdown fences if present
    - Ensures required headers are present
    - Confirms setup() and loop() both exist

    Returns cleaned code string, or None if invalid.
    """

    if not raw_code or not raw_code.strip():
        print("[VALIDATOR] Empty code received.")
        return None

    # Strip markdown fences
    code = re.sub(r"```[a-zA-Z]*", "", raw_code)
    code = code.replace("```", "").strip()

    includes = []

    # Ensure Arduino core include
    if "#include <Arduino.h>" not in code:
        includes.append("#include <Arduino.h>")

    # ✅ NEW: Auto-detect I2C usage (MPU, sensors, etc.)
    if "Wire" in code and "#include <Wire.h>" not in code:
        includes.append("#include <Wire.h>")

    # Prepend includes if needed
    if includes:
        code = "\n".join(includes) + "\n\n" + code

    # Confirm structural validity
    if "void setup()" not in code:
        print("[VALIDATOR] ✗ Missing void setup().")
        return None

    if "void loop()" not in code:
        print("[VALIDATOR] ✗ Missing void loop().")
        return None

    return code