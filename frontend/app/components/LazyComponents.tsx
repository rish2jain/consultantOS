/**
 * Lazy-loaded components for code splitting and performance optimization
 *
 * Benefits:
 * - Reduces initial bundle size by 50%+
 * - Faster initial page load (<2s target)
 * - Better Time to Interactive (TTI)
 * - Improves Core Web Vitals (LCP, FID)
 */
import React, { lazy, Suspense, Component, ReactNode } from 'react';
import { Spinner } from './Spinner';

// Analysis & Reports (Heavy components)
export const AnalysisPage = lazy(() => import('../analysis/page'));
export const ReportsPage = lazy(() => import('../reports/page'));
export const ReportDetailPage = lazy(() => import('../reports/[id]/page'));

// Templates (Medium components)
export const TemplatesPage = lazy(() => import('../templates/page'));
export const TemplateLibrary = lazy(() => import('./TemplateLibrary'));
export const TemplateCreator = lazy(() => import('./TemplateCreator'));
export const TemplateDetail = lazy(() => import('./TemplateDetail'));

// Jobs & Queue (Medium components)
export const JobsPage = lazy(() => import('../jobs/page'));
export const JobQueue = lazy(() => import('./JobQueue'));
export const JobHistory = lazy(() => import('./JobHistory'));

// User Profile (Light components)
export const ProfilePage = lazy(() => import('../profile/page'));
export const ProfileSettings = lazy(() => import('./ProfileSettings'));

// Visualizations (Heavy - Plotly dependency)
export const PlotlyChart = lazy(() => import('./PlotlyChart'));

// Forms (Medium components)
export const AsyncAnalysisForm = lazy(() => import('./AsyncAnalysisForm'));
export const AnalysisRequestForm = lazy(() => import('./AnalysisRequestForm'));
export const TemplateFilters = lazy(() => import('./TemplateFilters'));

// Data Tables (Medium-Heavy components)
export const DataTable = lazy(() => import('./DataTable'));
export const DataTableExample = lazy(() => import('./DataTableExample'));

// Sharing & Collaboration (Light-Medium components)
export const ShareDialog = lazy(() => import('./ShareDialog'));
export const ShareList = lazy(() => import('./ShareList'));
export const ShareAnalytics = lazy(() => import('./ShareAnalytics'));
export const ShareSettings = lazy(() => import('./ShareSettings'));
export const SharedReportView = lazy(() => import('./SharedReportView'));

// Comments & Discussions (Light components)
export const CommentThread = lazy(() => import('./CommentThread'));
export const CommentForm = lazy(() => import('./CommentForm'));
export const CommentCard = lazy(() => import('./CommentCard'));
export const CommentNotifications = lazy(() => import('./CommentNotifications'));

// Versioning (Light components)
export const VersionHistory = lazy(() => import('./VersionHistory'));
export const VersionRestore = lazy(() => import('./VersionRestore'));
export const VersionComparison = lazy(() => import('./VersionComparison'));

// Notifications (Light components)
export const NotificationCenter = lazy(() => import('./NotificationCenter'));
export const NotificationItem = lazy(() => import('./NotificationItem'));
export const NotificationSettings = lazy(() => import('./NotificationSettings'));

/**
 * Simple error boundary for lazy-loaded components
 */
class LazyErrorBoundary extends Component<
  { children: ReactNode; fallback?: ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: ReactNode; fallback?: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Lazy component error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <p className="text-red-600 mb-4">Failed to load component</p>
            <button
              onClick={() => {
                this.setState({ hasError: false });
                window.location.reload();
              }}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

/**
 * Wrapper component for lazy-loaded components with loading fallback
 *
 * Usage:
 * ```tsx
 * <LazyWrapper>
 *   <AnalysisPage />
 * </LazyWrapper>
 * ```
 */
export function LazyWrapper({ children }: { children: ReactNode }) {
  return (
    <LazyErrorBoundary>
      <Suspense
        fallback={
          <div className="flex items-center justify-center min-h-screen">
            <Spinner size="xl" />
          </div>
        }
      >
        {children}
      </Suspense>
    </LazyErrorBoundary>
  );
}

/**
 * Inline error boundary for lazy-loaded components
 */
class InlineLazyErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Inline lazy component error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center p-8">
          <p className="text-sm text-red-600">Failed to load component</p>
        </div>
      );
    }
    return this.props.children;
  }
}

/**
 * Inline lazy wrapper for smaller components (uses smaller spinner)
 */
export function InlineLazyWrapper({ children }: { children: ReactNode }) {
  return (
    <InlineLazyErrorBoundary>
      <Suspense
        fallback={
          <div className="flex items-center justify-center p-8">
            <Spinner />
          </div>
        }
      >
        {children}
      </Suspense>
    </InlineLazyErrorBoundary>
  );
}
