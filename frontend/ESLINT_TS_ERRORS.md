# ESLint and TypeScript Errors

This file documents the current ESLint and TypeScript errors that need to be fixed before production deployment.

**Note**: The Next.js config is set to ignore these errors in non-production environments (`NODE_ENV !== 'production'` or `DEV_DEMO=true`), but production builds will fail on these errors.

## ESLint Errors

### app/analysis/page.tsx
- Line 23:10 - `api` is defined but never used (@typescript-eslint/no-unused-vars)
- Line 51:10 - `reportId` is assigned a value but never used (@typescript-eslint/no-unused-vars)
- Line 79:42 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)
- Line 220:73 - `'` can be escaped with `&apos;`, `&lsquo;`, `&#39;`, `&rsquo;` (react/no-unescaped-entities)
- Line 392:61 - `'` can be escaped with `&apos;`, `&lsquo;`, `&#39;`, `&rsquo;` (react/no-unescaped-entities)

### app/analytics/page.tsx
- Line 20:3 - `FunnelChart` is defined but never used (@typescript-eslint/no-unused-vars)
- Line 21:3 - `Funnel` is defined but never used (@typescript-eslint/no-unused-vars)
- Line 22:3 - `LabelList` is defined but never used (@typescript-eslint/no-unused-vars)
- Line 25:3 - `TrendingUp` is defined but never used (@typescript-eslint/no-unused-vars)
- Line 26:3 - `TrendingDown` is defined but never used (@typescript-eslint/no-unused-vars)
- Line 28:3 - `Users` is defined but never used (@typescript-eslint/no-unused-vars)
- Line 32:3 - `CheckCircle` is defined but never used (@typescript-eslint/no-unused-vars)
- Line 33:3 - `XCircle` is defined but never used (@typescript-eslint/no-unused-vars)
- Line 35:3 - `Calendar` is defined but never used (@typescript-eslint/no-unused-vars)
- Line 37:3 - `BarChart3` is defined but never used (@typescript-eslint/no-unused-vars)
- Line 38:15 - `PieChartIcon` is defined but never used (@typescript-eslint/no-unused-vars)
- Line 39:16 - `LineChartIcon` is defined but never used (@typescript-eslint/no-unused-vars)
- Line 137:6 - React Hook useEffect has a missing dependency: 'loadAnalytics' (react-hooks/exhaustive-deps) [WARNING]

### app/components/AnalysisRequestForm.tsx
- Line 63:28 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)
- Line 171:22 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)
- Line 206:21 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)
- Line 216:24 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)
- Line 242:71 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)

### app/components/AsyncAnalysisForm.tsx
- Line 186:17 - `frameworks` is assigned a value but never used (@typescript-eslint/no-unused-vars)
- Line 235:29 - `company` is assigned a value but never used (@typescript-eslint/no-unused-vars)
- Line 278:29 - `industry` is assigned a value but never used (@typescript-eslint/no-unused-vars)

### app/components/CommentCard.tsx
- Line 4:40 - `User` is defined but never used (@typescript-eslint/no-unused-vars)

### app/components/CommentNotifications.tsx
- Line 115:6 - React Hook useEffect has a missing dependency: 'fetchNotificationsData' (react-hooks/exhaustive-deps) [WARNING]
- Line 320:27 - `"` can be escaped with `&quot;`, `&ldquo;`, `&#34;`, `&rdquo;` (react/no-unescaped-entities)
- Line 320:55 - `"` can be escaped with `&quot;`, `&ldquo;`, `&#34;`, `&rdquo;` (react/no-unescaped-entities)

### app/components/CommentThread.tsx
- Line 3:27 - `useEffect` is defined but never used (@typescript-eslint/no-unused-vars)

### app/components/CompetitiveLandscape.tsx
- Line 97:10 - `selectedCompetitor` is assigned a value but never used (@typescript-eslint/no-unused-vars)
- Line 220:31 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)
- Line 230:29 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)
- Line 232:23 - `pointIndex` is assigned a value but never used (@typescript-eslint/no-unused-vars)

### app/components/DataTable.tsx
- Line 22:20 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)
- Line 24:26 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)
- Line 122:20 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)

### app/components/DataTableExample.tsx
- Line 9:3 - `TableSort` is defined but never used (@typescript-eslint/no-unused-vars)
- Line 73:11 - `sortConfig` is assigned a value but never used (@typescript-eslint/no-unused-vars)
- Line 73:23 - `handleSort` is assigned a value but never used (@typescript-eslint/no-unused-vars)
- Line 87:5 - `activeFilterCount` is assigned a value but never used (@typescript-eslint/no-unused-vars)
- Line 103:9 - The 'columns' array makes the dependencies of useMemo Hook change on every render (react-hooks/exhaustive-deps) [WARNING]
- Line 155:46 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)

### app/components/EmailVerification.tsx
- Line 94:13 - `data` is assigned a value but never used (@typescript-eslint/no-unused-vars)
- Line 152:13 - `data` is assigned a value but never used (@typescript-eslint/no-unused-vars)
- Line 242:19 - `'` can be escaped with `&apos;`, `&lsquo;`, `&#39;`, `&rsquo;` (react/no-unescaped-entities)

### app/components/ErrorBoundary.tsx
- Line 20:15 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)

### app/components/ForecastChart.tsx
- Line 5:3 - `LineChart` is defined but never used (@typescript-eslint/no-unused-vars)
- Line 63:6 - React Hook useEffect has a missing dependency: 'loadForecast' (react-hooks/exhaustive-deps) [WARNING]

### app/components/IndustrySelector.tsx
- Line 266:46 - `"` can be escaped with `&quot;`, `&ldquo;`, `&#34;`, `&rdquo;` (react/no-unescaped-entities)
- Line 266:60 - `"` can be escaped with `&quot;`, `&ldquo;`, `&#34;`, `&rdquo;` (react/no-unescaped-entities)

### app/components/Input.tsx
- Line 54:34 - React Hook "React.useId" is called conditionally (react-hooks/rules-of-hooks)

### app/components/InteractiveDashboard.tsx
- Line 40:9 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)
- Line 71:11 - `lastMessage` is assigned a value but never used (@typescript-eslint/no-unused-vars)
- Line 71:37 - `reconnect` is assigned a value but never used (@typescript-eslint/no-unused-vars)
- Line 98:6 - React Hook useEffect has a missing dependency: 'fetchDashboard' (react-hooks/exhaustive-deps) [WARNING]
- Line 128:39 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)
- Line 322:20 - `"` can be escaped with `&quot;`, `&ldquo;`, `&#34;`, `&rdquo;` (react/no-unescaped-entities)
- Line 322:35 - `"` can be escaped with `&quot;`, `&ldquo;`, `&#34;`, `&rdquo;` (react/no-unescaped-entities)
- Line 327:41 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)
- Line 360:41 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)
- Line 381:32 - Unexpected any. Specify a different type (@typescript-eslint/no-explicit-any)

## TypeScript Errors

### app/components/analytics/FormulaBuilder.tsx
- Line 130:40 - error TS1382: Unexpected token. Did you mean `{'>'}` or `&gt;`?
- Line 130:44 - error TS1003: Identifier expected.
- Line 130:46 - error TS1382: Unexpected token. Did you mean `{'>'}` or `&gt;`?
- Line 130:51 - error TS1003: Identifier expected.

## Summary

- **Total ESLint Errors**: ~60+ errors across multiple files
- **Total TypeScript Errors**: 4 errors in FormulaBuilder.tsx
- **Common Issues**:
  - Unused variables/imports
  - `any` type usage (should be replaced with proper types)
  - Unescaped entities in JSX
  - Missing React Hook dependencies
  - Conditional React Hook calls

## Next Steps

1. Remove unused imports and variables
2. Replace `any` types with proper TypeScript types
3. Escape special characters in JSX strings
4. Fix React Hook dependency arrays
5. Fix conditional React Hook calls
6. Fix TypeScript syntax errors in FormulaBuilder.tsx

