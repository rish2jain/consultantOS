/**
 * React Error Boundary for graceful error handling
 *
 * Features:
 * - Catches JavaScript errors in component tree
 * - Logs errors to monitoring service
 * - Displays fallback UI instead of white screen
 * - Allows retry with component reset
 */
'use client';

import React, { Component, ReactNode } from 'react';
import { Button } from './Button';
import { Alert } from './Alert';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  resetKeys?: any[];
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to console
    console.error('ErrorBoundary caught error:', error, errorInfo);

    // Store error info in state
    this.setState({ errorInfo });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Log to monitoring service (e.g., Sentry, LogRocket)
    this.logErrorToService(error, errorInfo);
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    // Reset error boundary if resetKeys change
    if (this.state.hasError) {
      // Check for reference equality first
      if (this.props.resetKeys === prevProps.resetKeys) {
        return; // No change
      }
      
      // Handle undefined/null transitions
      if (!this.props.resetKeys || !prevProps.resetKeys) {
        this.reset();
        return;
      }
      
      // Both are arrays, compare length and elements
      if (this.props.resetKeys.length !== prevProps.resetKeys.length) {
        this.reset();
        return;
      }
      
      // Check index-by-index without non-null assertions
      for (let i = 0; i < this.props.resetKeys.length; i++) {
        if (this.props.resetKeys[i] !== prevProps.resetKeys[i]) {
          this.reset();
          return;
        }
      }
    }
  }

  logErrorToService(error: Error, errorInfo: React.ErrorInfo) {
    // Send error to backend logging endpoint
    try {
      fetch('/api/logs/client-error', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          error: {
            message: error.message,
            stack: error.stack,
            name: error.name,
          },
          errorInfo: {
            componentStack: errorInfo.componentStack,
          },
          context: {
            url: window.location.href,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString(),
          },
        }),
      }).catch((fetchError) => {
        console.error('Failed to log error to service:', fetchError);
      });
    } catch (e) {
      console.error('Error while logging to service:', e);
    }
  }

  reset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
          <div className="max-w-md w-full">
            <Alert
              variant="error"
              title="Something went wrong"
              description={
                <div>
                  <p className="mb-4">
                    We encountered an unexpected error. Our team has been notified and is working on a fix.
                  </p>
                  {this.state.error && process.env.NODE_ENV === 'development' && (
                    <details className="mb-4">
                      <summary className="cursor-pointer text-sm font-medium">
                        Technical details
                      </summary>
                      <pre className="mt-2 text-xs bg-gray-100 p-2 rounded overflow-auto max-h-40">
                        {this.state.error.toString()}
                        {this.state.errorInfo?.componentStack}
                      </pre>
                    </details>
                  )}
                  <div className="flex gap-2">
                    <Button onClick={this.reset} variant="primary">
                      Try Again
                    </Button>
                    <Button
                      onClick={() => window.location.reload()}
                      variant="secondary"
                    >
                      Reload Page
                    </Button>
                  </div>
                </div>
              }
            />
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Hook for programmatic error boundary reset
 *
 * Usage:
 * ```tsx
 * const [resetKey, reset] = useErrorReset();
 *
 * <ErrorBoundary resetKeys={[resetKey]}>
 *   <MyComponent />
 * </ErrorBoundary>
 * ```
 */
export function useErrorReset(): [number, () => void] {
  const [resetKey, setResetKey] = React.useState(0);

  const reset = React.useCallback(() => {
    setResetKey((key) => key + 1);
  }, []);

  return [resetKey, reset];
}

export default ErrorBoundary;
