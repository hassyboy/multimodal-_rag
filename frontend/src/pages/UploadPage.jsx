import UploadCard from '../components/UploadCard'
import { CloudUpload } from 'lucide-react'

export default function UploadPage() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-green-100 flex items-center justify-center">
            <CloudUpload size={22} className="text-green-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-800">Upload Documents</h1>
        </div>
        <p className="text-gray-500 text-sm ml-13">
          Upload government agricultural scheme PDFs to add them to the AI knowledge base.
          After uploading, click <strong>Process Documents</strong> to ingest into the RAG system.
        </p>
      </div>

      <UploadCard />

      {/* Info box */}
      <div className="mt-6 bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800">
        <p className="font-medium mb-1">How it works</p>
        <ol className="list-decimal ml-4 space-y-1 text-amber-700">
          <li>Upload one or more government scheme PDFs</li>
          <li>Click <strong>Process Documents</strong> to ingest into ChromaDB</li>
          <li>Go to <strong>Scheme Assistant</strong> and ask questions</li>
          <li>Ask in Kannada, English, or use your voice!</li>
        </ol>
      </div>
    </div>
  )
}
