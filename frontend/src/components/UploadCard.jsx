import { useState, useCallback } from 'react'
import { Upload, FileText, CheckCircle, XCircle, Loader, Cpu, Trash2 } from 'lucide-react'
import { uploadPdf, processDocuments, listDocuments } from '../services/api'
import LoadingSpinner from './LoadingSpinner'
import toast from 'react-hot-toast'

export default function UploadCard() {
  const [files, setFiles] = useState([])
  const [processing, setProcessing] = useState(false)
  const [processResult, setProcessResult] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const [loadingList, setLoadingList] = useState(false)

  // Load already-uploaded files from server on demand
  const loadExistingFiles = async () => {
    setLoadingList(true)
    try {
      const { data } = await listDocuments()
      if (data.files?.length > 0) {
        setFiles(data.files.map((f) => ({
          name: f.filename,
          size: f.size_kb * 1024,
          file: null,
          status: 'done',
          msg: `Already on server (${f.size_kb} KB)`,
        })))
        toast.success(`Found ${data.files.length} file(s) on server`)
      } else {
        toast('No files on server yet. Upload some PDFs first.')
      }
    } catch {
      toast.error('Could not reach backend. Is the server running?')
    } finally {
      setLoadingList(false)
    }
  }

  const addFiles = (newFiles) => {
    const pdfs = [...newFiles].filter((f) => f.name.endsWith('.pdf'))
    if (pdfs.length === 0) { toast.error('Only PDF files are accepted.'); return }
    setFiles((prev) => [
      ...prev,
      ...pdfs.map((f) => ({ name: f.name, size: f.size, file: f, status: 'pending', msg: '' })),
    ])
  }

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    addFiles(e.dataTransfer.files)
  }, [])

  const onFileInput = (e) => addFiles(e.target.files)

  const uploadAll = async () => {
    const pending = files.filter((f) => f.status === 'pending')
    if (pending.length === 0) { toast('No new files to upload.'); return }

    for (const fileObj of pending) {
      setFiles((prev) => prev.map((f) => f.name === fileObj.name ? { ...f, status: 'uploading' } : f))
      try {
        const { data } = await uploadPdf(fileObj.file)
        setFiles((prev) => prev.map((f) => f.name === fileObj.name ? { ...f, status: 'done', msg: data.message } : f))
      } catch (err) {
        const msg = err.response?.data?.detail || 'Upload failed'
        setFiles((prev) => prev.map((f) => f.name === fileObj.name ? { ...f, status: 'error', msg } : f))
      }
    }
    toast.success('Upload complete!')
  }

  const handleProcess = async () => {
    setProcessing(true)
    setProcessResult(null)
    try {
      const { data } = await processDocuments()
      setProcessResult(data)
      if (data.success) toast.success(`Ingested ${data.total_chunks} chunks!`)
      else toast.error(data.message)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Processing failed')
    } finally {
      setProcessing(false)
    }
  }

  const removeFile = (name) => setFiles((prev) => prev.filter((f) => f.name !== name))

  const statusIcon = (status) => {
    if (status === 'uploading') return <Loader size={15} className="animate-spin text-blue-500" />
    if (status === 'done') return <CheckCircle size={15} className="text-green-500" />
    if (status === 'error') return <XCircle size={15} className="text-red-500" />
    return <FileText size={15} className="text-gray-400" />
  }

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => document.getElementById('file-input').click()}
        className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all
          ${dragOver ? 'border-green-500 bg-green-50' : 'border-green-300 bg-white hover:bg-green-50'}`}
      >
        <Upload size={36} className="mx-auto text-green-400 mb-3" />
        <p className="text-gray-600 font-medium">Drag & drop PDFs here</p>
        <p className="text-gray-400 text-sm mt-1">or click to browse</p>
        <input id="file-input" type="file" multiple accept=".pdf" onChange={onFileInput} className="hidden" />
      </div>

      {/* Load existing files from server */}
      <button
        onClick={loadExistingFiles}
        disabled={loadingList}
        className="w-full py-2 rounded-xl border border-green-300 text-green-700 text-sm hover:bg-green-50 transition-all disabled:opacity-40"
      >
        {loadingList ? 'Loading...' : 'Load files already on server'}
      </button>

      {/* File list */}
      {files.length > 0 && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm divide-y divide-gray-50">
          {files.map((f) => (
            <div key={f.name} className="flex items-center gap-3 px-4 py-3">
              {statusIcon(f.status)}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-700 truncate">{f.name}</p>
                {f.msg && <p className="text-xs text-gray-400 truncate">{f.msg}</p>}
                {!f.msg && <p className="text-xs text-gray-400">{(f.size / 1024).toFixed(1)} KB</p>}
              </div>
              {f.status === 'pending' && (
                <button onClick={() => removeFile(f.name)} className="text-gray-300 hover:text-red-400 transition-colors">
                  <Trash2 size={14} />
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-3">
        <button
          onClick={uploadAll}
          disabled={files.filter((f) => f.status === 'pending').length === 0}
          className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-green-600 hover:bg-green-700 text-white font-medium text-sm disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        >
          <Upload size={16} /> Upload Files
        </button>

        <button
          onClick={handleProcess}
          disabled={processing}
          className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-emerald-700 hover:bg-emerald-800 text-white font-medium text-sm disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        >
          {processing
            ? <LoadingSpinner size="sm" label="Ingesting..." />
            : <><Cpu size={16} /> Process Documents</>
          }
        </button>
      </div>

      {/* Process result */}
      {processResult && (
        <div className={`rounded-xl p-4 text-sm ${processResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
          <p className={`font-medium ${processResult.success ? 'text-green-800' : 'text-red-800'}`}>
            {processResult.message}
          </p>
          {processResult.success && (
            <div className="mt-2 text-green-700 space-y-0.5">
              <p>Files processed: {processResult.processed_files?.join(', ')}</p>
              <p>Total chunks ingested: <strong>{processResult.total_chunks}</strong></p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
