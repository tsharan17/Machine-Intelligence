import { ElectronAPI } from '@electron-toolkit/preload'

declare global {
  interface Window {
    electron: ElectronAPI
    electronAPI: {
      getBackendPort: () => Promise<number>
      store: {
        set: (k: string, v: unknown) => Promise<void>
        get: (k: string) => Promise<unknown>
        delete: (k: string) => Promise<void>
      }
      openUrl: (url: string) => Promise<void>
    }
  }
}
