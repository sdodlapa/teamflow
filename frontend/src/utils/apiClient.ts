/**
 * Enhanced API Client with Error Handling - Day 16 Enhanced
 * Centralized HTTP client with automatic error handling, retries, loading states, and resilience
 */

interface ApiError extends Error {
  status?: number;
  statusText?: string;
  data?: any;
  code?: string;
  type?: 'network' | 'auth' | 'validation' | 'server' | 'timeout';
  retryable?: boolean;
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
    const error = new Error() as ApiError;
    
    // Determine error type and message based on status
    switch (response.status) {
      case 401:
        error.message = 'Authentication required. Please log in again.';
        error.type = 'auth';
        error.code = 'UNAUTHORIZED';
        error.retryable = false;
        break;
      case 403:
        error.message = 'You don\'t have permission to perform this action.';
        error.type = 'auth';
        error.code = 'FORBIDDEN';
        error.retryable = false;
        break;
      case 404:
        error.message = 'The requested resource was not found.';
        error.type = 'validation';
        error.code = 'NOT_FOUND';
        error.retryable = false;
        break;
      case 409:
        error.message = 'This action conflicts with existing data.';
        error.type = 'validation';
        error.code = 'CONFLICT';
        error.retryable = false;
        break;
      case 422:
        error.message = 'The request data is invalid.';
        error.type = 'validation';
        error.code = 'VALIDATION_ERROR';
        error.retryable = false;
        break;
      case 429:
        error.message = 'Too many requests. Please wait a moment before trying again.';
        error.type = 'server';
        error.code = 'RATE_LIMITED';
        error.retryable = true;
        break;
      case 500:
        error.message = 'Server error. Please try again later.';
        error.type = 'server';
        error.code = 'INTERNAL_ERROR';
        error.retryable = true;
        break;
      case 502:
        error.message = 'Bad gateway. The server is temporarily unavailable.';
        error.type = 'server';
        error.code = 'BAD_GATEWAY';
        error.retryable = true;
        break;
      case 503:
        error.message = 'Service temporarily unavailable. Please try again later.';
        error.type = 'server';
        error.code = 'SERVICE_UNAVAILABLE';
        error.retryable = true;
        break;
      case 504:
        error.message = 'Gateway timeout. The request took too long to process.';
        error.type = 'server';
        error.code = 'GATEWAY_TIMEOUT';
        error.retryable = true;
        break;
      default:
        error.message = `API Error: ${response.status} ${response.statusText}`;
        error.type = response.status >= 500 ? 'server' : 'validation';
        error.code = 'HTTP_ERROR';
        error.retryable = response.status >= 500;
    }

    // Try to extract more specific error from response data
    if (data) {
      if (typeof data === 'object') {
        if (data.detail && typeof data.detail === 'string') {
          error.message = data.detail;
        } else if (data.message && typeof data.message === 'string') {
          error.message = data.message;
        } else if (data.error && typeof data.error === 'string') {
          error.message = data.error;
        }
      }
    }

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
        const error = new Error('Request timeout - the server is taking too long to respond') as ApiError;
        error.name = 'NetworkError';
        error.type = 'timeout';
        error.code = 'TIMEOUT';
        error.retryable = true;
        reject(error);
      }, timeout);

      promise
        .then(resolve)
        .catch((err) => {
          // Enhance network errors
          if (err instanceof TypeError && err.message.includes('Failed to fetch')) {
            const networkError = new Error('Unable to connect to the server. Please check your internet connection.') as ApiError;
            networkError.name = 'NetworkError';
            networkError.type = 'network';
            networkError.code = 'CONNECTION_ERROR';
            networkError.retryable = true;
            reject(networkError);
          } else {
            reject(err);
          }
        })
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
    // Don't retry if explicitly marked as non-retryable
    if (error.retryable === false) {
      return false;
    }

    // Retry based on error type
    switch (error.type) {
      case 'network':
      case 'timeout':
      case 'server':
        return true;
      case 'auth':
      case 'validation':
        return false;
      default:
        // Fallback to status-based logic
        if (error.name === 'NetworkError' || !error.status) {
          return true;
        }
        
        // Retry on server errors (5xx) and rate limiting (429)
        if (error.status && (error.status >= 500 || error.status === 429)) {
          return true;
        }
        
        return false;
    }
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