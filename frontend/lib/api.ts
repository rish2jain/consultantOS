/**
 * ConsultantOS API Client
 *
 * Centralized API client for all backend interactions.
 * Handles authentication, error handling, and type-safe requests.
 * 
 * SECURITY: Uses in-memory API key storage (see lib/auth.ts for details)
 */

import { getApiKey } from './auth';
import { z } from 'zod';
import {
  ReportSchema,
  ReportsListResponseSchema,
  AnalysisResponseSchema,
  JobStatusSchema,
  MonitorListResponseSchema,
  AlertListResponseSchema,
  DashboardStatsSchema,
  ShareListResponseSchema,
  ShareAnalyticsSchema,
  CommentListResponseSchema,
  CommentSchema,
  VersionHistoryResponseSchema,
  VersionDiffSchema,
  VersionSchema,
  NotificationListResponseSchema,
  NotificationSettingsSchema,
  TemplateLibraryResponseSchema,
  TemplateSchema,
  UserProfileSchema,
  LoginResponseSchema,
  JobListResponseSchema,
  AsyncAnalysisResponseSchema,
  DeleteResponseSchema,
  ShareSchema,
  type Report,
  type ReportsListResponse,
  type AnalysisResponse,
  type JobStatus,
  type MonitorListResponse,
  type AlertListResponse,
  type DashboardStats,
  type ShareListResponse,
  type Share,
  type ShareAnalytics,
  type CommentListResponse,
  type Comment,
  type VersionHistoryResponse,
  type VersionDiff,
  type Version,
  type NotificationListResponse,
  type NotificationSettings,
  type TemplateLibraryResponse,
  type Template,
  type UserProfile,
  type LoginResponse,
  type JobListResponse,
  type AsyncAnalysisResponse,
  type DeleteResponse,
} from './api-schemas';

// Development mode flag
const isDevelopment = process.env.NODE_ENV === 'development';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (process.env.NODE_ENV === 'production' 
    ? 'https://consultantos-api-187550875653.us-central1.run.app'
    : 'http://localhost:8080');

// API Error class
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// Generic API request function with retry logic
async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit,
  retries: number = 2
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers = {
    'Content-Type': 'application/json',
    ...options?.headers,
  };

  // Add API key if available (from in-memory storage only)
  // SECURITY: API keys are stored in memory only, not in localStorage
  // See lib/auth.ts for security details
  const apiKey = getApiKey();

  if (apiKey) {
    headers['X-API-Key'] = apiKey;
  }

  // Retry logic for network errors
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      // Add timeout to fetch requests (30 seconds for Cloud Run cold starts)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);

      try {
        const response = await fetch(url, {
          ...options,
          headers,
          signal: controller.signal,
        });

        // Handle non-JSON responses (like health check)
        const contentType = response.headers.get('content-type');
        const isJson = contentType?.includes('application/json');

        if (!response.ok) {
          // Don't retry on client errors (4xx) except 429 (rate limit)
          if (response.status >= 400 && response.status < 500 && response.status !== 429) {
            const error = isJson ? await response.json() : { detail: response.statusText };
            throw new APIError(
              error.detail || error.message || 'API request failed',
              response.status,
              error
            );
          }
          // Retry on server errors (5xx) and rate limits (429)
          if (attempt < retries) {
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
            continue;
          }
          const error = isJson ? await response.json() : { detail: response.statusText };
          throw new APIError(
            error.detail || error.message || 'API request failed',
            response.status,
            error
          );
        }

        const result = isJson ? await response.json() : await response.text();
        return result as T;
      } finally {
        clearTimeout(timeoutId);
      }
    } catch (error) {
      // Handle network errors and timeouts
      if (error instanceof APIError) {
        throw error;
      }

      // Retry on network errors
      if (attempt < retries && (error instanceof TypeError || error instanceof DOMException)) {
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
        continue;
      }

      // Final error handling
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new APIError(
          `Unable to connect to the server. Please check if the backend is running at ${API_BASE_URL}`,
          0,
          { originalError: error.message }
        );
      }

      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new APIError(
          'Request timed out. Please try again.',
          0,
          { originalError: 'Timeout' }
        );
      }

      throw new APIError(
        error instanceof Error ? error.message : 'Network error',
        0,
        { originalError: String(error) }
      );
    }
  }

  // This should never be reached, but TypeScript needs it
  throw new APIError('Request failed after retries', 0);
}

// Analysis API
export const analysisAPI = {
  /**
   * Create synchronous analysis
   */
  createSync: async (data: {
    company: string;
    industry: string;
    frameworks: string[];
    depth?: 'quick' | 'standard' | 'deep';
    additional_context?: string;
    region?: string;
  }): Promise<AnalysisResponse> => {
    const response = await apiRequest('/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    // Validate response
    try {
      return AnalysisResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Analysis response validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
          console.error('Validation errors:', JSON.stringify(error.issues, null, 2));
        }
      }
      return response as AnalysisResponse;
    }
  },

  /**
   * Create asynchronous analysis
   */
  createAsync: async (data: {
    company: string;
    industry: string;
    frameworks: string[];
    depth?: 'quick' | 'standard' | 'deep';
    additional_context?: string;
    region?: string;
  }): Promise<AsyncAnalysisResponse> => {
    const response = await apiRequest('/analyze/async', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    // Validate response
    try {
      return AsyncAnalysisResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Async analysis response validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as AsyncAnalysisResponse;
    }
  },

  /**
   * Get report by ID
   */
  getReport: async (reportId: string): Promise<Report> => {
    const response = await apiRequest(`/reports/${reportId}`);
    
    // Validate and transform response
    try {
      const validated = ReportSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        // Zod validation error
        console.error('Report validation failed:', error.issues);
        if (isDevelopment) {
          // In development, log full error
          console.error('Response data:', response);
          console.error('Validation errors:', JSON.stringify(error.issues, null, 2));
        }
        // Log to Sentry if available
        if (typeof window !== 'undefined' && (window as any).Sentry) {
          (window as any).Sentry.captureException(error, {
            extra: {
              response,
              reportId,
              validationErrors: error.issues,
            },
          });
        }
      }
      // Return response as-is if validation fails (graceful degradation)
      return response as Report;
    }
  },

  /**
   * List reports with pagination
   */
  listReports: async (params?: {
    page?: number;
    limit?: number;
    sort_by?: string;
    order?: 'asc' | 'desc';
    search?: string;
  }): Promise<ReportsListResponse> => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.set('page', params.page.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.sort_by) queryParams.set('sort_by', params.sort_by);
    if (params?.order) queryParams.set('order', params.order);
    if (params?.search) queryParams.set('search', params.search);

    const query = queryParams.toString();
    const response = await apiRequest(`/reports${query ? `?${query}` : ''}`);
    
    // Validate and transform response
    try {
      const validated = ReportsListResponseSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        // Zod validation error
        console.error('Reports list validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
          console.error('Validation errors:', JSON.stringify(error.issues, null, 2));
        }
        // Log to Sentry if available
        if (typeof window !== 'undefined' && (window as any).Sentry) {
          (window as any).Sentry.captureException(error, {
            extra: {
              response,
              params,
              validationErrors: error.issues,
            },
          });
        }
      }
      // Return partial data with fallback - try to parse individual reports
      try {
        const responseData = response as any;
        const reports = Array.isArray(responseData.reports) 
          ? responseData.reports.map((r: any) => {
              try {
                return ReportSchema.parse(r);
              } catch {
                return r; // Return as-is if individual report fails
              }
            })
          : [];
        return {
          reports,
          total: responseData.total || responseData.count || reports.length,
          page: responseData.page || params?.page || 1,
          limit: responseData.limit || params?.limit || 50,
        };
      } catch {
        // Ultimate fallback
        return {
          reports: [],
          total: 0,
          page: params?.page || 1,
          limit: params?.limit || 50,
        };
      }
    }
  },

  /**
   * Delete report
   */
  deleteReport: async (reportId: string): Promise<DeleteResponse> => {
    const response = await apiRequest(`/reports/${reportId}`, {
      method: 'DELETE',
    });
    
    // Validate response
    try {
      return DeleteResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Delete response validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as DeleteResponse;
    }
  },
};

// Jobs API
export const jobsAPI = {
  /**
   * Get job status
   */
  getStatus: async (jobId: string): Promise<JobStatus> => {
    const response = await apiRequest(`/jobs/${jobId}/status`);
    
    // Validate response
    try {
      return JobStatusSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Job status validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
          console.error('Validation errors:', JSON.stringify(error.issues, null, 2));
        }
      }
      return response as JobStatus;
    }
  },

  /**
   * List jobs
   */
  listJobs: async (params?: {
    status?: string;
    page?: number;
    limit?: number;
  }): Promise<JobListResponse> => {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.set('status', params.status);
    if (params?.page) queryParams.set('page', params.page.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());

    const query = queryParams.toString();
    const response = await apiRequest(`/jobs${query ? `?${query}` : ''}`);
    
    // Validate response
    try {
      return JobListResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Job list validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      // Graceful fallback
      const responseData = response as any;
      return {
        jobs: Array.isArray(responseData.jobs) ? responseData.jobs : Array.isArray(responseData) ? responseData : [],
        total: responseData.total || (Array.isArray(responseData) ? responseData.length : 0),
        page: params?.page || 1,
        limit: params?.limit || 50,
      };
    }
  },

  /**
   * Cancel job
   */
  cancelJob: async (jobId: string): Promise<DeleteResponse> => {
    const response = await apiRequest(`/jobs/${jobId}`, {
      method: 'DELETE',
    });
    
    // Validate response
    try {
      return DeleteResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Cancel job response validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as DeleteResponse;
    }
  },
};

// Monitoring API
export const monitoringAPI = {
  list: async (params?: { status?: string }): Promise<MonitorListResponse> => {
    const query = new URLSearchParams();
    if (params?.status) query.set('status', params.status);
    const qs = query.toString();
    const response = await apiRequest(`/monitors${qs ? `?${qs}` : ''}`);
    
    // Validate response
    try {
      return MonitorListResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Monitor list validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      // Graceful fallback
      const responseData = response as any;
      return {
        monitors: Array.isArray(responseData.monitors) ? responseData.monitors : Array.isArray(responseData) ? responseData : [],
        total: responseData.total || (Array.isArray(responseData) ? responseData.length : 0),
        active_count: responseData.active_count || 0,
      };
    }
  },

  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await apiRequest('/monitors/stats/dashboard');
    
    // Validate response
    try {
      return DashboardStatsSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Dashboard stats validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as DashboardStats;
    }
  },

  listAlerts: async (monitorId: string, limit = 5): Promise<AlertListResponse> => {
    const response = await apiRequest(`/monitors/${monitorId}/alerts?limit=${limit}`);
    
    // Validate response
    try {
      return AlertListResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Alert list validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      // Graceful fallback
      const responseData = response as any;
      return {
        alerts: Array.isArray(responseData.alerts) ? responseData.alerts : Array.isArray(responseData) ? responseData : [],
        total: responseData.total || (Array.isArray(responseData) ? responseData.length : 0),
      };
    }
  },

  runManualCheck: async (monitorId: string): Promise<{ success: boolean; message?: string }> => {
    const response = await apiRequest(`/monitors/${monitorId}/check`, {
      method: 'POST',
    });
    return response as { success: boolean; message?: string };
  },

  markAlertRead: async (alertId: string): Promise<{ success: boolean }> => {
    const response = await apiRequest(`/monitors/alerts/${alertId}/read`, {
      method: 'POST',
    });
    return response as { success: boolean };
  },

  updateMonitorStatus: async (
    monitorId: string,
    status: 'active' | 'paused'
  ): Promise<{ success: boolean }> => {
    const response = await apiRequest(`/monitors/${monitorId}`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
    return response as { success: boolean };
  },
};

// Shares API
export const sharesAPI = {
  /**
   * Create share link
   */
  create: async (data: {
    report_id: string;
    password?: string;
    expires_at?: string;
    permissions: 'view' | 'download';
  }): Promise<Share> => {
    const response = await apiRequest('/shares', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    // Validate response
    try {
      return ShareSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Create share validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as Share;
    }
  },

  /**
   * Get shared report
   */
  get: async (shareId: string, password?: string): Promise<Report> => {
    const headers = password ? { 'X-Share-Password': password } : {};
    const response = await apiRequest(`/shares/${shareId}`, { headers });
    
    // Validate response
    try {
      return ReportSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Get shared report validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as Report;
    }
  },

  /**
   * Update share settings
   */
  update: async (shareId: string, data: {
    password?: string;
    expires_at?: string;
    permissions?: 'view' | 'download';
  }): Promise<Share> => {
    const response = await apiRequest(`/shares/${shareId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    
    // Validate response
    try {
      return ShareSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Update share validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as Share;
    }
  },

  /**
   * Revoke share
   */
  revoke: async (shareId: string): Promise<DeleteResponse> => {
    const response = await apiRequest(`/shares/${shareId}`, {
      method: 'DELETE',
    });
    
    // Validate response
    try {
      return DeleteResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Revoke share validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as DeleteResponse;
    }
  },

  /**
   * List user's shares
   */
  listMy: async (): Promise<ShareListResponse> => {
    const response = await apiRequest('/shares/my-shares');
    
    // Validate response
    try {
      return ShareListResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('List shares validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      // Graceful fallback
      const responseData = response as any;
      return {
        report_id: responseData.report_id || '',
        shares: Array.isArray(responseData.shares) ? responseData.shares : Array.isArray(responseData) ? responseData : [],
        total: responseData.total || (Array.isArray(responseData) ? responseData.length : 0),
      };
    }
  },

  /**
   * Get share analytics
   */
  getAnalytics: async (shareId: string, timeRange?: '7d' | '30d' | 'all'): Promise<ShareAnalytics> => {
    const query = timeRange ? `?range=${timeRange}` : '';
    const response = await apiRequest(`/analytics/shares/${shareId}${query}`);
    
    // Validate response
    try {
      return ShareAnalyticsSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Share analytics validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as ShareAnalytics;
    }
  },
};

// Comments API
export const commentsAPI = {
  /**
   * Get comments for report
   */
  list: async (reportId: string): Promise<CommentListResponse> => {
    const response = await apiRequest(`/comments/report/${reportId}`);
    
    // Validate response
    try {
      return CommentListResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Comment list validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      // Graceful fallback
      const responseData = response as any;
      return {
        report_id: reportId,
        comments: Array.isArray(responseData.comments) ? responseData.comments : Array.isArray(responseData) ? responseData.map((c: any) => ({ comment: c, replies: [] })) : [],
        total: responseData.total || (Array.isArray(responseData) ? responseData.length : 0),
      };
    }
  },

  /**
   * Create comment
   */
  create: async (reportId: string, text: string): Promise<Comment> => {
    const response = await apiRequest(`/comments/${reportId}`, {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
    
    // Validate response
    try {
      return CommentSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Create comment validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as Comment;
    }
  },

  /**
   * Update comment
   */
  update: async (commentId: string, text: string): Promise<Comment> => {
    const response = await apiRequest(`/comments/${commentId}`, {
      method: 'PUT',
      body: JSON.stringify({ text }),
    });
    
    // Validate response
    try {
      return CommentSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Update comment validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as Comment;
    }
  },

  /**
   * Delete comment
   */
  delete: async (commentId: string): Promise<DeleteResponse> => {
    const response = await apiRequest(`/comments/${commentId}`, {
      method: 'DELETE',
    });
    
    // Validate response
    try {
      return DeleteResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Delete comment validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as DeleteResponse;
    }
  },

  /**
   * Reply to comment
   */
  reply: async (commentId: string, text: string): Promise<Comment> => {
    const response = await apiRequest(`/comments/${commentId}/reply`, {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
    
    // Validate response
    try {
      return CommentSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Reply comment validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as Comment;
    }
  },
};

// Versions API
export const versionsAPI = {
  /**
   * List versions for report
   */
  list: async (reportId: string): Promise<VersionHistoryResponse> => {
    const response = await apiRequest(`/versions/report/${reportId}`);
    
    // Handle empty or invalid responses
    if (!response || typeof response !== 'object' || Object.keys(response).length === 0) {
      // Return empty version history if response is empty
      return {
        report_id: reportId,
        versions: [],
        current_version: undefined,
        total_versions: 0,
      };
    }
    
    // Validate response
    try {
      return VersionHistoryResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Version list validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
          console.error('Validation errors:', JSON.stringify(error.issues, null, 2));
        }
      }
      // Graceful fallback
      const responseData = response as any;
      return {
        report_id: reportId,
        versions: Array.isArray(responseData.versions) ? responseData.versions : Array.isArray(responseData) ? responseData : [],
        current_version: responseData.current_version || undefined,
        total_versions: responseData.total_versions || (Array.isArray(responseData) ? responseData.length : 0),
      };
    }
  },

  /**
   * Get specific version
   */
  get: async (reportId: string, versionId: string): Promise<Version> => {
    const response = await apiRequest(`/versions/${reportId}/${versionId}`);
    
    // Validate response
    try {
      return VersionSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Get version validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as Version;
    }
  },

  /**
   * Compare versions
   */
  compare: async (reportId: string, versionA: string, versionB: string): Promise<VersionDiff> => {
    const response = await apiRequest(`/versions/${reportId}/compare?v1=${versionA}&v2=${versionB}`);
    
    // Validate response
    try {
      return VersionDiffSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Version compare validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as VersionDiff;
    }
  },

  /**
   * Restore version
   */
  restore: async (reportId: string, versionId: string): Promise<{ success: boolean; message?: string }> => {
    const response = await apiRequest(`/versions/${reportId}/${versionId}/restore`, {
      method: 'POST',
    });
    return response as { success: boolean; message?: string };
  },
};

// Notifications API
export const notificationsAPI = {
  /**
   * List notifications
   */
  list: async (type?: string): Promise<NotificationListResponse> => {
    const query = type ? `?type=${type}` : '';
    const response = await apiRequest(`/notifications${query}`);
    
    // Validate response
    try {
      return NotificationListResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Notification list validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      // Graceful fallback
      const responseData = response as any;
      return {
        notifications: Array.isArray(responseData.notifications) ? responseData.notifications : Array.isArray(responseData) ? responseData : [],
        count: responseData.count || (Array.isArray(responseData) ? responseData.length : 0),
        unread_count: responseData.unread_count || 0,
      };
    }
  },

  /**
   * Mark as read
   */
  markRead: async (notificationId: string): Promise<{ success: boolean }> => {
    const response = await apiRequest(`/notifications/${notificationId}/read`, {
      method: 'PUT',
    });
    return response as { success: boolean };
  },

  /**
   * Mark all as read
   */
  markAllRead: async (): Promise<{ success: boolean }> => {
    const response = await apiRequest('/notifications/read-all', {
      method: 'PUT',
    });
    return response as { success: boolean };
  },

  /**
   * Delete notification
   */
  delete: async (notificationId: string): Promise<DeleteResponse> => {
    const response = await apiRequest(`/notifications/${notificationId}`, {
      method: 'DELETE',
    });
    
    // Validate response
    try {
      return DeleteResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Delete notification validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as DeleteResponse;
    }
  },

  /**
   * Clear all notifications
   */
  clearAll: async (): Promise<DeleteResponse> => {
    const response = await apiRequest('/notifications/clear-all', {
      method: 'DELETE',
    });
    
    // Validate response
    try {
      return DeleteResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Clear notifications validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as DeleteResponse;
    }
  },

  /**
   * Get notification settings
   */
  getSettings: async (): Promise<NotificationSettings> => {
    const response = await apiRequest('/notifications/settings');
    
    // Validate response
    try {
      return NotificationSettingsSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Get notification settings validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as NotificationSettings;
    }
  },

  /**
   * Update notification settings
   */
  updateSettings: async (settings: {
    new_comments?: boolean;
    comment_replies?: boolean;
    report_shared?: boolean;
    new_versions?: boolean;
    analysis_complete?: boolean;
    email_enabled?: boolean;
    frequency?: 'instant' | 'daily' | 'weekly';
  }): Promise<NotificationSettings> => {
    const response = await apiRequest('/notifications/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
    
    // Validate response
    try {
      return NotificationSettingsSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Update notification settings validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as NotificationSettings;
    }
  },
};

// Templates API
export const templatesAPI = {
  /**
   * List templates
   */
  list: async (params?: {
    search?: string;
    category?: string;
    frameworks?: string[];
    visibility?: 'public' | 'private' | 'all';
    page?: number;
    limit?: number;
  }): Promise<TemplateLibraryResponse> => {
    const queryParams = new URLSearchParams();
    if (params?.search) queryParams.set('search', params.search);
    if (params?.category) queryParams.set('category', params.category);
    if (params?.frameworks) queryParams.set('frameworks', params.frameworks.join(','));
    if (params?.visibility) queryParams.set('visibility', params.visibility);
    if (params?.page) queryParams.set('page', params.page.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());

    const query = queryParams.toString();
    const response = await apiRequest(`/templates${query ? `?${query}` : ''}`);
    
    // Validate response
    try {
      return TemplateLibraryResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Template list validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      // Graceful fallback
      const responseData = response as any;
      return {
        templates: Array.isArray(responseData.templates) ? responseData.templates : Array.isArray(responseData) ? responseData : [],
        total: responseData.total || (Array.isArray(responseData) ? responseData.length : 0),
        page: params?.page || 1,
        page_size: params?.limit || 20,
      };
    }
  },

  /**
   * Get template by ID
   */
  get: async (templateId: string): Promise<Template> => {
    const response = await apiRequest(`/templates/${templateId}`);
    
    // Validate response
    try {
      return TemplateSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Get template validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as Template;
    }
  },

  /**
   * Create template
   */
  create: async (data: {
    name: string;
    description: string;
    category: string;
    frameworks: string[];
    default_settings: any;
    visibility: 'public' | 'private';
  }): Promise<Template> => {
    const response = await apiRequest('/templates', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    // Validate response
    try {
      return TemplateSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Create template validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as Template;
    }
  },

  /**
   * Update template
   */
  update: async (templateId: string, data: any): Promise<Template> => {
    const response = await apiRequest(`/templates/${templateId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    
    // Validate response
    try {
      return TemplateSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Update template validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as Template;
    }
  },

  /**
   * Delete template
   */
  delete: async (templateId: string): Promise<DeleteResponse> => {
    const response = await apiRequest(`/templates/${templateId}`, {
      method: 'DELETE',
    });
    
    // Validate response
    try {
      return DeleteResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Delete template validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as DeleteResponse;
    }
  },

  /**
   * Fork template
   */
  fork: async (templateId: string): Promise<Template> => {
    const response = await apiRequest(`/templates/${templateId}/fork`, {
      method: 'POST',
    });
    
    // Validate response
    try {
      return TemplateSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Fork template validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as Template;
    }
  },
};

// Users API
export const usersAPI = {
  /**
   * Login user
   */
  login: async (data: {
    email: string;
    password: string;
  }): Promise<LoginResponse> => {
    // Validate input before sending request
    if (!data.email || !data.password) {
      throw new APIError('Email and password are required', 400);
    }
    if (!data.email.trim() || !data.password.trim()) {
      throw new APIError('Email and password cannot be empty', 400);
    }
    // Basic email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email.trim())) {
      throw new APIError('Invalid email format', 400);
    }
    
    const response = await apiRequest('/users/login', {
      method: 'POST',
      body: JSON.stringify({
        email: data.email.trim(),
        password: data.password,
      }),
    });
    
    // Validate response
    try {
      return LoginResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Login response validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as LoginResponse;
    }
  },

  /**
   * Register user
   */
  register: async (data: {
    email: string;
    password: string;
    full_name: string;
    company?: string;
  }): Promise<{ success: boolean; message?: string; user_id?: string }> => {
    const response = await apiRequest('/users/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return response as { success: boolean; message?: string; user_id?: string };
  },

  /**
   * Verify email
   */
  verifyEmail: async (code: string): Promise<{ success: boolean; message?: string }> => {
    const response = await apiRequest('/users/verify-email', {
      method: 'POST',
      body: JSON.stringify({ code }),
    });
    return response as { success: boolean; message?: string };
  },

  /**
   * Request password reset
   */
  requestPasswordReset: async (email: string): Promise<{ success: boolean; message?: string }> => {
    const response = await apiRequest('/users/request-password-reset', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
    return response as { success: boolean; message?: string };
  },

  /**
   * Reset password
   */
  resetPassword: async (token: string, newPassword: string): Promise<{ success: boolean; message?: string }> => {
    const response = await apiRequest('/users/reset-password', {
      method: 'POST',
      body: JSON.stringify({ token, new_password: newPassword }),
    });
    return response as { success: boolean; message?: string };
  },

  /**
   * Get user profile
   */
  getProfile: async (): Promise<UserProfile> => {
    const response = await apiRequest('/users/profile');
    
    // Validate response
    try {
      return UserProfileSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Get profile validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as UserProfile;
    }
  },

  /**
   * Update profile
   */
  updateProfile: async (data: {
    full_name?: string;
    company?: string;
    job_title?: string;
  }): Promise<UserProfile> => {
    const response = await apiRequest('/users/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    
    // Validate response
    try {
      return UserProfileSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Update profile validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as UserProfile;
    }
  },

  /**
   * Change password
   */
  changePassword: async (currentPassword: string, newPassword: string): Promise<{ success: boolean; message?: string }> => {
    const response = await apiRequest('/users/change-password', {
      method: 'POST',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });
    return response as { success: boolean; message?: string };
  },

  /**
   * Delete account
   */
  deleteAccount: async (): Promise<DeleteResponse> => {
    const response = await apiRequest('/users/profile', {
      method: 'DELETE',
    });
    
    // Validate response
    try {
      return DeleteResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Delete account validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as DeleteResponse;
    }
  },

  /**
   * Create demo mode session
   */
  demoMode: async (): Promise<LoginResponse> => {
    const response = await apiRequest('/users/demo-mode', {
      method: 'POST',
    });
    
    // Validate response
    try {
      return LoginResponseSchema.parse(response);
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Demo mode response validation failed:', error.issues);
        if (isDevelopment) {
          console.error('Response data:', response);
        }
      }
      return response as LoginResponse;
    }
  },
};

// Health check
export const healthAPI = {
  check: () => apiRequest('/health'),
};

// Export all APIs
export const api = {
  analysis: analysisAPI,
  jobs: jobsAPI,
  shares: sharesAPI,
  comments: commentsAPI,
  versions: versionsAPI,
  notifications: notificationsAPI,
  templates: templatesAPI,
  users: usersAPI,
  health: healthAPI,
};

export default api;
