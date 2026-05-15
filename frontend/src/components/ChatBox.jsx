import { useState, useRef, useEffect } from 'react'
import { Send, Bot, Mic, MicOff, RotateCcw } from 'lucide-react'
import MessageBubble from './MessageBubble'
import LoadingSpinner from './LoadingSpinner'
import { askQuestion, voiceAsk } from '../services/api'
import toast from 'react-hot-toast'

const WELCOME = {
  role: 'ai',
  text: 'ನಮಸ್ಕಾರ! ನಾನು AgriConnect AI ಸಹಾಯಕ.\n\nYou can ask me about government agricultural schemes in Kannada or English. Try:\n• "ನನಗೆ PM-KISAN ಬಗ್ಗೆ ಹೇಳಿ"\n• "What is Krishi Vikas Yojana?"\n• Or tap the 🎤 MIC button below to speak!',
  meta: null,
}

// ─── Inline Voice Recorder ────────────────────────────────────────
function VoiceButton({ onResult, disabled }) {
  const [status, setStatus] = useState('idle') // idle | recording | preview | sending
  const [audioUrl, setAudioUrl] = useState(null)
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])

  const start = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      chunksRef.current = []
      setAudioUrl(null)
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      mediaRecorderRef.current = recorder
      recorder.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data) }
      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop())
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setAudioUrl(URL.createObjectURL(blob))
        setStatus('preview')
      }
      recorder.start()
      setStatus('recording')
      toast('Recording… tap again to stop', { icon: '🎤' })
    } catch {
      toast.error('Microphone access denied. Please allow mic permissions in browser.')
      setStatus('idle')
    }
  }

  const stop = () => { mediaRecorderRef.current?.stop(); setStatus('preview') }

  const send = async () => {
    const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
    setStatus('sending')
    try { await onResult(blob) }
    finally { setStatus('idle'); setAudioUrl(null); chunksRef.current = [] }
  }

  const reset = () => { setStatus('idle'); setAudioUrl(null); chunksRef.current = [] }

  if (status === 'idle') return (
    <button
      onClick={start}
      disabled={disabled}
      title="Speak your question"
      className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-green-600 hover:bg-green-700 text-white font-medium text-sm disabled:opacity-40 transition-all shadow-sm"
    >
      <Mic size={17} /> Voice
    </button>
  )

  if (status === 'recording') return (
    <button
      onClick={stop}
      className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-red-500 hover:bg-red-600 text-white font-medium text-sm transition-all shadow-sm animate-pulse"
    >
      <MicOff size={17} /> Stop
    </button>
  )

  if (status === 'preview') return (
    <div className="flex items-center gap-2">
      <audio controls src={audioUrl} className="h-8 w-32 rounded" />
      <button onClick={send} className="px-3 py-2 rounded-lg bg-green-600 hover:bg-green-700 text-white text-xs font-medium">Send</button>
      <button onClick={reset} title="Discard" className="px-2 py-2 rounded-lg bg-gray-200 hover:bg-gray-300 text-gray-600"><RotateCcw size={13} /></button>
    </div>
  )

  if (status === 'sending') return (
    <div className="flex items-center gap-2 px-3 py-2.5 rounded-xl bg-gray-100">
      <LoadingSpinner size="sm" label="Processing…" />
    </div>
  )

  return null
}

// ─── Main ChatBox ─────────────────────────────────────────────────
export default function ChatBox() {
  const [messages, setMessages] = useState([WELCOME])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [lang, setLang] = useState('kn')    // 'kn' = Kannada, 'en' = English
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const addMessage = (role, text, meta = null) =>
    setMessages((prev) => [...prev, { role, text, meta }])

  const handleTextSend = async () => {
    const q = input.trim()
    if (!q || loading) return
    setInput('')
    addMessage('user', q)
    setLoading(true)
    try {
      const { data } = await askQuestion(q)
      addMessage('ai', data.answer || 'No answer returned.', {
        language: data.language,
        sources_count: data.sources?.length || 0,
      })
    } catch (err) {
      const msg = err.response?.data?.detail || 'Backend offline. Please start the server.'
      addMessage('ai', `⚠️ ${msg}`)
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleVoice = async (audioBlob) => {
    addMessage('user', '🎤 Voice message…')
    setLoading(true)
    try {
      // Pass language hint so Whisper uses the correct decoder
      const { data } = await voiceAsk(audioBlob, lang)
      setMessages((prev) => {
        const updated = [...prev]
        updated[updated.length - 1] = {
          role: 'user',
          text: `🎤 "${data.transcribed_text}"`,
          meta: null,
        }
        return updated
      })
      addMessage('ai', data.answer, {
        language: data.language,
        transcribed_text: data.transcribed_text,
        sources_count: data.sources_count || 0,
        audioPath: data.audio_response_path,
      })
    } catch (err) {
      const msg = err.response?.data?.detail || 'Voice processing failed.'
      setMessages((prev) => {
        const updated = [...prev]
        updated[updated.length - 1] = { role: 'user', text: '🎤 [Voice message — failed]', meta: null }
        return updated
      })
      addMessage('ai', `⚠️ ${msg}`)
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m, i) => <MessageBubble key={i} message={m} />)}

        {/* Typing indicator */}
        {loading && (
          <div className="flex items-center gap-2 message-enter">
            <div className="w-8 h-8 rounded-full bg-green-600 text-white flex items-center justify-center text-xs font-bold">AI</div>
            <div className="bg-white border border-gray-100 shadow-sm px-4 py-3 rounded-2xl rounded-bl-sm flex gap-1.5 items-center">
              <div className="w-2 h-2 bg-green-400 rounded-full dot-1" />
              <div className="w-2 h-2 bg-green-400 rounded-full dot-2" />
              <div className="w-2 h-2 bg-green-400 rounded-full dot-3" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="border-t border-gray-100 bg-white p-3 shadow-[0_-2px_12px_rgba(0,0,0,0.05)]">
        <div className="max-w-3xl mx-auto space-y-2">
          {/* Voice row — prominent, with language toggle */}
          <div className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-xl px-3 py-2">
            {/* Language toggle */}
            <div className="flex rounded-lg overflow-hidden border border-green-300 shrink-0">
              <button
                onClick={() => setLang('kn')}
                className={`px-3 py-1 text-xs font-semibold transition-all ${
                  lang === 'kn' ? 'bg-green-600 text-white' : 'bg-white text-green-700 hover:bg-green-50'
                }`}
              >
                ಕನ್ನಡ
              </button>
              <button
                onClick={() => setLang('en')}
                className={`px-3 py-1 text-xs font-semibold transition-all ${
                  lang === 'en' ? 'bg-green-600 text-white' : 'bg-white text-green-700 hover:bg-green-50'
                }`}
              >
                English
              </button>
            </div>
            <span className="text-xs text-green-700 flex-1">
              {lang === 'kn' ? '🎤 ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡಿ' : '🎤 Speak in English'}
            </span>
            <VoiceButton onResult={handleVoice} disabled={loading} />
          </div>

          {/* Text row */}
          <div className="flex items-end gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleTextSend() }
              }}
              placeholder="Or type your question here… (Kannada or English)"
              disabled={loading}
              rows={1}
              className="flex-1 resize-none border border-gray-200 rounded-2xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent disabled:bg-gray-50 transition-all"
              style={{ minHeight: '42px', maxHeight: '100px' }}
              onInput={(e) => {
                e.target.style.height = 'auto'
                e.target.style.height = Math.min(e.target.scrollHeight, 100) + 'px'
              }}
            />
            <button
              onClick={handleTextSend}
              disabled={loading || !input.trim()}
              className="w-10 h-10 rounded-full bg-green-600 hover:bg-green-700 text-white flex items-center justify-center disabled:opacity-40 disabled:cursor-not-allowed transition-all shrink-0"
            >
              {loading ? <LoadingSpinner size="sm" /> : <Send size={16} />}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
