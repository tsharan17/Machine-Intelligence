import { app, BrowserWindow, ipcMain, shell } from 'electron'
import { join } from 'path'
import { spawn } from 'child_process'
import Store from 'electron-store'

const store = new Store()

function startPython() {
  const py = spawn('python', [join(__dirname, '../../../backend/main.py')])
  py.stdout.on('data', d => console.log('[Python]', d.toString()))
  py.stderr.on('data', d => console.error('[Python]', d.toString()))
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    backgroundColor: '#0F0F1A',
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      devTools: true,
      webSecurity: false,
    }
  })

  win.webContents.openDevTools()

  if (process.env.ELECTRON_RENDERER_URL) {
    win.loadURL(process.env.ELECTRON_RENDERER_URL)
  } else {
    win.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

app.whenReady().then(() => {
  startPython()
  setTimeout(createWindow, 2500)
})

ipcMain.handle('store:set', (_, k, v) => store.set(k, v))
ipcMain.handle('store:get', (_, k) => store.get(k))
ipcMain.handle('store:delete', (_, k) => store.delete(k))
ipcMain.handle('open-url', (_, url) => shell.openExternal(url))