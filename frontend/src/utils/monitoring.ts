// Production monitoring utilities for TeamFlow
// This file provides error tracking, performance monitoring, and observability

// Type definitions
interface User {
  id: string;
  email?: string;
  username?: string;
}

interface ErrorContext {
  [key: string]: any;
}

interface WebVitalMetric {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
}

// Performance monitoring utilities
export class PerformanceMonitor {
  private static measureStart = new Map<string, number>();
  private static isProduction = import.meta.env.VITE_ENVIRONMENT === 'production';

  static startMeasure(name: string): void {
    if (typeof performance !== 'undefined') {
      this.measureStart.set(name, performance.now());
    }
  }

  static endMeasure(name: string): number {
    if (typeof performance === 'undefined') return 0;
    
    const startTime = this.measureStart.get(name);
    if (!startTime) return 0;
    
    const duration = performance.now() - startTime;
    this.measureStart.delete(name);
    
    // Log slow operations
    if (duration > 1000) {
      console.warn(`Slow operation: ${name} took ${duration.toFixed(2)}ms`);
      
      // In production, you would send this to your monitoring service
      if (this.isProduction) {
        this.sendToMonitoring('performance_warning', {
          operation: name,
          duration: duration.toFixed(2),
          type: 'slow_operation'
        });
      }
    }
    
    return duration;
  }

  static trackPageLoad(pageName: string): void {
    if (typeof window === 'undefined' || !('performance' in window)) return;
    
    // Wait for page load to complete
    window.addEventListener('load', () => {
      setTimeout(() => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        if (navigation) {
          const loadTime = navigation.loadEventEnd - navigation.fetchStart;
          
          console.log(`Page load: ${pageName} - ${loadTime.toFixed(2)}ms`);
          
          // Report slow page loads
          if (loadTime > 3000) {
            console.warn(`Slow page load: ${pageName} - ${loadTime.toFixed(2)}ms`);
            
            if (this.isProduction) {
              this.sendToMonitoring('performance_warning', {
                page: pageName,
                loadTime: loadTime.toFixed(2),
                type: 'slow_page_load'
              });
            }
          }
        }
      }, 100);
    });
  }

  static trackAPICall(endpoint: string, method: string, duration: number, status: number): void {
    // Log API performance
    const logData = {
      method,
      endpoint,
      duration: duration.toFixed(2),
      status
    };

    if (duration > 2000) {
      console.warn(`Slow API call: ${method} ${endpoint} - ${duration.toFixed(2)}ms`);
      
      if (this.isProduction) {
        this.sendToMonitoring('performance_warning', {
          ...logData,
          type: 'slow_api_call'
        });
      }
    }
    
    // Track errors
    if (status >= 400) {
      console.error(`API Error: ${method} ${endpoint} - ${status}`);
      
      if (this.isProduction) {
        this.sendToMonitoring('api_error', {
          ...logData,
          type: 'api_error'
        });
      }
    }
  }

  static reportError(error: Error, context?: ErrorContext): void {
    console.error('Application Error:', error);
    
    if (this.isProduction) {
      this.sendToMonitoring('application_error', {
        message: error.message,
        stack: error.stack,
        context: context || {},
        type: 'application_error'
      });
    }
  }

  static setUser(user: User): void {
    if (this.isProduction) {
      // Store user context for monitoring
      sessionStorage.setItem('monitoring_user', JSON.stringify({
        id: user.id,
        email: user.email,
        username: user.username
      }));
    }
  }

  static clearUser(): void {
    if (this.isProduction) {
      sessionStorage.removeItem('monitoring_user');
    }
  }

  // Health check utility
  static async performHealthCheck(): Promise<boolean> {
    try {
      const response = await fetch('/health', {
        method: 'GET',
        timeout: 5000
      } as RequestInit);
      
      return response.ok;
    } catch (error) {
      console.error('Health check failed:', error);
      if (this.isProduction) {
        this.reportError(error as Error, { type: 'health_check_failure' });
      }
      return false;
    }
  }

  // Send monitoring data to external service
  private static sendToMonitoring(eventType: string, data: any): void {
    // In production, you would integrate with services like:
    // - Sentry for error tracking
    // - LogRocket for session replay
    // - DataDog for metrics
    // - Custom webhook for internal monitoring
    
    const monitoringData = {
      timestamp: new Date().toISOString(),
      eventType,
      data,
      userAgent: navigator.userAgent,
      url: window.location.href,
      user: this.getCurrentUser()
    };

    // For now, we'll use console.log in development
    // and could send to a monitoring endpoint in production
    if (import.meta.env.DEV) {
      console.log('Monitoring Event:', monitoringData);
    } else {
      // Example: Send to monitoring endpoint
      // fetch('/api/monitoring', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(monitoringData)
      // }).catch(console.error);
    }
  }

  private static getCurrentUser(): User | null {
    try {
      const userData = sessionStorage.getItem('monitoring_user');
      return userData ? JSON.parse(userData) : null;
    } catch {
      return null;
    }
  }
}

// Web Vitals tracking (for performance monitoring)
export const trackWebVitals = (metric: WebVitalMetric): void => {
  if (PerformanceMonitor['isProduction']) {
    console.log(`Web Vital: ${metric.name} = ${metric.value} (${metric.rating})`);
    
    // Report poor Core Web Vitals
    if (metric.rating === 'poor') {
      PerformanceMonitor['sendToMonitoring']('web_vital_poor', {
        name: metric.name,
        value: metric.value,
        rating: metric.rating,
        type: 'web_vital'
      });
    }
  }
};

// Global error handler
export const initializeGlobalErrorHandling = (): void => {
  // Catch unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    PerformanceMonitor.reportError(
      new Error(event.reason || 'Unhandled promise rejection'),
      { type: 'unhandled_promise_rejection' }
    );
  });

  // Catch global JavaScript errors
  window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    PerformanceMonitor.reportError(
      event.error || new Error(event.message),
      {
        type: 'global_error',
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      }
    );
  });
};

// Network monitoring
export class NetworkMonitor {
  static trackNetworkStatus(): void {
    if ('navigator' in window && 'onLine' in navigator) {
      const updateStatus = () => {
        const status = navigator.onLine ? 'online' : 'offline';
        console.log(`Network status: ${status}`);
        
        if (!navigator.onLine && PerformanceMonitor['isProduction']) {
          PerformanceMonitor['sendToMonitoring']('network_offline', {
            type: 'network_status',
            status: 'offline'
          });
        }
      };

      window.addEventListener('online', updateStatus);
      window.addEventListener('offline', updateStatus);
    }
  }

  static async measureConnectionSpeed(): Promise<number> {
    try {
      const startTime = performance.now();
      await fetch('/favicon.ico?t=' + Date.now(), { 
        method: 'HEAD',
        cache: 'no-cache' 
      });
      const endTime = performance.now();
      
      const duration = endTime - startTime;
      console.log(`Connection test: ${duration.toFixed(2)}ms`);
      
      return duration;
    } catch (error) {
      console.error('Connection speed test failed:', error);
      return -1;
    }
  }
}

export default PerformanceMonitor;