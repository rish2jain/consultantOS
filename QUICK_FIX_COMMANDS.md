# Frontend Build Fix - Quick Commands Reference

**Project**: ConsultantOS Dashboard Frontend
**Status**: Build FAILED - 231 errors
**Estimated Fix Time**: 3-4 hours

---

## Critical Issues (Fix First - 15 Minutes)

### Issue 1: Fix FormulaBuilder.tsx:130

**Open file**:
```bash
cd /Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend
code app/components/analytics/FormulaBuilder.tsx
```

**Navigate to line 130** - Find this line:
```jsx
Supported: +, -, *, /, ^, %, >, <, >=, <=, ==, !=, SUM, AVG, MIN, MAX, COUNT, ABS, SQRT, ROUND
```

**Replace with**:
```jsx
Supported: +, -, *, /, ^, %, &gt;, &lt;, &gt;=, &lt;=, ==, !=, SUM, AVG, MIN, MAX, COUNT, ABS, SQRT, ROUND
```

**Or use sed** (if comfortable with command line):
```bash
sed -i '' 's/, >, </,  &gt;, &lt;/g' app/components/analytics/FormulaBuilder.tsx
sed -i '' 's/>=/&gt;=/g' app/components/analytics/FormulaBuilder.tsx
sed -i '' 's/<=/&lt;=/g' app/components/analytics/FormulaBuilder.tsx
```

---

### Issue 2: Fix Input.tsx:54

**Open file**:
```bash
code app/components/Input.tsx
```

**Navigate to line 54** - Find this section:
```tsx
const Input: React.FC<InputProps> = ({
  label,
  helperText,
  error,
  success,
  size = 'md',
  leftIcon,
  rightIcon,
  fullWidth = false,
  showCounter = false,
  maxLength,
  className = '',
  id,
  type = 'text',
  value,
  disabled,
  ...props
}) => {
  const [showPassword, setShowPassword] = React.useState(false);
  const inputId = id || `input-${React.useId()}`;  // ← LINE 54: CHANGE THIS
```

**Replace line 54 with**:
```tsx
  const [showPassword, setShowPassword] = React.useState(false);
  const generatedId = React.useId();  // Move hook call outside conditional
  const inputId = id || `input-${generatedId}`;
```

---

## Verify Critical Fixes

```bash
# Navigate to frontend directory
cd /Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend

# Run build to see if critical errors are fixed
npm run build

# Expected result: Error count drops from 231 to ~215
```

---

## Phase 2: Type Safety (102 Errors - 90 Minutes)

### Option A: Manual Approach (Recommended for first few)

1. Open build.log and find an `any` error
2. Open the file and line referenced
3. Replace `any` with proper type

**Example pattern**:
```tsx
// BROKEN
const handleClick = (e: any) => { }

// FIXED
import { MouseEventHandler } from 'react';
const handleClick: MouseEventHandler<HTMLButtonElement> = (e) => { }
```

### Option B: Bulk Fix (Use with caution)

```bash
# Find all 'any' types in TypeScript files
grep -r ": any" app/ lib/ --include="*.ts" --include="*.tsx" | wc -l

# See specific occurrences
grep -r ": any" app/ lib/ --include="*.ts" --include="*.tsx" | head -20
```

### Tools to Help:

**ESLint with --fix** (fixes some issues automatically):
```bash
npm run lint -- --fix
```

**VS Code Extension**: ESLint extension will highlight and suggest fixes

---

## Phase 3: Cleanup (50 Minutes)

### Remove Unused Imports/Variables

```bash
# Run lint fix to remove some automatically
npm run lint -- --fix

# For remaining issues, manually remove from:
# - Unused imports (check line numbers in error output)
# - Unused variables (add underscore prefix or remove)
```

**Example pattern**:
```tsx
// BROKEN - TrendingUp not used
import { TrendingUp, TrendingDown } from 'lucide-react';

// FIXED
import { TrendingDown } from 'lucide-react';
```

### Escape HTML Entities

Find and replace patterns:
```bash
# Find unescaped apostrophes
grep -r "[^&]'" app/ lib/ --include="*.tsx" | grep -v "&apos;"

# Find unescaped quotes
grep -r '[^&]"' app/ lib/ --include="*.tsx" | grep -v "&quot;"
```

**Fix manually or using find/replace in your editor**.

---

## Phase 4: Full Build Test

```bash
cd /Users/rish2jain/Documents/Hackathons/ConsultantOS/frontend

# Clean build (remove cache)
rm -rf .next

# Run full build
npm run build

# Expected: Build successful, exit code 0

# Verify standalone output exists
ls -la .next/standalone/

# Check what was generated
du -sh .next/
```

---

## Phase 5: Local Testing

```bash
# Test development server
npm run dev

# Server will start on http://localhost:3000
# Open in browser and test basic functionality

# For production testing (uses standalone output)
npm run build
npm start  # Uses .next/standalone

# Server will start on http://localhost:3000
```

---

## Phase 6: Docker Testing

```bash
# Build Docker image (from frontend directory)
docker build -t consultantos-frontend:latest .

# Run Docker image
docker run -p 3000:3000 consultantos-frontend:latest

# Test in browser: http://localhost:3000

# Check logs
docker logs [container-id]

# Stop container
docker stop [container-id]
```

---

## Phase 7: Cloud Run Deployment

### Update Environment Variables

```bash
# Set API URL for production
export NEXT_PUBLIC_API_URL=https://consultantos-api-187550875653.us-central1.run.app

# Or edit .env.local directly
nano .env.local
# Change: NEXT_PUBLIC_API_URL=https://consultantos-api-187550875653.us-central1.run.app
```

### Deploy to Cloud Run

```bash
# From project root directory
cd /Users/rish2jain/Documents/Hackathons/ConsultantOS

# Build and push to Artifact Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/consultantos-frontend:latest \
  --timeout=3600

# Deploy to Cloud Run
gcloud run deploy consultantos-frontend \
  --image gcr.io/YOUR_PROJECT_ID/consultantos-frontend:latest \
  --region us-central1 \
  --memory 1Gi \
  --cpu 1 \
  --allow-unauthenticated \
  --set-env-vars "NEXT_PUBLIC_API_URL=https://consultantos-api-187550875653.us-central1.run.app"

# View service URL
gcloud run services describe consultantos-frontend --region us-central1 --format='value(status.url)'
```

---

## Useful Diagnostic Commands

### Check Build Status
```bash
cd frontend
npm run build 2>&1 | tail -50  # Last 50 lines
npm run build 2>&1 | grep "Error:" | wc -l  # Count errors
```

### Check Specific Error
```bash
grep "Input.tsx" build.log
grep "FormulaBuilder" build.log
```

### List All Errors by Type
```bash
grep "Error:" build.log | sed 's/.*Error: //' | sort | uniq -c | sort -rn
```

### Find Files with Most Errors
```bash
grep "^\./" build.log | cut -d: -f1 | sort | uniq -c | sort -rn | head -10
```

### Check File Sizes
```bash
cd frontend
du -sh .next/
du -sh node_modules/
du -sh .next/standalone/
```

---

## Checklist for Successful Deployment

- [ ] Phase 1: Critical issues fixed (2 files)
- [ ] Phase 2: Type safety improved (102 `any` instances)
- [ ] Phase 3: Unused code removed (86+ instances)
- [ ] Phase 4: HTML entities escaped (25 instances)
- [ ] Phase 5: Build completes (0 errors)
- [ ] Phase 6: Local testing passes
- [ ] Phase 7: Docker image builds
- [ ] Phase 8: Docker image runs locally
- [ ] Phase 9: Cloud Run deployment
- [ ] Phase 10: Production testing

---

## Rollback Commands (If Something Goes Wrong)

```bash
# Revert all changes and start over
git checkout app/components/Input.tsx
git checkout app/components/analytics/FormulaBuilder.tsx

# Or for specific file
git diff app/components/Input.tsx  # See what changed
git checkout HEAD -- app/components/Input.tsx  # Revert

# Clean build artifacts
rm -rf .next node_modules
npm install
npm run build
```

---

## Getting Help

**For specific errors**: Check `build.log` in project root

**For context**: Read FRONTEND_BUILD_ANALYSIS.md

**For deployment**: Read CLOUD_RUN_DEPLOYMENT_READINESS.md

**For general overview**: Read FRONTEND_BUILD_TEST_INDEX.md

---

## Time Estimates

| Phase | Task | Time |
|-------|------|------|
| 1 | Fix 2 critical issues | 15 min |
| 2 | Add TypeScript types | 90 min |
| 3 | Cleanup code | 50 min |
| 4 | Full build test | 5 min |
| 5 | Local testing | 10 min |
| 6 | Docker testing | 10 min |
| 7 | Cloud Run deploy | 10 min |
| **Total** | **All phases** | **3-4 hours** |

---

## Notes

- Save files after each fix
- Run build test after each phase
- Use version control (git) to track changes
- Test locally before deploying
- Keep build.log for reference

---

**Last Updated**: November 10, 2025
**Status**: Ready for implementation
