import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: process.env.NODE_ENV === 'production' ? '/algo-trading-app/' : '/',
  server: {
    port: 5173,
    host: true, // Allow external connections
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      '.loca.lt', // Allow all localtunnel subdomains
      '.ngrok.io', // Allow ngrok domains
      '.ngrok-free.dev', // Allow ngrok free domains
      '.serveo.net' // Allow serveo domains
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      },
      '/webhook': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist'
  },
  define: {
    __PRODUCTION_API_URL__: JSON.stringify('https://uncurdling-joane-pantomimical.ngrok-free.dev')
  }
})