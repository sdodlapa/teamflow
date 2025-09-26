import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  showDetails?: boolean;
  level?: 'page' | 'component' | 'critical';
  maxRetries?: number;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  retryCount: number;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
    retryCount: 0,
  };

  public static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    if (import.meta.env.DEV) {
      console.error('Error Boundary caught an error:', error, errorInfo);
    }

    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    this.setState({
      error,
      errorInfo,
    });
  }

  private handleRetry = () => {
    const maxRetries = this.props.maxRetries || 3;
    
    if (this.state.retryCount < maxRetries) {
      this.setState(prevState => ({
        hasError: false,
        error: null,
        errorInfo: null,
        retryCount: prevState.retryCount + 1,
      }));
    }
  };

  private handleReload = () => {
    window.location.reload();
  };

  private handleGoHome = () => {
    window.location.href = '/';
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return this.renderErrorUI();
    }
    return this.props.children;
  }

  private renderErrorUI() {
    const { level = 'page', maxRetries = 3 } = this.props;
    const { retryCount } = this.state;
    const canRetry = retryCount < maxRetries;

    if (level === 'critical') {
      return this.renderCriticalError();
    }

    if (level === 'component') {
      return this.renderComponentError();
    }

    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="max-w-lg w-full bg-white rounded-lg shadow-sm border p-8 text-center">
          <div className="mx-auto w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mb-6">
            <Bug className="h-8 w-8 text-orange-600" />
          </div>
          
          <h1 className="text-xl font-bold text-gray-900 mb-2">
            Oops! Something went wrong
          </h1>
          <p className="text-gray-600 mb-6">
            This page encountered an error. Don't worry, it's not your fault.
          </p>
          
          {retryCount > 0 && (
            <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                Retry attempt {retryCount} of {maxRetries}
              </p>
            </div>
          )}
          
          <div className="space-y-3 mb-6">
            {canRetry && (
              <button
                onClick={this.handleRetry}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </button>
            )}
            
            <button
              onClick={this.handleGoHome}
              className="w-full bg-gray-600 text-white py-3 px-4 rounded-lg hover:bg-gray-700 transition-colors flex items-center justify-center"
            >
              <Home className="h-4 w-4 mr-2" />
              Go to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  private renderCriticalError() {
    return (
      <div className="min-h-screen bg-red-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-6">
            <AlertTriangle className="h-8 w-8 text-red-600" />
          </div>
          
          <h1 className="text-xl font-bold text-gray-900 mb-2">
            Critical Application Error
          </h1>
          <p className="text-gray-600 mb-6">
            Something went wrong and the application needs to restart. Your data is safe.
          </p>
          
          <button
            onClick={this.handleReload}
            className="w-full bg-red-600 text-white py-3 px-4 rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Restart Application
          </button>
        </div>
      </div>
    );
  }

  private renderComponentError() {
    const { maxRetries = 3 } = this.props;
    const { retryCount } = this.state;
    const canRetry = retryCount < maxRetries;

    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <AlertTriangle className="h-5 w-5 text-red-600 mr-2" />
          <h3 className="text-sm font-medium text-red-800">
            Component Error
          </h3>
        </div>
        
        <p className="text-sm text-red-700 mb-4">
          This section couldn't load properly.
        </p>
        
        {retryCount > 0 && (
          <div className="mb-4 p-2 bg-red-100 border border-red-300 rounded text-xs text-red-800">
            Retry {retryCount}/{maxRetries}
          </div>
        )}
        
        <div className="flex space-x-3">
          {canRetry && (
            <button
              onClick={this.handleRetry}
              className="text-sm bg-red-600 text-white px-3 py-2 rounded hover:bg-red-700 transition-colors flex items-center"
            >
              <RefreshCw className="h-3 w-3 mr-1" />
              Retry
            </button>
          )}
        </div>
      </div>
    );
  }
}

export default ErrorBoundary;

// Higher-Order Component for easier usage
export const withErrorBoundary = <P extends object>(
  WrappedComponent: React.ComponentType<P>,
  errorBoundaryProps?: Omit<Props, 'children'>
) => {
  const WithErrorBoundaryComponent = (props: P) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <WrappedComponent {...props} />
    </ErrorBoundary>
  );

  WithErrorBoundaryComponent.displayName = 
    `withErrorBoundary(${WrappedComponent.displayName || WrappedComponent.name})`;

  return WithErrorBoundaryComponent;
};
