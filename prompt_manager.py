"""
prompt_manager.py

Builds the final prompt sent to the LLM.
"""

from pathlib import Path

PROMPT_DIR = Path("prompts")
SYSTEM_PROMPT_FILE = PROMPT_DIR / "firmware_system_prompt.txt"


def build_prompt(user_command: str) -> str:
    if not user_command or not user_command.strip():
        raise ValueError("Empty user command received.")

    if not SYSTEM_PROMPT_FILE.exists():
        raise FileNotFoundError(
            f"System prompt file not found: {SYSTEM_PROMPT_FILE}"
        )

    with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
        system_prompt = f.read().strip()

    if not system_prompt:
        raise ValueError("System prompt file is empty.")

    # Enforce library discipline at prompt level
    library_rules = """
LIBRARY RULES (MANDATORY):
- Always include <Arduino.h>
- If I2C (Wire) is used, 반드시 include <Wire.h>
- If SPI is used, 반드시 include <SPI.h>
- If Serial/UART is used, include <HardwareSerial.h> when required
- Do NOT assume implicit library inclusion
"""

    final_prompt = (
        system_prompt
        + "\n\n"
        + library_rules.strip()
        + "\n\n"
        + "USER COMMAND:\n"
        + user_command.strip()
    )

    return final_prompt
