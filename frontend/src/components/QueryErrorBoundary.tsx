/**
 * React Query Error Recovery - Day 16 Implementation
 * Enhanced error handling for React Query with automatic retries and user-friendly fallbacks
 */

import { QueryErrorResetBoundary } from '@tanstack/react-query';
import React from 'react';
import ErrorBoundary from '../components/ErrorBoundary';
import { useErrorHandler } from '../utils/errorHandling';

interface QueryErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error: Error; retry: () => void }>;
  level?: 'page' | 'component' | 'critical';
  onError?: (error: Error, errorInfo: any) => void;
}

// Default fallback component for query errors
const DefaultQueryErrorFallback: React.FC<{ error: Error; retry: () => void }> = ({ 
  error, 
  retry 
}) => {
  const { handleError, clearError } = useErrorHandler();

  React.useEffect(() => {
    handleError(error, 'QueryError');
  }, [error, handleError]);

  const handleRetry = () => {
    clearError();
    retry();
  };

  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800 font-medium mb-2">Unable to load data</p>
        <p className="text-red-600 text-sm">{error.message}</p>
      </div>
      <button
        onClick={handleRetry}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        Try Again
      </button>
    </div>
  );
};

// Enhanced error boundary for React Query operations
const QueryErrorBoundary: React.FC<QueryErrorBoundaryProps> = ({
  children,
  fallback: FallbackComponent = DefaultQueryErrorFallback,
  level = 'component',
  onError
}) => {
  return (
    <QueryErrorResetBoundary>
      {({ reset }) => (
        <ErrorBoundary
          level={level}
          onError={onError}
          showDetails={import.meta.env.DEV}
          fallback={
            <FallbackComponent
              error={new Error('Query failed to load')}
              retry={reset}
            />
          }
        >
          {children}
        </ErrorBoundary>
      )}
    </QueryErrorResetBoundary>
  );
};

// Hook for handling individual query errors
export const useQueryErrorHandler = () => {
  const { handleError, clearError } = useErrorHandler();

  const handleQueryError = React.useCallback((error: Error, context?: string) => {
    // Log query-specific errors
    console.error('Query error:', error, context);
    
    // Convert to user-friendly error message
    let userMessage = error.message;
    
    if (error.message.includes('fetch')) {
      userMessage = 'Unable to load data. Please check your connection and try again.';
    } else if (error.message.includes('401')) {
      userMessage = 'Your session has expired. Please log in again.';
    } else if (error.message.includes('403')) {
      userMessage = 'You don\'t have permission to access this data.';
    } else if (error.message.includes('500')) {
      userMessage = 'Server error. Please try again in a moment.';
    }

    const queryError = new Error(userMessage);
    handleError(queryError, context);
  }, [handleError]);

  return {
    handleQueryError,
    clearError
  };
};

// Enhanced query options for better error handling
export const createQueryOptions = (key: string[], fetcher: () => Promise<any>) => {
  return {
    queryKey: key,
    queryFn: fetcher,
    retry: (failureCount: number, error: Error) => {
      // Don't retry on authentication errors
      if (error.message.includes('401') || error.message.includes('403')) {
        return false;
      }
      
      // Retry up to 3 times for other errors
      return failureCount < 3;
    },
    retryDelay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
    refetchOnWindowFocus: false,
    refetchOnReconnect: true, // Refetch when reconnecting to internet
  };
};

export default QueryErrorBoundary;