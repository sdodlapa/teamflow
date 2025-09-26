import { Toaster } from 'react-hot-toast';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import ErrorBoundary from './components/ErrorBoundary';
import OfflineIndicator from './components/OfflineIndicator';
import { ToastProvider } from './contexts/ToastContext';
import { queryClient } from './lib/queryClient';
import AppRouter from './router/AppRouter';
import { reportError } from './utils/errorHandling';
import './index.css';

function App() {
  // Global error handler for the main application
  const handleGlobalError = (error: Error, errorInfo: any) => {
    console.error('Global application error:', error, errorInfo);
    reportError(error, { context: 'App_ErrorBoundary', errorInfo });
  };

  // Handle offline retry logic
  const handleOfflineRetry = () => {
    // Refetch all queries when coming back online
    queryClient.refetchQueries();
    
    // You could also trigger any specific retry logic here
    window.location.reload();
  };

  return (
    <div className="app">
      <ErrorBoundary 
        level="critical"
        showDetails={import.meta.env.DEV}
        onError={handleGlobalError}
        maxRetries={1}
      >
        <OfflineIndicator onRetry={handleOfflineRetry} />
        <QueryClientProvider client={queryClient}>
          <ToastProvider>
            <AppRouter />
          </ToastProvider>
          <ReactQueryDevtools initialIsOpen={false} />
        </QueryClientProvider>
      </ErrorBoundary>
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </div>
  );
}

export default App;