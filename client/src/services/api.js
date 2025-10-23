export function getApiBaseUrl() {
  // Debug logging for API URL resolution
  console.log('🔍 API URL Resolution Debug:', {
    isDev: import.meta.env.DEV,
    isProd: import.meta.env.PROD,
    viteApiUrl: import.meta.env.VITE_API_URL,
    windowApiUrl: window.__PRODUCTION_API_URL__,
    mode: import.meta.env.MODE
  });

  // In development (Vite), use relative URLs to leverage proxy
  if (import.meta.env.DEV) {
    console.log('✅ Using development proxy (empty base URL)');
    return '' // Empty string for relative URLs in dev (proxy handles it)
  }
  
  // In production, prioritize environment variable
  const apiUrl = import.meta.env.VITE_API_URL || 
                 window.__PRODUCTION_API_URL__ || 
                 'https://uncurdling-joane-pantomimical.ngrok-free.dev';
  
  console.log('🚀 Using production API URL:', apiUrl);
  return apiUrl;
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
