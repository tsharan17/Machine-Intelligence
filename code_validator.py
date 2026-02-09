"""
code_validator.py

Validates and cleans LLM-generated Arduino/ESP32 firmware code.
"""

import re


FORBIDDEN_KEYWORDS = [
    "WiFi",
    "Bluetooth",
    "delayMicroseconds",
    "while(true)",
    "for(;;)"
]

VALID_GPIO_PINS_ESP32 = {
    0, 2, 4, 5, 12, 13, 14, 15,
    18, 19, 21, 22, 23, 25, 26, 27,
    32, 33
}


def _strip_markdown(code: str) -> str:
    code = re.sub(r"```[a-zA-Z]*", "", code)
    code = code.replace("```", "")
    return code.strip()


def _ensure_required_includes(code: str) -> str:
    includes = []

    if "#include <Arduino.h>" not in code:
        includes.append("#include <Arduino.h>")

    if "Wire." in code and "#include <Wire.h>" not in code:
        includes.append("#include <Wire.h>")

    if "SPI." in code and "#include <SPI.h>" not in code:
        includes.append("#include <SPI.h>")

    if "Serial" in code and "#include <HardwareSerial.h>" not in code:
        includes.append("#include <HardwareSerial.h>")

    if includes:
        code = "\n".join(includes) + "\n\n" + code

    return code


def _has_required_functions(code: str) -> bool:
    return (
        re.search(r"\bvoid\s+setup\s*\(", code) is not None
        and re.search(r"\bvoid\s+loop\s*\(", code) is not None
    )


def _contains_forbidden_constructs(code: str) -> bool:
    return any(keyword in code for keyword in FORBIDDEN_KEYWORDS)


def _validate_gpio_usage(code: str) -> bool:
    pins = re.findall(r"pinMode\s*\(\s*(\d+)", code)
    pins += re.findall(r"digitalWrite\s*\(\s*(\d+)", code)

    for pin in pins:
        if int(pin) not in VALID_GPIO_PINS_ESP32:
            return False
    return True


def validate_and_clean_code(raw_code: str) -> str | None:
    if not raw_code or not raw_code.strip():
        print("[VALIDATOR ERROR] Empty code received")
        return None

    code = _strip_markdown(raw_code)
    code = _ensure_required_includes(code)

    if not _has_required_functions(code):
        print("[VALIDATOR ERROR] Missing setup() or loop()")
        return None

    if _contains_forbidden_constructs(code):
        print("[VALIDATOR ERROR] Forbidden constructs detected")
        return None

    if not _validate_gpio_usage(code):
        print("[VALIDATOR ERROR] Invalid or unsafe GPIO pin used")
        return None

    return code.strip()
