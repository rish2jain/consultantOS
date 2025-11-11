# ConsultantOS - Dashboard User Testing Guide

**Version**: 2.0.0
**Last Updated**: 2025-11-10
**Component**: Intelligence Dashboard (Frontend)

## Overview

This guide provides comprehensive testing scenarios for the ConsultantOS Intelligence Dashboard. The dashboard provides real-time monitoring of competitive intelligence, alert management, monitor control, analytics, report management, and job queue tracking.

### Dashboard Features

- **Tabbed Interface**: Four main tabs (Overview, Analytics, Reports, Jobs)
- **Real-time Statistics**: Total monitors, active monitors, unread alerts, 24h alerts
- **Monitor Management**: View, pause, resume, and manually trigger checks
- **Alert Feed**: Recent alerts with confidence scores, change detection, and read/unread status
- **Analytics Dashboard**: Productivity metrics, business metrics, and visualizations
- **Report Management**: Search, filter, and manage analysis reports
- **Job Queue Management**: Track and manage background jobs with progress monitoring
- **Auto-refresh**: Dashboard updates every 30 seconds (tab-specific)
- **Status Indicators**: Visual status badges (active, paused, error)
- **Error Handling**: Displays monitor errors and system issues
- **Consolidated API**: Single `/dashboard/overview` endpoint for faster loading

## Quick Setup

### Prerequisites

1. **Backend API Running**

   - Production: `https://consultantos-api-bdndyf33xa-uc.a.run.app`
   - Local: `http://localhost:8080`

   **⚠️ Important**:

   - Ensure the backend has monitoring endpoints enabled. See `DASHBOARD_DEPLOYMENT_STATUS.md` for deployment details.
   - For local testing, verify backend is actually listening:

     ```bash
     # Should return JSON response
     curl http://localhost:8080/health

     # Should show process listening
     lsof -iTCP:8080 -sTCP:LISTEN
     ```

   - If backend process exists but isn't listening, check the terminal for startup errors

2. **Frontend Running**

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   - Access at: `http://localhost:3000`
   - **⚠️ Important**: Ensure `frontend/.env.local` contains:
     ```bash
     NEXT_PUBLIC_API_URL=http://localhost:8080
     ```
   - **Restart frontend** after changing `.env.local` to pick up new API URL

3. **User Account with API Key**
   - Register/login to get API key
   - API key stored in browser (in-memory)

### Test Data Setup

Before testing, ensure you have:

1. **At least one monitor created** (via `/monitors/new` or API)
2. **Some alerts generated** (from monitor checks)
3. **Mixed monitor statuses** (active, paused) for comprehensive testing

**Quick Setup via API:**

```bash
export API_URL="http://localhost:8080"  # or production URL
export API_KEY="your-api-key-here"

# Create a test monitor
curl -X POST "$API_URL/monitors" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "config": {
      "frequency": "daily",
      "frameworks": ["porter", "swot"],
      "alert_threshold": 0.7,
      "notification_channels": ["dashboard"]
    }
  }'

# Trigger a check to generate alerts
curl -X POST "$API_URL/monitors/{monitor_id}/check" \
  -H "X-API-Key: $API_KEY"
```

## Testing Scenarios

### Scenario 1: Dashboard Initial Load

**Objective**: Verify dashboard loads correctly with existing data

**Steps**:

1. Navigate to `http://localhost:3000/dashboard`
2. Wait for initial load (should show loading spinner)
3. Verify dashboard renders with data

**Expected Results**:

- ✅ Loading spinner appears briefly
- ✅ Tab navigation visible (Overview, Analytics, Reports, Jobs)
- ✅ Overview tab active by default
- ✅ Statistics cards display (Total Monitors, Active Monitors, Unread Alerts, Alerts 24h)
- ✅ Active Monitors section shows monitor list
- ✅ Recent Alerts section shows alert feed
- ✅ Single API call to `/dashboard/overview` (check Network tab)
- ✅ No console errors

**Edge Cases to Test**:

- Empty state (no monitors): Should show "No monitors yet" message with "Create Monitor" button
- Empty alerts: Should show "No alerts yet" message
- API error: Should display error message gracefully with retry button

**Test Data Requirements**:

- At least 1 monitor
- At least 1 alert (optional for empty state testing)

**Performance Note**:

- Should load faster than before (50-70% improvement) due to consolidated API endpoint

---

### Scenario 2: Statistics Overview Cards

**Objective**: Verify statistics cards display correct data

**Steps**:

1. Navigate to dashboard
2. Observe the 4 statistics cards at the top
3. Verify numbers match actual data

**Expected Results**:

- ✅ **Total Monitors**: Shows count of all monitors (active + paused)
- ✅ **Active Monitors**: Shows count of active monitors only (green number)
- ✅ **Unread Alerts**: Shows count of unread alerts (orange number)
- ✅ **Alerts (24h)**: Shows count of alerts created in last 24 hours (blue number)
- ✅ Numbers update when data changes

**Verification**:

```bash
# Compare with API response
curl -X GET "$API_URL/monitors/stats/dashboard" \
  -H "X-API-Key: $API_KEY"
```

**Edge Cases**:

- Zero monitors: All stats show 0
- Zero alerts: Unread and 24h alerts show 0
- Large numbers: Numbers display correctly (no overflow)

---

### Scenario 3: Monitor List Display

**Objective**: Verify monitor list displays correctly with all information

**Steps**:

1. Navigate to dashboard
2. Review the "Active Monitors" section
3. Check each monitor entry

**Expected Results**:

- ✅ Company name displayed prominently
- ✅ Status badge shows correct status (active/paused/error) with color coding:
  - Active: Green badge
  - Paused: Yellow badge
  - Error: Red badge
- ✅ Industry displayed below company name
- ✅ Frequency displayed (e.g., "daily checks")
- ✅ Alert count displayed
- ✅ Last check time displayed (relative format: "5m ago", "2h ago", "3d ago")
- ✅ Error message displayed if `error_count > 0` (red background)
- ✅ Action buttons visible (Check Now, Pause/Resume)

**Monitor Entry Structure**:

```
[Company Name] [Status Badge]
Industry Name
Frequency • X alerts • Last check: X ago
[Error message if applicable]
[Check Now] [Pause/Resume]
```

**Edge Cases**:

- Monitor with no last_check: Should not show "Last check" line
- Monitor with errors: Should show error message in red box
- Very long company names: Should truncate or wrap gracefully
- Monitor with 0 alerts: Should show "0 alerts"

---

### Scenario 4: Monitor Actions - Manual Check

**Objective**: Verify "Check Now" button triggers immediate monitor check

**Steps**:

1. Navigate to dashboard
2. Find a monitor in the list
3. Click "Check Now" button
4. Observe the monitor's last_check time

**Expected Results**:

- ✅ Button is clickable
- ✅ Click triggers API call to `/monitors/{id}/check`
- ✅ Dashboard refreshes after check completes
- ✅ Last check time updates to "just now" or "1m ago"
- ✅ New alerts may appear in Recent Alerts section
- ✅ No error messages

**Verification**:

```bash
# Manually trigger check via API
curl -X POST "$API_URL/monitors/{monitor_id}/check" \
  -H "X-API-Key: $API_KEY"
```

**Edge Cases**:

- Check fails: Should show error (check console/network tab)
- Check takes long time: Button should be disabled or show loading state
- Multiple rapid clicks: Should handle gracefully (prevent duplicate requests)

---

### Scenario 5: Monitor Actions - Pause/Resume

**Objective**: Verify pause and resume functionality

**Steps - Pause**:

1. Find an active monitor
2. Click "Pause" button
3. Observe status change

**Expected Results - Pause**:

- ✅ Button click triggers API call to update status
- ✅ Status badge changes from "active" (green) to "paused" (yellow)
- ✅ Button changes from "Pause" to "Resume"
- ✅ Monitor stops running scheduled checks

**Steps - Resume**:

1. Find a paused monitor
2. Click "Resume" button
3. Observe status change

**Expected Results - Resume**:

- ✅ Button click triggers API call to update status
- ✅ Status badge changes from "paused" (yellow) to "active" (green)
- ✅ Button changes from "Resume" to "Pause"
- ✅ Monitor resumes scheduled checks

**Verification**:

```bash
# Pause monitor
curl -X PUT "$API_URL/monitors/{monitor_id}" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"status": "paused"}'

# Resume monitor
curl -X PUT "$API_URL/monitors/{monitor_id}" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"status": "active"}'
```

**Edge Cases**:

- Pause fails: Should show error message
- Resume fails: Should show error message
- Status update conflict: Should handle gracefully

---

### Scenario 6: Alert Feed Display

**Objective**: Verify alert feed displays correctly

**Steps**:

1. Navigate to dashboard
2. Review the "Recent Alerts" section
3. Check alert entries

**Expected Results**:

- ✅ Alerts displayed in reverse chronological order (newest first)
- ✅ Unread alerts have blue background highlight
- ✅ Read alerts have white background
- ✅ Each alert shows:
  - Title (bold)
  - Summary text
  - Timestamp (relative: "5m ago", "2h ago")
  - Confidence score (e.g., "85% confidence")
  - Unread indicator (blue dot) if unread
- ✅ Maximum 10 alerts displayed
- ✅ Scrollable if more than 10 alerts

**Alert Entry Structure**:

```
[Title]
Summary text...
5m ago • 85% confidence [Blue dot if unread]
```

**Edge Cases**:

- No alerts: Shows "No alerts yet" message
- Many alerts: Section is scrollable
- Very long titles/summaries: Should truncate or wrap gracefully
- Alerts from different monitors: All mixed together chronologically

---

### Scenario 7: Alert Interaction - Mark as Read

**Objective**: Verify clicking alert marks it as read

**Steps**:

1. Find an unread alert (blue background)
2. Click on the alert
3. Observe the alert's appearance

**Expected Results**:

- ✅ Click triggers API call to `/monitors/alerts/{id}/read`
- ✅ Alert background changes from blue to white
- ✅ Blue dot indicator disappears
- ✅ Unread count in stats decreases
- ✅ Alert remains in feed (not removed)

**Verification**:

```bash
# Mark alert as read via API
curl -X POST "$API_URL/monitors/alerts/{alert_id}/read" \
  -H "X-API-Key: $API_KEY"
```

**Edge Cases**:

- Clicking read alert: Should not trigger API call (or handle gracefully)
- Mark as read fails: Should show error (check console)
- Multiple rapid clicks: Should handle gracefully

---

### Scenario 8: Tab Navigation

**Objective**: Verify tab navigation works correctly

**Steps**:

1. Navigate to dashboard
2. Click each tab: Overview, Analytics, Reports, Jobs
3. Verify content loads for each tab

**Expected Results**:

- ✅ Tab buttons are clickable
- ✅ Active tab highlighted with blue border
- ✅ Content switches correctly when clicking tabs
- ✅ Overview tab: Shows monitors and alerts
- ✅ Analytics tab: Shows metrics and charts
- ✅ Reports tab: Shows report list
- ✅ Jobs tab: Shows job queue
- ✅ No console errors during tab switching

**Edge Cases**:

- Rapid tab switching: Should handle gracefully
- Tab with no data: Should show appropriate empty state
- API error on tab load: Should show error message

---

### Scenario 9: Analytics Tab

**Objective**: Verify Analytics tab displays metrics and visualizations

**Steps**:

1. Navigate to dashboard
2. Click "Analytics" tab
3. Review metrics and charts

**Expected Results**:

- ✅ Productivity metrics display:
  - Reports per day
  - Average processing time
  - Success rate
- ✅ Business metrics display:
  - Total reports
  - Average confidence
  - High confidence reports count
- ✅ Charts render:
  - Framework distribution (bar chart)
  - Report status pipeline (pie chart)
- ✅ Job queue metrics display
- ✅ Data loads from `/dashboard/analytics?days=30`

**Verification**:

```bash
curl -X GET "$API_URL/dashboard/analytics?days=30" \
  -H "X-API-Key: $API_KEY"
```

**Edge Cases**:

- No data: Charts show "No data available" message
- Large datasets: Charts render without performance issues
- API error: Shows error message gracefully

---

### Scenario 10: Reports Tab - List and View

**Objective**: Verify Reports tab displays and manages reports

**Steps**:

1. Navigate to dashboard
2. Click "Reports" tab
3. Review report list
4. Click "View" on a report

**Expected Results**:

- ✅ Report list displays with:
  - Company name
  - Industry
  - Frameworks used
  - Confidence score
  - Status
  - Created date
- ✅ "+ New Analysis" button visible
- ✅ "View" button navigates to report detail page
- ✅ Reports load from `/dashboard/reports?action=list`

**Verification**:

```bash
curl -X GET "$API_URL/dashboard/reports?action=list&page=1&page_size=10" \
  -H "X-API-Key: $API_KEY"
```

**Edge Cases**:

- No reports: Shows "No reports yet" with "Create Analysis" button
- Many reports: List is scrollable
- Report with missing data: Handles gracefully

---

### Scenario 11: Reports Tab - Search

**Objective**: Verify report search functionality

**Steps**:

1. Navigate to Reports tab
2. Type in search box (e.g., "Tesla")
3. Wait for results (300ms debounce)

**Expected Results**:

- ✅ Search input is visible and functional
- ✅ Search triggers after 300ms delay (debounced)
- ✅ Results filter to matching reports
- ✅ Search query sent to `/dashboard/reports?action=search&search_query=...`
- ✅ Results update without page reload

**Edge Cases**:

- Empty search: Shows all reports
- No matches: Shows "No reports found" message
- Special characters: Handles gracefully (URL encoding)

---

### Scenario 12: Reports Tab - Filter

**Objective**: Verify report filtering by status

**Steps**:

1. Navigate to Reports tab
2. Select status from dropdown (e.g., "Completed")
3. Review filtered results

**Expected Results**:

- ✅ Status dropdown visible with options:
  - All Statuses
  - Completed
  - Processing
  - Pending
  - Failed
- ✅ Filter triggers API call to `/dashboard/reports?action=filter&status=...`
- ✅ Results update to show only matching status
- ✅ "Reset Filters" button clears filters

**Edge Cases**:

- Invalid status: Handles gracefully
- No matches: Shows appropriate message

---

### Scenario 13: Jobs Tab - List and Status

**Objective**: Verify Jobs tab displays job queue

**Steps**:

1. Navigate to dashboard
2. Click "Jobs" tab
3. Review job list

**Expected Results**:

- ✅ Active jobs displayed with:
  - Job ID (truncated)
  - Status badge (running/pending)
  - Progress bar (if running)
  - Created date
  - Error message (if failed)
- ✅ "Refresh" button reloads job list
- ✅ Jobs load from `/dashboard/jobs?action=list&status=pending,running`

**Verification**:

```bash
curl -X GET "$API_URL/dashboard/jobs?action=list&status=pending,running&limit=20" \
  -H "X-API-Key: $API_KEY"
```

**Edge Cases**:

- No jobs: Shows "No active jobs" message
- Running job: Shows progress bar
- Failed job: Shows error message in red box

---

### Scenario 14: Jobs Tab - Cancel Job

**Objective**: Verify job cancellation functionality

**Steps**:

1. Navigate to Jobs tab
2. Find a running job
3. Click "Cancel" button
4. Observe job status change

**Expected Results**:

- ✅ "Cancel" button visible on running jobs
- ✅ Click triggers API call to `/dashboard/jobs/{job_id}/cancel`
- ✅ Job status updates after cancellation
- ✅ Job list refreshes automatically

**Verification**:

```bash
curl -X POST "$API_URL/dashboard/jobs/{job_id}/cancel" \
  -H "X-API-Key: $API_KEY"
```

**Edge Cases**:

- Cancel fails: Shows error message
- Job already completed: Button disabled or hidden

---

### Scenario 15: Jobs Tab - View History

**Objective**: Verify job history viewing

**Steps**:

1. Navigate to Jobs tab
2. Click "View History" button
3. Review job history

**Expected Results**:

- ✅ "View History" button visible
- ✅ Click loads job history from `/dashboard/jobs?action=history&limit=20`
- ✅ History shows completed and failed jobs
- ✅ Jobs display with status and completion time

**Edge Cases**:

- No history: Shows appropriate message
- Large history: List is scrollable

---

### Scenario 16: Auto-refresh Functionality

**Objective**: Verify dashboard auto-refreshes every 30 seconds

**Steps**:

1. Navigate to dashboard
2. Note the current data (e.g., alert count, last check time)
3. Wait 30+ seconds
4. Observe if data updates

**Expected Results**:

- ✅ Dashboard automatically refreshes every 30 seconds
- ✅ Statistics cards update with new values
- ✅ Monitor list updates (last check times, statuses)
- ✅ Alert feed updates (new alerts appear)
- ✅ Tab-specific refresh:
  - Overview: Refreshes overview data
  - Analytics: Refreshes analytics (if on Analytics tab)
  - Reports: Refreshes reports (if on Reports tab)
  - Jobs: Refreshes jobs (if on Jobs tab)
- ✅ No page reload (smooth update)
- ✅ No console errors during refresh

**Verification**:

- Open browser DevTools → Network tab
- Observe API calls every 30 seconds:
  - Overview tab: `GET /dashboard/overview`
  - Analytics tab: `GET /dashboard/analytics`
  - Reports tab: `GET /dashboard/reports`
  - Jobs tab: `GET /dashboard/jobs`

**Edge Cases**:

- API error during refresh: Should handle gracefully (show error, retry next cycle)
- User navigates away: Refresh interval should be cleared
- Multiple tabs open: Each tab refreshes independently
- Tab switch during refresh: Should handle gracefully

---

### Scenario 17: Navigation - Create New Monitor

**Objective**: Verify "New Monitor" button navigation

**Steps**:

1. Click "+ New Monitor" button in header
2. Verify navigation

**Expected Results**:

- ✅ Button is visible and clickable
- ✅ Click navigates to `/monitors/new`
- ✅ No errors during navigation

**Edge Cases**:

- Navigation fails: Should show error or handle gracefully
- User not authenticated: Should redirect to login (if applicable)

---

### Scenario 18: Navigation - Create New Analysis

**Objective**: Verify "New Analysis" button navigation

**Steps**:

1. Navigate to Reports tab
2. Click "+ New Analysis" button
3. Verify navigation

**Expected Results**:

- ✅ Button is visible and clickable
- ✅ Click navigates to `/analysis`
- ✅ No errors during navigation

**Edge Cases**:

- Navigation fails: Should show error or handle gracefully

---

### Scenario 19: Error Handling

**Objective**: Verify error handling and display

**Steps**:

1. Navigate to dashboard
2. Simulate various error conditions:
   - Invalid API key
   - Network failure
   - API server down
   - Invalid response format

**Expected Results**:

- ✅ Network errors: Display user-friendly error message
- ✅ API errors: Display error message (not raw error)
- ✅ Invalid responses: Handle gracefully (don't crash)
- ✅ Loading states: Show loading spinner during requests
- ✅ Error recovery: Retry or allow manual refresh

**Error Simulation**:

```bash
# Test with invalid API key
curl -X GET "$API_URL/monitors" \
  -H "X-API-Key: invalid-key"
# Should return 401/403

# Test with server down
# Stop backend server, then access dashboard
```

**Edge Cases**:

- Partial data load: Should show available data, indicate partial load
- Timeout: Should show timeout error
- CORS errors: Should display appropriate message

---

### Scenario 20: Responsive Design

**Objective**: Verify dashboard works on different screen sizes

**Steps**:

1. Open dashboard in browser
2. Resize browser window or use DevTools device emulation
3. Test different breakpoints:
   - Mobile (375px)
   - Tablet (768px)
   - Desktop (1920px)

**Expected Results**:

- ✅ Mobile: Single column layout, cards stack vertically
- ✅ Tablet: 2-column layout for stats, monitors and alerts stack
- ✅ Desktop: Full 3-column layout (stats, monitors, alerts)
- ✅ All text readable at all sizes
- ✅ Buttons clickable/tappable on mobile
- ✅ No horizontal scrolling
- ✅ Images/icons scale appropriately

**Breakpoints**:

- Mobile: `< 768px`
- Tablet: `768px - 1024px`
- Desktop: `> 1024px`

---

### Scenario 21: Performance Testing

**Objective**: Verify dashboard performance with large datasets

**Steps**:

1. Create test data:
   - 20+ monitors
   - 100+ alerts
2. Load dashboard
3. Measure load time and interactions

**Expected Results**:

- ✅ Initial load < 3 seconds
- ✅ Smooth scrolling in alert feed
- ✅ No lag when clicking buttons
- ✅ Auto-refresh doesn't cause jank
- ✅ Memory usage reasonable (check DevTools)

**Performance Metrics**:

- Time to First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.5s
- Cumulative Layout Shift (CLS): < 0.1

**Optimization Notes**:

- Alerts limited to 10 most recent
- Monitors paginated if > 50 (future enhancement)
- API calls debounced/throttled

---

## API Integration Testing

### Endpoints Used by Dashboard

The dashboard uses these API endpoints:

#### Overview Tab

1. **GET `/dashboard/overview?alert_limit=10&report_limit=5`** - Consolidated dashboard data (monitors, stats, alerts)
2. **POST `/monitors/{id}/check`** - Trigger manual check
3. **PUT `/monitors/{id}`** - Update monitor (pause/resume)
4. **POST `/monitors/alerts/{id}/read`** - Mark alert as read

#### Analytics Tab

1. **GET `/dashboard/analytics?days=30`** - Get analytics metrics and charts

#### Reports Tab

1. **GET `/dashboard/reports?action=list&page=1&page_size=10`** - List reports
2. **GET `/dashboard/reports?action=search&search_query=...`** - Search reports
3. **GET `/dashboard/reports?action=filter&status=...`** - Filter reports

#### Jobs Tab

1. **GET `/dashboard/jobs?action=list&status=pending,running&limit=20`** - List active jobs
2. **GET `/dashboard/jobs?action=history&limit=20`** - Get job history
3. **POST `/dashboard/jobs/{job_id}/cancel`** - Cancel a job

#### Legacy Endpoints (Still Available)

- **GET `/monitors`** - List all monitors (replaced by `/dashboard/overview`)
- **GET `/monitors/stats/dashboard`** - Get dashboard statistics (replaced by `/dashboard/overview`)
- **GET `/monitors/{id}/alerts?limit=5`** - Get alerts for monitor (replaced by `/dashboard/overview`)

### Testing API Responses

**Dashboard Overview Response (Consolidated):**

```json
{
  "monitors": [
    {
      "id": "monitor-123",
      "company": "Tesla",
      "industry": "Electric Vehicles",
      "status": "active",
      "config": {
        "frequency": "daily",
        "frameworks": ["porter", "swot"],
        "alert_threshold": 0.7
      },
      "last_check": "2025-11-10T14:00:00Z",
      "total_alerts": 5,
      "error_count": 0
    }
  ],
  "stats": {
    "total_monitors": 5,
    "active_monitors": 4,
    "paused_monitors": 1,
    "total_alerts_24h": 12,
    "unread_alerts": 3,
    "avg_alert_confidence": 0.82,
    "top_change_types": [
      ["market_share", 5],
      ["product_launch", 3]
    ]
  },
  "recent_alerts": [
    {
      "id": "alert-123",
      "monitor_id": "monitor-123",
      "title": "Market Share Change Detected",
      "summary": "Tesla's market share increased by 2%...",
      "confidence": 0.85,
      "created_at": "2025-11-10T14:00:00Z",
      "read": false,
      "changes_detected": [...]
    }
  ]
}
```

**Analytics Response:**

```json
{
  "productivity": {
    "reports_per_day": 2.5,
    "avg_processing_time": 45.2,
    "success_rate": 95.5,
    "total_reports": 150,
    "reports_this_month": 45,
    "reports_last_month": 38
  },
  "business": {
    "total_frameworks_used": 8,
    "framework_distribution": {
      "porter": 45,
      "swot": 32,
      "pestel": 18
    },
    "avg_confidence_score": 0.82,
    "high_confidence_reports": 120,
    "industry_distribution": {...},
    "company_distribution": {...}
  },
  "dashboard": {
    "report_status_pipeline": {
      "completed": 120,
      "processing": 5,
      "pending": 3,
      "failed": 2
    },
    "confidence_distribution": [...],
    "framework_effectiveness": {...},
    "job_queue_metrics": {
      "pending": 2,
      "running": 1,
      "completed": 150,
      "failed": 3
    },
    "user_activity": {...}
  }
}
```

**Reports Response:**

```json
{
  "reports": [
    {
      "report_id": "report-123",
      "company": "Tesla",
      "industry": "Electric Vehicles",
      "frameworks": ["porter", "swot"],
      "status": "completed",
      "confidence_score": 0.85,
      "created_at": "2025-11-10T14:00:00Z",
      "updated_at": "2025-11-10T14:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 10
}
```

**Jobs Response:**

```json
{
  "jobs": [
    {
      "id": "job-123",
      "status": "running",
      "progress": 65,
      "created_at": "2025-11-10T14:00:00Z",
      "updated_at": "2025-11-10T14:15:00Z",
      "error": null
    }
  ],
  "total": 5
}
```

---

## Browser Compatibility Testing

### Supported Browsers

Test on these browsers:

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile Safari (iOS)
- ✅ Chrome Mobile (Android)

### Browser-Specific Issues to Check

1. **Safari**:

   - Date formatting
   - Auto-refresh interval behavior
   - CSS grid/flexbox support

2. **Firefox**:

   - API fetch behavior
   - CSS animations

3. **Mobile Browsers**:
   - Touch interactions
   - Viewport scaling
   - Performance on slower devices

---

## Accessibility Testing

### WCAG 2.1 Compliance

**Keyboard Navigation**:

- ✅ All interactive elements accessible via keyboard
- ✅ Tab order is logical
- ✅ Focus indicators visible

**Screen Readers**:

- ✅ Semantic HTML elements
- ✅ ARIA labels where needed
- ✅ Alt text for images/icons

**Color Contrast**:

- ✅ Text meets WCAG AA contrast ratios (4.5:1 for normal text)
- ✅ Status badges have sufficient contrast

**Testing Tools**:

- Chrome DevTools Lighthouse
- axe DevTools extension
- WAVE browser extension

---

## Common Issues & Troubleshooting

### Issue: Dashboard shows "Loading..." indefinitely or "Failed to fetch"

**Possible Causes**:

1. API server not running
2. Backend process running but not listening on port (stuck during startup)
3. CORS issues
4. Invalid API key
5. Network connectivity
6. Syntax errors in dashboard code (fixed in v2.0.0)
7. **Monitoring endpoints not enabled** (fixed in v2.0.0)
8. Frontend configured to wrong API URL

**Solutions**:

1. **Check backend server status**:

   ```bash
   curl http://localhost:8080/health
   # Should return: {"status":"healthy",...}
   ```

2. **If connection refused, verify backend is actually listening**:

   ```bash
   # Check if process is running
   ps aux | grep -E "(uvicorn|main.py)" | grep -v grep

   # Check if port is listening
   lsof -iTCP:8080 -sTCP:LISTEN

   # If process exists but not listening, it may be stuck during startup
   # Check the terminal where you started the backend for errors
   ```

3. **Restart backend if needed**:

   ```bash
   # Kill existing processes
   pkill -f "uvicorn.*8080"
   pkill -f "main.py"

   # Start fresh
   cd /Users/rish2jain/Documents/Hackathons/ConsultantOS
   python main.py
   ```

4. **Verify frontend API URL configuration**:

   - Check `frontend/.env.local` contains: `NEXT_PUBLIC_API_URL=http://localhost:8080`
   - Restart frontend dev server after changing `.env.local`
   - Verify in browser Network tab that requests go to `localhost:8080` (not production)

5. Check browser console for errors (look for `ERR_CONNECTION_REFUSED`)

6. Verify API key is set: Check localStorage/sessionStorage

7. Check network tab for failed requests

8. **Fixed**: JSX structure error in Reports tab (v2.0.0) - ensure code is up to date

9. **Fixed**: Monitoring endpoints now enabled in `main.py` - requires backend restart

**Note**: If you see "Failed to load dashboard overview" error message with a Retry button, the UI is working correctly. The error indicates the API endpoints are not available. Common causes:

- **Backend server not running locally**: Start with `python main.py`
- **Backend stuck during startup**: Check terminal for import/startup errors
- **Frontend using wrong API URL**: Verify `.env.local` and restart frontend
- **Production API endpoints not deployed**: See `DASHBOARD_DEPLOYMENT_STATUS.md`
- **Monitoring endpoints not enabled**: Check `consultantos/api/main.py` line 359

**Local Testing Checklist**:

- [ ] Backend process running: `ps aux | grep main.py`
- [ ] Backend listening on port: `lsof -iTCP:8080 -sTCP:LISTEN`
- [ ] Health endpoint responds: `curl http://localhost:8080/health`
- [ ] Frontend `.env.local` configured: `NEXT_PUBLIC_API_URL=http://localhost:8080`
- [ ] Frontend restarted after `.env.local` change
- [ ] Browser Network tab shows requests to `localhost:8080`

**Local Backend Verification**:

```bash
# 1. Check if backend is running
curl http://localhost:8080/health
# Expected: {"status":"healthy",...}

# 2. Verify monitoring endpoints are enabled
curl http://localhost:8080/monitors/stats/dashboard \
  -H "X-API-Key: YOUR_KEY"
# Expected: JSON with monitor statistics

# 3. Verify dashboard endpoints are available
curl http://localhost:8080/dashboard/overview \
  -H "X-API-Key: YOUR_KEY"
# Expected: JSON with dashboard overview data

# 4. Check Swagger docs
open http://localhost:8080/docs
# Should show all endpoints including /dashboard/* and /monitors/*
```

**Production Deployment Verification**:

```bash
# Verify monitoring endpoints are enabled
curl https://consultantos-api-bdndyf33xa-uc.a.run.app/monitors/stats/dashboard \
  -H "X-API-Key: YOUR_KEY"

# Verify dashboard endpoints are available
curl https://consultantos-api-bdndyf33xa-uc.a.run.app/dashboard/overview \
  -H "X-API-Key: YOUR_KEY"
```

### Issue: Statistics don't update

**Possible Causes**:

1. Auto-refresh not working
2. API returning stale data
3. Cache issues

**Solutions**:

1. Check browser console for errors
2. Manually refresh page
3. Clear browser cache
4. Check API response directly

### Issue: Alerts not appearing

**Possible Causes**:

1. No alerts generated yet
2. Alerts filtered out
3. API error

**Solutions**:

1. Trigger manual check on monitor
2. Check API response: `GET /monitors/{id}/alerts`
3. Verify alert threshold settings
4. Check browser console for errors

### Issue: Buttons not working

**Possible Causes**:

1. JavaScript errors
2. API authentication issues
3. Event handlers not bound

**Solutions**:

1. Check browser console for errors
2. Verify API key is set
3. Check network tab for API calls
4. Try hard refresh (Ctrl+Shift+R / Cmd+Shift+R)

---

## Test Checklist

Use this checklist to ensure comprehensive testing:

### Functional Testing

- [ ] Dashboard loads with existing data
- [ ] Tab navigation works (Overview, Analytics, Reports, Jobs)
- [ ] Statistics cards display correctly
- [ ] Monitor list displays all information
- [ ] "Check Now" button works
- [ ] Pause/Resume buttons work
- [ ] Alert feed displays correctly
- [ ] Clicking alert marks it as read
- [ ] Analytics tab displays metrics and charts
- [ ] Reports tab displays report list
- [ ] Report search works (with debounce)
- [ ] Report filtering works
- [ ] Jobs tab displays job queue
- [ ] Job cancellation works
- [ ] Job history viewing works
- [ ] Auto-refresh works (30s interval, tab-specific)
- [ ] "New Monitor" button navigates correctly
- [ ] "New Analysis" button navigates correctly
- [ ] Error handling works gracefully
- [ ] Consolidated API endpoint loads faster

### Edge Cases

- [ ] Empty state (no monitors)
- [ ] Empty alerts
- [ ] Empty reports
- [ ] Empty jobs
- [ ] Monitor with errors
- [ ] Network failures
- [ ] API errors
- [ ] Invalid responses
- [ ] Large datasets (20+ monitors, 100+ alerts, 100+ reports)
- [ ] Rapid tab switching
- [ ] Search with special characters
- [ ] Filter with no matches
- [ ] Job cancellation during execution

### UI/UX

- [ ] Responsive design (mobile/tablet/desktop)
- [ ] Loading states
- [ ] Error messages
- [ ] Status badges (colors correct)
- [ ] Timestamp formatting
- [ ] Button hover states
- [ ] Scrollable sections
- [ ] Tab highlighting
- [ ] Chart rendering (bar, pie)
- [ ] Progress bars for jobs
- [ ] Search input debouncing
- [ ] Filter dropdown functionality

### Performance

- [ ] Initial load < 3 seconds (improved with consolidated API)
- [ ] Smooth scrolling
- [ ] No lag on interactions
- [ ] Memory usage reasonable
- [ ] Tab switching is instant
- [ ] Charts render without delay
- [ ] Search debouncing prevents excessive API calls

### Browser Compatibility

- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari
- [ ] Mobile browsers

### Accessibility

- [ ] Keyboard navigation
- [ ] Screen reader compatibility
- [ ] Color contrast
- [ ] Focus indicators

---

## Reporting Issues

When reporting issues, include:

1. **Browser & Version**: e.g., Chrome 120.0.6099.109
2. **OS**: e.g., macOS 14.1
3. **Steps to Reproduce**: Detailed steps
4. **Expected Behavior**: What should happen
5. **Actual Behavior**: What actually happens
6. **Console Errors**: Copy from browser console
7. **Network Errors**: Copy from network tab
8. **Screenshots**: If applicable
9. **API Response**: If relevant (sanitize sensitive data)

**Example Issue Report**:

```
Browser: Chrome 120.0.6099.109
OS: macOS 14.1

Steps:
1. Navigate to /dashboard
2. Click "Check Now" on a monitor
3. Wait for check to complete

Expected: Last check time updates
Actual: Last check time doesn't update

Console Errors:
- None

Network:
- POST /monitors/abc123/check returns 200 OK
- GET /monitors returns updated data

Screenshot: [attached]
```

---

## Next Steps

After completing testing:

1. **Document Findings**: Record all issues found
2. **Prioritize Issues**: Critical vs. Nice-to-have
3. **Create Tickets**: For each bug/issue
4. **Retest Fixes**: After issues are resolved
5. **Update Guide**: Add new scenarios as features evolve

---

## Additional Resources

- **API Documentation**: `/docs` (Swagger UI)
- **Backend Health**: `/health`
- **Frontend Code**: `frontend/app/dashboard/page.tsx`
- **Backend Endpoints**:
  - `consultantos/api/monitoring_endpoints.py` (monitoring endpoints)
  - `consultantos/api/dashboard_agents_endpoints.py` (dashboard agents endpoints)
- **Dashboard Agents**: `consultantos/agents/dashboard_*.py`
- **Implementation Docs**:
  - `DASHBOARD_IMPLEMENTATION_COMPLETE.md`
  - `DASHBOARD_ENHANCEMENTS_COMPLETE.md`
  - `FINAL_IMPLEMENTATION_SUMMARY.md`

---

## Changelog

### Version 2.0.1 (2025-11-10)

- Added local testing troubleshooting section
- Added backend startup verification steps
- Added frontend `.env.local` configuration notes
- Added connection refused error troubleshooting
- Added backend process status checking commands
- Enhanced deployment verification with local testing steps

### Version 2.0.0 (2025-11-10)

- Added tabbed interface testing (Overview, Analytics, Reports, Jobs)
- Added consolidated `/dashboard/overview` endpoint documentation
- Added Analytics tab testing scenarios
- Added Reports tab testing scenarios (list, search, filter)
- Added Jobs tab testing scenarios (list, cancel, history)
- Updated API endpoints list
- Added performance improvements documentation
- Updated test checklist with new features

### Version 1.0.0 (2025-11-10)

- Initial testing guide for basic dashboard functionality

---

**Last Updated**: 2025-11-10
**Maintainer**: ConsultantOS Team
