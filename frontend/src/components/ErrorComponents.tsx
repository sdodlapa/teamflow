/**
 * Error Display Components
 * User-friendly error messages and handling
 */

import React from 'react';
import { 
  AlertCircle, 
  Wifi, 
  Server, 
  Shield, 
  RefreshCw, 
  Home,
  X 
} from 'lucide-react';

// Error types for better categorization
export type ErrorType = 
  | 'network' 
  | 'server' 
  | 'authentication' 
  | 'authorization' 
  | 'validation' 
  | 'not-found' 
  | 'generic';

interface ErrorDisplayProps {
  type?: ErrorType;
  title?: string;
  message?: string;
  details?: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  showRetry?: boolean;
  showHome?: boolean;
  className?: string;
}

const errorConfig = {
  network: {
    icon: Wifi,
    title: 'Connection Problem',
    message: 'Please check your internet connection and try again.',
    color: 'text-orange-500',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
  },
  server: {
    icon: Server,
    title: 'Server Error',
    message: 'Something went wrong on our end. Please try again later.',
    color: 'text-red-500',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
  },
  authentication: {
    icon: Shield,
    title: 'Authentication Required',
    message: 'Please log in to access this resource.',
    color: 'text-blue-500',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
  },
  authorization: {
    icon: Shield,
    title: 'Access Denied',
    message: "You don't have permission to access this resource.",
    color: 'text-red-500',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
  },
  validation: {
    icon: AlertCircle,
    title: 'Invalid Input',
    message: 'Please check your input and try again.',
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
  },
  'not-found': {
    icon: AlertCircle,
    title: 'Not Found',
    message: 'The requested resource could not be found.',
    color: 'text-gray-500',
    bgColor: 'bg-gray-50',
    borderColor: 'border-gray-200',
  },
  generic: {
    icon: AlertCircle,
    title: 'Error',
    message: 'Something went wrong. Please try again.',
    color: 'text-red-500',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
  },
};

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  type = 'generic',
  title,
  message,
  details,
  onRetry,
  onDismiss,
  showRetry = true,
  showHome = false,
  className = '',
}) => {
  const config = errorConfig[type];
  const Icon = config.icon;

  return (
    <div className={`rounded-lg border p-6 ${config.bgColor} ${config.borderColor} ${className}`}>
      <div className="flex items-start">
        <Icon className={`h-6 w-6 ${config.color} mt-0.5 mr-3 flex-shrink-0`} />
        <div className="flex-1">
          <h3 className={`text-lg font-medium ${config.color} mb-2`}>
            {title || config.title}
          </h3>
          <p className="text-gray-700 mb-4">
            {message || config.message}
          </p>
          
          {details && (
            <details className="mb-4">
              <summary className="cursor-pointer text-sm font-medium text-gray-600 hover:text-gray-800">
                Show Details
              </summary>
              <div className="mt-2 p-3 bg-white rounded border border-gray-200">
                <pre className="text-xs text-gray-600 whitespace-pre-wrap overflow-x-auto">
                  {details}
                </pre>
              </div>
            </details>
          )}

          <div className="flex flex-wrap gap-3">
            {onRetry && showRetry && (
              <button
                onClick={onRetry}
                className="flex items-center px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                <RefreshCw className="mr-2 h-4 w-4" />
                Try Again
              </button>
            )}
            
            {showHome && (
              <button
                onClick={() => window.location.href = '/dashboard'}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                <Home className="mr-2 h-4 w-4" />
                Go Home
              </button>
            )}
          </div>
        </div>

        {onDismiss && (
          <button
            onClick={onDismiss}
            className="flex-shrink-0 ml-4 text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>
    </div>
  );
};

// Inline error message for forms
interface InlineErrorProps {
  message: string;
  className?: string;
}

export const InlineError: React.FC<InlineErrorProps> = ({ 
  message, 
  className = '' 
}) => {
  return (
    <div className={`flex items-center mt-1 text-sm text-red-600 ${className}`}>
      <AlertCircle className="h-4 w-4 mr-1 flex-shrink-0" />
      <span>{message}</span>
    </div>
  );
};

// Toast notification error
interface ErrorToastProps {
  message: string;
  onClose: () => void;
  duration?: number;
}

export const ErrorToast: React.FC<ErrorToastProps> = ({ 
  message, 
  onClose, 
  duration = 5000 
}) => {
  React.useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [onClose, duration]);

  return (
    <div className="fixed top-4 right-4 max-w-sm w-full bg-red-50 border border-red-200 rounded-lg shadow-lg z-50">
      <div className="p-4">
        <div className="flex">
          <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 mr-3 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm text-red-800">{message}</p>
          </div>
          <button
            onClick={onClose}
            className="ml-4 text-red-400 hover:text-red-600"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};