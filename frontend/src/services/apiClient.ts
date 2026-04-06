import axios from 'axios';
import type { ApiError } from '@/types/api';
import { getAuthToken, clearAuth } from '@/utils/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const apiClient = axios.create({
  // @ts-ignore - Ignore TS error for env variable, Vite will replace this statically
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutos para permitir análise completa da LLM
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper to check if backend is local
export const isLocalBackend = 
  API_BASE_URL.includes('localhost') || 
  API_BASE_URL.includes('127.0.0.1') || 
  (typeof window !== 'undefined' && window.location.hostname === 'localhost');

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available using the central utility
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
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
      clearAuth();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }

    // Try to get the best possible message
    const message = error.response?.data?.message || 
                    error.response?.data?.detail || 
                    error.message || 
                    'Erro desconhecido na API';

    // Transform error to consistent format that also works with alert() calls
    // We create a custom error object that has a message property
    const apiError = new Error(message) as any;
    apiError.code = error.response?.data?.code || error.code || 'UNKNOWN_ERROR';
    apiError.details = error.response?.data?.details || error.response?.data;
    apiError.status = error.response?.status;
    apiError.isApiError = true;

    return Promise.reject(apiError);
  }
);

export default apiClient;