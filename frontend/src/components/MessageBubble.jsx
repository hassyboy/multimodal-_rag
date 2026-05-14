import { useState, useRef } from 'react'
import { Volume2, VolumeX, Play, Pause } from 'lucide-react'

function AudioPlayer({ src, label = 'Play Response' }) {
  const audioRef = useRef(null)
  const [playing, setPlaying] = useState(false)

  const toggle = () => {
    if (!audioRef.current) return
    if (playing) {
      audioRef.current.pause()
      setPlaying(false)
    } else {
      audioRef.current.play()
      setPlaying(true)
    }
  }

  return (
    <div className="flex items-center gap-2 mt-2">
      <button
        onClick={toggle}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-green-100 hover:bg-green-200 text-green-700 text-xs font-medium transition-all"
      >
        {playing ? <Pause size={13} /> : <Play size={13} />}
        {playing ? 'Pause' : label}
      </button>
      {/* Waveform dots animation when playing */}
      {playing && (
        <div className="flex items-end gap-0.5 h-4">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="w-1 bg-green-500 rounded-full"
              style={{
                height: `${Math.floor(Math.random() * 12 + 4)}px`,
                animation: `bounce-dot 0.6s ease-in-out ${i * 0.1}s infinite alternate`,
              }}
            />
          ))}
        </div>
      )}
      <audio
        ref={audioRef}
        src={src}
        onEnded={() => setPlaying(false)}
        className="hidden"
      />
    </div>
  )
}

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} message-enter`}>
      {/* Avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-green-600 text-white flex items-center justify-center text-xs font-bold mr-2 shrink-0 mt-1">
          AI
        </div>
      )}

      <div className={`max-w-[80%] ${isUser ? 'max-w-[70%]' : ''}`}>
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap
            ${isUser
              ? 'bg-green-600 text-white rounded-br-sm'
              : 'bg-white text-gray-800 border border-gray-100 shadow-sm rounded-bl-sm'
            }`}
        >
          {message.text}
        </div>

        {/* AI metadata */}
        {!isUser && message.meta && (
          <div className="mt-1.5 px-1 space-y-1">
            {message.meta.language && (
              <span className="inline-block px-2 py-0.5 bg-green-50 text-green-700 text-xs rounded-full border border-green-200">
                {message.meta.language === 'kannada' ? 'ಕನ್ನಡ' : 'English'}
              </span>
            )}
            {message.meta.transcribed_text && (
              <p className="text-xs text-gray-400 italic">
                Heard: "{message.meta.transcribed_text}"
              </p>
            )}
            {message.meta.sources_count > 0 && (
              <p className="text-xs text-gray-400">
                {message.meta.sources_count} source{message.meta.sources_count !== 1 ? 's' : ''} retrieved
              </p>
            )}
            {message.meta.audioPath && (
              <AudioPlayer src={`/api/audio/${encodeURIComponent(message.meta.audioPath.split(/[\\/]/).pop())}`} />
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center text-xs font-bold ml-2 shrink-0 mt-1">
          You
        </div>
      )}
    </div>
  )
}
