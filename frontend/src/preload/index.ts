// src/preload/index.ts
import { contextBridge, ipcRenderer } from 'electron'
 
contextBridge.exposeInMainWorld('electronAPI', {
  store: {
    set: (k: string, v: unknown) => ipcRenderer.invoke('store:set', k, v),
    get: (k: string) => ipcRenderer.invoke('store:get', k),
    delete: (k: string) => ipcRenderer.invoke('store:delete', k),
  },
  openUrl: (url: string) => ipcRenderer.invoke('open-url', url),
})
 
