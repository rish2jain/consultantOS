# Quick Start: Adding Zod Validation to ConsultantOS

This is a step-by-step guide to add Zod runtime validation to catch API contract mismatches immediately.

## Step 1: Install Zod

```bash
cd frontend
npm install zod
```

## Step 2: Create API Schemas

Create `frontend/lib/api-schemas.ts`:

```typescript
import { z } from 'zod';

// Report schema matching backend Pydantic model
export const ReportSchema = z.object({
  report_id: z.string(),
  company: z.string(),
  industry: z.string().optional(),
  frameworks: z.array(z.string()),
  created_at: z.string(),
  status: z.enum(['completed', 'processing', 'failed', 'partial_success']),
  confidence_score: z.number().min(0).max(1).optional(),
  user_id: z.string().optional(),
  pdf_url: z.string().url().optional(),
  execution_time_seconds: z.number().optional(),
}).transform((data) => ({
  // Transform to frontend format - map report_id to id
  id: data.report_id,
  ...data,
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
  frameworks: z.array(z.enum(['porter', 'swot', 'pestel', 'blue_ocean'])),
  depth: z.enum(['quick', 'standard', 'deep']).optional(),
  additional_context: z.string().optional(),
  region: z.string().optional(),
});

export type AnalysisRequest = z.infer<typeof AnalysisRequestSchema>;
```

## Step 3: Update API Client

Update `frontend/lib/api.ts` to use validation:

```typescript
import { ReportSchema, ReportsListResponseSchema } from './api-schemas';

export const analysisAPI = {
  // ... existing code ...

  listReports: async (params?: {...}) => {
    const queryParams = new URLSearchParams();
    // ... build query ...
    
    const response = await apiRequest(`/reports${query ? `?${query}` : ''}`);
    
    // Validate response
    try {
      const validated = ReportsListResponseSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('API response validation failed:', error.errors);
        // Log to Sentry in production
        if (typeof window !== 'undefined' && window.Sentry) {
          window.Sentry.captureException(error, {
            extra: {
              response,
              errors: error.errors,
            },
          });
        }
        // Return partial data with warning
        return {
          reports: response.reports || [],
          total: response.total || 0,
        };
      }
      throw error;
    }
  },

  getReport: async (reportId: string) => {
    const response = await apiRequest(`/reports/${reportId}`);
    
    // Validate and transform
    try {
      const validated = ReportSchema.parse(response);
      return validated;
    } catch (error) {
      if (error instanceof z.ZodError) {
        console.error('Report validation failed:', error.errors);
        // Handle gracefully
      }
      throw error;
    }
  },
};
```

## Step 4: Development Mode Validation

Add development-only strict validation:

```typescript
// frontend/lib/api.ts
const isDevelopment = process.env.NODE_ENV === 'development';

export const analysisAPI = {
  listReports: async (params?: {...}) => {
    const response = await apiRequest(`/reports${query}`);
    
    if (isDevelopment) {
      // Strict validation in development
      return ReportsListResponseSchema.parse(response);
    } else {
      // Graceful validation in production
      return ReportsListResponseSchema.safeParse(response).data || response;
    }
  },
};
```

## Benefits

✅ **Immediate**: Catches `report_id` vs `id` mismatches  
✅ **Runtime Safety**: Validates API responses match expected structure  
✅ **Type Inference**: TypeScript types from Zod schemas  
✅ **Transformation**: Can map fields during validation  
✅ **Error Reporting**: Clear error messages for mismatches  

## Next Steps

1. Add Zod validation to all API endpoints
2. Set up OpenAPI type generation for long-term type safety
3. Add contract testing with Pact
4. Enable TypeScript strict mode

See `docs/API_CONTRACT_TESTING_GUIDE.md` for full implementation plan.

