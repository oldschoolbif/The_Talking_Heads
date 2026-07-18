import axios from 'axios';

// Use direct URL to backend - no proxy to avoid CORS issues
const getApiBaseUrl = () => {
  // Always use direct URL to backend API
  // This ensures CORS headers are properly handled
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  // Default to direct backend URL
  return 'http://localhost:8001/api';
};

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Add request interceptor to ensure fresh requests and cache-busting
api.interceptors.request.use(
  (config) => {
    // Add timestamp to prevent browser caching of failed CORS requests
    // Only add to GET requests and only if params don't already exist
    if (config.method === 'get' || config.method === 'GET') {
      config.params = config.params || {};
      // Only add _t if it's not already set
      if (!config.params._t) {
        config.params._t = Date.now();
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add error interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Suppress console errors for expected cases
    const isExpected404 = error.config?.url?.includes('/status/') && error.response?.status === 404;
    const isCORS = error.message?.includes('CORS') || error.message?.includes('Access-Control') || 
                   (error.response?.status === 0 && error.message?.includes('Network')) ||
                   (error.code === 'ERR_NETWORK' && !error.response);
    
    // Check if this is a real CORS error or just a network issue
    // Real CORS errors have specific characteristics we can detect
    const isRealCORS = error.message?.includes('CORS') || 
                       error.message?.includes('Access-Control') ||
                       (error.response?.status === 0 && error.message?.includes('Network') && error.config?.url?.includes('localhost:8001'));
    
    // Don't log CORS or network errors - they're often browser cache issues
    // The backend is configured correctly, so these should resolve on refresh
    if (isRealCORS || (error.code === 'ERR_NETWORK' && !error.response)) {
      // Log for debugging but don't spam console
      if (isRealCORS) {
        console.warn('[CORS] Possible CORS issue detected. Backend headers are configured correctly - this may be a browser cache issue.');
      }
      return Promise.reject(new Error('Network error. Please refresh the page.'));
    }
    
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error') || error.message.includes('ECONNREFUSED')) {
      if (!isExpected404 && !isCORS) {
        console.error('API connection error:', error);
      }
      return Promise.reject(new Error('Unable to connect to the server. Please make sure the backend is running and try refreshing.'));
    }
    
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      return Promise.reject(new Error('Request timed out. The server may be busy. Please try again.'));
    }
    
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const data = error.response.data;
      
      // Don't log expected 404s for status polling (job might have been cleared on restart)
      if (status === 404 && isExpected404) {
        // Silently handle - job might have been cleared on backend restart
        // Don't log to console to reduce noise
        return Promise.reject(new Error('Job not found. The backend may have restarted. Please start a new generation.'));
      } else if (status === 404) {
        // Only log non-status 404s, and suppress if it's a status endpoint
        if (!isExpected404 && !error.config?.url?.includes('/status/')) {
          console.warn('404 error:', error.config?.url);
        }
        return Promise.reject(new Error(data?.error || 'The requested resource was not found.'));
      } else if (status === 500) {
        // Return the actual error message from the server
        const errorMsg = data?.error || data?.message || 'Server error occurred. Please try again later.';
        console.error('Server error (500):', errorMsg);
        return Promise.reject(new Error(errorMsg));
      } else if (status === 400) {
        return Promise.reject(new Error(data?.error || data?.message || 'Invalid request. Please check your input.'));
      } else if (status === 403) {
        return Promise.reject(new Error('Access denied. Please check your permissions.'));
      } else {
        return Promise.reject(new Error(data?.error || data?.message || `Server error (${status}). Please try again.`));
      }
    }
    
    // Fallback for other errors - suppress CORS and network errors
    if (!isExpected404 && !isCORS && error.code !== 'ERR_NETWORK') {
      console.error('API error:', error);
    }
    return Promise.reject(new Error(error.message || 'An unexpected error occurred. Please try again.'));
  }
);

// Scripts API
export const getScripts = async () => {
  const response = await api.get('/scripts');
  return response.data;
};

export const getScript = async (filename) => {
  const response = await api.get(`/scripts/${filename}`);
  return response.data;
};

export const saveScript = async (filename, content) => {
  const response = await api.post(`/scripts/${filename}`, { content });
  return response.data;
};

// Personas API
export const getPersonas = async () => {
  try {
    const response = await api.get('/personas');
    console.log('Personas API response:', response.data?.length || 0, 'personas');
    if (response.data && response.data.length > 0) {
      console.log('First persona:', response.data[0]);
    }
    return response.data || [];
  } catch (error) {
    console.error('Error fetching personas:', error);
    throw error;
  }
};

// Configuration API
export const getConfig = async () => {
  const response = await api.get('/config');
  return response.data;
};

export const updateConfig = async (config) => {
  const response = await api.post('/config', config);
  return response.data;
};

// Video Generation API
export const generateVideo = async (params) => {
  const response = await api.post('/generate', params);
  return response.data;
};

export const getVideoStatus = async (jobId) => {
  // Remove query params from jobId if present (shouldn't be, but be safe)
  const cleanJobId = jobId.split('?')[0];
  const response = await api.get(`/status/${cleanJobId}`);
  return response.data;
};

// Voice Sample API (for persona previews)
export const generateVoiceSample = async (personaKey, text = 'Hello, this is a sample of my voice.') => {
  const response = await api.post('/voice-sample', { persona_key: personaKey, text });
  return response.data;
};

// Avatar Image API (get avatar preview image)
export const getAvatarImage = async (avatarId, provider = 'heygen') => {
  const response = await api.get(`/avatar-image/${provider}/${avatarId}`);
  return response.data;
};

export default api;

