import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,  // 2 minutes for LLM responses
})

// ─── Text Q&A ────────────────────────────────────────────────────
export const askQuestion = (question) =>
  api.post('/ask', { question })

export const personalizedAsk = (question, sessionId = null) =>
  api.post('/personalized-ask', { question, session_id: sessionId })

// ─── Voice ───────────────────────────────────────────────────────
export const voiceAsk = (audioBlob) => {
  const form = new FormData()
  // IMPORTANT: field name must match FastAPI parameter name: audio
  form.append('audio', audioBlob, 'recording.webm')
  // Do NOT set Content-Type manually — axios sets it with correct multipart boundary
  return api.post('/voice-ask', form)
}

// ─── Upload & Ingestion ──────────────────────────────────────────
export const uploadPdf = (file) => {
  const form = new FormData()
  // IMPORTANT: field name must match FastAPI parameter name: file
  form.append('file', file, file.name)
  // Do NOT set Content-Type manually — axios sets it with correct multipart boundary
  return api.post('/upload-pdf', form)
}

export const processDocuments = () =>
  api.post('/process-documents')

export const listDocuments = () =>
  api.get('/documents')

// ─── Health ──────────────────────────────────────────────────────
export const healthCheck = () =>
  api.get('/health')
