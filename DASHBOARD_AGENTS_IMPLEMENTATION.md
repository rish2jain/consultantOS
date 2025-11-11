# Dashboard Agents Implementation Plan

**Last Updated**: 2025-11-10  
**Status**: In Progress  
**Purpose**: Address all dashboard feature gaps using agent-based architecture

## Overview

This document outlines the implementation of specialized agents to address all features identified in `DASHBOARD_FEATURES_GAP_ANALYSIS.md`. The agent-based approach provides:

- **Modularity**: Each agent handles a specific domain
- **Scalability**: Agents can be optimized independently
- **Maintainability**: Clear separation of concerns
- **Reusability**: Agents can be used across different endpoints

## Implemented Agents

### 1. ✅ DashboardAnalyticsAgent

**Location**: `consultantos/agents/dashboard_analytics_agent.py`

**Purpose**: Generates comprehensive analytics and metrics for dashboard

**Features**:
- Productivity metrics (reports per day, processing time, success rate)
- Business metrics (framework usage, confidence scores, industry distribution)
- Dashboard analytics (status pipeline, confidence distribution, framework effectiveness)
- Job queue metrics
- User activity tracking

**Usage**:
```python
from consultantos.agents.dashboard_analytics_agent import DashboardAnalyticsAgent

agent = DashboardAnalyticsAgent()
result = await agent.execute({
    "user_id": "user123",
    "days": 30
})
```

**API Endpoint**: `GET /dashboard/analytics`

---

### 2. ✅ DashboardDataAgent

**Location**: `consultantos/agents/dashboard_data_agent.py`

**Purpose**: Aggregates dashboard overview data efficiently

**Features**:
- Consolidates monitors, stats, alerts, jobs, and reports
- Single endpoint for dashboard initialization
- Reduces waterfall requests
- Parallel data gathering

**Usage**:
```python
from consultantos.agents.dashboard_data_agent import DashboardDataAgent

agent = DashboardDataAgent()
result = await agent.execute({
    "user_id": "user123",
    "alert_limit": 10,
    "report_limit": 5
})
```

**API Endpoint**: `GET /dashboard/overview`

---

### 3. ✅ ReportManagementAgent

**Location**: `consultantos/agents/report_management_agent.py`

**Purpose**: Handles report listing, filtering, searching, and actions

**Features**:
- Full report list with pagination
- Advanced filtering (company, industry, framework, status, date range)
- Keyword search
- Report actions (delete, archive)
- Export support (future)

**Usage**:
```python
from consultantos.agents.report_management_agent import ReportManagementAgent

agent = ReportManagementAgent()

# List reports
result = await agent.execute({
    "action": "list",
    "user_id": "user123",
    "page": 1,
    "page_size": 50
})

# Filter reports
result = await agent.execute({
    "action": "filter",
    "user_id": "user123",
    "filters": {
        "company": "Tesla",
        "status": "completed"
    }
})

# Search reports
result = await agent.execute({
    "action": "search",
    "user_id": "user123",
    "search_query": "electric vehicles"
})
```

**API Endpoint**: `GET /dashboard/reports` (with query params for filtering)

---

### 4. ✅ JobManagementAgent

**Location**: `consultantos/agents/job_management_agent.py`

**Purpose**: Handles job queue, progress tracking, and history

**Features**:
- Job queue dashboard
- Real-time progress tracking
- Job history (completed and failed)
- Job actions (cancel, retry)
- Job analytics

**Usage**:
```python
from consultantos.agents.job_management_agent import JobManagementAgent

agent = JobManagementAgent()

# List active jobs
result = await agent.execute({
    "action": "list",
    "user_id": "user123",
    "status": "pending,running"
})

# Get job status
result = await agent.execute({
    "action": "status",
    "job_id": "job123"
})

# Cancel job
result = await agent.execute({
    "action": "cancel",
    "job_id": "job123",
    "user_id": "user123"
})
```

**API Endpoint**: `GET /dashboard/jobs`

---

## Agents to Implement

### 5. NotificationAgent (Phase 2)

**Purpose**: Manages notification center and preferences

**Features**:
- Notification center with filtering
- Notification preferences management
- Real-time notification updates
- Notification history

**Priority**: 🟡 Medium

---

### 6. VersionControlAgent (Phase 2)

**Purpose**: Handles version history and comparison

**Features**:
- Version history timeline
- Version comparison (diff view)
- Version rollback
- Version labels and notes

**Priority**: 🟡 Medium

---

### 7. TemplateAgent (Phase 3)

**Purpose**: Manages template gallery and custom frameworks

**Features**:
- Template gallery browsing
- Template preview
- Template usage stats
- Custom framework builder

**Priority**: 🟢 Low

---

### 8. VisualizationAgent (Phase 3)

**Purpose**: Generates and manages visualizations

**Features**:
- Visualization gallery
- Chart builder
- Chart embedding
- Multiple chart types

**Priority**: 🟡 Medium

---

### 9. AlertFeedbackAgent (Phase 3)

**Purpose**: Handles alert feedback and improvement

**Features**:
- Alert feedback forms
- Alert details view
- Alert improvement tracking
- Feedback analytics

**Priority**: 🟡 Medium

---

## API Endpoints to Create

### Dashboard Endpoints

```python
# consultantos/api/dashboard_agents_endpoints.py

@router.get("/dashboard/overview")
async def get_dashboard_overview(
    user_id: str = Depends(get_current_user_id),
    alert_limit: int = Query(10),
    report_limit: int = Query(5)
):
    """Get consolidated dashboard overview"""
    agent = DashboardDataAgent()
    result = await agent.execute({
        "user_id": user_id,
        "alert_limit": alert_limit,
        "report_limit": report_limit
    })
    return result["data"]

@router.get("/dashboard/analytics")
async def get_dashboard_analytics(
    user_id: str = Depends(get_current_user_id),
    days: int = Query(30)
):
    """Get dashboard analytics"""
    agent = DashboardAnalyticsAgent()
    result = await agent.execute({
        "user_id": user_id,
        "days": days
    })
    return result["data"]

@router.get("/dashboard/reports")
async def list_reports(
    user_id: str = Depends(get_current_user_id),
    action: str = Query("list"),
    page: int = Query(1),
    page_size: int = Query(50),
    company: Optional[str] = None,
    industry: Optional[str] = None,
    status: Optional[str] = None,
    search_query: Optional[str] = None
):
    """List, filter, or search reports"""
    agent = ReportManagementAgent()
    
    input_data = {
        "action": action,
        "user_id": user_id,
        "page": page,
        "page_size": page_size
    }
    
    if action == "filter":
        input_data["filters"] = {
            "company": company,
            "industry": industry,
            "status": status
        }
    elif action == "search":
        input_data["search_query"] = search_query
    
    result = await agent.execute(input_data)
    return result["data"]

@router.get("/dashboard/jobs")
async def list_jobs(
    user_id: str = Depends(get_current_user_id),
    action: str = Query("list"),
    status: Optional[str] = None,
    job_id: Optional[str] = None,
    limit: int = Query(50)
):
    """List jobs, get status, or manage jobs"""
    agent = JobManagementAgent()
    
    result = await agent.execute({
        "action": action,
        "user_id": user_id,
        "status": status,
        "job_id": job_id,
        "limit": limit
    })
    return result["data"]
```

---

## Frontend Integration

### Update Dashboard Page

```typescript
// frontend/app/dashboard/page.tsx

// Replace sequential fetching with single overview call
async function loadDashboardData() {
  try {
    setLoading(true);
    const apiKey = getApiKey() || '';
    
    // Single consolidated call
    const overviewRes = await fetch(`${API_URL}/dashboard/overview`, {
      headers: { 'X-API-Key': apiKey }
    });
    
    if (!overviewRes.ok) throw new Error('Failed to load dashboard');
    
    const overview = await overviewRes.json();
    
    setMonitors(overview.monitors || []);
    setStats(overview.stats || {});
    setRecentAlerts(overview.recent_alerts || []);
    setActiveJobs(overview.active_jobs || []);
    setRecentReports(overview.recent_reports || []);
    
    setError(null);
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to load dashboard');
  } finally {
    setLoading(false);
  }
}

// Add analytics loading
async function loadAnalytics() {
  try {
    const apiKey = getApiKey() || '';
    const analyticsRes = await fetch(`${API_URL}/dashboard/analytics?days=30`, {
      headers: { 'X-API-Key': apiKey }
    });
    
    if (analyticsRes.ok) {
      const analytics = await analyticsRes.json();
      setAnalytics(analytics);
    }
  } catch (err) {
    console.error('Failed to load analytics:', err);
  }
}
```

---

## Implementation Status

### Phase 1: Core Functionality (High Priority) ✅

- [x] DashboardAnalyticsAgent
- [x] DashboardDataAgent
- [x] ReportManagementAgent
- [x] JobManagementAgent
- [ ] API endpoints for dashboard agents
- [ ] Frontend integration

### Phase 2: Core Enhancements (Medium Priority)

- [ ] NotificationAgent
- [ ] VersionControlAgent
- [ ] API endpoints
- [ ] Frontend integration

### Phase 3: Advanced Features (Lower Priority)

- [ ] TemplateAgent
- [ ] VisualizationAgent
- [ ] AlertFeedbackAgent
- [ ] API endpoints
- [ ] Frontend integration

---

## Next Steps

1. **Create API Endpoints** (Priority: High)
   - Add `dashboard_agents_endpoints.py` router
   - Register router in `main.py`
   - Add authentication and error handling

2. **Update Frontend** (Priority: High)
   - Replace sequential fetching with `/dashboard/overview`
   - Add analytics dashboard section
   - Add report management UI with filtering
   - Add job queue UI

3. **Testing** (Priority: High)
   - Unit tests for each agent
   - Integration tests for API endpoints
   - E2E tests for dashboard workflows

4. **Documentation** (Priority: Medium)
   - API documentation
   - Agent usage examples
   - Frontend integration guide

---

## Benefits of Agent-Based Approach

1. **Separation of Concerns**: Each agent handles one domain
2. **Testability**: Agents can be tested independently
3. **Reusability**: Agents can be used in multiple contexts
4. **Scalability**: Agents can be optimized or replaced individually
5. **Maintainability**: Clear boundaries and responsibilities
6. **Consistency**: All agents follow the same pattern (BaseAgent)

---

**Last Updated**: 2025-11-10  
**Maintainer**: ConsultantOS Team

