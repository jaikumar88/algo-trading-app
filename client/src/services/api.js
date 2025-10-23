import axios from 'axios'

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

// Create axios instance with default headers for ngrok
export const apiClient = axios.create({
  headers: {
    'ngrok-skip-browser-warning': 'true',
    'User-Agent': 'TradingClient/1.0'
  }
});

// Configure axios instance to use proper base URL
apiClient.interceptors.request.use((config) => {
  // If URL is relative, prepend the API base URL
  if (config.url && config.url.startsWith('/')) {
    config.url = apiUrl(config.url);
  }
  
  console.log('📡 API Request:', config.method?.toUpperCase(), config.url);
  return config;
}, (error) => {
  console.error('❌ API Request Error:', error);
  return Promise.reject(error);
});

// Add response interceptor for debugging
apiClient.interceptors.response.use((response) => {
  console.log('✅ API Response:', response.config.url, response.status);
  return response;
}, (error) => {
  console.error('❌ API Response Error:', error.config?.url, error.response?.status, error.message);
  return Promise.reject(error);
});

// Helper function to check if we're in development
export function isDevelopment() {
  return import.meta.env.DEV
}

// Helper function to check if we're in production
export function isProduction() {
  return import.meta.env.PROD
}

