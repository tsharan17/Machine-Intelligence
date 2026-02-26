import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"

VALID_TYPES = {
    "digital_output",
    "digital_input",
    "analog_input",
    "pwm_output"
}


def resolve_interfaces(component_name: str):

    prompt = f"""
Return STRICT JSON only.
No explanation.

For component: {component_name}

FORMAT:
{{
  "name": "{component_name}",
  "interfaces": [
    {{
      "label": "INTERFACE_NAME",
      "signal_type": "digital_output|digital_input|analog_input|pwm_output"
    }}
  ]
}}
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()

        raw = response.json().get("response", "").strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        data = json.loads(raw)

        if "interfaces" not in data or not data["interfaces"]:
            raise ValueError("No interfaces returned")

        for iface in data["interfaces"]:
            if "label" not in iface or "signal_type" not in iface:
                raise ValueError("Malformed interface structure")

            if iface["signal_type"] not in VALID_TYPES:
                raise ValueError("Invalid signal type detected")

        return data

    except Exception as e:
        print("[HARDWARE RESOLVE ERROR]", e)
        return None