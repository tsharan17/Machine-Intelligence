import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"


def extract_components_and_logic(command: str):

    prompt = f"""
Return STRICT JSON only.
No explanation.

Extract hardware components and describe intended behavior.

FORMAT:
{{
  "components": ["component1", "component2"],
  "logic_description": "short description"
}}

Command:
{command}
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

        return json.loads(raw)

    except Exception as e:
        print("[COMPONENT EXTRACT ERROR]", e)
        return None