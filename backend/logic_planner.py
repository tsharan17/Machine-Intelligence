from backend.llm_client import query_llm_json


def plan_logic(command: str) -> dict | None:
    """
    Uses LLM to interpret a natural language command into a structured
    list of hardware actions.

    Returns:
        {
            "actions": [
                {
                    "type": "blink",
                    "component": "LED",
                    "times": 5,
                    "interval_ms": 500,
                    "threshold_cm": 0,
                    "with": "BUZZER"
                }
            ]
        }
    """

    prompt = f"""
Return STRICT JSON only.
No explanation. No markdown.

Interpret this hardware command into structured actions.

Allowed action types:
  - blink           : toggle a digital output on/off repeatedly
  - detect_distance : use ultrasonic sensor to measure distance
  - detect_light    : use analog sensor to measure light level
  - simple_on_off   : turn a component fully on or off
  - read_motion     : read IMU sensor data (MPU9250 / MPU6500)

FORMAT:
{{
  "actions": [
    {{
      "type": "blink",
      "component": "LED",
      "times": 5,
      "interval_ms": 500,
      "threshold_cm": 0,
      "with": null
    }}
  ]
}}

Rules:
- Component names must match: LED, BUZZER, ULTRASONIC, SERVO, SERIAL, MPU9250, MPU6500
- "times": 0 means repeat forever
- "interval_ms": milliseconds between on/off toggle
- "threshold_cm": only relevant for detect_distance actions
- "with": optional paired component name (e.g. BUZZER paired with LED blink)
- If command says "5 times" → times: 5
- If command says "blink" with no count → times: 0
- If command mentions MPU, IMU, gyroscope, or accelerometer → use "read_motion"

Command:
{command}
"""

    result = query_llm_json(prompt)

    if not result:
        print("[LOGIC PLANNER] LLM returned no result.")
        return None

    if "actions" not in result or not isinstance(result["actions"], list):
        print("[LOGIC PLANNER] Malformed response — missing 'actions' list.")
        return None

    # Normalize component names
    for action in result["actions"]:
        if "component" in action and action["component"]:
            action["component"] = action["component"].upper().strip()
        if "with" in action and action["with"]:
            action["with"] = action["with"].upper().strip()

    return result