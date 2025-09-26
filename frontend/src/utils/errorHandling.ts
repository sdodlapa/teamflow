/**
 * Error Handling Utilities - Day 16 Implementation
 * Provides hooks and utilities for consistent error handling across the application
 */

import { useState, useCallback, useEffect } from 'react';

// Types for different error states
export interface AppError {
  message: string;
  type: 'validation' | 'network' | 'auth' | 'unknown';
  code?: string;
  details?: any;
}

export interface NetworkError extends AppError {
  type: 'network';
  status?: number;
  retry?: () => void;
}

export interface ValidationError extends AppError {
  type: 'validation';
  field?: string;
}

// Hook for error state management
export const useErrorHandler = () => {
  const [error, setError] = useState<AppError | null>(null);
  const [isRetrying, setIsRetrying] = useState(false);

  const handleError = useCallback((error: Error | AppError, context?: string) => {
    let appError: AppError;

    if ('type' in error) {
      // Already an AppError
      appError = error;
    } else {
      // Convert generic Error to AppError
      appError = {
        message: error.message,
        type: 'unknown',
        details: { context, stack: error.stack }
      };

      // Try to detect network errors
      if (error.message.includes('fetch') || error.message.includes('network')) {
        appError.type = 'network';
      }
    }

    setError(appError);

    // Log to console in development
    if (import.meta.env.DEV) {
      console.error('Error handled:', appError, context);
    }

    // In production, send to error reporting service
    if (import.meta.env.PROD) {
      // Example: Sentry.captureException(error, { extra: { context, appError } });
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
    setIsRetrying(false);
  }, []);

  const retryOperation = useCallback((operation: () => Promise<void> | void) => {
    setIsRetrying(true);
    
    try {
      const result = operation();
      
      // Handle async operations
      if (result instanceof Promise) {
        result
          .then(() => {
            clearError();
          })
          .catch((retryError) => {
            setIsRetrying(false);
            handleError(retryError, 'retry_operation');
          });
      } else {
        clearError();
      }
    } catch (retryError) {
      setIsRetrying(false);
      handleError(retryError as Error, 'retry_operation_sync');
    }
  }, [handleError, clearError]);

  return {
    error,
    isRetrying,
    handleError,
    clearError,
    retryOperation,
  };
};

// Hook for API error handling with automatic retry
export const useApiError = (maxRetries: number = 3) => {
  const [retryCount, setRetryCount] = useState(0);
  const { error, isRetrying, handleError, clearError, retryOperation } = useErrorHandler();

  const handleApiError = useCallback((error: Error, operation?: () => Promise<void>) => {
    const networkError: NetworkError = {
      message: error.message,
      type: 'network',
      code: 'API_ERROR',
      retry: operation ? () => {
        if (retryCount < maxRetries) {
          setRetryCount(prev => prev + 1);
          retryOperation(operation);
        }
      } : undefined
    };

    // Check for specific status codes
    if (error.message.includes('401')) {
      networkError.status = 401;
      networkError.message = 'Authentication required. Please log in again.';
      networkError.code = 'UNAUTHORIZED';
    } else if (error.message.includes('403')) {
      networkError.status = 403;
      networkError.message = 'You don\'t have permission to perform this action.';
      networkError.code = 'FORBIDDEN';
    } else if (error.message.includes('404')) {
      networkError.status = 404;
      networkError.message = 'The requested resource was not found.';
      networkError.code = 'NOT_FOUND';
    } else if (error.message.includes('500')) {
      networkError.status = 500;
      networkError.message = 'Server error. Please try again later.';
      networkError.code = 'SERVER_ERROR';
    }

    handleError(networkError);
  }, [handleError, retryCount, maxRetries, retryOperation]);

  const resetRetries = useCallback(() => {
    setRetryCount(0);
  }, []);

  return {
    error: error as NetworkError | null,
    isRetrying,
    retryCount,
    canRetry: retryCount < maxRetries,
    handleApiError,
    clearError,
    resetRetries,
  };
};

// Hook for offline detection
export const useOfflineDetection = () => {
  const [isOffline, setIsOffline] = useState(!navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOffline;
};

// Utility function to create standardized error messages
export const createErrorMessage = (type: string, context?: string): string => {
  const messages: Record<string, string> = {
    network: 'Unable to connect to the server. Please check your internet connection.',
    auth: 'Authentication failed. Please log in again.',
    validation: 'Please check your input and try again.',
    not_found: 'The requested item was not found.',
    server: 'A server error occurred. Please try again later.',
    unknown: 'An unexpected error occurred. Please try again.',
  };

  const baseMessage = messages[type] || messages.unknown;
  return context ? `${baseMessage} (${context})` : baseMessage;
};

// Error reporting utility for production
export const reportError = (error: Error | AppError, context?: any) => {
  if (import.meta.env.PROD) {
    // In production, send to error reporting service
    console.error('Error reported:', {
      error: 'type' in error ? error : {
        message: error.message,
        stack: error.stack,
        type: 'unknown'
      },
      context,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent
    });
    
    // Example integration with error reporting service:
    // Sentry.captureException(error, { extra: context });
    // LogRocket.captureException(error);
  }
};