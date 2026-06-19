import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// En Docker : le proxy pointe vers nginx-siege (réseau interne).
// En dev local : pointe vers localhost:8000 (API siège en direct).
const API_TARGET = process.env.VITE_PROXY_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  build: {
    chunkSizeWarningLimit: 900,
    rollupOptions: {
      output: {
        // Découpage des libs lourdes en chunks séparés (mis en cache navigateur,
        // chargés uniquement par les pages qui en ont besoin).
        manualChunks: {
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-charts': ['recharts'],
          'vendor-select': ['react-select'],
        },
      },
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    // Quand le front est servi via Nginx (port 80) mais que Vite tourne
    // derrière le proxy, il faut forcer le client HMR à se connecter sur le port public.
    hmr: {
      protocol: 'ws',
      clientPort: 80,
    },
    proxy: {
      '/api': {
        target: API_TARGET,
        rewrite: path => path.replace(/^\/api/, ''),
        changeOrigin: true,
      },
    },
  },
})
