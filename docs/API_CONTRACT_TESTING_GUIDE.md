# API Contract Testing & Type Safety Guide

This guide outlines tools, approaches, and libraries to proactively detect API/UX contract mismatches, type errors, and integration issues in ConsultantOS.

## Problem Statement

Common issues we've encountered:

- **API Response Mismatches**: Backend returns `report_id`, frontend expects `id`
- **Type Mismatches**: Props passed as strings instead of booleans (`loading` vs `isLoading`)
- **Missing Fields**: API responses missing expected fields
- **Circular Dependencies**: Import issues causing runtime failures
- **Invalid Props**: React props that don't match component interfaces

## Recommended Solutions

### 1. Type-Safe API Client Generation

#### Option A: OpenAPI TypeScript Code Generation

**Tools:**

- **openapi-typescript-codegen** - Generates TypeScript types and clients from OpenAPI spec
- **orval** - More advanced, supports React Query hooks
- **openapi-typescript** - Just types, no client code

**Implementation:**

```bash
# Install
npm install -D openapi-typescript-codegen

# Generate types from FastAPI's auto-generated OpenAPI spec
npx openapi-typescript-codegen \
  --input http://localhost:8080/openapi.json \
  --output frontend/lib/api-generated \
  --client axios
```

**Benefits:**

- Automatic type generation from FastAPI's OpenAPI schema
- Compile-time type checking
- Catches field name mismatches (`report_id` vs `id`)
- Auto-completion in IDE

**FastAPI Integration:**
FastAPI automatically generates OpenAPI schema at `/openapi.json`. We can:

1. Export schema during build
2. Generate TypeScript types in CI/CD
3. Fail builds if types don't match

#### Option B: tRPC (Type-Safe RPC)

**Best for:** New projects or major refactors

- End-to-end type safety
- No code generation needed
- Real-time type checking

**Trade-off:** Requires significant refactoring of existing REST API

### 2. Runtime Validation with Zod

**Current State:** Backend uses Pydantic, frontend has no validation

**Solution:** Add Zod schemas to frontend API client

```typescript
// frontend/lib/api-schemas.ts
import { z } from 'zod';

export const ReportSchema = z.object({
  report_id: z.string(),
  company: z.string(),
  industry: z.string(),
  frameworks: z.array(z.string()),
  created_at: z.string(),
  status: z.enum(['completed', 'processing', 'failed']),
  confidence_score: z.number().optional(),
});

export const ReportsListResponseSchema = z.object({
  reports: z.array(ReportSchema),
  total: z.number(),
  page: z.number(),
  limit: z.number(),
});

// Usage in api.ts
import { ReportSchema, ReportsListResponseSchema } from './api-schemas';

export const analysisAPI = {
  listReports: async (params?: {...}) => {
    const response = await apiRequest(`/reports${query}`);
    // Validate at runtime
    const validated = ReportsListResponseSchema.parse(response);
    return validated;
  },
};
```

**Benefits:**

- Catches API contract violations at runtime
- Provides clear error messages
- Can transform data (e.g., `report_id` → `id`) during validation
- Works with TypeScript for type inference

**Integration:**

- Add Zod validation layer in `frontend/lib/api.ts`
- Log validation errors to Sentry/monitoring
- Fail fast in development, graceful degradation in production

### 3. Contract Testing with Pact

**Tool:** Pact (https://pact.io)

**Purpose:** Verify API contracts between frontend and backend

**Implementation:**

```typescript
// frontend/tests/contracts/reports.contract.test.ts
import { Pact } from "@pact-foundation/pact";

describe("Reports API Contract", () => {
  it("should return reports with correct structure", async () => {
    await provider.addInteraction({
      state: "reports exist",
      uponReceiving: "a request for reports",
      withRequest: {
        method: "GET",
        path: "/reports",
      },
      willRespondWith: {
        status: 200,
        body: {
          reports: [
            {
              report_id: like("Tesla_20240101120000"),
              company: like("Tesla"),
              industry: like("Electric Vehicles"),
              frameworks: eachLike("porter"),
            },
          ],
        },
      },
    });

    const response = await api.analysis.listReports();
    expect(response.reports[0]).toHaveProperty("report_id");
  });
});
```

**Benefits:**

- Detects breaking changes before deployment
- Documents expected API contracts
- Can run in CI/CD pipeline
- Supports consumer-driven contracts

### 4. Static Analysis Tools

#### ESLint with TypeScript

**Already in use, but can enhance:**

```json
// frontend/.eslintrc.json
{
  "rules": {
    "@typescript-eslint/no-unsafe-assignment": "error",
    "@typescript-eslint/no-unsafe-member-access": "error",
    "@typescript-eslint/no-unsafe-call": "error",
    "react/prop-types": "error" // Even with TypeScript
  }
}
```

#### React Prop Validation

**Tool:** `eslint-plugin-react` with prop-types checking

```typescript
// Add runtime prop validation even with TypeScript
import PropTypes from 'prop-types';

export const Button: React.FC<ButtonProps> = ({ ... }) => {
  // Component code
};

Button.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  variant: PropTypes.oneOf(['primary', 'secondary', 'outline']),
};
```

### 5. API Schema Validation Middleware

**Backend Enhancement:** Add response validation middleware

```python
# consultantos/api/middleware.py
from fastapi import Request
from fastapi.responses import JSONResponse
import json

async def validate_response_schema(request: Request, call_next):
    """Validate API responses match OpenAPI schema"""
    response = await call_next(request)

    # In development, validate responses
    if settings.environment == "development":
        # Check if response matches expected schema
        # Log warnings for mismatches
        pass

    return response
```

### 6. Integration Testing

**Tool:** Playwright or Cypress for E2E testing

**Focus Areas:**

- API calls from frontend
- Response handling
- Error states
- Loading states

```typescript
// frontend/tests/e2e/reports.spec.ts
test("delete report uses correct ID", async ({ page }) => {
  await page.goto("/reports");

  // Intercept API calls
  await page.route("**/reports/*", (route) => {
    const url = route.request().url();
    const reportId = url.split("/reports/")[1];

    // Verify correct ID format (not "report-0")
    expect(reportId).toMatch(/^[A-Za-z0-9_]+$/);
    expect(reportId).not.toMatch(/^report-\d+$/);
  });

  await page.click('[data-testid="delete-button"]');
});
```

### 7. TypeScript Strict Mode

**Enable in `frontend/tsconfig.json`:**

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

**Benefits:**

- Catches type mismatches at compile time
- Prevents `undefined`/`null` issues
- Forces explicit type handling

### 8. API Response Transformation Layer

**Current Issue:** Backend uses `report_id`, frontend expects `id`

**Solution:** Centralized transformation in API client

```typescript
// frontend/lib/api-transformers.ts
export function transformReport(apiReport: ApiReport): Report {
  return {
    id: apiReport.report_id, // Map report_id to id
    ...apiReport,
  };
}

// Use in api.ts
export const analysisAPI = {
  listReports: async () => {
    const response = await apiRequest("/reports");
    return {
      ...response,
      reports: response.reports.map(transformReport),
    };
  },
};
```

### 9. Monitoring & Alerting

**Tools:**

- **Sentry** - Already integrated, can add API contract violation tracking
- **Datadog** - Full-stack monitoring
- **Custom logging** - Track API response shape mismatches

**Implementation:**

```typescript
// frontend/lib/api.ts
try {
  const response = await apiRequest("/reports");
  const validated = ReportsListResponseSchema.safeParse(response);

  if (!validated.success) {
    // Log to Sentry
    Sentry.captureException(new Error("API contract violation"), {
      extra: {
        errors: validated.error.errors,
        response: response,
      },
    });
  }
} catch (error) {
  // Handle error
}
```

### 10. Development-Time Tools

#### React DevTools Profiler

- Identify prop drilling issues
- Detect unnecessary re-renders from API changes

#### Network Tab Monitoring

- Browser DevTools to inspect API responses
- Verify response structure matches expectations

#### TypeScript Language Server

- Real-time type checking in IDE
- Catches mismatches as you type

## Recommended Implementation Plan

### Phase 1: Quick Wins (1-2 days)

1. ✅ Add Zod validation to API client
2. ✅ Enable TypeScript strict mode
3. ✅ Add response transformation layer
4. ✅ Enhance ESLint rules

### Phase 2: Type Generation (3-5 days)

1. Set up OpenAPI schema export from FastAPI
2. Generate TypeScript types in CI/CD
3. Update API client to use generated types
4. Add validation layer with Zod

### Phase 3: Contract Testing (1 week)

1. Set up Pact for contract testing
2. Write consumer contracts for key endpoints
3. Integrate into CI/CD pipeline
4. Add contract tests for critical flows

### Phase 4: Monitoring (Ongoing)

1. Add API contract violation tracking to Sentry
2. Set up alerts for schema mismatches
3. Dashboard for API health metrics

## Tools Comparison

| Tool                           | Type               | Best For              | Effort | Impact |
| ------------------------------ | ------------------ | --------------------- | ------ | ------ |
| **Zod**                        | Runtime Validation | Immediate protection  | Low    | High   |
| **openapi-typescript-codegen** | Type Generation    | Long-term type safety | Medium | High   |
| **Pact**                       | Contract Testing   | CI/CD integration     | High   | Medium |
| **TypeScript Strict**          | Compile-time       | Type safety           | Low    | High   |
| **ESLint**                     | Static Analysis    | Code quality          | Low    | Medium |
| **Playwright**                 | E2E Testing        | Integration testing   | Medium | High   |

## Quick Start: Zod Validation

**Immediate action you can take:**

```bash
cd frontend
npm install zod
```

```typescript
// frontend/lib/api-schemas.ts
import { z } from "zod";

// Define schemas matching backend Pydantic models
export const ReportSchema = z
  .object({
    report_id: z.string(),
    company: z.string(),
    industry: z.string().optional(),
    frameworks: z.array(z.string()),
    created_at: z.string(),
    status: z.enum(["completed", "processing", "failed", "partial_success"]),
    confidence_score: z.number().min(0).max(1).optional(),
    user_id: z.string().optional(),
  })
  .transform((data) => ({
    // Transform to frontend format
    id: data.report_id,
    ...data,
  }));

export type Report = z.infer<typeof ReportSchema>;
```

This would have caught the `report_id` vs `id` issue immediately!

## Additional Resources

- [Zod Documentation](https://zod.dev/)
- [OpenAPI TypeScript Codegen](https://github.com/ferdikoomen/openapi-typescript-codegen)
- [Pact Documentation](https://docs.pact.io/)
- [FastAPI OpenAPI Export](https://fastapi.tiangolo.com/advanced/openapi-callbacks/)
- [TypeScript Strict Mode](https://www.typescriptlang.org/tsconfig#strict)

## Conclusion

The most impactful immediate actions:

1. **Add Zod validation** - Catches issues at runtime
2. **Enable TypeScript strict mode** - Catches issues at compile time
3. **Add response transformation layer** - Handles field name mismatches
4. **Generate types from OpenAPI** - Long-term type safety

These tools work together to create multiple layers of protection against API/UX contract mismatches.
