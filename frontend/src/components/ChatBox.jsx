import { useState, useRef, useEffect } from 'react'
import { Send, Mic, MicOff, Volume2, VolumeX } from 'lucide-react'
import MessageBubble from './MessageBubble'
import LoadingSpinner from './LoadingSpinner'
import { askQuestion } from '../services/api'
import toast from 'react-hot-toast'

// ─── Welcome message ───────────────────────────────────────────────────────
const WELCOME = {
  role: 'ai',
  text: 'ನಮಸ್ಕಾರ! ನಾನು AgriConnect AI ಸಹಾಯಕ.\n\nYou can ask me about government agricultural schemes.\nTry:\n• "ಪಿಎಂ ಕಿಸಾನ್ ಯೋಜನೆ ಬಗ್ಗೆ ಹೇಳಿ"\n• "What is PM-KISAN scheme?"\n• Tap 🎤 Voice, speak in ಕನ್ನಡ or English!',
  meta: null,
}

// ─── Browser TTS helper ────────────────────────────────────────────────────
function speakText(text, language) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = language === 'kannada' ? 'kn-IN' : 'en-IN'
  u.rate = 0.9
  window.speechSynthesis.speak(u)
}

// ─── Voice Button using Web Speech API ────────────────────────────────────
// Uses browser's built-in Google speech recognition (kn-IN) — 
// far better Kannada accuracy than Whisper base model.
function VoiceButton({ lang, onTranscript, disabled }) {
  const [status, setStatus] = useState('idle') // idle | listening
  const recRef = useRef(null)

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

  const start = () => {
    if (!SpeechRecognition) {
      toast.error('Speech recognition not supported. Please use Chrome or Edge browser.')
      return
    }
    const recognition = new SpeechRecognition()
    recognition.lang        = lang === 'kn' ? 'kn-IN' : 'en-IN'
    recognition.interimResults = false
    recognition.maxAlternatives = 1
    recRef.current = recognition

    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript.trim()
      const confidence = e.results[0][0].confidence
      setStatus('idle')
      if (transcript) {
        onTranscript(transcript, lang === 'kn' ? 'kannada' : 'english', confidence)
      } else {
        toast.error('Could not understand speech. Please try again.')
      }
    }

    recognition.onerror = (e) => {
      setStatus('idle')
      if (e.error === 'no-speech') toast.error('No speech detected. Speak louder and closer to the mic.')
      else if (e.error === 'not-allowed') toast.error('Microphone permission denied.')
      else toast.error(`Speech error: ${e.error}`)
    }

    recognition.onend = () => setStatus('idle')

    recognition.start()
    setStatus('listening')
    toast(`Listening in ${lang === 'kn' ? 'ಕನ್ನಡ' : 'English'}… speak now`, { icon: '🎤', duration: 2500 })
  }

  const stop = () => {
    recRef.current?.stop()
    setStatus('idle')
  }

  if (status === 'idle') return (
    <button
      onClick={start}
      disabled={disabled}
      title={lang === 'kn' ? 'ಕನ್ನಡದಲ್ಲಿ ಮಾತನಾಡಿ' : 'Speak in English'}
      className="flex items-center gap-2 px-4 py-2 rounded-xl bg-green-600 hover:bg-green-700 text-white font-medium text-sm disabled:opacity-40 transition-all shadow-sm"
    >
      <Mic size={16} />
      {lang === 'kn' ? 'ಮಾತನಾಡಿ' : 'Speak'}
    </button>
  )

  return (
    <button
      onClick={stop}
      className="flex items-center gap-2 px-4 py-2 rounded-xl bg-red-500 hover:bg-red-600 text-white font-medium text-sm animate-pulse transition-all shadow-sm"
    >
      <MicOff size={16} /> ನಿಲ್ಲಿಸಿ / Stop
    </button>
  )
}

// ─── Main ChatBox ─────────────────────────────────────────────────────────
export default function ChatBox() {
  const [messages, setMessages] = useState([WELCOME])
  const [input, setInput]       = useState('')
  const [loading, setLoading]   = useState(false)
  const [lang, setLang]         = useState('kn')   // 'kn' = Kannada, 'en' = English
  const [speaking, setSpeaking] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const addMessage = (role, text, meta = null) =>
    setMessages((prev) => [...prev, { role, text, meta }])

  // ── Text question ─────────────────────────────────────────────────
  const handleTextSend = async () => {
    const q = input.trim()
    if (!q || loading) return
    setInput('')
    addMessage('user', q)
    await queryBackend(q, lang === 'kn' ? 'kannada' : 'english')
  }

  // ── Voice transcript from Web Speech API ──────────────────────────
  const handleTranscript = async (transcript, language, confidence) => {
    addMessage('user', `🎤 "${transcript}"`)
    toast.success(`Heard: "${transcript.slice(0, 40)}${transcript.length > 40 ? '…' : ''}"`, { duration: 3000 })
    await queryBackend(transcript, language)
  }

  // ── Shared query logic ────────────────────────────────────────────
  const queryBackend = async (question, language) => {
    setLoading(true)
    try {
      const { data } = await askQuestion(question)
      const answer = data.answer || 'No answer returned.'
      addMessage('ai', answer, {
        language,
        sources_count: data.sources?.length || 0,
        canSpeak: true,
      })
      // Auto-speak the response in the correct language
      speakText(answer, language)
      setSpeaking(true)
      setTimeout(() => setSpeaking(false), 500)
    } catch (err) {
      const msg = err.response?.data?.detail || 'Backend offline. Make sure the server is running on port 8000.'
      addMessage('ai', `⚠️ ${msg}`)
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const stopSpeaking = () => {
    window.speechSynthesis?.cancel()
    setSpeaking(false)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m, i) => (
          <MessageBubble
            key={i}
            message={m}
            onSpeak={() => speakText(m.text, m.meta?.language || 'kannada')}
          />
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="flex items-center gap-2 message-enter">
            <div className="w-8 h-8 rounded-full bg-green-600 text-white flex items-center justify-center text-xs font-bold shrink-0">AI</div>
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

          {/* Voice row with language toggle */}
          <div className="flex items-center gap-2 bg-green-50 border border-green-200 rounded-xl px-3 py-2">
            {/* ಕನ್ನಡ / English pill toggle */}
            <div className="flex rounded-lg overflow-hidden border border-green-300 text-xs font-semibold shrink-0">
              <button
                onClick={() => setLang('kn')}
                className={`px-3 py-1.5 transition-all ${lang === 'kn' ? 'bg-green-600 text-white' : 'bg-white text-green-700 hover:bg-green-50'}`}
              >
                ಕನ್ನಡ
              </button>
              <button
                onClick={() => setLang('en')}
                className={`px-3 py-1.5 transition-all ${lang === 'en' ? 'bg-green-600 text-white' : 'bg-white text-green-700 hover:bg-green-50'}`}
              >
                English
              </button>
            </div>

            <span className="text-xs text-green-700 flex-1 font-medium">
              {lang === 'kn' ? '🎤 ಕನ್ನಡದಲ್ಲಿ ಪ್ರಶ್ನೆ ಕೇಳಿ' : '🎤 Ask your question by voice'}
            </span>

            {/* Stop speaking button (when AI is talking) */}
            {speaking && (
              <button
                onClick={stopSpeaking}
                className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-amber-100 text-amber-700 text-xs font-medium mr-1"
              >
                <VolumeX size={13} /> Stop
              </button>
            )}

            <VoiceButton lang={lang} onTranscript={handleTranscript} disabled={loading} />
          </div>

          {/* Text input row */}
          <div className="flex items-end gap-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleTextSend() } }}
              placeholder={lang === 'kn' ? 'ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ… (ಕನ್ನಡ ಅಥವಾ English)' : 'Type your question here… (Kannada or English)'}
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
              className="w-10 h-10 rounded-full bg-green-600 hover:bg-green-700 text-white flex items-center justify-center disabled:opacity-40 transition-all shrink-0"
            >
              {loading ? <LoadingSpinner size="sm" /> : <Send size={16} />}
            </button>
          </div>

        </div>
      </div>
    </div>
  )
}
