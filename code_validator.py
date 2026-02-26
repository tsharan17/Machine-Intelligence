import re

def validate_and_clean_code(raw_code: str):

    if not raw_code:
        print("[VALIDATOR] Empty code")
        return None

    code = re.sub(r"```[a-zA-Z]*", "", raw_code)
    code = code.replace("```", "").strip()

    if "#include <Arduino.h>" not in code:
        code = "#include <Arduino.h>\n\n" + code

    if "void setup()" not in code or "void loop()" not in code:
        print("[VALIDATOR] Missing setup() or loop()")
        return None

    return code