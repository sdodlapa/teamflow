/**
 * Enhanced API Client with Error Handling
 * Centralized HTTP client with automatic error handling, retries, and loading states
 */

interface ApiError extends Error {
  status?: number;
  statusText?: string;
  data?: any;
  code?: string;
  response?: {
    status: number;
    statusText: string;
    data: any;
  };
}

interface RequestConfig extends RequestInit {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
}

interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Headers;
}

class ApiClient {
  private baseURL: string;
  private defaultTimeout: number = 10000; // 10 seconds
  private defaultRetries: number = 3;
  private defaultRetryDelay: number = 1000; // 1 second

  constructor(baseURL: string = '/api/v1') {
    this.baseURL = baseURL;
  }

  // Helper to create an API error
  private createApiError(response: Response, data?: any): ApiError {
    const error = new Error(`API Error: ${response.status} ${response.statusText}`) as ApiError;
    error.status = response.status;
    error.statusText = response.statusText;
    error.data = data;
    error.response = {
      status: response.status,
      statusText: response.statusText,
      data,
    };
    return error;
  }

  // Helper to handle network timeout
  private withTimeout<T>(promise: Promise<T>, timeout: number): Promise<T> {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        const error = new Error('Request timeout') as ApiError;
        error.name = 'NetworkError';
        error.code = 'NETWORK_ERROR';
        reject(error);
      }, timeout);

      promise
        .then(resolve)
        .catch(reject)
        .finally(() => clearTimeout(timeoutId));
    });
  }

  // Helper for retry logic
  private async withRetry<T>(
    fn: () => Promise<T>,
    retries: number,
    delay: number
  ): Promise<T> {
    try {
      return await fn();
    } catch (error) {
      if (retries <= 0 || !this.shouldRetry(error as ApiError)) {
        throw error;
      }

      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay));
      
      // Exponential backoff
      return this.withRetry(fn, retries - 1, delay * 2);
    }
  }

  // Determine if we should retry the request
  private shouldRetry(error: ApiError): boolean {
    // Retry on network errors
    if (error.name === 'NetworkError' || !error.status) {
      return true;
    }

    // Retry on server errors (5xx)
    if (error.status && error.status >= 500) {
      return true;
    }

    // Don't retry on client errors (4xx)
    return false;
  }

  // Get authorization header
  private getAuthHeader(): Record<string, string> {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  // Core request method
  private async request<T = any>(
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<ApiResponse<T>> {
    const {
      timeout = this.defaultTimeout,
      retries = this.defaultRetries,
      retryDelay = this.defaultRetryDelay,
      headers = {},
      ...fetchConfig
    } = config;

    const url = `${this.baseURL}${endpoint}`;
    
    const requestHeaders = {
      'Content-Type': 'application/json',
      ...this.getAuthHeader(),
      ...headers,
    };

    const fetchFn = async (): Promise<ApiResponse<T>> => {
      const response = await fetch(url, {
        ...fetchConfig,
        headers: requestHeaders,
      });

      let data: T;
      const contentType = response.headers.get('content-type');
      
      if (contentType?.includes('application/json')) {
        data = await response.json();
      } else {
        data = (await response.text()) as unknown as T;
      }

      if (!response.ok) {
        throw this.createApiError(response, data);
      }

      return {
        data,
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
      };
    };

    // Apply timeout and retry logic
    return this.withRetry(
      () => this.withTimeout(fetchFn(), timeout),
      retries,
      retryDelay
    );
  }

  // HTTP method helpers
  async get<T = any>(endpoint: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'GET' });
  }

  async post<T = any>(endpoint: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T = any>(endpoint: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T = any>(endpoint: string, data?: any, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T = any>(endpoint: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...config, method: 'DELETE' });
  }

  // File upload helper
  async upload<T = any>(endpoint: string, formData: FormData, config?: RequestConfig): Promise<ApiResponse<T>> {
    const { headers = {}, ...restConfig } = config || {};
    
    // Don't set Content-Type for FormData - let browser set it with boundary
    const uploadHeaders = {
      ...this.getAuthHeader(),
      ...(headers as Record<string, string>),
    };
    delete (uploadHeaders as any)['Content-Type'];

    return this.request<T>(endpoint, {
      ...restConfig,
      method: 'POST',
      body: formData,
      headers: uploadHeaders,
    });
  }
}

// Create and export default API client instance
export const apiClient = new ApiClient();

// Export types for use in other files
export type { ApiError, ApiResponse, RequestConfig };