/**
 * Error Handling Demo Page
 * Demonstrates all error handling and loading state components
 */

import React, { useState } from 'react';
import Layout from '../components/Layout';
import { ErrorDisplay, ErrorType, InlineError } from '../components/ErrorComponents';
import { LoadingSpinner, LoadingSkeleton, LoadingButton } from '../components/LoadingComponents';
import { useErrorHandler } from '../hooks/useErrorHandler';
import { useToast } from '../contexts/ToastContext';
import { Bug, Zap } from 'lucide-react';

const ErrorHandlingDemo: React.FC = () => {
  const [demoStates, setDemoStates] = useState({
    showNetworkError: false,
    showServerError: false,
    showValidationError: false,
    showLoading: false,
    formErrors: {} as Record<string, string>,
  });
  const { loading, error, executeWithLoading, clearError } = useErrorHandler();
  const toast = useToast();

  // Demo functions to trigger different error types
  const triggerNetworkError = () => {
    setDemoStates(prev => ({ ...prev, showNetworkError: true }));
  };

  const triggerServerError = () => {
    setDemoStates(prev => ({ ...prev, showServerError: true }));
  };

  const triggerValidationError = () => {
    setDemoStates(prev => ({ 
      ...prev, 
      formErrors: { 
        email: 'Please enter a valid email address',
        password: 'Password must be at least 8 characters'
      } 
    }));
  };

  const triggerAsyncError = async () => {
    await executeWithLoading(async () => {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Randomly throw different types of errors
      const errorTypes = ['network', 'server', 'auth'];
      const randomType = errorTypes[Math.floor(Math.random() * errorTypes.length)];
      
      switch (randomType) {
        case 'network':
          const networkError = new Error('Network connection failed') as any;
          networkError.name = 'NetworkError';
          throw networkError;
        case 'server':
          const serverError = new Error('Internal server error') as any;
          serverError.response = { status: 500, data: { message: 'Database connection failed' } };
          throw serverError;
        case 'auth':
          const authError = new Error('Authentication required') as any;
          authError.response = { status: 401, data: { message: 'Please log in to continue' } };
          throw authError;
        default:
          throw new Error('Something went wrong');
      }
    });
  };

  const triggerToastNotifications = () => {
    toast.success('Operation completed successfully!');
    setTimeout(() => {
      toast.warning('This is a warning message');
    }, 1000);
    setTimeout(() => {
      toast.error('An error occurred while processing your request');
    }, 2000);
    setTimeout(() => {
      toast.info('Here\'s some helpful information');
    }, 3000);
  };

  const clearFormErrors = () => {
    setDemoStates(prev => ({ ...prev, formErrors: {} }));
  };

  const clearDemoStates = () => {
    setDemoStates({
      showNetworkError: false,
      showServerError: false,
      showValidationError: false,
      showLoading: false,
      formErrors: {},
    });
  };

  const errorExamples: Array<{ type: ErrorType; title: string; message: string; icon: string }> = [
    {
      type: 'network',
      title: 'Connection Error',
      message: 'Unable to connect to the server. Please check your internet connection.',
      icon: '📡',
    },
    {
      type: 'server',
      title: 'Server Error',
      message: 'Our servers are experiencing issues. Please try again later.',
      icon: '🖥️',
    },
    {
      type: 'authentication',
      title: 'Authentication Required',
      message: 'Please log in to access this resource.',
      icon: '🔒',
    },
    {
      type: 'validation',
      title: 'Invalid Input',
      message: 'Please check your input and try again.',
      icon: '⚠️',
    },
  ];

  return (
    <Layout>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <Bug className="text-red-500" size={32} />
            <h1 className="text-3xl font-bold text-gray-900">Error Handling Demo</h1>
          </div>
          <p className="text-gray-600">
            Comprehensive demonstration of error handling, loading states, and user feedback components.
          </p>
        </div>

        {/* Interactive Demos */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Error Trigger Demo */}
          <div className="bg-white border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Zap className="text-yellow-500" size={24} />
              Interactive Error Triggers
            </h2>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={triggerNetworkError}
                  className="px-4 py-2 bg-orange-100 text-orange-700 hover:bg-orange-200 rounded-md border border-orange-300 transition-colors"
                >
                  Network Error
                </button>
                <button
                  onClick={triggerServerError}
                  className="px-4 py-2 bg-red-100 text-red-700 hover:bg-red-200 rounded-md border border-red-300 transition-colors"
                >
                  Server Error
                </button>
                <button
                  onClick={triggerValidationError}
                  className="px-4 py-2 bg-yellow-100 text-yellow-700 hover:bg-yellow-200 rounded-md border border-yellow-300 transition-colors"
                >
                  Validation Error
                </button>
                <button
                  onClick={triggerToastNotifications}
                  className="px-4 py-2 bg-blue-100 text-blue-700 hover:bg-blue-200 rounded-md border border-blue-300 transition-colors"
                >
                  Toast Messages
                </button>
              </div>

              <div className="pt-4 border-t">
                <LoadingButton
                  onClick={triggerAsyncError}
                  isLoading={loading}
                  loadingText="Simulating Error..."
                  className="w-full px-4 py-3 bg-purple-600 text-white hover:bg-purple-700 rounded-md"
                >
                  Async Error Simulation
                </LoadingButton>
              </div>

              <button
                onClick={clearDemoStates}
                className="w-full px-4 py-2 bg-gray-100 text-gray-700 hover:bg-gray-200 rounded-md border border-gray-300 transition-colors text-sm"
              >
                Clear All Demos
              </button>
            </div>
          </div>

          {/* Loading States Demo */}
          <div className="bg-white border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Loading States</h2>
            
            <div className="space-y-6">
              {/* Spinner Sizes */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Loading Spinners</h3>
                <div className="flex items-center gap-4">
                  <div className="text-center">
                    <LoadingSpinner size="sm" />
                    <div className="text-xs text-gray-500 mt-1">Small</div>
                  </div>
                  <div className="text-center">
                    <LoadingSpinner size="md" />
                    <div className="text-xs text-gray-500 mt-1">Medium</div>
                  </div>
                  <div className="text-center">
                    <LoadingSpinner size="lg" className="text-blue-600" />
                    <div className="text-xs text-gray-500 mt-1">Large</div>
                  </div>
                </div>
              </div>

              {/* Loading Skeleton */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Loading Skeleton</h3>
                <LoadingSkeleton rows={3} />
              </div>

              {/* Loading Button States */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Button States</h3>
                <div className="space-y-2">
                  <LoadingButton
                    isLoading={false}
                    className="w-full px-4 py-2 bg-green-600 text-white hover:bg-green-700 rounded-md"
                  >
                    Normal Button
                  </LoadingButton>
                  <LoadingButton
                    isLoading={true}
                    loadingText="Loading..."
                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-md"
                  >
                    Loading Button
                  </LoadingButton>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Live Error Displays */}
        <div className="space-y-6">
          {/* useErrorHandler Hook Demo */}
          {error && (
            <ErrorDisplay
              type={error.type}
              message={error.message}
              details={error.details}
              onRetry={() => {
                clearError();
                triggerAsyncError();
              }}
              onDismiss={clearError}
            />
          )}

          {/* Manual Error Displays */}
          {demoStates.showNetworkError && (
            <ErrorDisplay
              type="network"
              onDismiss={() => setDemoStates(prev => ({ ...prev, showNetworkError: false }))}
              showRetry={true}
            />
          )}

          {demoStates.showServerError && (
            <ErrorDisplay
              type="server"
              title="Service Unavailable"
              message="Our servers are currently undergoing maintenance. Please try again in a few minutes."
              onDismiss={() => setDemoStates(prev => ({ ...prev, showServerError: false }))}
              showHome={true}
            />
          )}

          {/* Form with Validation Errors */}
          {Object.keys(demoStates.formErrors).length > 0 && (
            <div className="bg-white border rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">Form Validation Demo</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    className="w-full px-3 py-2 border border-red-300 rounded-md focus:ring-red-500 focus:border-red-300"
                    placeholder="user@example.com"
                  />
                  {demoStates.formErrors.email && (
                    <InlineError message={demoStates.formErrors.email} />
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                  <input
                    type="password"
                    className="w-full px-3 py-2 border border-red-300 rounded-md focus:ring-red-500 focus:border-red-300"
                    placeholder="Enter password"
                  />
                  {demoStates.formErrors.password && (
                    <InlineError message={demoStates.formErrors.password} />
                  )}
                </div>
                <button
                  onClick={clearFormErrors}
                  className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-md"
                >
                  Fix Validation Errors
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Error Types Reference */}
        <div className="mt-12">
          <h2 className="text-2xl font-semibold mb-6">Error Types Reference</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {errorExamples.map((example, index) => (
              <div key={index} className="bg-white border rounded-lg p-6">
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-2xl">{example.icon}</span>
                  <h3 className="text-lg font-semibold">{example.title}</h3>
                </div>
                <ErrorDisplay
                  type={example.type}
                  title={example.title}
                  message={example.message}
                  showRetry={false}
                  className="border-0 p-0"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Implementation Guide */}
        <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-blue-900 mb-4">Implementation Guide</h2>
          <div className="text-blue-800 space-y-4">
            <div>
              <h3 className="font-medium mb-2">🔧 Error Handling Hook</h3>
              <p className="text-sm">Use <code className="bg-blue-100 px-2 py-1 rounded">useErrorHandler()</code> for centralized error management and loading states.</p>
            </div>
            <div>
              <h3 className="font-medium mb-2">🎯 Error Boundary</h3>
              <p className="text-sm">Wrap your app with <code className="bg-blue-100 px-2 py-1 rounded">ErrorBoundary</code> to catch JavaScript errors.</p>
            </div>
            <div>
              <h3 className="font-medium mb-2">📱 Toast Notifications</h3>
              <p className="text-sm">Use <code className="bg-blue-100 px-2 py-1 rounded">useToast()</code> for success/error messages and notifications.</p>
            </div>
            <div>
              <h3 className="font-medium mb-2">⚡ API Client</h3>
              <p className="text-sm">Enhanced API client with automatic retries, timeout handling, and error categorization.</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ErrorHandlingDemo;