import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"


def generate_firmware_code(prompt: str) -> str | None:
    """
    Sends a prompt to the local Ollama LLM and returns generated firmware code.
    """

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
        code = data.get("response", "").strip()

        if not code:
            print("[LLM ERROR] Empty response from model")
            return None

        return code

    except requests.exceptions.RequestException as e:
        print(f"[LLM ERROR] Ollama request failed: {e}")
        return None
