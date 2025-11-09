# Phase 3 Performance Optimizations - Integration Checklist

## Backend Integration

### 1. Update Database Service (consultantos/api/main.py)

- [ ] Replace import: `from consultantos.database_optimized import get_db_service`
- [ ] Test batch operations: `db.get_reports_batch(report_ids)`
- [ ] Verify connection pooling in logs
- [ ] Monitor query performance

### 2. Update Cache Service

- [ ] Replace import: `from consultantos.cache_optimized import cache_key, cached_analysis, CacheType`
- [ ] Update cache decorators with `CacheType` enums
- [ ] Monitor cache hit rates at `/metrics`
- [ ] Verify TTL behavior for different cache types

### 3. Add API Middleware (consultantos/api/main.py)

```python
from consultantos.api.middleware import (
    CachingMiddleware,
    RequestTimingMiddleware
)

# Add after CORS middleware
app.add_middleware(RequestTimingMiddleware)
app.add_middleware(CachingMiddleware)
```

- [ ] Add middleware to FastAPI app
- [ ] Test ETag support with curl: `curl -H "If-None-Match: <etag>" http://localhost:8080/health`
- [ ] Verify `X-Response-Time` headers in responses
- [ ] Check slow request logging

## Frontend Integration

### 1. Update Root Layout (frontend/app/layout.tsx)

```typescript
import ErrorBoundary from './components/ErrorBoundary';
import { initPerformanceMonitoring } from './utils/performance';

export default function RootLayout({ children }) {
  useEffect(() => {
    initPerformanceMonitoring();
  }, []);

  return (
    <ErrorBoundary>
      {children}
    </ErrorBoundary>
  );
}
```

- [ ] Add ErrorBoundary wrapper
- [ ] Initialize performance monitoring
- [ ] Test error boundary with intentional error
- [ ] Verify Web Vitals tracking in console (dev mode)

### 2. Implement Lazy Loading (frontend/app/*/page.tsx)

```typescript
import { LazyWrapper, AnalysisPage } from '../components/LazyComponents';

export default function AnalysisRoute() {
  return (
    <LazyWrapper>
      <AnalysisPage />
    </LazyWrapper>
  );
}
```

- [ ] Update analysis route
- [ ] Update reports route
- [ ] Update templates route
- [ ] Update jobs route
- [ ] Update profile route

### 3. Build and Test

```bash
cd frontend
npm run build
npm run start
```

- [ ] Build succeeds without errors
- [ ] Bundle size reduced (check `.next/static/chunks/`)
- [ ] Route transitions work smoothly
- [ ] Loading states appear correctly

## Performance Testing

### 1. Create Baseline

```bash
# Start API server
python main.py

# In another terminal, create baseline
python scripts/measure_performance.py --baseline
```

- [ ] API server running
- [ ] Baseline created at `performance_reports/baseline.json`
- [ ] Review baseline metrics

### 2. Run Performance Tests

```bash
python scripts/measure_performance.py --compare
```

- [ ] API response times <500ms (p95)
- [ ] Cache hit rate >80%
- [ ] Frontend bundle <400KB (initial)
- [ ] All tests pass

## Monitoring

### 1. Check Metrics Endpoint

```bash
curl http://localhost:8080/metrics
```

- [ ] Cache stats available
- [ ] Hit rate tracking working
- [ ] Performance metrics present

### 2. Verify Logs

- [ ] Connection pooling initialized
- [ ] Cache hits/misses logged
- [ ] Slow requests logged (if >1s)
- [ ] No errors in startup

## Rollback Plan

If issues occur:

1. Restore backups:
```bash
cp consultantos/database.py.backup consultantos/database.py
cp consultantos/cache.py.backup consultantos/cache.py
```

2. Remove middleware from main.py

3. Revert frontend changes:
```bash
git checkout frontend/app/layout.tsx
git checkout frontend/app/*/page.tsx
```

4. Rebuild frontend:
```bash
cd frontend
npm run build
```

## Success Criteria

- [x] All backend tests pass
- [x] All frontend builds succeed
- [ ] API p95 response time <500ms
- [ ] Cache hit rate >80%
- [ ] Frontend bundle reduced by >50%
- [ ] Initial page load <2 seconds
- [ ] All Core Web Vitals in "Good" range
- [ ] No production errors

## Notes

- Original modules preserved as `.backup` files
- Optimized modules created alongside originals
- Can switch back by reverting imports
- Monitor performance metrics for 24 hours before declaring success
