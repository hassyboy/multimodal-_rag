import { useState, useRef } from 'react'
import { Mic, MicOff, Send, RotateCcw } from 'lucide-react'
import LoadingSpinner from './LoadingSpinner'

export default function VoiceRecorder({ onResult, disabled }) {
  const [status, setStatus] = useState('idle') // idle | recording | sending
  const [audioUrl, setAudioUrl] = useState(null)
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      chunksRef.current = []
      setAudioUrl(null)

      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      mediaRecorderRef.current = recorder

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop())
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setAudioUrl(URL.createObjectURL(blob))
        setStatus('preview')
      }

      recorder.start()
      setStatus('recording')
    } catch {
      alert('Microphone access denied. Please allow microphone permissions.')
      setStatus('idle')
    }
  }

  const stopRecording = () => {
    mediaRecorderRef.current?.stop()
  }

  const sendAudio = async () => {
    const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
    setStatus('sending')
    try {
      await onResult(blob)
    } finally {
      setStatus('idle')
      setAudioUrl(null)
      chunksRef.current = []
    }
  }

  const reset = () => {
    setStatus('idle')
    setAudioUrl(null)
    chunksRef.current = []
  }

  return (
    <div className="flex items-center gap-2">
      {status === 'idle' && (
        <button
          onClick={startRecording}
          disabled={disabled}
          title="Start voice recording"
          className="relative w-10 h-10 rounded-full bg-green-100 hover:bg-green-200 text-green-700 flex items-center justify-center transition-all disabled:opacity-40"
        >
          <Mic size={18} />
        </button>
      )}

      {status === 'recording' && (
        <button
          onClick={stopRecording}
          className="relative w-10 h-10 rounded-full bg-red-500 hover:bg-red-600 text-white flex items-center justify-center recording-pulse transition-all"
          title="Stop recording"
        >
          <MicOff size={18} />
        </button>
      )}

      {status === 'preview' && (
        <div className="flex items-center gap-2">
          <audio controls src={audioUrl} className="h-8 w-36 rounded" />
          <button
            onClick={sendAudio}
            className="w-8 h-8 rounded-full bg-green-600 hover:bg-green-700 text-white flex items-center justify-center"
            title="Send recording"
          >
            <Send size={14} />
          </button>
          <button
            onClick={reset}
            className="w-8 h-8 rounded-full bg-gray-200 hover:bg-gray-300 text-gray-600 flex items-center justify-center"
            title="Discard and re-record"
          >
            <RotateCcw size={14} />
          </button>
        </div>
      )}

      {status === 'sending' && (
        <div className="flex items-center gap-2 px-3">
          <LoadingSpinner size="sm" label="Processing voice..." />
        </div>
      )}
    </div>
  )
}
