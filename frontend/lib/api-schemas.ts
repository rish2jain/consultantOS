/**
 * Zod schemas for API response validation
 * 
 * These schemas match the backend Pydantic models and provide:
 * - Runtime validation of API responses
 * - Type inference for TypeScript
 * - Automatic transformation (e.g., report_id -> id)
 */

import { z } from "zod";

// Optional URL schema that accepts null, undefined, valid URLs, or relative paths
const optionalUrlSchema = z.union([
  z.string().url(), // Valid absolute URLs
  z.string().startsWith("/"), // Relative paths starting with /
  z.null(), // Explicit null
]).optional(); // Also allows undefined

// Report schema matching backend ReportMetadata model
export const ReportSchema = z
  .object({
    report_id: z.string(),
    company: z.string(),
    // industry can be null, undefined, or a string (for backward compatibility with older reports)
    industry: z.union([z.string(), z.null()]).optional(),
    frameworks: z.array(z.string()),
    created_at: z.string(),
    status: z.enum(["completed", "processing", "failed", "partial_success"]),
    confidence_score: z.number().min(0).max(1).optional(),
    user_id: z.string().optional(),
    // pdf_url can be null, undefined, a valid URL string, or a relative path
    pdf_url: optionalUrlSchema,
    execution_time_seconds: z.number().optional(),
    framework_analysis: z.any().optional(), // Complex nested structure
    metadata: z.record(z.string(), z.any()).optional(),
    partial_results: z.boolean().optional(),
    errors: z.union([z.array(z.string()), z.record(z.string(), z.any())]).optional(),
  })
  .transform((data) => ({
    // Transform to frontend format - map report_id to id and normalize metadata flags
    id: data.report_id,
    ...data,
    metadata: data.metadata ?? {},
    partial_results:
      data.partial_results ??
      (typeof data.metadata?.partial_results === 'boolean'
        ? data.metadata.partial_results
        : false),
    errors:
      data.errors ??
      (data.metadata?.errors ? data.metadata.errors : undefined),
  }));

export type Report = z.infer<typeof ReportSchema>;

// Reports list response
export const ReportsListResponseSchema = z.object({
  reports: z.array(ReportSchema),
  total: z.number().optional(),
  count: z.number().optional(),
  page: z.number().optional(),
  limit: z.number().optional(),
  total_pages: z.number().optional(),
});

export type ReportsListResponse = z.infer<typeof ReportsListResponseSchema>;

// Analysis request schema
export const AnalysisRequestSchema = z.object({
  company: z.string().min(1),
  industry: z.string().min(1),
  frameworks: z.array(z.enum(["porter", "swot", "pestel", "blue_ocean"])),
  depth: z.enum(["quick", "standard", "deep"]).optional(),
  additional_context: z.string().optional(),
  region: z.string().optional(),
});

export type AnalysisRequest = z.infer<typeof AnalysisRequestSchema>;

// Analysis response schema
export const AnalysisResponseSchema = z.object({
  status: z.string(),
  report_id: z.string(),
  report_url: optionalUrlSchema,
  pdf_url: optionalUrlSchema,
  company: z.string(),
  industry: z.string().optional(),
  frameworks: z.array(z.string()).optional(),
  confidence_score: z.number().min(0).max(1).optional(),
  execution_time_seconds: z.number().optional(),
  executive_summary: z.any().optional(),
  framework_analysis: z.any().optional(),
});

export type AnalysisResponse = z.infer<typeof AnalysisResponseSchema>;

// Job status schema - matches backend JobQueue.get_status() and list_jobs() response
export const JobStatusSchema = z
  .object({
    job_id: z.string(),
    status: z.enum(["pending", "running", "processing", "completed", "failed", "cancelled", "not_found", "error"]),
    progress: z.number().min(0).max(100).optional(),
    result: z.any().optional(),
    error: z.union([z.string(), z.null()]).optional(),
    created_at: z.string(),
    updated_at: z.string().optional(),
    // Additional fields from backend
    company: z.string().optional(),
    industry: z.string().optional(),
    frameworks: z.array(z.string()).optional(),
    report_id: z.union([z.string(), z.null()]).optional(),
  })
  .transform((data) => ({
    // Transform to frontend format - map job_id to id
    id: data.job_id,
    ...data,
  }));

export type JobStatus = z.infer<typeof JobStatusSchema>;

// Comment schema
export const CommentSchema = z.object({
  id: z.string(),
  report_id: z.string(),
  text: z.string(),
  user: z.object({
    id: z.string(),
    name: z.string(),
  }).optional(),
  created_at: z.string(),
  updated_at: z.string().optional(),
  parent_id: z.string().optional(),
  replies: z.array(z.lazy(() => CommentSchema)).optional(),
});

export type Comment = z.infer<typeof CommentSchema>;

// Version schema - matches backend ReportVersion model
export const VersionSchema = z
  .object({
    version_id: z.string(),
    report_id: z.string(),
    version_number: z.number(),
    created_at: z.string(),
    created_by: z.string(),
    status: z.enum(["draft", "published", "archived"]).optional(),
    company: z.string(),
    industry: z.union([z.string(), z.null()]).optional(),
    frameworks: z.array(z.string()),
    executive_summary: z.any().optional(),
    pdf_url: optionalUrlSchema,
    signed_url: optionalUrlSchema,
    change_summary: z.union([z.string(), z.null()]).optional(),
    parent_version_id: z.union([z.string(), z.null()]).optional(),
    confidence_score: z.number().min(0).max(1).optional(),
    execution_time_seconds: z.number().optional(),
  })
  .transform((data) => ({
    // Transform to frontend format - map version_id to id
    id: data.version_id,
    // Compute is_current from context (will be set by VersionHistoryResponseSchema)
    is_current: false, // This will be set by the parent schema
    ...data,
  }));

export type Version = z.infer<typeof VersionSchema>;

// Monitor schema
export const MonitorSchema = z.object({
  id: z.string(),
  user_id: z.string(),
  company: z.string(),
  industry: z.string(),
  config: z.object({
    frequency: z.enum(['hourly', 'daily', 'weekly', 'monthly']),
    frameworks: z.array(z.string()),
    alert_threshold: z.number().min(0).max(1),
    notification_channels: z.array(z.string()),
    keywords: z.array(z.string()).optional(),
    competitors: z.array(z.string()).optional(),
  }),
  status: z.enum(['active', 'paused', 'deleted', 'error']),
  created_at: z.string(),
  last_check: z.string().optional(),
  next_check: z.string().optional(),
  last_snapshot: z.any().optional(),
});

export type Monitor = z.infer<typeof MonitorSchema>;

// Monitor list response
export const MonitorListResponseSchema = z.object({
  monitors: z.array(MonitorSchema),
  total: z.number(),
  active_count: z.number().optional(),
});

export type MonitorListResponse = z.infer<typeof MonitorListResponseSchema>;

// Alert schema
export const AlertSchema = z.object({
  id: z.string(),
  monitor_id: z.string(),
  title: z.string(),
  summary: z.string(),
  confidence: z.number().min(0).max(1),
  changes_detected: z.array(z.any()),
  created_at: z.string(),
  read: z.boolean(),
  read_at: z.string().optional(),
});

export type Alert = z.infer<typeof AlertSchema>;

// Alert list response
export const AlertListResponseSchema = z.object({
  alerts: z.array(AlertSchema),
  total: z.number().optional(),
});

export type AlertListResponse = z.infer<typeof AlertListResponseSchema>;

// Dashboard stats schema
export const DashboardStatsSchema = z.object({
  total_monitors: z.number(),
  active_monitors: z.number(),
  total_alerts: z.number(),
  unread_alerts: z.number(),
  recent_changes: z.array(z.any()).optional(),
});

export type DashboardStats = z.infer<typeof DashboardStatsSchema>;

// Share schema
export const ShareSchema = z.object({
  share_id: z.string(),
  report_id: z.string(),
  shared_by: z.string(),
  permission: z.enum(['view', 'comment', 'edit', 'admin']),
  expires_at: z.string().optional(),
  share_type: z.enum(['link', 'email', 'user']),
  shared_with: z.string().optional(),
  share_token: z.string().optional(),
  public_url: z.string().optional(),
  created_at: z.string(),
  last_accessed: z.string().optional(),
  access_count: z.number(),
  active: z.boolean(),
});

export type Share = z.infer<typeof ShareSchema>;

// Share list response
export const ShareListResponseSchema = z.object({
  report_id: z.string(),
  shares: z.array(ShareSchema),
  total: z.number(),
});

export type ShareListResponse = z.infer<typeof ShareListResponseSchema>;

// Share analytics schema
export const ShareAnalyticsSchema = z.object({
  share_id: z.string(),
  total_views: z.number(),
  unique_views: z.number(),
  access_timeline: z.array(z.any()).optional(),
  referrers: z.array(z.any()).optional(),
  geographic_data: z.array(z.any()).optional(),
});

export type ShareAnalytics = z.infer<typeof ShareAnalyticsSchema>;

// Comment list response (using existing CommentSchema)
const CommentThreadSchema = z.object({
  comment: CommentSchema,
  replies: z.array(CommentSchema).optional(),
  total_replies: z.number().optional(),
});

export const CommentListResponseSchema = z.object({
  report_id: z.string(),
  comments: z.array(CommentThreadSchema),
  total: z.number(),
});

export type CommentListResponse = z.infer<typeof CommentListResponseSchema>;

// Version history response - matches backend VersionHistory model
export const VersionHistoryResponseSchema = z
  .object({
    report_id: z.string(),
    versions: z.array(VersionSchema),
    current_version: z.union([z.string(), z.null()]).optional(),
    total_versions: z.number(),
  })
  .transform((data) => ({
    ...data,
    // Mark the current version
    versions: data.versions.map((v) => ({
      ...v,
      is_current: v.id === data.current_version,
    })),
  }));

export type VersionHistoryResponse = z.infer<typeof VersionHistoryResponseSchema>;

// Version diff schema
export const VersionDiffSchema = z.object({
  from_version: z.string(),
  to_version: z.string(),
  changes: z.record(z.string(), z.any()),
  summary: z.string(),
});

export type VersionDiff = z.infer<typeof VersionDiffSchema>;

// Notification schema
export const NotificationSchema = z.object({
  id: z.string(),
  type: z.string(),
  title: z.string(),
  description: z.string(),
  read: z.boolean(),
  created_at: z.string(),
  link: z.string().optional(),
  metadata: z.record(z.string(), z.any()).optional(),
});

export type Notification = z.infer<typeof NotificationSchema>;

// Notification list response
export const NotificationListResponseSchema = z.object({
  notifications: z.array(NotificationSchema),
  count: z.number(),
  unread_count: z.number().optional(),
});

export type NotificationListResponse = z.infer<typeof NotificationListResponseSchema>;

// Notification settings schema
export const NotificationSettingsSchema = z.object({
  in_app_enabled: z.boolean(),
  email_enabled: z.boolean(),
  email_frequency: z.enum(['instant', 'daily', 'weekly']),
  new_comments: z.boolean().optional(),
  comment_replies: z.boolean().optional(),
  report_shared: z.boolean().optional(),
  new_versions: z.boolean().optional(),
  analysis_complete: z.boolean().optional(),
});

export type NotificationSettings = z.infer<typeof NotificationSettingsSchema>;

// Template schema
export const TemplateSchema = z.object({
  template_id: z.string(),
  name: z.string(),
  category: z.string(),
  description: z.string().optional(),
  framework_type: z.string(),
  prompt_template: z.string().optional(),
  structure: z.record(z.string(), z.any()).optional(),
  examples: z.array(z.any()).optional(),
  created_by: z.string(),
  created_at: z.string(),
  updated_at: z.string().optional(),
  visibility: z.enum(['private', 'public', 'shared']),
  usage_count: z.number().optional(),
  rating: z.number().optional(),
  tags: z.array(z.string()).optional(),
  industry: z.string().optional(),
  region: z.string().optional(),
});

export type Template = z.infer<typeof TemplateSchema>;

// Template library response
export const TemplateLibraryResponseSchema = z.object({
  templates: z.array(TemplateSchema),
  total: z.number(),
  page: z.number().optional(),
  page_size: z.number().optional(),
});

export type TemplateLibraryResponse = z.infer<typeof TemplateLibraryResponseSchema>;

// User profile schema
export const UserProfileSchema = z.object({
  user_id: z.string(),
  email: z.string().email(),
  name: z.string().optional(),
  company: z.string().optional(),
  job_title: z.string().optional(),
  created_at: z.string().optional(),
  subscription_tier: z.string().optional(),
});

export type UserProfile = z.infer<typeof UserProfileSchema>;

// Login response schema
export const LoginResponseSchema = z.object({
  access_token: z.string(),
  token_type: z.string(),
  user: z.object({
    user_id: z.string(),
    email: z.string(),
    name: z.string().optional(),
    subscription_tier: z.string().optional(),
  }),
});

export type LoginResponse = z.infer<typeof LoginResponseSchema>;

// Job list response schema
export const JobListResponseSchema = z.object({
  jobs: z.array(JobStatusSchema),
  total: z.number().optional(),
  page: z.number().optional(),
  limit: z.number().optional(),
});

export type JobListResponse = z.infer<typeof JobListResponseSchema>;

// Async analysis response schema
export const AsyncAnalysisResponseSchema = z.object({
  job_id: z.string(),
  status: z.string(),
  message: z.string().optional(),
});

export type AsyncAnalysisResponse = z.infer<typeof AsyncAnalysisResponseSchema>;

// Delete response schema
export const DeleteResponseSchema = z.object({
  success: z.boolean(),
  message: z.string().optional(),
});

export type DeleteResponse = z.infer<typeof DeleteResponseSchema>;
