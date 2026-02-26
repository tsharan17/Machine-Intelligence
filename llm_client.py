import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"


def generate_firmware_code(prompt: str):

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )
        response.raise_for_status()

        data = response.json()
        raw = data.get("response", "").strip()

        raw = raw.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(raw)

        return parsed

    except Exception as e:
        print("[LLM ERROR]", e)
        print("RAW OUTPUT:\n", raw)
        return None