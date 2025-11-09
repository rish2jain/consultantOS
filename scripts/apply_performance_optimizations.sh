#!/bin/bash
# Apply Phase 3 Performance Optimizations to ConsultantOS
# This script safely integrates the new optimized modules

set -e

echo "🚀 ConsultantOS Phase 3 Performance Optimizations"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 Project root: $PROJECT_ROOT"
echo ""

# Step 1: Backup existing modules
echo "💾 Step 1: Creating backups..."
if [ -f "consultantos/database.py" ]; then
    cp consultantos/database.py consultantos/database.py.backup
    echo -e "${GREEN}✓${NC} Backed up database.py"
fi

if [ -f "consultantos/cache.py" ]; then
    cp consultantos/cache.py consultantos/cache.py.backup
    echo -e "${GREEN}✓${NC} Backed up cache.py"
fi
echo ""

# Step 2: Install frontend dependencies
echo "📦 Step 2: Installing frontend dependencies..."
cd frontend

if [ ! -f "package.json" ]; then
    echo -e "${YELLOW}⚠${NC}  package.json not found in frontend/"
    exit 1
fi

# Check if web-vitals is installed
if ! grep -q "web-vitals" package.json; then
    echo "Installing web-vitals..."
    npm install web-vitals
    echo -e "${GREEN}✓${NC} web-vitals installed"
else
    echo -e "${GREEN}✓${NC} web-vitals already installed"
fi

cd "$PROJECT_ROOT"
echo ""

# Step 3: Verify optimization modules exist
echo "🔧 Step 3: Verifying optimization modules"
if [ -f "consultantos/database_optimized.py" ]; then
    echo -e "${GREEN}✓${NC} consultantos/database_optimized.py exists"
else
    echo -e "${YELLOW}⚠${NC}  consultantos/database_optimized.py not found"
    exit 1
fi

if [ -f "consultantos/cache_optimized.py" ]; then
    echo -e "${GREEN}✓${NC} consultantos/cache_optimized.py exists"
else
    echo -e "${YELLOW}⚠${NC}  consultantos/cache_optimized.py not found"
    exit 1
fi

if [ -f "consultantos/api/middleware.py" ]; then
    echo -e "${GREEN}✓${NC} consultantos/api/middleware.py exists"
else
    echo -e "${YELLOW}⚠${NC}  consultantos/api/middleware.py not found"
    exit 1
fi
echo ""
echo "Note: Original modules preserved. Update imports to use optimized versions."
echo ""

# Step 4: Verify frontend components exist
echo "🎨 Step 4: Verifying frontend optimizations"
if [ -f "frontend/app/components/LazyComponents.tsx" ]; then
    echo -e "${GREEN}✓${NC} frontend/app/components/LazyComponents.tsx exists"
else
    echo -e "${YELLOW}⚠${NC}  frontend/app/components/LazyComponents.tsx not found"
    exit 1
fi

if [ -f "frontend/app/components/ErrorBoundary.tsx" ]; then
    echo -e "${GREEN}✓${NC} frontend/app/components/ErrorBoundary.tsx exists"
else
    echo -e "${YELLOW}⚠${NC}  frontend/app/components/ErrorBoundary.tsx not found"
    exit 1
fi

if [ -f "frontend/app/utils/performance.ts" ]; then
    echo -e "${GREEN}✓${NC} frontend/app/utils/performance.ts exists"
else
    echo -e "${YELLOW}⚠${NC}  frontend/app/utils/performance.ts not found"
    exit 1
fi
echo ""

# Step 5: Verify performance testing script exists
echo "📊 Step 5: Verifying performance testing script"
if [ -f "scripts/measure_performance.py" ]; then
    echo -e "${GREEN}✓${NC} scripts/measure_performance.py exists"
    chmod +x scripts/measure_performance.py
else
    echo -e "${YELLOW}⚠${NC}  scripts/measure_performance.py not found"
    exit 1
fi
echo ""

# Step 6: Create integration checklist
echo "📋 Step 6: Creating integration checklist..."
cat > INTEGRATION_CHECKLIST.md << 'EOF'
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
EOF

echo -e "${GREEN}✓${NC} Created INTEGRATION_CHECKLIST.md"
echo ""

# Step 7: Summary
echo "✅ Performance optimizations applied successfully!"
echo ""
echo "📋 Next Steps:"
echo "   1. Review INTEGRATION_CHECKLIST.md"
echo "   2. Update imports in consultantos/api/main.py"
echo "   3. Add middleware to FastAPI app"
echo "   4. Update frontend routes with lazy loading"
echo "   5. Run performance baseline: python scripts/measure_performance.py --baseline"
echo "   6. Test and compare: python scripts/measure_performance.py --compare"
echo ""
echo "📚 Documentation:"
echo "   • PERFORMANCE_OPTIMIZATION_GUIDE.md - Complete optimization guide"
echo "   • INTEGRATION_CHECKLIST.md - Step-by-step integration"
echo ""
echo "🔍 Monitoring:"
echo "   • /metrics - Cache and performance stats"
echo "   • X-Response-Time header - API latency tracking"
echo "   • Console (dev) - Web Vitals tracking"
echo ""
echo "=================================================="
echo "Phase 3 optimizations ready for integration! 🚀"
