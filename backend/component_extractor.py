from backend.llm_client import query_llm_json


def extract_components_and_logic(command: str) -> dict | None:
    """
    Uses LLM to extract hardware component names and a brief logic description
    from a natural language command.

    Returns:
        {
            "components": ["LED", "BUZZER"],
            "logic_description": "Blink LED 5 times with buzzer beeping simultaneously"
        }
    """

    prompt = f"""
Return STRICT JSON only.
No explanation. No markdown.

Extract hardware components and describe intended behavior.

FORMAT:
{{
  "components": ["ComponentName1", "ComponentName2"],
  "logic_description": "short plain english description of behavior"
}}

Rules:
- Component names must be simple and generic: "LED", "BUZZER", "ULTRASONIC", "SERVO", "SERIAL"
- Do not include brand names or model numbers
- Keep logic_description under 20 words

Command:
{command}
"""

    result = query_llm_json(prompt)

    if not result:
        print("[COMPONENT EXTRACTOR] LLM returned no result.")
        return None

    if "components" not in result or not isinstance(result["components"], list):
        print("[COMPONENT EXTRACTOR] Malformed response — missing 'components' list.")
        return None

    # Normalize to uppercase
    result["components"] = [c.upper().strip() for c in result["components"]]

    return result