# build.ps1 — Machine Intelligence Production Build Script
# Run from the project root:  .\build.ps1
# Requires: Python 3.11+, Node 20+, npm

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Machine Intelligence — Production Build    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── Step 0: Verify prerequisites ─────────────────────────────────────────────
Write-Host "▶ Checking prerequisites..." -ForegroundColor Yellow

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found. Install Python 3.11+ and add to PATH."
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js not found. Install Node 20+ from https://nodejs.org"
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Error "npm not found."
}

$pyVersion = python --version
$nodeVersion = node --version
Write-Host "  ✓ $pyVersion" -ForegroundColor Green
Write-Host "  ✓ Node $nodeVersion" -ForegroundColor Green

# ── Step 1: Install Python dependencies ──────────────────────────────────────
Write-Host ""
Write-Host "▶ Installing Python dependencies..." -ForegroundColor Yellow
Set-Location "$Root\backend"
python -m pip install --upgrade pip | Out-Null
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { Write-Error "pip install failed." }
Write-Host "  ✓ Python dependencies installed" -ForegroundColor Green

# ── Step 2: Pre-download Whisper model ───────────────────────────────────────
Write-Host ""
Write-Host "▶ Pre-downloading Whisper 'medium' model (~1.5 GB)..." -ForegroundColor Yellow
Write-Host "  This only runs once. Skip with Ctrl+C if already downloaded." -ForegroundColor Gray
python -c "import whisper; whisper.load_model('medium'); print('Model ready.')"
if ($LASTEXITCODE -ne 0) { Write-Error "Whisper model download failed." }
Write-Host "  ✓ Whisper model ready" -ForegroundColor Green

# ── Step 3: Install PyInstaller ───────────────────────────────────────────────
Write-Host ""
Write-Host "▶ Installing PyInstaller..." -ForegroundColor Yellow
python -m pip install pyinstaller | Out-Null
Write-Host "  ✓ PyInstaller ready" -ForegroundColor Green

# ── Step 4: Bundle Python backend ─────────────────────────────────────────────
Write-Host ""
Write-Host "▶ Bundling Python backend with PyInstaller..." -ForegroundColor Yellow
Set-Location "$Root\backend"
python -m PyInstaller build_backend.spec --clean --noconfirm
if ($LASTEXITCODE -ne 0) { Write-Error "PyInstaller build failed." }
Write-Host "  ✓ Backend bundled → backend/dist/machine_intelligence_backend/" -ForegroundColor Green

# ── Step 5: Install Node dependencies ─────────────────────────────────────────
Write-Host ""
Write-Host "▶ Installing Node dependencies..." -ForegroundColor Yellow
Set-Location "$Root\frontend"
npm install
if ($LASTEXITCODE -ne 0) { Write-Error "npm install failed." }
Write-Host "  ✓ Node dependencies installed" -ForegroundColor Green

# ── Step 6: TypeScript type-check ────────────────────────────────────────────
Write-Host ""
Write-Host "▶ Running TypeScript type check..." -ForegroundColor Yellow
npm run typecheck
if ($LASTEXITCODE -ne 0) { Write-Error "TypeScript errors found. Fix them before building." }
Write-Host "  ✓ Types OK" -ForegroundColor Green

# ── Step 7: Build Electron app ────────────────────────────────────────────────
Write-Host ""
Write-Host "▶ Building Electron app + NSIS installer..." -ForegroundColor Yellow
npm run build:win
if ($LASTEXITCODE -ne 0) { Write-Error "Electron build failed." }

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║          ✓  BUILD COMPLETE                   ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Installer: frontend\dist\Machine Intelligence Setup 1.0.0.exe" -ForegroundColor Cyan
Write-Host ""
Write-Host "To publish a GitHub release:" -ForegroundColor Yellow
Write-Host "  cd frontend && npm run build:win -- --publish always" -ForegroundColor Gray
Write-Host ""

Set-Location $Root
