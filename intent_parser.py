import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"


def extract_intent(command: str):
    prompt = f"""
Convert this command into structured hardware JSON.

Command:
{command}

Return STRICT JSON only.

Format:

{{
  "components": [
    {{
      "name": "component_name",
      "interfaces": [
        {{
          "label": "interface_label",
          "signal_type": "digital_input|digital_output|analog_input|pwm_output"
        }}
      ]
    }}
  ],
  "logic": []
}}

Rules:
- Ultrasonic sensor must have trigger (digital_output) and echo (digital_input)
- LED must have signal (digital_output)
- Servo must have signal (pwm_output)
- Temperature sensor analog → analog_input
- Always separate interfaces clearly
- No explanations. JSON only.
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    data = response.json()

    raw = data.get("response", "").strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    return json.loads(raw)
