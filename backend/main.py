# backend/main.py
import argparse
import os
import sys

# ── Port config (must come before FastAPI/uvicorn import) ─────────────────────
parser = argparse.ArgumentParser(description="Machine Intelligence Backend")
parser.add_argument('--port', type=int, default=8765,
                    help="Port to listen on (default: 8765)")
args, _ = parser.parse_known_args()
PORT = args.port

# ── PyInstaller path fix ──────────────────────────────────────────────────────
# When frozen, the bundled modules live in sys._MEIPASS.
# We add it to sys.path so relative imports continue to work.
if getattr(sys, 'frozen', False):
    sys.path.insert(0, sys._MEIPASS)            # type: ignore[attr-defined]
    # Components folder packed alongside backend
    components_dir = os.path.join(sys._MEIPASS, 'components')  # type: ignore[attr-defined]
    if os.path.isdir(components_dir) and components_dir not in sys.path:
        sys.path.insert(0, components_dir)

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile, subprocess

from whisper_stt import transcribe_audio
from component_extractor import extract_components_and_logic
from hardware_resolver import resolve_interfaces
from pin_allocator import allocate_pins
from board_mapper import load_board
from logic_planner import plan_logic
from firmware_generator import generate_firmware
from code_validator import validate_and_clean_code
from firmware_writer import write_firmware

app = FastAPI(title="Machine Intelligence API", version="1.0.0")

# Allow Electron renderer to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


class Command(BaseModel):
    command: str
    board: str = 'esp32'


@app.get('/health')
async def health():
    return {'status': 'ok', 'port': PORT}


@app.post('/transcribe')
async def transcribe(audio: UploadFile = File(...)):
    """Transcribe uploaded audio using Whisper STT."""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        tmp.write(await audio.read())
        path = tmp.name
    try:
        text = transcribe_audio(path)
        return {'text': text}
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


@app.post('/generate')
async def generate(req: Command):
    """Run the full firmware generation pipeline."""
    extracted = extract_components_and_logic(req.command)
    if not extracted:
        raise HTTPException(400, 'Could not understand command')

    resolved = []
    for name in extracted['components']:
        r = resolve_interfaces(name)
        if r:
            resolved.append(r)

    board_profile = load_board(req.board)
    pin_map = allocate_pins(resolved, board_profile)
    plan_logic(req.command)
    logic_description = extracted.get('logic_description', req.command)
    firmware = generate_firmware(logic_description, resolved)
    clean = validate_and_clean_code(firmware)

    if not clean:
        raise HTTPException(500, 'Firmware validation failed')

    return {'firmware': clean, 'pin_map': pin_map}


def _pio_command() -> list[str]:
    """
    Return the correct pio command to use.
    When frozen by PyInstaller, platformio is bundled as a Python module
    so we call it as `python -m platformio` instead of bare `pio`.
    """
    if getattr(sys, 'frozen', False):
        return [sys.executable, '-m', 'platformio']
    return ['pio']


@app.post('/build')
async def build(req: Command):
    """Generate firmware and compile with PlatformIO."""
    result = await generate(req)
    write_firmware(result['firmware'], result['pin_map'])
    proc = subprocess.run(
        _pio_command() + ['run'],
        capture_output=True,
        text=True,
    )
    return {'success': proc.returncode == 0, 'log': proc.stdout + proc.stderr}


@app.post('/upload')
async def upload():
    """Upload compiled firmware to connected board."""
    proc = subprocess.run(
        _pio_command() + ['run', '--target', 'upload'],
        capture_output=True,
        text=True,
    )
    return {'success': proc.returncode == 0, 'log': proc.stdout + proc.stderr}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host='127.0.0.1',
        port=PORT,
        log_level='info',
    )
