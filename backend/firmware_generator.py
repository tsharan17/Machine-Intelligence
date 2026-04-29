import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"


def sanitize_body(body: str):
    lines = body.splitlines()
    clean = []
    for line in lines:
        line = line.strip()
        if line:
            clean.append("    " + line)
    return "\n".join(clean)


def generate_firmware(logic_description: str, resolved_components: list):

    prompt = f"""
Return STRICT JSON only.
No explanation.

Generate Arduino logic bodies.

RULES:
- Do NOT include #include
- Do NOT include setup()
- Do NOT include loop()
- Do NOT declare pin variables
- Use ONLY interface labels exactly as provided.

Example:
digitalWrite(TRIG, HIGH);
digitalWrite(BUZZER, HIGH);

FORMAT:
{{
  "setup_body": "code",
  "loop_body": "code"
}}

Components:
{json.dumps(resolved_components, indent=2)}

Logic:
{logic_description}
"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()

        raw = response.json()["response"].strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)

        setup_body = sanitize_body(data["setup_body"])
        loop_body = sanitize_body(data["loop_body"])

        return f"""#include <Arduino.h>

void setup() {{
{setup_body}
}}

void loop() {{
{loop_body}
}}
"""

    except Exception as e:
        print("[FIRMWARE GEN ERROR]", e)
        return None