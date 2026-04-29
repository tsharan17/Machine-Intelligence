// src/preload/index.ts
import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  /** Returns the dynamically-allocated port the Python backend is listening on */
  getBackendPort: (): Promise<number> => ipcRenderer.invoke('get-backend-port'),

  store: {
    set: (k: string, v: unknown) => ipcRenderer.invoke('store:set', k, v),
    get: (k: string) => ipcRenderer.invoke('store:get', k),
    delete: (k: string) => ipcRenderer.invoke('store:delete', k),
  },

  openUrl: (url: string) => ipcRenderer.invoke('open-url', url),
})
