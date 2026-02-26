import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"


def plan_logic(command: str):

    prompt = f"""
Return STRICT JSON only.
No explanation.

Interpret the command into structured intent.

Allowed action types:
- blink
- detect_distance
- detect_light
- simple_on_off

Format:

{{
  "actions": [
    {{
      "type": "...",
      "component": "...",
      "times": 0,
      "interval_ms": 0,
      "threshold_cm": 0,
      "with": null
    }}
  ]
}}

Command:
{command}
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()

    raw = response.json()["response"].strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    return json.loads(raw)