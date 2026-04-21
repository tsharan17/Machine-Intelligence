// src/renderer/src/App.tsx
import { useState, useEffect, useRef } from 'react'
import { createClient } from '@supabase/supabase-js'
import Editor from '@monaco-editor/react'
import axios from 'axios'
 
const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)
const BACKEND = 'http://localhost:8765'
const CLOUD   = import.meta.env.VITE_CLOUD_API_URL
 
export default function App() {
  const [user, setUser]         = useState<any>(null)
  const [token, setToken]       = useState('')
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [isSignUp, setIsSignUp] = useState(false)
  const [authError, setAuthError] = useState('')
 
  const [firmware, setFirmware] = useState('// Firmware will appear here...')
  const [pinMap, setPinMap]     = useState<Record<string,number>>({})
  const [buildLog, setBuildLog] = useState('')
  const [status, setStatus]     = useState('')
  const [recording, setRecording] = useState(false)
  const [tier, setTier]         = useState('free')
  const [buildsUsed, setBuildsUsed] = useState(0)
 
  const mediaRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
 
  // Check if already logged in
  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      if (data.session) {
        setUser(data.session.user)
        setToken(data.session.access_token)
      }
    })
  }, [])
 
  // ── Auth ──────────────────────────────────────────────────────────────
  const handleAuth = async () => {
    setAuthError('')
    try {
      if (isSignUp) {
        const { data, error } = await supabase.auth.signUp({ email, password })
        if (error) throw error
        // Create profile row in database
        await supabase.from('profiles').insert({ id: data.user!.id, email })
        alert('Account created! Please sign in.')
        setIsSignUp(false)
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) throw error
        setUser(data.user)
        setToken(data.session!.access_token)
      }
    } catch (e: any) { setAuthError(e.message) }
  }
 
  const handleSignOut = async () => {
    await supabase.auth.signOut()
    setUser(null); setToken('')
  }
 
  // ── Voice recording ───────────────────────────────────────────────────
  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const recorder = new MediaRecorder(stream)
    chunksRef.current = []
    recorder.ondataavailable = e => chunksRef.current.push(e.data)
    recorder.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: 'audio/wav' })
      setStatus('Transcribing...')
      const fd = new FormData()
      fd.append('audio', blob, 'cmd.wav')
      const r = await axios.post(`${BACKEND}/transcribe`, fd)
      setStatus(`Heard: '${r.data.text}' — Generating firmware...`)
      await generate(r.data.text)
      stream.getTracks().forEach(t => t.stop())
    }
    recorder.start()
    mediaRef.current = recorder
    setRecording(true)
    setStatus('Recording... release to stop')
  }
 
  const stopRecording = () => {
    mediaRef.current?.stop()
    setRecording(false)
  }
 
  // ── Generate firmware ─────────────────────────────────────────────────
  const generate = async (command: string) => {
    try {
      // Check build quota with cloud API
      //await axios.post(`${CLOUD}/license/use-build`, {},
        //{ headers: { Authorization: `Bearer ${token}` } })
 
      const r = await axios.post(`${BACKEND}/generate`, { command, board: 'esp32' })
      setFirmware(r.data.firmware)
      setPinMap(r.data.pin_map)
      setBuildsUsed(b => b + 1)
      setStatus('Firmware ready!')
    } catch (e: any) {
      if (e.response?.status === 402) {
        setStatus('Build limit reached!')
        alert('You have used all 10 free builds. Upgrade to Pro for unlimited builds.')
      } else {
        setStatus('Error: ' + e.message)
      }
    }
  }
 
  // ── Build and Upload ──────────────────────────────────────────────────
  const build = async () => {
    setStatus('Building...')
    const r = await axios.post(`${BACKEND}/build`, { command: '', board: 'esp32' })
    setBuildLog(r.data.log)
    setStatus(r.data.success ? 'Build successful!' : 'Build failed — check log')
  }
 
  const upload = async () => {
    setStatus('Uploading to board...')
    const r = await axios.post(`${BACKEND}/upload`)
    setBuildLog(r.data.log)
    setStatus(r.data.success ? 'Uploaded!' : 'Upload failed')
  }
 
  // ══════════════════════════════════════════════════════════════════════
  // LOGIN SCREEN
  if (!user) return (
    <div className='min-h-screen bg-gray-950 flex items-center justify-center'>
      <div className='bg-gray-900 p-8 rounded-xl w-96 border border-gray-800'>
        <h1 className='text-2xl font-bold text-white mb-1'>Machine Intelligence</h1>
        <p className='text-gray-400 text-sm mb-6'>AI-powered firmware development</p>
        <input value={email} onChange={e => setEmail(e.target.value)}
          type='email' placeholder='Email'
          className='w-full bg-gray-800 border border-gray-700 rounded px-3 py-2
                     mb-3 text-white text-sm outline-none focus:border-blue-500' />
        <input value={password} onChange={e => setPassword(e.target.value)}
          type='password' placeholder='Password'
          className='w-full bg-gray-800 border border-gray-700 rounded px-3 py-2
                     mb-4 text-white text-sm outline-none focus:border-blue-500' />
        {authError && <p className='text-red-400 text-xs mb-3'>{authError}</p>}
        <button onClick={handleAuth}
          className='w-full bg-blue-600 hover:bg-blue-500 text-white font-semibold
                     py-2 rounded text-sm'>
          {isSignUp ? 'Create Account' : 'Sign In'}
        </button>
        <p className='text-center text-gray-500 text-xs mt-4 cursor-pointer
                      hover:text-white'
          onClick={() => setIsSignUp(!isSignUp)}>
          {isSignUp ? 'Already have an account? Sign in' : "No account? Sign up free"}
        </p>
      </div>
    </div>
  )
 
  // ══════════════════════════════════════════════════════════════════════
  // MAIN IDE
  return (
    <div className='flex flex-col h-screen bg-gray-950 text-white select-none'>
 
      {/* Top Bar */}
      <div className='flex items-center justify-between px-4 py-2 bg-gray-900
                      border-b border-gray-800 flex-shrink-0'>
        <span className='font-bold text-blue-400 text-lg'>Machine Intelligence</span>
 
        {/* Voice Button */}
        <button
          onMouseDown={startRecording} onMouseUp={stopRecording}
          className={`w-12 h-12 rounded-full text-xl transition-all
            ${recording ? 'bg-red-600 scale-110 animate-pulse' : 'bg-blue-700 hover:bg-blue-600'}`}>
          🎤
        </button>
 
        <div className='flex gap-2 items-center'>
          <button onClick={build}
            className='px-3 py-1.5 bg-green-800 hover:bg-green-700 rounded text-sm'>
            ⚙ Build
          </button>
          <button onClick={upload}
            className='px-3 py-1.5 bg-blue-800 hover:bg-blue-700 rounded text-sm'>
            ⚡ Upload
          </button>
          <span className={`px-2 py-1 rounded text-xs font-bold
            ${tier === 'pro' ? 'bg-yellow-600' : 'bg-gray-700'}`}>
            {tier === 'pro' ? '⭐ PRO' : `FREE ${buildsUsed}/10`}
          </span>
          <button onClick={handleSignOut}
            className='text-gray-500 hover:text-white text-xs'>
            Sign out
          </button>
        </div>
      </div>
 
      {/* Status bar */}
      {status && (
        <div className='px-4 py-1 bg-blue-950 text-blue-300 text-xs border-b border-blue-900'>
          {status}
        </div>
      )}
 
      {/* 3-panel layout */}
      <div className='flex flex-1 overflow-hidden'>
 
        {/* Left sidebar */}
        <div className='w-44 bg-gray-900 border-r border-gray-800 p-3 flex-shrink-0'>
          <p className='text-xs text-gray-500 uppercase mb-2'>Components</p>
          {['LED','Buzzer','Ultrasonic','Servo','DHT11','OLED','Relay'].map(c => (
            <div key={c} className='text-sm py-1.5 px-2 rounded text-gray-400
                                    hover:bg-gray-800 hover:text-white cursor-pointer'>
              {c}
            </div>
          ))}
        </div>
 
        {/* Code editor */}
        <div className='flex-1'>
          <Editor
            height='100%'
            language='cpp'
            theme='vs-dark'
            value={firmware}
            options={{ fontSize: 13, minimap: { enabled: false }, readOnly: false }}
          />
        </div>
 
        {/* Right panel */}
        <div className='w-72 bg-gray-900 border-l border-gray-800 flex flex-col'>
 
          {/* Pin map */}
          <div className='p-3 border-b border-gray-800'>
            <p className='text-xs text-gray-500 uppercase mb-2'>Pin Connections</p>
            {Object.entries(pinMap).length === 0 ? (
              <p className='text-xs text-gray-600'>Generate firmware to see pins</p>
            ) : (
              Object.entries(pinMap).map(([name, pin]) => (
                <div key={name} className='flex justify-between text-xs py-1
                                           border-b border-gray-800'>
                  <span className='text-gray-400'>{name}</span>
                  <span className='text-green-400 font-mono'>GPIO {pin}</span>
                </div>
              ))
            )}
          </div>
 
          {/* Build log */}
          <div className='flex-1 p-3 overflow-y-auto'>
            <p className='text-xs text-gray-500 uppercase mb-2'>Build Log</p>
            <pre className='text-xs text-gray-400 whitespace-pre-wrap font-mono'>
              {buildLog || 'Build output will appear here...'}
            </pre>
          </div>
        </div>
      </div>
    </div>
  )
}
 
