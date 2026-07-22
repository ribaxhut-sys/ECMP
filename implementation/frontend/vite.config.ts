import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// CORS mitigation (IMPLEMENTATION_PLAN §13): proxy /v1 to the backend so the
// browser talks same-origin to Vite; no backend CORSMiddleware required.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
