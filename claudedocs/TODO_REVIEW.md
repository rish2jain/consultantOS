# TODO Review - Comprehensive Analysis

**Date**: 2025-01-27  
**Total TODOs Found**: 20

## Summary by Priority

### 🔴 High Priority (Security & Core Features)
- **Security**: 3 TODOs (CSP hardening)
- **Authorization**: 1 TODO (dashboard ownership check)
- **Authentication**: 1 TODO (BFF pattern migration)

### 🟡 Medium Priority (Feature Implementation)
- **Notifications**: 6 TODOs (complete notification system)
- **Alerting**: 2 TODOs (Slack/webhook integration)
- **Analytics**: 1 TODO (job queue metrics)
- **Dashboard**: 1 TODO (PDF export)

### 🟢 Low Priority (Enhancements)
- **Alert Scoring**: 2 TODOs (adaptive scoring/thresholding)
- **Billing**: 1 TODO (team member counting)
- **Frontend**: 2 TODOs (share functionality, @ mentions)

---

## Detailed Review

### 🔴 HIGH PRIORITY

#### 1. Security - Content Security Policy (CSP) Hardening
**Location**: `docs/archive/implementation_reports/SECURITY_HARDENING_PHASE2.md:129-141`

**Current State**:
- Using `'unsafe-inline'` and `'unsafe-eval'` in CSP
- Weakens XSS protection
- Marked for Phase 3 migration

**TODOs**:
1. Migrate to nonce- or hash-based CSP (line 129)
2. Replace `'unsafe-inline'` with nonce-based CSP (line 140)
3. Replace `'unsafe-inline'` in style-src (line 141)

**Recommendation**:
- **Priority**: HIGH (Security vulnerability)
- **Effort**: Medium (requires frontend coordination)
- **Timeline**: Should be addressed in next security sprint
- **Dependencies**: Frontend must support nonce injection

**Action Items**:
1. Generate per-response nonces in middleware
2. Update frontend templates to inject nonces
3. Remove `eval()` usage or use strict CSP
4. Compute script hashes for inline scripts

---

#### 2. Authorization - Dashboard Ownership Check
**Location**: `consultantos/api/dashboard_endpoints.py:123`

**Current State**:
- Missing authorization check for dashboard access
- Users could potentially access other users' dashboards

**TODO**:
```python
# TODO: Add authorization check - verify user owns dashboard
```

**Recommendation**:
- **Priority**: HIGH (Security issue - data leakage risk)
- **Effort**: Low (simple ownership check)
- **Timeline**: Should be fixed immediately

**Action Items**:
1. Add `user_id` check before returning dashboard
2. Verify `dashboard.user_id == authenticated_user_id`
3. Return 403 if unauthorized

---

#### 3. Authentication - BFF Pattern Migration
**Location**: `frontend/lib/auth.ts:28`

**Current State**:
- Current auth uses API key pattern
- TODO suggests migrating to Backend-for-Frontend (BFF) with cookies

**TODO**:
```typescript
// TODO: Migrate to BFF pattern with secure cookie-based authentication
```

**Recommendation**:
- **Priority**: HIGH (Security best practice)
- **Effort**: High (architectural change)
- **Timeline**: Plan for Phase 2/3

**Action Items**:
1. Design BFF architecture
2. Implement secure cookie-based auth
3. Migrate frontend to use BFF endpoints
4. Deprecate API key pattern

---

### 🟡 MEDIUM PRIORITY

#### 4. Notifications System - Complete Implementation
**Location**: `consultantos/api/notifications_endpoints.py`

**Current State**:
- All endpoints return placeholder responses
- No actual storage/retrieval implemented
- 6 TODOs across the file

**TODOs**:
1. Line 66: Implement actual notification storage/retrieval
2. Line 84: Implement actual notification update (mark as read)
3. Line 100: Implement actual notification update (mark all as read)
4. Line 116: Implement actual notification deletion
5. Line 132: Implement actual notification clearing
6. Line 147: Implement actual settings retrieval
7. Line 174: Implement actual settings update

**Recommendation**:
- **Priority**: MEDIUM (Feature completeness)
- **Effort**: Medium (requires database schema + CRUD operations)
- **Timeline**: Next feature sprint

**Action Items**:
1. Design notification schema in Firestore
2. Implement notification service layer
3. Add notification creation triggers (from alerts, reports, etc.)
4. Implement all CRUD operations
5. Add notification preferences storage

---

#### 5. Alerting - Slack & Webhook Integration
**Location**: `consultantos/monitoring/intelligence_monitor.py:984,989`

**Current State**:
- Placeholder methods for Slack and webhook alerts
- No actual integration implemented

**TODOs**:
1. Line 984: Implement Slack webhook integration
2. Line 989: Implement webhook delivery

**Recommendation**:
- **Priority**: MEDIUM (Feature enhancement)
- **Effort**: Medium (requires webhook client + error handling)
- **Timeline**: When alerting becomes critical feature

**Action Items**:
1. Add Slack webhook client (httpx/requests)
2. Implement webhook delivery with retry logic
3. Add webhook configuration to Monitor model
4. Handle webhook failures gracefully
5. Add webhook delivery status tracking

---

#### 6. Analytics - Job Queue Performance Metrics
**Location**: `consultantos/api/analytics_endpoints.py:425`

**Current State**:
- Placeholder for job queue metrics
- Job history tracking not implemented

**TODO**:
```python
# TODO: Implement job queue performance metrics when job history is available
```

**Recommendation**:
- **Priority**: MEDIUM (Observability)
- **Effort**: Medium (requires job history tracking)
- **Timeline**: When job queue becomes bottleneck

**Action Items**:
1. Implement job history tracking
2. Add metrics: avg_wait_time, avg_processing_time, queue_depth
3. Query and aggregate metrics for analytics endpoint
4. Add job queue dashboard visualization

---

#### 7. Dashboard - PDF Export
**Location**: `consultantos/api/dashboard_endpoints.py:292`

**Current State**:
- Endpoint returns 501 Not Implemented
- PDF generator exists but not integrated

**TODO**:
```python
# TODO: Implement PDF export using existing pdf_generator
```

**Recommendation**:
- **Priority**: MEDIUM (Feature completeness)
- **Effort**: Low (PDF generator already exists)
- **Timeline**: Next feature sprint

**Action Items**:
1. Integrate existing `pdf_generator` module
2. Convert dashboard data to report format
3. Add watermark: "Snapshot taken at [timestamp]"
4. Return PDF as download response

---

### 🟢 LOW PRIORITY

#### 8. Alert Scoring - Adaptive Algorithms
**Location**: `consultantos/monitoring/alert_scorer.py:256,363`

**Current State**:
- Basic scoring implemented
- No adaptive learning from user feedback

**TODOs**:
1. Line 256: Implement adaptive scoring based on feedback
2. Line 363: Implement adaptive thresholding

**Recommendation**:
- **Priority**: LOW (Enhancement)
- **Effort**: High (requires ML/statistical modeling)
- **Timeline**: Phase 3 or when feedback data is sufficient

**Action Items**:
1. Track feedback per change_type, monitor, user
2. Adjust weights for high false positive change types
3. Personalize scoring based on user feedback patterns
4. Implement adaptive thresholding algorithm
5. A/B test scoring improvements

---

#### 9. Billing - Team Member Counting
**Location**: `consultantos/billing/usage_tracker.py:259`

**Current State**:
- Returns 1 (just the user)
- Team management not implemented

**TODO**:
```python
# TODO: Implement team member counting when team management is added
```

**Recommendation**:
- **Priority**: LOW (Depends on team feature)
- **Effort**: Low (simple count query)
- **Timeline**: When team management is implemented

**Action Items**:
1. Wait for team management implementation
2. Query team members from database
3. Return accurate count for billing calculations

---

#### 10. Frontend - Share Functionality
**Location**: `frontend/app/reports/page.tsx:339`

**Current State**:
- Share button exists but only logs to console
- No actual sharing implemented

**TODO**:
```typescript
// TODO: Implement share functionality
```

**Recommendation**:
- **Priority**: LOW (UX enhancement)
- **Effort**: Low (can use existing sharing endpoints)
- **Timeline**: Next frontend sprint

**Action Items**:
1. Integrate with existing `/api/sharing` endpoints
2. Add share dialog/modal
3. Support link sharing, email sharing
4. Add copy-to-clipboard functionality

---

#### 11. Frontend - @ Mention Suggestions
**Location**: `frontend/app/components/CommentForm.tsx:215`

**Current State**:
- Comment form exists
- No @ mention autocomplete

**TODO**:
```typescript
// TODO: Add @ mention suggestions
```

**Recommendation**:
- **Priority**: LOW (UX enhancement)
- **Effort**: Medium (requires user search + autocomplete)
- **Timeline**: When comments become heavily used

**Action Items**:
1. Add user search endpoint
2. Implement autocomplete component
3. Parse @ mentions in comment text
4. Link mentions to user profiles

---

## Recommendations Summary

### Immediate Actions (This Sprint)
1. ✅ **Fix dashboard authorization** - Security risk, low effort
2. ✅ **Plan CSP migration** - Security risk, requires planning

### Short Term (Next 2 Sprints)
3. ✅ **Complete notifications system** - Feature completeness
4. ✅ **Implement dashboard PDF export** - Low effort, high value
5. ✅ **Add Slack/webhook alerting** - Feature enhancement

### Medium Term (Phase 2)
6. ✅ **BFF authentication migration** - Architectural improvement
7. ✅ **Job queue metrics** - Observability
8. ✅ **Share functionality** - UX enhancement

### Long Term (Phase 3)
9. ✅ **Adaptive alert scoring** - ML enhancement
10. ✅ **@ mention suggestions** - UX polish
11. ✅ **Team member counting** - Depends on team feature

---

## TODO Categories

### By Type
- **Security**: 4 TODOs
- **Feature Implementation**: 9 TODOs
- **Enhancement**: 7 TODOs

### By Component
- **API Endpoints**: 9 TODOs
- **Monitoring/Alerting**: 4 TODOs
- **Frontend**: 2 TODOs
- **Billing**: 1 TODO
- **Security**: 3 TODOs
- **Analytics**: 1 TODO

### By Effort
- **Low Effort** (< 1 day): 6 TODOs
- **Medium Effort** (1-3 days): 10 TODOs
- **High Effort** (> 3 days): 4 TODOs

---

## Notes

1. **Notifications System**: Largest gap - 6 TODOs for a single feature. Consider prioritizing this for feature completeness.

2. **Security TODOs**: CSP hardening is documented but not implemented. Should be scheduled for security sprint.

3. **Placeholder Endpoints**: Several endpoints return 501 or empty responses. Consider adding feature flags to hide incomplete features.

4. **Dependencies**: Some TODOs depend on other features (team management, job history). Track dependencies.

5. **Documentation**: Most TODOs have good context. Consider adding issue tracking links for better project management.

---

## Next Steps

1. Create GitHub issues for high-priority TODOs
2. Add TODO tracking to project board
3. Schedule security sprint for CSP migration
4. Prioritize notifications system completion
5. Review and update TODO comments with issue links

