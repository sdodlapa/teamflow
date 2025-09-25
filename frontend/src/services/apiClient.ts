// API client configuration and base setup
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

// Types for API configuration
interface ApiConfig {
  baseURL: string;
  timeout: number;
}

interface ApiError {
  message: string;
  status?: number;
  code?: string;
  details?: any;
}

class ApiClient {
  private client: AxiosInstance;
  
  constructor(config: ApiConfig) {
    this.client = axios.create(config);
    
    // Request interceptor for authentication
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await axios.post('/api/v1/auth/refresh', {
                refresh_token: refreshToken
              });
              
              const { access_token } = response.data;
              localStorage.setItem('access_token', access_token);
              
              // Retry original request with new token
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/auth/login';
            return Promise.reject(refreshError);
          }
        }
        
        // Transform error for consistent handling
        const apiError: ApiError = {
          message: error.response?.data?.detail || error.message || 'An error occurred',
          status: error.response?.status,
          code: error.response?.data?.code,
          details: error.response?.data
        };
        
        return Promise.reject(apiError);
      }
    );
  }
  
  // HTTP method wrappers
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get(url, config);
    return response.data;
  }
  
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post(url, data, config);
    return response.data;
  }
  
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put(url, data, config);
    return response.data;
  }
  
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete(url, config);
    return response.data;
  }
  
  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.patch(url, data, config);
    return response.data;
  }
  
  // File upload helper
  async uploadFile<T = any>(url: string, file: File, progressCallback?: (progress: number) => void): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);
    
    const config: AxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressCallback && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          progressCallback(progress);
        }
      }
    };
    
    return this.post(url, formData, config);
  }
}

// Create default API client instance
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = new ApiClient({
  baseURL: API_BASE_URL,
  timeout: 30000 // 30 seconds
});

export type { ApiError };
export default apiClient;