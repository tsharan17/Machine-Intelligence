# backend/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile, os, subprocess
 
from whisper_stt import transcribe_audio
from component_extractor import extract_components_and_logic
from hardware_resolver import resolve_interfaces
from pin_allocator import allocate_pins
from board_mapper import load_board
from logic_planner import plan_logic
from firmware_generator import generate_firmware
from code_validator import validate_and_clean_code
from firmware_writer import write_firmware
 
app = FastAPI()
 
# This allows the Electron app to talk to this Python server
app.add_middleware(CORSMiddleware,
    allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
 
 
class Command(BaseModel):
    command: str
    board: str = 'esp32'
 
 
@app.get('/health')
async def health():
    return {'status': 'ok'}
 
 
@app.post('/transcribe')
async def transcribe(audio: UploadFile = File(...)):
    # Save audio to temp file, run Whisper on it
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        tmp.write(await audio.read())
        path = tmp.name
    try:
        text = transcribe_audio(path)
        return {'text': text}
    finally:
        os.unlink(path)
 
 
@app.post('/generate')
async def generate(req: Command):
    # Run your existing pipeline
    extracted = extract_components_and_logic(req.command)
    if not extracted:
        raise HTTPException(400, 'Could not understand command')
 
    resolved = []
    for name in extracted['components']:
        r = resolve_interfaces(name)
        if r: resolved.append(r)
 
    board_profile = load_board(req.board)
    pin_map = allocate_pins(resolved, board_profile)
    logic = plan_logic(req.command)
    logic_description = extracted.get('logic_description', req.command)
    firmware = generate_firmware(logic_description, resolved)
    clean = validate_and_clean_code(firmware)
 
    if not clean:
        raise HTTPException(500, 'Firmware validation failed')
 
    return {'firmware': clean, 'pin_map': pin_map}
 
 
@app.post('/build')
async def build(req: Command):
    result = await generate(req)
    write_firmware(result['firmware'], result['pin_map'])
    proc = subprocess.run(['pio', 'run'], capture_output=True, text=True)
    return {'success': proc.returncode == 0, 'log': proc.stdout + proc.stderr}
 
 
@app.post('/upload')
async def upload():
    proc = subprocess.run(
        ['pio', 'run', '--target', 'upload'],
        capture_output=True, text=True
    )
    return {'success': proc.returncode == 0, 'log': proc.stdout + proc.stderr}
 
 
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8765)
