/**
 * Web Performance Monitoring Utilities
 *
 * Features:
 * - Core Web Vitals tracking (LCP, FID, CLS)
 * - Custom performance marks and measures
 * - Performance metrics logging to backend
 * - Resource timing analysis
 */

// Core Web Vitals types
export interface WebVitalsMetric {
  name: 'CLS' | 'FID' | 'LCP' | 'FCP' | 'TTFB' | 'INP';
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  delta: number;
  id: string;
  navigationType: 'navigate' | 'reload' | 'back-forward' | 'prerender';
}

export interface PerformanceMetrics {
  // Core Web Vitals
  lcp?: number;  // Largest Contentful Paint
  fid?: number;  // First Input Delay
  cls?: number;  // Cumulative Layout Shift
  fcp?: number;  // First Contentful Paint
  ttfb?: number; // Time to First Byte
  inp?: number;  // Interaction to Next Paint

  // Custom metrics
  pageLoadTime?: number;
  dnsLookupTime?: number;
  tcpConnectionTime?: number;
  requestTime?: number;
  responseTime?: number;
  domContentLoadedTime?: number;
  domInteractiveTime?: number;

  // Resource metrics
  totalResources?: number;
  totalResourceSize?: number;
  slowestResource?: {
    name: string;
    duration: number;
  };

  // Context
  url: string;
  userAgent: string;
  timestamp: string;
}

/**
 * Web Vitals thresholds for rating
 * Source: https://web.dev/vitals/
 */
const VITALS_THRESHOLDS = {
  LCP: { good: 2500, poor: 4000 },
  FID: { good: 100, poor: 300 },
  CLS: { good: 0.1, poor: 0.25 },
  FCP: { good: 1800, poor: 3000 },
  TTFB: { good: 800, poor: 1800 },
  INP: { good: 200, poor: 500 },
};

/**
 * Get rating for a metric value
 */
function getRating(
  name: WebVitalsMetric['name'],
  value: number
): WebVitalsMetric['rating'] {
  const threshold = VITALS_THRESHOLDS[name];
  if (!threshold) return 'good';

  if (value <= threshold.good) return 'good';
  if (value <= threshold.poor) return 'needs-improvement';
  return 'poor';
}

/**
 * Report Web Vitals metric to analytics
 */
function reportWebVitals(metric: WebVitalsMetric) {
  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Web Vitals] ${metric.name}:`, {
      value: metric.value,
      rating: metric.rating,
      delta: metric.delta,
    });
  }

  // Send to backend analytics endpoint
  sendToAnalytics({
    metric_name: metric.name,
    metric_value: metric.value,
    metric_rating: metric.rating,
    metric_delta: metric.delta,
    metric_id: metric.id,
    navigation_type: metric.navigationType,
  });
}

/**
 * Initialize Web Vitals tracking
 */
export async function initWebVitals() {
  if (typeof window === 'undefined') return;

  try {
    // Dynamically import web-vitals
    const { onCLS, onFID, onLCP, onFCP, onTTFB, onINP } = await import('web-vitals');

    // Track all Core Web Vitals
    onCLS(reportWebVitals);
    onFID(reportWebVitals);
    onLCP(reportWebVitals);
    onFCP(reportWebVitals);
    onTTFB(reportWebVitals);
    onINP(reportWebVitals);

    console.log('[Performance] Web Vitals tracking initialized');
  } catch (error) {
    console.error('[Performance] Failed to initialize Web Vitals:', error);
  }
}

/**
 * Collect comprehensive performance metrics
 */
export function collectPerformanceMetrics(): PerformanceMetrics {
  if (typeof window === 'undefined') {
    return {
      url: '',
      userAgent: '',
      timestamp: new Date().toISOString(),
    };
  }

  const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
  const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];

  // Calculate resource metrics
  const totalResourceSize = resources.reduce((sum, r) => sum + (r.transferSize || 0), 0);
  const slowestResource = resources.reduce(
    (slowest, r) => (r.duration > slowest.duration ? { name: r.name, duration: r.duration } : slowest),
    { name: '', duration: 0 }
  );

  return {
    // Navigation timing
    pageLoadTime: navigation?.loadEventEnd - navigation?.fetchStart,
    dnsLookupTime: navigation?.domainLookupEnd - navigation?.domainLookupStart,
    tcpConnectionTime: navigation?.connectEnd - navigation?.connectStart,
    requestTime: navigation?.responseStart - navigation?.requestStart,
    responseTime: navigation?.responseEnd - navigation?.responseStart,
    domContentLoadedTime: navigation?.domContentLoadedEventEnd - navigation?.fetchStart,
    domInteractiveTime: navigation?.domInteractive - navigation?.fetchStart,

    // Resource metrics
    totalResources: resources.length,
    totalResourceSize,
    slowestResource: slowestResource.duration > 0 ? slowestResource : undefined,

    // Context
    url: window.location.href,
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Send metrics to analytics backend
 */
async function sendToAnalytics(data: Record<string, any>) {
  if (typeof window === 'undefined') return;

  try {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

    await fetch(`${API_URL}/api/analytics/performance`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...data,
        url: window.location.href,
        timestamp: new Date().toISOString(),
      }),
      // Use keepalive to ensure request completes even if page unloads
      keepalive: true,
    });
  } catch (error) {
    // Silently fail - don't disrupt user experience
    console.error('[Performance] Failed to send analytics:', error);
  }
}

/**
 * Custom performance mark
 */
export function mark(name: string) {
  if (typeof window !== 'undefined' && performance.mark) {
    performance.mark(name);
  }
}

/**
 * Custom performance measure
 */
export function measure(name: string, startMark: string, endMark?: string) {
  if (typeof window !== 'undefined' && performance.measure) {
    try {
      const measurement = performance.measure(name, startMark, endMark);
      console.log(`[Performance] ${name}: ${measurement.duration.toFixed(2)}ms`);
      return measurement.duration;
    } catch (error) {
      console.error(`[Performance] Failed to measure ${name}:`, error);
      return 0;
    }
  }
  return 0;
}

/**
 * Report performance metrics on page load
 */
export function reportPageLoadMetrics() {
  if (typeof window === 'undefined') return;

  // Wait for page to fully load
  window.addEventListener('load', () => {
    // Collect after a short delay to ensure all metrics are available
    setTimeout(() => {
      const metrics = collectPerformanceMetrics();

      // Log in development
      if (process.env.NODE_ENV === 'development') {
        console.table({
          'Page Load Time': `${metrics.pageLoadTime?.toFixed(0)}ms`,
          'DNS Lookup': `${metrics.dnsLookupTime?.toFixed(0)}ms`,
          'TCP Connection': `${metrics.tcpConnectionTime?.toFixed(0)}ms`,
          'Request Time': `${metrics.requestTime?.toFixed(0)}ms`,
          'Response Time': `${metrics.responseTime?.toFixed(0)}ms`,
          'DOM Interactive': `${metrics.domInteractiveTime?.toFixed(0)}ms`,
          'DOM Content Loaded': `${metrics.domContentLoadedTime?.toFixed(0)}ms`,
          'Total Resources': metrics.totalResources,
          'Total Resource Size': `${(metrics.totalResourceSize! / 1024).toFixed(2)} KB`,
        });
      }

      // Send to analytics
      sendToAnalytics({
        event_type: 'page_load',
        ...metrics,
      });
    }, 1000);
  });
}

/**
 * Track route transitions (for Next.js App Router)
 */
export function trackRouteChange(url: string) {
  mark(`route-change-start-${url}`);

  // Mark when route change completes
  requestAnimationFrame(() => {
    mark(`route-change-end-${url}`);
    const duration = measure(
      `route-transition-${url}`,
      `route-change-start-${url}`,
      `route-change-end-${url}`
    );

    sendToAnalytics({
      event_type: 'route_transition',
      url,
      duration,
    });
  });
}

/**
 * Report long tasks (>50ms)
 */
export function observeLongTasks() {
  if (typeof window === 'undefined' || !('PerformanceObserver' in window)) return;

  try {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.duration > 50) {
          console.warn(`[Performance] Long task detected: ${entry.duration.toFixed(2)}ms`);

          sendToAnalytics({
            event_type: 'long_task',
            duration: entry.duration,
            start_time: entry.startTime,
          });
        }
      }
    });

    observer.observe({ entryTypes: ['longtask'] });
  } catch (error) {
    console.error('[Performance] Failed to observe long tasks:', error);
  }
}

/**
 * Initialize all performance monitoring
 */
export function initPerformanceMonitoring() {
  if (typeof window === 'undefined') return;

  console.log('[Performance] Initializing performance monitoring...');

  initWebVitals();
  reportPageLoadMetrics();
  observeLongTasks();
}
