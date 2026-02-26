from pathlib import Path

PROMPT_DIR = Path("prompts")
SYSTEM_PROMPT_FILE = PROMPT_DIR / "firmware_system_prompt.txt"


def build_prompt(user_command: str) -> str:

    with open(SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
        system_prompt = f.read().strip()

    STRICT_RULES = """
RETURN STRICT JSON ONLY.
NO explanations.
NO markdown.

FORMAT:

{
  "components": [
    {
      "name": "LED",
      "signal_type": "digital_output"
    }
  ],
  "firmware_code": "FULL ARDUINO CODE HERE"
}

CRITICAL RULES:
- Use {{COMPONENTNAME_PIN}} placeholders directly inside pinMode() and digitalWrite()
- Example: pinMode({{LED_PIN}}, OUTPUT);
- DO NOT define #define LED_PIN
- DO NOT declare const pin variables
- DO NOT use LED_BUILTIN
- Always include setup() and loop()
"""

    return (
        system_prompt
        + "\n\n"
        + STRICT_RULES
        + "\n\nUSER COMMAND:\n"
        + user_command.strip()
    )
