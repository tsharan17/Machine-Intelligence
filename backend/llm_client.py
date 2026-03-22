import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"


def query_llm(prompt: str) -> str:
    """
    Send a prompt to the local Ollama LLM.
    Returns the raw text response, or empty string on failure.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("response", "").strip()

    except requests.exceptions.ConnectionError:
        print("[LLM ERROR] Cannot connect to Ollama. Is it running? Run: ollama serve")
        return ""
    except requests.exceptions.Timeout:
        print("[LLM ERROR] Request timed out after 120s.")
        return ""
    except Exception as e:
        print(f"[LLM ERROR] {e}")
        return ""


def query_llm_json(prompt: str) -> dict | None:
    """
    Send a prompt expecting a JSON response.
    Strips markdown fences and parses JSON.
    Returns parsed dict, or None on failure.
    """
    raw = query_llm(prompt)
    if not raw:
        return None

    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[LLM ERROR] JSON parse failed: {e}")
        print(f"[LLM ERROR] Raw output:\n{raw[:500]}")
        return None