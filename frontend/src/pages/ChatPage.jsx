import ChatBox from '../components/ChatBox'
import { Leaf } from 'lucide-react'

export default function ChatPage() {
  return (
    <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-56px)]">
      {/* Page header */}
      <div className="px-4 py-3 border-b border-gray-100 bg-white flex items-center gap-2">
        <Leaf size={18} className="text-green-500" />
        <div>
          <h1 className="text-sm font-semibold text-gray-800">Agricultural Scheme Assistant</h1>
          <p className="text-xs text-gray-400">Ask in Kannada (ಕನ್ನಡ) or English · Voice supported</p>
        </div>
      </div>

      {/* Chat area fills remaining height */}
      <div className="flex-1 overflow-hidden">
        <ChatBox />
      </div>
    </div>
  )
}
