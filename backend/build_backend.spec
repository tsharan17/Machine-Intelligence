# build_backend.spec
# PyInstaller spec for Machine Intelligence backend
# Run from the `backend/` directory:
#   pyinstaller build_backend.spec
#
# Output: dist/machine_intelligence_backend/  (entire folder goes into frontend/resources/backend/)

import os
import sys

block_cipher = None

# ── Paths ────────────────────────────────────────────────────────────────────
BACKEND_DIR   = SPECPATH                                      # .../backend
PROJECT_ROOT  = os.path.dirname(SPECPATH)                     # project root
COMPONENTS_DIR = os.path.join(PROJECT_ROOT, 'components')     # .../components
PIN_PROFILES  = os.path.join(BACKEND_DIR, 'pin_profiles')

# ── Collect Whisper data (tokenizer assets, etc.) ────────────────────────────
from PyInstaller.utils.hooks import collect_data_files, collect_all

datas = []
datas += collect_data_files('whisper')          # multilingual.tiktoken etc.
datas += collect_data_files('platformio')       # platform definitions, boards

# ── Bundle pre-downloaded Whisper model ──────────────────────────────────────
# Model must be downloaded first: `python -c "import whisper; whisper.load_model('medium')"`
# It lives in ~/.cache/whisper/ on Windows → %USERPROFILE%\.cache\whisper
whisper_cache = os.path.join(os.path.expanduser('~'), '.cache', 'whisper')
if os.path.isdir(whisper_cache):
    for fname in os.listdir(whisper_cache):
        full = os.path.join(whisper_cache, fname)
        if os.path.isfile(full):
            datas.append((full, 'whisper_models'))
            print(f"[SPEC] Bundling Whisper model: {fname}")
else:
    print("[SPEC] WARNING: No Whisper models found in ~/.cache/whisper")
    print("[SPEC]          Run: python -c \"import whisper; whisper.load_model('medium')\"")

# ── Bundle component Python modules ──────────────────────────────────────────
if os.path.isdir(COMPONENTS_DIR):
    for fname in os.listdir(COMPONENTS_DIR):
        if fname.endswith('.py'):
            datas.append((os.path.join(COMPONENTS_DIR, fname), 'components'))

# ── Bundle pin profiles ───────────────────────────────────────────────────────
if os.path.isdir(PIN_PROFILES):
    datas.append((PIN_PROFILES, 'pin_profiles'))

# ── Hidden imports ────────────────────────────────────────────────────────────
hiddenimports = [
    # uvicorn
    'uvicorn', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto',
    'uvicorn.loops.asyncio', 'uvicorn.protocols', 'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto', 'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl', 'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto', 'uvicorn.lifespan',
    'uvicorn.lifespan.off', 'uvicorn.lifespan.on',
    # fastapi
    'fastapi', 'fastapi.responses', 'fastapi.middleware.cors',
    # pydantic
    'pydantic', 'pydantic.v1', 'pydantic_core',
    # whisper + torch
    'whisper', 'torch', 'torchaudio', 'numba', 'numba.core', 'llvmlite',
    # platformio
    'platformio', 'platformio.commands', 'platformio.__main__',
    'click',
    # audio / multipart
    'soundfile', 'sounddevice', 'multipart', 'python_multipart',
    'aiofiles',
    # local backend modules (all files in backend/)
    'whisper_stt', 'component_extractor', 'hardware_resolver', 'pin_allocator',
    'board_mapper', 'logic_planner', 'firmware_generator', 'code_validator',
    'firmware_writer', 'component_registry', 'hardware_documentation',
    'intent_parser', 'llm_client', 'prompt_manager', 'resource_allocator',
    'resource_ir', 'speech_input', 'device_detector', 'error_handler',
    'circuit_printer', 'command_cleaner', 'firmware_builder',
    'firmware_compiler', 'platformio_runner', 'pin_profiles',
]

a = Analysis(
    ['main.py'],
    pathex=[
        BACKEND_DIR,
        COMPONENTS_DIR,
    ],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'IPython', 'jupyter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='machine_intelligence_backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,    # Keep console visible — useful for debugging crashes
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='machine_intelligence_backend',
)
