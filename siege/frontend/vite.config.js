import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// En Docker : le proxy pointe vers nginx-siege (réseau interne).
// En dev local : pointe vers localhost:8000 (API siège en direct).
const API_TARGET = process.env.VITE_PROXY_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: API_TARGET,
        rewrite: path => path.replace(/^\/api/, ''),
        changeOrigin: true,
      },
    },
  },
})
