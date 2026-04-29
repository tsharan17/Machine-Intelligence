// src/renderer/src/App.tsx
import { useState, useEffect, useRef, useCallback } from 'react'
import { createClient } from '@supabase/supabase-js'
import Editor from '@monaco-editor/react'
import axios from 'axios'

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

// ── Types ─────────────────────────────────────────────────────────────────────
type Toast = { id: number; msg: string; type: 'info' | 'success' | 'error' }
type Tab = 'editor' | 'pinmap' | 'log'

// ── Toast component ───────────────────────────────────────────────────────────
function Toasts({ toasts, remove }: { toasts: Toast[]; remove: (id: number) => void }) {
  return (
    <div style={{ position: 'fixed', bottom: 24, right: 24, zIndex: 9999, display: 'flex', flexDirection: 'column', gap: 8 }}>
      {toasts.map(t => (
        <div key={t.id} onClick={() => remove(t.id)} style={{
          padding: '10px 16px', borderRadius: 8, cursor: 'pointer', fontSize: 13,
          backdropFilter: 'blur(12px)', maxWidth: 340, animation: 'fadeIn .2s ease',
          background: t.type === 'error' ? 'rgba(239,68,68,0.18)' : t.type === 'success' ? 'rgba(34,197,94,0.18)' : 'rgba(99,102,241,0.18)',
          border: `1px solid ${t.type === 'error' ? 'rgba(239,68,68,0.4)' : t.type === 'success' ? 'rgba(34,197,94,0.4)' : 'rgba(99,102,241,0.4)'}`,
          color: t.type === 'error' ? '#fca5a5' : t.type === 'success' ? '#86efac' : '#a5b4fc',
        }}>{t.msg}</div>
      ))}
    </div>
  )
}

// ── Main App ──────────────────────────────────────────────────────────────────
export default function App() {
  // Backend
  const [backendUrl, setBackendUrl] = useState('')
  const [backendReady, setBackendReady] = useState(false)

  // Auth
  const [user, setUser]         = useState<any>(null)
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [isSignUp, setIsSignUp] = useState(false)
  const [authError, setAuthError] = useState('')
  const [authLoading, setAuthLoading] = useState(false)

  // Workspace
  const [firmware, setFirmware] = useState('// Your generated firmware will appear here...\n// Press 🎤 and describe your hardware project.')
  const [pinMap, setPinMap]     = useState<Record<string, number>>({})
  const [buildLog, setBuildLog] = useState('')
  const [recording, setRecording] = useState(false)
  const [tier, _setTier]        = useState('free')
  const [buildsUsed, setBuildsUsed] = useState(0)
  const [activeTab, setActiveTab] = useState<Tab>('editor')
  const [busy, setBusy]         = useState(false)
  const [busyLabel, setBusyLabel] = useState('')

  // Toasts
  const [toasts, setToasts]     = useState<Toast[]>([])
  const toastId                 = useRef(0)

  const mediaRef  = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])

  // ── Toast helpers ──────────────────────────────────────────────────────────
  const toast = useCallback((msg: string, type: Toast['type'] = 'info', ms = 4000) => {
    const id = ++toastId.current
    setToasts(t => [...t, { id, msg, type }])
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), ms)
  }, [])

  const removeToast = useCallback((id: number) => setToasts(t => t.filter(x => x.id !== id)), [])

  // ── Backend URL discovery ──────────────────────────────────────────────────
  useEffect(() => {
    const discover = async () => {
      try {
        // Try Electron IPC first
        if (window.electronAPI?.getBackendPort) {
          const port = await window.electronAPI.getBackendPort()
          setBackendUrl(`http://127.0.0.1:${port}`)
          setBackendReady(true)
          return
        }
      } catch { /* fall through */ }
      // Fallback: read from URL query (dev mode injection)
      const params = new URLSearchParams(window.location.search)
      const port = params.get('backendPort') || '8765'
      setBackendUrl(`http://127.0.0.1:${port}`)
      setBackendReady(true)
    }
    discover()
  }, [])

  // ── Session restore ────────────────────────────────────────────────────────
  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      if (data.session) setUser(data.session.user)
    })
  }, [])

  // ── Auth ───────────────────────────────────────────────────────────────────
  const handleAuth = async () => {
    setAuthError(''); setAuthLoading(true)
    try {
      if (isSignUp) {
        const { data, error } = await supabase.auth.signUp({ email, password })
        if (error) throw error
        await supabase.from('profiles').insert({ id: data.user!.id, email })
        toast('Account created! Please sign in.', 'success')
        setIsSignUp(false)
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) throw error
        setUser(data.user)
      }
    } catch (e: any) { setAuthError(e.message) }
    finally { setAuthLoading(false) }
  }

  const handleSignOut = async () => {
    await supabase.auth.signOut(); setUser(null)
  }

  // ── Voice recording ────────────────────────────────────────────────────────
  const startRecording = async () => {
    if (busy) return
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const recorder = new MediaRecorder(stream)
    chunksRef.current = []
    recorder.ondataavailable = e => chunksRef.current.push(e.data)
    recorder.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: 'audio/wav' })
      setBusy(true); setBusyLabel('Transcribing...')
      try {
        const fd = new FormData()
        fd.append('audio', blob, 'cmd.wav')
        const r = await axios.post(`${backendUrl}/transcribe`, fd)
        const text = r.data.text
        if (!text) { toast('No speech detected — try again', 'error'); return }
        toast(`Heard: "${text}"`, 'info')
        await generate(text)
      } catch (e: any) {
        toast('Transcription failed: ' + e.message, 'error')
      } finally {
        setBusy(false); setBusyLabel('')
        stream.getTracks().forEach(t => t.stop())
      }
    }
    recorder.start(); mediaRef.current = recorder
    setRecording(true)
  }

  const stopRecording = () => { mediaRef.current?.stop(); setRecording(false) }

  // ── Generate firmware ──────────────────────────────────────────────────────
  const generate = async (command: string) => {
    setBusy(true); setBusyLabel('Generating firmware...')
    try {
      const r = await axios.post(`${backendUrl}/generate`, { command, board: 'esp32' })
      setFirmware(r.data.firmware)
      setPinMap(r.data.pin_map)
      setBuildsUsed(b => b + 1)
      setActiveTab('editor')
      toast('Firmware generated!', 'success')
    } catch (e: any) {
      if (e.response?.status === 402) {
        toast('Build limit reached! Upgrade to Pro.', 'error', 6000)
      } else {
        toast('Generation failed: ' + (e.response?.data?.detail || e.message), 'error')
      }
    } finally { setBusy(false); setBusyLabel('') }
  }

  // ── Build / Upload ─────────────────────────────────────────────────────────
  const build = async () => {
    setBusy(true); setBusyLabel('Compiling with PlatformIO...')
    try {
      const r = await axios.post(`${backendUrl}/build`, { command: '', board: 'esp32' })
      setBuildLog(r.data.log); setActiveTab('log')
      toast(r.data.success ? 'Build successful!' : 'Build failed — check log', r.data.success ? 'success' : 'error')
    } catch (e: any) { toast('Build error: ' + e.message, 'error') }
    finally { setBusy(false); setBusyLabel('') }
  }

  const upload = async () => {
    setBusy(true); setBusyLabel('Uploading to board...')
    try {
      const r = await axios.post(`${backendUrl}/upload`)
      setBuildLog(r.data.log); setActiveTab('log')
      toast(r.data.success ? 'Uploaded to board!' : 'Upload failed', r.data.success ? 'success' : 'error')
    } catch (e: any) { toast('Upload error: ' + e.message, 'error') }
    finally { setBusy(false); setBusyLabel('') }
  }

  const COMPONENTS = ['LED', 'Buzzer', 'Ultrasonic', 'Servo', 'DHT11', 'OLED', 'Relay', 'IR Sensor', 'PIR', 'RGB LED', 'LDR', 'Potentiometer']

  // ══════════════════════════════════════════════════════════════════════════════
  // LOADING SCREEN (while backend discovers port)
  if (!backendReady) return (
    <div style={{ minHeight:'100vh', background:'#0f0f1a', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:20, fontFamily:'-apple-system,"Segoe UI",sans-serif' }}>
      <div style={{ fontSize:52 }}>🧠</div>
      <div style={{ fontSize:22, fontWeight:700, background:'linear-gradient(90deg,#818cf8,#c084fc)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent' }}>Machine Intelligence</div>
      <div style={{ width:200, height:3, background:'rgba(255,255,255,0.08)', borderRadius:99, overflow:'hidden' }}>
        <div style={{ height:'100%', background:'linear-gradient(90deg,#818cf8,#c084fc)', animation:'load 1.5s ease-in-out infinite', width:'60%' }}/>
      </div>
      <div style={{ color:'rgba(255,255,255,0.35)', fontSize:13 }}>Connecting to AI engine...</div>
      <style>{`@keyframes load{0%{margin-left:0;width:30%}50%{margin-left:40%;width:40%}100%{margin-left:100%;width:10%}}`}</style>
    </div>
  )

  // ══════════════════════════════════════════════════════════════════════════════
  // LOGIN SCREEN
  if (!user) return (
    <div style={{ minHeight:'100vh', background:'linear-gradient(135deg,#0f0f1a 0%,#1a1a2e 60%,#0d0d1f 100%)', display:'flex', alignItems:'center', justifyContent:'center', fontFamily:'-apple-system,"Segoe UI",sans-serif' }}>
      <style>{`
        .auth-input{width:100%;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:10px 14px;color:#fff;font-size:14px;outline:none;transition:border .2s;box-sizing:border-box;}
        .auth-input:focus{border-color:rgba(129,140,248,0.6);}
        .auth-btn{width:100%;padding:11px;border-radius:8px;border:none;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;font-weight:600;font-size:14px;cursor:pointer;transition:opacity .2s;}
        .auth-btn:hover{opacity:0.9;} .auth-btn:disabled{opacity:0.5;cursor:not-allowed;}
        @keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
      `}</style>
      <div style={{ background:'rgba(255,255,255,0.03)', border:'1px solid rgba(255,255,255,0.08)', borderRadius:16, padding:40, width:380, backdropFilter:'blur(20px)', animation:'fadeIn .3s ease' }}>
        <div style={{ textAlign:'center', marginBottom:28 }}>
          <div style={{ fontSize:40, marginBottom:10 }}>🧠</div>
          <div style={{ fontSize:22, fontWeight:700, background:'linear-gradient(90deg,#818cf8,#c084fc)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent' }}>Machine Intelligence</div>
          <div style={{ color:'rgba(255,255,255,0.35)', fontSize:13, marginTop:6 }}>AI-Powered Firmware IDE</div>
        </div>
        <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
          <input className="auth-input" type="email" placeholder="Email address" value={email} onChange={e => setEmail(e.target.value)} onKeyDown={e => e.key==='Enter' && handleAuth()} />
          <input className="auth-input" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} onKeyDown={e => e.key==='Enter' && handleAuth()} />
          {authError && <div style={{ color:'#fca5a5', fontSize:12, padding:'8px 12px', background:'rgba(239,68,68,0.1)', borderRadius:6 }}>{authError}</div>}
          <button className="auth-btn" onClick={handleAuth} disabled={authLoading}>{authLoading ? 'Please wait...' : isSignUp ? 'Create Account' : 'Sign In'}</button>
          <p style={{ color:'rgba(255,255,255,0.3)', fontSize:12, textAlign:'center', cursor:'pointer', margin:0 }} onClick={() => { setIsSignUp(!isSignUp); setAuthError('') }}>
            {isSignUp ? 'Already have an account? Sign in' : "Don't have an account? Sign up free"}
          </p>
        </div>
      </div>
      <Toasts toasts={toasts} remove={removeToast} />
    </div>
  )

  // ══════════════════════════════════════════════════════════════════════════════
  // MAIN IDE
  return (
    <div style={{ display:'flex', flexDirection:'column', height:'100vh', background:'#0f0f1a', color:'#e2e8f0', fontFamily:'-apple-system,"Segoe UI",sans-serif', userSelect:'none' }}>
      <style>{`
        @keyframes fadeIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
        .topbtn{padding:6px 14px;border-radius:7px;border:none;font-size:13px;font-weight:500;cursor:pointer;transition:all .15s;display:flex;align-items:center;gap:6px;}
        .topbtn:hover{filter:brightness(1.2);}
        .topbtn:disabled{opacity:0.45;cursor:not-allowed;}
        .sidebar-item{padding:7px 10px;border-radius:6px;font-size:12px;color:rgba(255,255,255,0.45);cursor:pointer;transition:all .15s;border:1px solid transparent;}
        .sidebar-item:hover{background:rgba(99,102,241,0.12);color:rgba(255,255,255,0.8);border-color:rgba(99,102,241,0.2);}
        .tab{padding:4px 12px;border-radius:6px;font-size:12px;cursor:pointer;border:none;background:transparent;color:rgba(255,255,255,0.4);transition:all .15s;}
        .tab.active{background:rgba(99,102,241,0.2);color:#a5b4fc;}
        .pin-row{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.05);font-size:12px;}
        ::-webkit-scrollbar{width:5px;} ::-webkit-scrollbar-track{background:transparent;} ::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.1);border-radius:99px;}
      `}</style>

      {/* ── Top Bar ── */}
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'0 16px', height:52, background:'rgba(255,255,255,0.03)', borderBottom:'1px solid rgba(255,255,255,0.07)', flexShrink:0 }}>
        <div style={{ display:'flex', alignItems:'center', gap:10 }}>
          <span style={{ fontSize:20 }}>🧠</span>
          <span style={{ fontWeight:700, fontSize:15, background:'linear-gradient(90deg,#818cf8,#c084fc)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent' }}>Machine Intelligence</span>
          {busy && <div style={{ fontSize:12, color:'rgba(255,255,255,0.35)', animation:'pulse 1.2s infinite' }}>⚙ {busyLabel}</div>}
        </div>

        <div style={{ display:'flex', alignItems:'center', gap:8 }}>
          {/* Voice button */}
          <button
            onMouseDown={startRecording} onMouseUp={stopRecording} onMouseLeave={() => recording && stopRecording()}
            disabled={busy}
            style={{ width:40, height:40, borderRadius:'50%', border:'none', cursor:'pointer', fontSize:16, display:'flex', alignItems:'center', justifyContent:'center', transition:'all .2s',
              background: recording ? 'rgba(239,68,68,0.8)' : 'rgba(99,102,241,0.25)',
              boxShadow: recording ? '0 0 20px rgba(239,68,68,0.5)' : 'none',
              animation: recording ? 'pulse 0.8s infinite' : 'none' }}>
            🎤
          </button>

          <button className="topbtn" onClick={build} disabled={busy} style={{ background:'rgba(34,197,94,0.15)', color:'#86efac', border:'1px solid rgba(34,197,94,0.25)' }}>⚙ Build</button>
          <button className="topbtn" onClick={upload} disabled={busy} style={{ background:'rgba(59,130,246,0.15)', color:'#93c5fd', border:'1px solid rgba(59,130,246,0.25)' }}>⚡ Upload</button>

          <div style={{ padding:'4px 10px', borderRadius:6, fontSize:12, fontWeight:600,
            background: tier === 'pro' ? 'rgba(251,191,36,0.2)' : 'rgba(255,255,255,0.06)',
            color: tier === 'pro' ? '#fbbf24' : 'rgba(255,255,255,0.4)',
            border: `1px solid ${tier === 'pro' ? 'rgba(251,191,36,0.3)' : 'rgba(255,255,255,0.08)'}` }}>
            {tier === 'pro' ? '⭐ PRO' : `FREE · ${buildsUsed}/10`}
          </div>

          <button onClick={handleSignOut} style={{ background:'none', border:'none', color:'rgba(255,255,255,0.3)', fontSize:12, cursor:'pointer', padding:'4px 8px' }}>Sign out</button>
        </div>
      </div>

      {/* ── 3-Panel Layout ── */}
      <div style={{ display:'flex', flex:1, overflow:'hidden' }}>

        {/* Left Sidebar */}
        <div style={{ width:160, background:'rgba(255,255,255,0.02)', borderRight:'1px solid rgba(255,255,255,0.06)', padding:12, flexShrink:0, overflowY:'auto' }}>
          <div style={{ fontSize:10, color:'rgba(255,255,255,0.25)', letterSpacing:1, textTransform:'uppercase', marginBottom:10, paddingLeft:4 }}>Components</div>
          {COMPONENTS.map(c => (
            <div key={c} className="sidebar-item" onClick={() => generate(`Use a ${c}`)}>
              {c}
            </div>
          ))}
        </div>

        {/* Center — Tabbed editor / pinmap / log */}
        <div style={{ flex:1, display:'flex', flexDirection:'column', overflow:'hidden' }}>
          {/* Tab bar */}
          <div style={{ display:'flex', gap:4, padding:'6px 12px', borderBottom:'1px solid rgba(255,255,255,0.06)', flexShrink:0, background:'rgba(255,255,255,0.02)' }}>
            {(['editor','pinmap','log'] as Tab[]).map(t => (
              <button key={t} className={`tab ${activeTab===t?'active':''}`} onClick={() => setActiveTab(t)}>
                {t === 'editor' ? '📄 Firmware' : t === 'pinmap' ? '🔌 Pins' : '📋 Build Log'}
              </button>
            ))}
          </div>

          {/* Tab content */}
          {activeTab === 'editor' && (
            <div style={{ flex:1 }}>
              <Editor height="100%" language="cpp" theme="vs-dark" value={firmware}
                onChange={v => setFirmware(v || '')}
                options={{ fontSize:13, minimap:{ enabled:false }, lineNumbers:'on', wordWrap:'on', scrollBeyondLastLine:false, renderLineHighlight:'line', fontFamily:'"JetBrains Mono","Fira Code",monospace' }} />
            </div>
          )}

          {activeTab === 'pinmap' && (
            <div style={{ flex:1, overflowY:'auto', padding:20 }}>
              {Object.entries(pinMap).length === 0 ? (
                <div style={{ color:'rgba(255,255,255,0.2)', fontSize:14, textAlign:'center', marginTop:60 }}>Generate firmware to see pin connections</div>
              ) : (
                <div style={{ maxWidth:480 }}>
                  <div style={{ fontSize:12, color:'rgba(255,255,255,0.3)', marginBottom:12, textTransform:'uppercase', letterSpacing:1 }}>GPIO Assignments</div>
                  {Object.entries(pinMap).map(([name, pin]) => (
                    <div key={name} className="pin-row">
                      <span style={{ color:'rgba(255,255,255,0.6)' }}>{name}</span>
                      <span style={{ color:'#86efac', fontFamily:'monospace', fontWeight:600 }}>GPIO {pin}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'log' && (
            <div style={{ flex:1, overflowY:'auto', padding:16 }}>
              <pre style={{ fontSize:12, color:'rgba(255,255,255,0.5)', fontFamily:'"JetBrains Mono","Fira Code",monospace', whiteSpace:'pre-wrap', lineHeight:1.6 }}>
                {buildLog || 'Build output will appear here after you click ⚙ Build...'}
              </pre>
            </div>
          )}
        </div>

        {/* Right — quick reference */}
        <div style={{ width:240, background:'rgba(255,255,255,0.02)', borderLeft:'1px solid rgba(255,255,255,0.06)', padding:16, overflowY:'auto', flexShrink:0 }}>
          <div style={{ fontSize:10, color:'rgba(255,255,255,0.25)', letterSpacing:1, textTransform:'uppercase', marginBottom:12 }}>Quick Guide</div>
          {[
            { icon:'🎤', title:'Voice', desc:'Hold mic button, speak your hardware description' },
            { icon:'⚙', title:'Build', desc:'Compile firmware with PlatformIO' },
            { icon:'⚡', title:'Upload', desc:'Flash firmware to connected ESP32/Arduino' },
          ].map(x => (
            <div key={x.title} style={{ marginBottom:16, padding:12, background:'rgba(255,255,255,0.03)', borderRadius:8, border:'1px solid rgba(255,255,255,0.06)' }}>
              <div style={{ fontSize:18, marginBottom:4 }}>{x.icon}</div>
              <div style={{ fontSize:13, fontWeight:600, color:'rgba(255,255,255,0.7)', marginBottom:4 }}>{x.title}</div>
              <div style={{ fontSize:11, color:'rgba(255,255,255,0.3)', lineHeight:1.5 }}>{x.desc}</div>
            </div>
          ))}
          <div style={{ marginTop:8, padding:12, background:'rgba(99,102,241,0.08)', borderRadius:8, border:'1px solid rgba(99,102,241,0.15)' }}>
            <div style={{ fontSize:10, color:'#a5b4fc', fontWeight:600, marginBottom:6 }}>EXAMPLE COMMANDS</div>
            {['Blink LED 5 times with buzzer', 'Detect motion with PIR sensor', 'Read temperature with DHT11'].map(ex => (
              <div key={ex} onClick={() => generate(ex)} style={{ fontSize:11, color:'rgba(255,255,255,0.4)', padding:'4px 0', cursor:'pointer', borderBottom:'1px solid rgba(255,255,255,0.04)', transition:'color .15s' }}
                onMouseEnter={e => (e.currentTarget.style.color='rgba(165,180,252,0.8)')}
                onMouseLeave={e => (e.currentTarget.style.color='rgba(255,255,255,0.4)')}>
                → {ex}
              </div>
            ))}
          </div>
        </div>
      </div>

      <Toasts toasts={toasts} remove={removeToast} />
    </div>
  )
}
