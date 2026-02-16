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
        raw_output = data.get("response", "").strip()

        if not raw_output:
            print("[LLM ERROR] Empty response")
            return None, None

        # Clean accidental markdown
        raw_output = raw_output.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(raw_output)

        firmware_code = parsed.get("firmware_code")
        pin_map = parsed.get("pin_connections", {})

        return firmware_code, pin_map

    except json.JSONDecodeError:
        print("[LLM ERROR] Invalid JSON returned by model")
        print(raw_output)
        return None, None

    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return None, None
