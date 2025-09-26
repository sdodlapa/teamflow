/**
 * Offline Indicator Component - Day 16 Implementation
 * Shows user when the application is offline and provides recovery options
 */

import React, { useState, useEffect } from 'react';
import { WifiOff, Wifi, RefreshCw } from 'lucide-react';

interface OfflineIndicatorProps {
  onRetry?: () => void;
  showRetryButton?: boolean;
}

const OfflineIndicator: React.FC<OfflineIndicatorProps> = ({ 
  onRetry, 
  showRetryButton = true 
}) => {
  const [isOffline, setIsOffline] = useState(!navigator.onLine);
  const [isRetrying, setIsRetrying] = useState(false);
  const [justCameOnline, setJustCameOnline] = useState(false);

  useEffect(() => {
    const handleOnline = () => {
      setIsOffline(false);
      setJustCameOnline(true);
      // Hide the "just came online" message after 3 seconds
      setTimeout(() => setJustCameOnline(false), 3000);
    };

    const handleOffline = () => {
      setIsOffline(true);
      setJustCameOnline(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleRetry = async () => {
    if (!onRetry) return;
    
    setIsRetrying(true);
    try {
      await onRetry();
    } finally {
      setIsRetrying(false);
    }
  };

  // Don't render if online and not just came online
  if (!isOffline && !justCameOnline) {
    return null;
  }

  return (
    <>
      {/* Offline Banner */}
      {isOffline && (
        <div className="fixed top-0 left-0 right-0 z-50 bg-red-600 text-white px-4 py-3 text-center">
          <div className="flex items-center justify-center space-x-2">
            <WifiOff className="h-4 w-4" />
            <span className="text-sm font-medium">
              You're currently offline. Some features may not work.
            </span>
            {showRetryButton && onRetry && (
              <button
                onClick={handleRetry}
                disabled={isRetrying}
                className="ml-3 px-3 py-1 bg-red-700 hover:bg-red-800 rounded text-xs font-medium transition-colors disabled:opacity-50 flex items-center"
              >
                <RefreshCw className={`h-3 w-3 mr-1 ${isRetrying ? 'animate-spin' : ''}`} />
                {isRetrying ? 'Retrying...' : 'Retry'}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Back Online Banner */}
      {justCameOnline && (
        <div className="fixed top-0 left-0 right-0 z-50 bg-green-600 text-white px-4 py-3 text-center animate-fade-in">
          <div className="flex items-center justify-center space-x-2">
            <Wifi className="h-4 w-4" />
            <span className="text-sm font-medium">
              You're back online! The application will sync automatically.
            </span>
          </div>
        </div>
      )}

      {/* Spacer to prevent content from being hidden behind banners */}
      {(isOffline || justCameOnline) && (
        <div className="h-12" />
      )}
    </>
  );
};

export default OfflineIndicator;