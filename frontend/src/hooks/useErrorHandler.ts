/**
 * useErrorHandler Hook
 * Centralized error handling and loading state management
 */

import { useState, useCallback } from 'react';
import { ErrorType } from '../components/ErrorComponents';

interface ErrorState {
  type: ErrorType;
  message: string;
  details?: string;
}

interface UseErrorHandlerReturn {
  loading: boolean;
  error: ErrorState | null;
  setLoading: (loading: boolean) => void;
  setError: (error: ErrorState | null) => void;
  clearError: () => void;
  handleError: (error: unknown) => void;
  executeWithLoading: <T>(asyncFn: () => Promise<T>) => Promise<T | null>;
}

// Helper function to determine error type from HTTP status or error object
const getErrorType = (error: any): ErrorType => {
  if (!error) return 'generic';
  
  // Network errors
  if (error.name === 'NetworkError' || error.code === 'NETWORK_ERROR') {
    return 'network';
  }
  
  // HTTP status codes
  if (error.response?.status) {
    const status = error.response.status;
    switch (status) {
      case 401:
        return 'authentication';
      case 403:
        return 'authorization';
      case 404:
        return 'not-found';
      case 422:
        return 'validation';
      case 500:
      case 502:
      case 503:
      case 504:
        return 'server';
      default:
        return 'generic';
    }
  }
  
  return 'generic';
};

// Helper function to extract error message
const getErrorMessage = (error: any): string => {
  // API error with message
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  
  // Network errors
  if (error.name === 'NetworkError') {
    return 'Unable to connect to the server. Please check your internet connection.';
  }
  
  // Generic error message
  if (error.message) {
    return error.message;
  }
  
  return 'An unexpected error occurred. Please try again.';
};

// Helper function to extract error details for debugging
const getErrorDetails = (error: any): string | undefined => {
  try {
    return JSON.stringify({
      name: error.name,
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      stack: error.stack,
    }, null, 2);
  } catch {
    return error.toString();
  }
};

export const useErrorHandler = (): UseErrorHandlerReturn => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ErrorState | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const handleError = useCallback((error: unknown) => {
    console.error('Error handled:', error);
    
    const errorState: ErrorState = {
      type: getErrorType(error),
      message: getErrorMessage(error),
      details: import.meta.env.DEV ? getErrorDetails(error) : undefined,
    };
    
    setError(errorState);
    setLoading(false);
  }, []);

  const executeWithLoading = useCallback(async <T>(
    asyncFn: () => Promise<T>
  ): Promise<T | null> => {
    try {
      setLoading(true);
      clearError();
      const result = await asyncFn();
      setLoading(false);
      return result;
    } catch (err) {
      handleError(err);
      return null;
    }
  }, [clearError, handleError]);

  return {
    loading,
    error,
    setLoading,
    setError,
    clearError,
    handleError,
    executeWithLoading,
  };
};