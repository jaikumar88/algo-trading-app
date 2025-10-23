export function getApiBaseUrl() {
  // In development (Vite), use relative URLs to leverage proxy
  if (import.meta.env.DEV) {
    return '' // Empty string for relative URLs in dev (proxy handles it)
  }
  
  // In production, use environment variable or fallback to ngrok URL
  return import.meta.env.VITE_API_URL || 
         window.__PRODUCTION_API_URL__ || 
         'https://uncurdling-joane-pantomimical.ngrok-free.dev'
}

export function apiUrl(path) {
  const base = getApiBaseUrl()
  return `${base}${path}`
}

// Helper function to check if we're in development
export function isDevelopment() {
  return import.meta.env.DEV
}

// Helper function to check if we're in production
export function isProduction() {
  return import.meta.env.PROD
}
