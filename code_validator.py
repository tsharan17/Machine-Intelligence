import re


FORBIDDEN_KEYWORDS = [
    "WiFi",
    "Bluetooth",
    "while(true)",
    "for(;;)"
]


def validate_and_clean_code(raw_code: str):

    if not raw_code:
        return None

    code = re.sub(r"```[a-zA-Z]*", "", raw_code)
    code = code.replace("```", "").strip()

    # Force include if missing
    if "#include <Arduino.h>" not in code:
        code = "#include <Arduino.h>\n\n" + code

    if "void setup()" not in code or "void loop()" not in code:
        print("[VALIDATOR] Missing setup/loop")
        return None

    for word in FORBIDDEN_KEYWORDS:
        if word in code:
            print("[VALIDATOR] Forbidden construct used")
            return None

    return code