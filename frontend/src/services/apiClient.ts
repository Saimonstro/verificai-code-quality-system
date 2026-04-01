import axios from 'axios';
import type { ApiError } from '@/types/api';

const apiClient = axios.create({
  // @ts-ignore - Ignore TS error for env variable, Vite will replace this statically
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 300000, // 5 minutos para permitir análise completa da LLM
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available from Zustand store
    try {
      const authData = localStorage.getItem('auth-storage');
      if (authData) {
        const parsed = JSON.parse(authData);
        const token = parsed.state?.token;
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      }
    } catch (error) {
      // Ignore parsing errors
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - clear auth store
      localStorage.removeItem('auth-storage');
      window.location.href = '/login';
    }

    // Transform error to consistent format
    const apiError: ApiError = {
      message: error.response?.data?.message || error.message || 'Unknown error',
      code: error.response?.data?.code || error.code || 'UNKNOWN_ERROR',
      details: error.response?.data?.details || error.response?.data,
    };

    return Promise.reject(apiError);
  }
);

export default apiClient;