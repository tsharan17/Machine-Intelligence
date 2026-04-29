import {
  app,
  BrowserWindow,
  ipcMain,
  shell,
  dialog,
} from 'electron'
import { join } from 'path'
import { spawn, ChildProcess } from 'child_process'
import { createServer } from 'net'
import * as http from 'http'
import Store from 'electron-store'

// ── Globals ──────────────────────────────────────────────────────────────────
const store = new Store()
const isDev = !!process.env.ELECTRON_RENDERER_URL

let backendProcess: ChildProcess | null = null
let ollamaProcess: ChildProcess | null = null
let backendPort = 8765
let splashWindow: BrowserWindow | null = null
let mainWindow: BrowserWindow | null = null

// ── Prevent multiple instances ────────────────────────────────────────────────
const gotLock = app.requestSingleInstanceLock()
if (!gotLock) {
  app.quit()
  process.exit(0)
}
app.on('second-instance', () => {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore()
    mainWindow.focus()
  }
})

// ── Windows taskbar identity ──────────────────────────────────────────────────
app.setAppUserModelId('Machine Intelligence')

// ── Utilities ─────────────────────────────────────────────────────────────────

/** Find an available TCP port */
function getFreePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const server = createServer()
    server.unref()
    server.on('error', reject)
    server.listen(0, '127.0.0.1', () => {
      const addr = server.address() as { port: number }
      server.close(() => resolve(addr.port))
    })
  })
}

/** Poll backend /health until it responds or we time out */
function waitForBackend(port: number, maxMs = 40_000): Promise<boolean> {
  return new Promise((resolve) => {
    const deadline = Date.now() + maxMs
    const attempt = () => {
      const req = http.get(
        { hostname: '127.0.0.1', port, path: '/health', timeout: 1000 },
        (res) => {
          if (res.statusCode === 200) {
            resolve(true)
          } else {
            scheduleNext()
          }
          res.resume()
        }
      )
      req.on('error', scheduleNext)
      req.on('timeout', scheduleNext)
    }
    const scheduleNext = () => {
      if (Date.now() >= deadline) {
        resolve(false)
      } else {
        setTimeout(attempt, 600)
      }
    }
    attempt()
  })
}

/** Check if Ollama API is reachable */
function isOllamaRunning(): Promise<boolean> {
  return new Promise((resolve) => {
    const req = http.get(
      { hostname: 'localhost', port: 11434, path: '/', timeout: 2000 },
      (res) => {
        resolve(res.statusCode !== undefined)
        res.resume()
      }
    )
    req.on('error', () => resolve(false))
    req.on('timeout', () => resolve(false))
  })
}

/** Try to start Ollama in the background */
function spawnOllama(): ChildProcess | null {
  try {
    const proc = spawn('ollama', ['serve'], {
      stdio: ['ignore', 'pipe', 'pipe'],
      detached: false,
      windowsHide: true,
    })
    proc.stdout?.on('data', (d) => console.log('[Ollama]', d.toString().trim()))
    proc.stderr?.on('data', (d) => console.log('[Ollama]', d.toString().trim()))
    proc.on('error', (e) => console.warn('[Ollama] spawn error:', e.message))
    return proc
  } catch {
    return null
  }
}

// ── Splash window ─────────────────────────────────────────────────────────────
function createSplash(): BrowserWindow {
  const win = new BrowserWindow({
    width: 420,
    height: 260,
    frame: false,
    transparent: true,
    resizable: false,
    alwaysOnTop: true,
    center: true,
    skipTaskbar: true,
    webPreferences: { nodeIntegration: false, contextIsolation: true },
  })

  const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 60%, #16213e 100%);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 16px;
    color: #fff;
    height: 260px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 20px;
    overflow: hidden;
  }
  .logo { font-size: 38px; }
  .title { font-size: 20px; font-weight: 700; letter-spacing: 0.5px;
           background: linear-gradient(90deg,#818cf8,#c084fc);
           -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .subtitle { font-size: 12px; color: rgba(255,255,255,0.4); }
  .bar-track {
    width: 220px; height: 3px;
    background: rgba(255,255,255,0.08);
    border-radius: 99px; overflow: hidden;
  }
  .bar-fill {
    height: 100%;
    background: linear-gradient(90deg,#818cf8,#c084fc);
    border-radius: 99px;
    animation: load 3s ease-in-out infinite;
  }
  @keyframes load { 0%{width:0%} 50%{width:80%} 100%{width:100%} }
  .status { font-size: 11px; color: rgba(255,255,255,0.35); min-height:16px; }
</style>
</head>
<body>
  <div class="logo">🧠</div>
  <div>
    <div class="title">Machine Intelligence</div>
    <div class="subtitle" style="text-align:center;margin-top:4px">AI-Powered Firmware IDE</div>
  </div>
  <div class="bar-track"><div class="bar-fill"></div></div>
  <div class="status" id="s">Starting AI engine...</div>
  <script>
    const msgs = [
      'Loading Whisper model...', 'Starting firmware pipeline...',
      'Connecting AI engine...', 'Almost ready...'
    ]
    let i = 0
    setInterval(()=>{ document.getElementById('s').textContent = msgs[i++ % msgs.length] }, 1800)
  </script>
</body>
</html>`

  win.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`)
  return win
}

// ── Backend launcher ──────────────────────────────────────────────────────────
function spawnBackend(port: number): ChildProcess {
  if (isDev) {
    // Development: run Python source directly
    const scriptPath = join(__dirname, '../../../backend/main.py')
    const proc = spawn('python', [scriptPath, '--port', String(port)], {
      stdio: ['ignore', 'pipe', 'pipe'],
    })
    proc.stdout?.on('data', (d) => console.log('[Backend]', d.toString().trim()))
    proc.stderr?.on('data', (d) => console.error('[Backend]', d.toString().trim()))
    return proc
  } else {
    // Production: run PyInstaller bundle
    const exePath = join(
      process.resourcesPath,
      'backend',
      'machine_intelligence_backend',
      'machine_intelligence_backend.exe'
    )
    const proc = spawn(exePath, ['--port', String(port)], {
      stdio: ['ignore', 'pipe', 'pipe'],
      windowsHide: true,
    })
    proc.stdout?.on('data', (d) => console.log('[Backend]', d.toString().trim()))
    proc.stderr?.on('data', (d) => console.error('[Backend]', d.toString().trim()))
    return proc
  }
}

// ── Main window ────────────────────────────────────────────────────────────────
function createMainWindow(port: number): BrowserWindow {
  const win = new BrowserWindow({
    width: 1440,
    height: 920,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: '#0F0F1A',
    show: false, // show only after ready-to-show
    titleBarStyle: 'hiddenInset',
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
      devTools: isDev,
      webSecurity: !isDev, // relaxed only in dev
    },
  })

  // Expose port to renderer via query string
  if (isDev && process.env.ELECTRON_RENDERER_URL) {
    win.loadURL(`${process.env.ELECTRON_RENDERER_URL}?backendPort=${port}`)
    win.webContents.openDevTools()
  } else {
    win.loadFile(join(__dirname, '../renderer/index.html'), {
      query: { backendPort: String(port) },
    })
  }

  win.once('ready-to-show', () => {
    splashWindow?.destroy()
    splashWindow = null
    win.show()
    win.focus()
  })

  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  return win
}

// ── Graceful shutdown ─────────────────────────────────────────────────────────
function killAll() {
  try { backendProcess?.kill('SIGTERM') } catch { /* noop */ }
  try { ollamaProcess?.kill('SIGTERM') } catch { /* noop */ }
  backendProcess = null
  ollamaProcess = null
}

app.on('before-quit', killAll)
process.on('exit', killAll)
process.on('SIGINT', () => { killAll(); app.quit() })

// ── App lifecycle ─────────────────────────────────────────────────────────────
app.whenReady().then(async () => {
  // 1. Show splash immediately
  splashWindow = createSplash()

  // 2. Find a free port
  try {
    backendPort = await getFreePort()
  } catch {
    backendPort = 8765
  }

  // 3. Spawn Python backend
  backendProcess = spawnBackend(backendPort)
  backendProcess.on('exit', (code) => {
    if (code !== 0 && mainWindow) {
      dialog.showErrorBox(
        'Backend Crashed',
        `The AI engine exited unexpectedly (code ${code}).\nPlease restart the application.`
      )
    }
  })

  // 4. Check / start Ollama
  const ollamaUp = await isOllamaRunning()
  if (!ollamaUp) {
    console.log('[Main] Ollama not running — attempting to start...')
    ollamaProcess = spawnOllama()
    // Give Ollama 4 seconds to come up
    await new Promise((r) => setTimeout(r, 4000))
    const nowUp = await isOllamaRunning()
    if (!nowUp) {
      console.warn('[Main] Ollama unavailable.')
      // Non-blocking warning shown after main window opens
      setTimeout(() => {
        dialog
          .showMessageBox({
            type: 'warning',
            title: 'Ollama Not Found',
            message: 'AI Engine (Ollama) is not installed.',
            detail:
              'Machine Intelligence uses Ollama to generate firmware.\n\n' +
              '1. Download Ollama from https://ollama.com\n' +
              '2. After installing, run in a terminal:\n' +
              '   ollama pull qwen2.5-coder:7b\n\n' +
              'The app will function but firmware generation will fail until Ollama is set up.',
            buttons: ['Download Ollama', 'Continue Without Ollama'],
            defaultId: 0,
          })
          .then(({ response }) => {
            if (response === 0) shell.openExternal('https://ollama.com')
          })
      }, 1500)
    }
  }

  // 5. Wait for backend to be ready
  const ready = await waitForBackend(backendPort, 40_000)
  if (!ready) {
    splashWindow?.destroy()
    dialog.showErrorBox(
      'Startup Failed',
      'The AI engine could not start within 40 seconds.\n\n' +
        'Please check that Python and all dependencies are installed, then try again.'
    )
    app.quit()
    return
  }

  // 6. Open main window
  mainWindow = createMainWindow(backendPort)

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      mainWindow = createMainWindow(backendPort)
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    killAll()
    app.quit()
  }
})

// ── IPC handlers ──────────────────────────────────────────────────────────────
ipcMain.handle('get-backend-port', () => backendPort)
ipcMain.handle('store:set', (_, k, v) => store.set(k, v))
ipcMain.handle('store:get', (_, k) => store.get(k))
ipcMain.handle('store:delete', (_, k) => store.delete(k))
ipcMain.handle('open-url', (_, url) => shell.openExternal(url))