import { useState, useRef, useEffect } from 'react'
import { Send, Bot } from 'lucide-react'
import MessageBubble from './MessageBubble'
import VoiceRecorder from './VoiceRecorder'
import LoadingSpinner from './LoadingSpinner'
import { askQuestion, voiceAsk } from '../services/api'
import toast from 'react-hot-toast'

const WELCOME = {
  role: 'ai',
  text: 'ನಮಸ್ಕಾರ! ನಾನು AgriConnect AI ಸಹಾಯಕ.\n\nYou can ask me about government agricultural schemes in Kannada or English. Try:\n• "ನನಗೆ PM-KISAN ಬಗ್ಗೆ ಹೇಳಿ"\n• "What is Krishi Vikas Yojana?"\n• Or tap the mic to speak!',
  meta: null,
}

export default function ChatBox() {
  const [messages, setMessages] = useState([WELCOME])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const addMessage = (role, text, meta = null) => {
    setMessages((prev) => [...prev, { role, text, meta }])
  }

  const handleTextSend = async () => {
    const q = input.trim()
    if (!q || loading) return
    setInput('')
    addMessage('user', q)
    setLoading(true)

    try {
      const { data } = await askQuestion(q)
      addMessage('ai', data.answer, {
        language: data.language,
        sources_count: data.sources?.length || 0,
      })
    } catch (err) {
      const msg = err.response?.data?.detail || 'Backend offline. Please start the server.'
      addMessage('ai', `Error: ${msg}`)
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleVoice = async (audioBlob) => {
    addMessage('user', '🎤 Voice message sent...')
    setLoading(true)

    try {
      const { data } = await voiceAsk(audioBlob)

      // Replace placeholder with transcription
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
      addMessage('ai', `Error: ${msg}`)
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}

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

      {/* Input area */}
      <div className="border-t border-gray-100 bg-white p-3">
        <div className="flex items-end gap-2 max-w-3xl mx-auto">
          <VoiceRecorder onResult={handleVoice} disabled={loading} />

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleTextSend() } }}
            placeholder="Ask about government schemes... (Kannada or English)"
            disabled={loading}
            rows={1}
            className="flex-1 resize-none border border-gray-200 rounded-2xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent disabled:bg-gray-50 transition-all"
            style={{ minHeight: '42px', maxHeight: '120px' }}
            onInput={(e) => {
              e.target.style.height = 'auto'
              e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
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
  )
}
