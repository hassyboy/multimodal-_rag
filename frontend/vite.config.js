import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '127.0.0.1',   // Force IPv4 — avoids ::1 vs 127.0.0.1 mismatch on Windows
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',  // Explicit IPv4 — never resolves to ::1
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/audio': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
