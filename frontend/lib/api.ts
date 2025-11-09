/**
 * ConsultantOS API Client
 *
 * Centralized API client for all backend interactions.
 * Handles authentication, error handling, and type-safe requests.
 * 
 * SECURITY: Uses in-memory API key storage (see lib/auth.ts for details)
 */

import { getApiKey } from './auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

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

// Generic API request function
async function apiRequest<T>(
  endpoint: string,
  options?: RequestInit
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

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle non-JSON responses (like health check)
    const contentType = response.headers.get('content-type');
    const isJson = contentType?.includes('application/json');

    if (!response.ok) {
      const error = isJson ? await response.json() : { detail: response.statusText };
      throw new APIError(
        error.detail || error.message || 'API request failed',
        response.status,
        error
      );
    }

    return isJson ? response.json() : response.text();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError(
      error instanceof Error ? error.message : 'Network error',
      0
    );
  }
}

// Analysis API
export const analysisAPI = {
  /**
   * Create synchronous analysis
   */
  createSync: (data: {
    company: string;
    industry: string;
    frameworks: string[];
    depth?: 'quick' | 'standard' | 'deep';
    additional_context?: string;
    region?: string;
  }) => apiRequest('/analyze', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  /**
   * Create asynchronous analysis
   */
  createAsync: (data: {
    company: string;
    industry: string;
    frameworks: string[];
    depth?: 'quick' | 'standard' | 'deep';
    additional_context?: string;
    region?: string;
  }) => apiRequest<{ job_id: string; status: string }>('/analyze/async', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  /**
   * Get report by ID
   */
  getReport: (reportId: string) => apiRequest(`/reports/${reportId}`),

  /**
   * List reports with pagination
   */
  listReports: (params?: {
    page?: number;
    limit?: number;
    sort_by?: string;
    order?: 'asc' | 'desc';
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.set('page', params.page.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.sort_by) queryParams.set('sort_by', params.sort_by);
    if (params?.order) queryParams.set('order', params.order);

    const query = queryParams.toString();
    return apiRequest(`/reports${query ? `?${query}` : ''}`);
  },

  /**
   * Delete report
   */
  deleteReport: (reportId: string) => apiRequest(`/reports/${reportId}`, {
    method: 'DELETE',
  }),
};

// Jobs API
export const jobsAPI = {
  /**
   * Get job status
   */
  getStatus: (jobId: string) => apiRequest<{
    id: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    progress: number;
    result?: any;
    error?: string;
    created_at: string;
    updated_at: string;
  }>(`/jobs/${jobId}/status`),

  /**
   * List jobs
   */
  listJobs: (params?: {
    status?: string;
    page?: number;
    limit?: number;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.set('status', params.status);
    if (params?.page) queryParams.set('page', params.page.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());

    const query = queryParams.toString();
    return apiRequest(`/jobs${query ? `?${query}` : ''}`);
  },

  /**
   * Cancel job
   */
  cancelJob: (jobId: string) => apiRequest(`/jobs/${jobId}`, {
    method: 'DELETE',
  }),
};

// Shares API
export const sharesAPI = {
  /**
   * Create share link
   */
  create: (data: {
    report_id: string;
    password?: string;
    expires_at?: string;
    permissions: 'view' | 'download';
  }) => apiRequest('/shares', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  /**
   * Get shared report
   */
  get: (shareId: string, password?: string) => {
    const headers = password ? { 'X-Share-Password': password } : {};
    return apiRequest(`/shares/${shareId}`, { headers });
  },

  /**
   * Update share settings
   */
  update: (shareId: string, data: {
    password?: string;
    expires_at?: string;
    permissions?: 'view' | 'download';
  }) => apiRequest(`/shares/${shareId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  /**
   * Revoke share
   */
  revoke: (shareId: string) => apiRequest(`/shares/${shareId}`, {
    method: 'DELETE',
  }),

  /**
   * List user's shares
   */
  listMy: () => apiRequest('/shares/my-shares'),

  /**
   * Get share analytics
   */
  getAnalytics: (shareId: string, timeRange?: '7d' | '30d' | 'all') => {
    const query = timeRange ? `?range=${timeRange}` : '';
    return apiRequest(`/analytics/shares/${shareId}${query}`);
  },
};

// Comments API
export const commentsAPI = {
  /**
   * Get comments for report
   */
  list: (reportId: string) => apiRequest(`/comments/report/${reportId}`),

  /**
   * Create comment
   */
  create: (reportId: string, text: string) => apiRequest(`/comments/${reportId}`, {
    method: 'POST',
    body: JSON.stringify({ text }),
  }),

  /**
   * Update comment
   */
  update: (commentId: string, text: string) => apiRequest(`/comments/${commentId}`, {
    method: 'PUT',
    body: JSON.stringify({ text }),
  }),

  /**
   * Delete comment
   */
  delete: (commentId: string) => apiRequest(`/comments/${commentId}`, {
    method: 'DELETE',
  }),

  /**
   * Reply to comment
   */
  reply: (commentId: string, text: string) => apiRequest(`/comments/${commentId}/reply`, {
    method: 'POST',
    body: JSON.stringify({ text }),
  }),
};

// Versions API
export const versionsAPI = {
  /**
   * List versions for report
   */
  list: (reportId: string) => apiRequest(`/versions/report/${reportId}`),

  /**
   * Get specific version
   */
  get: (reportId: string, versionId: string) =>
    apiRequest(`/versions/${reportId}/${versionId}`),

  /**
   * Compare versions
   */
  compare: (reportId: string, versionA: string, versionB: string) =>
    apiRequest(`/versions/${reportId}/compare?v1=${versionA}&v2=${versionB}`),

  /**
   * Restore version
   */
  restore: (reportId: string, versionId: string) =>
    apiRequest(`/versions/${reportId}/${versionId}/restore`, {
      method: 'POST',
    }),
};

// Notifications API
export const notificationsAPI = {
  /**
   * List notifications
   */
  list: (type?: string) => {
    const query = type ? `?type=${type}` : '';
    return apiRequest(`/notifications${query}`);
  },

  /**
   * Mark as read
   */
  markRead: (notificationId: string) =>
    apiRequest(`/notifications/${notificationId}/read`, {
      method: 'PUT',
    }),

  /**
   * Mark all as read
   */
  markAllRead: () => apiRequest('/notifications/read-all', {
    method: 'PUT',
  }),

  /**
   * Delete notification
   */
  delete: (notificationId: string) =>
    apiRequest(`/notifications/${notificationId}`, {
      method: 'DELETE',
    }),

  /**
   * Clear all notifications
   */
  clearAll: () => apiRequest('/notifications/clear-all', {
    method: 'DELETE',
  }),

  /**
   * Get notification settings
   */
  getSettings: () => apiRequest('/notifications/settings'),

  /**
   * Update notification settings
   */
  updateSettings: (settings: {
    new_comments?: boolean;
    comment_replies?: boolean;
    report_shared?: boolean;
    new_versions?: boolean;
    analysis_complete?: boolean;
    email_enabled?: boolean;
    frequency?: 'instant' | 'daily' | 'weekly';
  }) => apiRequest('/notifications/settings', {
    method: 'PUT',
    body: JSON.stringify(settings),
  }),
};

// Templates API
export const templatesAPI = {
  /**
   * List templates
   */
  list: (params?: {
    search?: string;
    category?: string;
    frameworks?: string[];
    visibility?: 'public' | 'private' | 'all';
    page?: number;
    limit?: number;
  }) => {
    const queryParams = new URLSearchParams();
    if (params?.search) queryParams.set('search', params.search);
    if (params?.category) queryParams.set('category', params.category);
    if (params?.frameworks) queryParams.set('frameworks', params.frameworks.join(','));
    if (params?.visibility) queryParams.set('visibility', params.visibility);
    if (params?.page) queryParams.set('page', params.page.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());

    const query = queryParams.toString();
    return apiRequest(`/templates${query ? `?${query}` : ''}`);
  },

  /**
   * Get template by ID
   */
  get: (templateId: string) => apiRequest(`/templates/${templateId}`),

  /**
   * Create template
   */
  create: (data: {
    name: string;
    description: string;
    category: string;
    frameworks: string[];
    default_settings: any;
    visibility: 'public' | 'private';
  }) => apiRequest('/templates', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  /**
   * Update template
   */
  update: (templateId: string, data: any) => apiRequest(`/templates/${templateId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  /**
   * Delete template
   */
  delete: (templateId: string) => apiRequest(`/templates/${templateId}`, {
    method: 'DELETE',
  }),

  /**
   * Fork template
   */
  fork: (templateId: string) => apiRequest(`/templates/${templateId}/fork`, {
    method: 'POST',
  }),
};

// Users API
export const usersAPI = {
  /**
   * Login user
   */
  login: (data: {
    email: string;
    password: string;
  }) => {
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
    
    return apiRequest<{
      access_token: string;
      token_type: string;
      user: {
        user_id: string;
        email: string;
        name?: string;
        subscription_tier?: string;
      };
    }>('/users/login', {
      method: 'POST',
      body: JSON.stringify({
        email: data.email.trim(),
        password: data.password,
      }),
    });
  },

  /**
   * Register user
   */
  register: (data: {
    email: string;
    password: string;
    full_name: string;
    company?: string;
  }) => apiRequest('/users/register', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  /**
   * Verify email
   */
  verifyEmail: (code: string) => apiRequest('/users/verify-email', {
    method: 'POST',
    body: JSON.stringify({ code }),
  }),

  /**
   * Request password reset
   */
  requestPasswordReset: (email: string) => apiRequest('/users/request-password-reset', {
    method: 'POST',
    body: JSON.stringify({ email }),
  }),

  /**
   * Reset password
   */
  resetPassword: (token: string, newPassword: string) =>
    apiRequest('/users/reset-password', {
      method: 'POST',
      body: JSON.stringify({ token, new_password: newPassword }),
    }),

  /**
   * Get user profile
   */
  getProfile: () => apiRequest('/users/profile'),

  /**
   * Update profile
   */
  updateProfile: (data: {
    full_name?: string;
    company?: string;
    job_title?: string;
  }) => apiRequest('/users/profile', {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  /**
   * Change password
   */
  changePassword: (currentPassword: string, newPassword: string) =>
    apiRequest('/users/change-password', {
      method: 'POST',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    }),

  /**
   * Delete account
   */
  deleteAccount: () => apiRequest('/users/profile', {
    method: 'DELETE',
  }),
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
