# Dashboard Features Gap Analysis

**Last Updated**: 2025-11-10  
**Purpose**: Identify features available in ConsultantOS that are not yet integrated into the dashboard UI

## Current Dashboard Implementation

### Main Dashboard (`/app/page.tsx`)

- ✅ Recent reports list (last 5)
- ✅ Active jobs count
- ✅ Basic metrics (total reports, reports this month, avg confidence)
- ✅ Quick actions navigation

### Monitoring Dashboard (`/app/dashboard/page.tsx`)

- ✅ Monitor list with status
- ✅ Monitor controls (pause/resume, manual check)
- ✅ Alert feed (recent 10 alerts)
- ✅ Dashboard statistics (monitors, alerts counts)
- ✅ Auto-refresh (30s interval)

### Observed UX & Architecture Gaps

- ⚠️ **Sequential Fetching**: `loadDashboardData` performs serial calls + per-monitor loops, causing slow paints and duplicative requests. Replace with `Promise.all` or a consolidated `/dashboard/overview` endpoint.
- ⚠️ **Unhandled Error States**: `error` state is set but never rendered; users see blank cards when APIs fail.
- ⚠️ **Unused State Hooks**: `selectedMonitor` is defined yet unused—ideal for a detail drawer hosting deeper analytics and collaboration features.
- ⚠️ **Component Silos**: Rich widgets (e.g., `InteractiveDashboard`, `ScenarioPlanner`, `NotificationCenter`) exist but are not wired into `/dashboard`. Bridging them would surface live metrics, what-if analysis, and notifications without context switching.
- ⚠️ **Limited Information Density**: Key API responses already include `avg_alert_confidence`, `top_change_types`, and job data that never reach the UI. Visual encodings (sparklines, tags, badges) are missing, reducing at-a-glance value.

### Component Integration Opportunities

| Component                                                              | Location                                           | Current Status                 | Dashboard Opportunity                                                                       |
| ---------------------------------------------------------------------- | -------------------------------------------------- | ------------------------------ | ------------------------------------------------------------------------------------------- |
| `InteractiveDashboard`                                                 | `frontend/app/components/InteractiveDashboard.tsx` | Used only on `/dashboard/[id]` | Embed as a live preview panel per monitor or a hero widget showing real-time KPIs + alerts. |
| `ScenarioPlanner`                                                      | `frontend/app/components/ScenarioPlanner.tsx`      | Standalone tool                | Mount inside a monitor detail drawer to act on alerts with what-if analysis.                |
| `NotificationCenter`                                                   | `frontend/app/components/NotificationCenter.tsx`   | Available but not mounted      | Place in global header to unify alert/jobs/comment notifications.                           |
| Data table primitives (`DataTable`, `TableFilters`, `TablePagination`) | `frontend/app/components`                          | Not used on monitors page      | Power filterable, sortable monitors/reports tables with column visibility + saved views.    |
| `JobHistory`, `JobQueue`, `JobStatusIndicator`                         | `frontend/app/components`                          | Used in jobs area only         | Surface job status per monitor/report, align with Job Management gaps below.                |
| `MetricCard`, `Card`, `Badge` variants                                 | `frontend/app/components/ui`                       | Partially used                 | Standardize dashboard metrics + add confidence/velocity cues across sections.               |

---

## Features NOT Integrated into Dashboard

### 1. Analytics & Metrics (High Priority)

**Available Endpoints:**

- `GET /analytics/productivity` - Productivity metrics
- `GET /analytics/business` - Business metrics
- `GET /analytics/dashboard` - Comprehensive dashboard analytics
- `GET /analytics/reports/{report_id}` - Report-specific analytics
- `GET /analytics/shares/{share_id}` - Share analytics

**Missing Features:**

- ❌ **Productivity Metrics**: Reports per day, average processing time, success rate
- ❌ **Business Metrics**: Revenue impact, client engagement, framework usage
- ❌ **Dashboard Analytics**:
  - Report status pipeline (funnel visualization)
  - Confidence score distribution (histogram)
  - Analysis type breakdown (pie chart)
  - Job queue performance metrics
  - Framework effectiveness scores
  - User activity calendar heatmap
- ❌ **Report Analytics**: Share counts, access counts, comment counts per report
- ❌ **Share Analytics**: Access patterns, geographic distribution

**Suggested UI Integration:**

- Drop the productivity + business KPI cards into the primary dashboard hero using `MetricCard` + sparklines from `PlotlyChart`.
- Use `InteractiveDashboard` sections (`sections` array) to render configurable charts fed by `/analytics/dashboard` data (funnel, histogram, pie).
- Attach per-report analytics in the report list drawer, leveraging `ShareAnalytics` data to show mini heatmaps.

**Integration Priority**: 🔴 **HIGH** - These provide valuable insights for users

---

### 2. Report Management Features

**Available Endpoints:**

- `GET /reports` - List all reports (with filtering)
- `GET /reports/{report_id}` - Get report details
- `POST /enhanced-reports/generate` - Generate enhanced reports
- `GET /reports/{report_id}/versions` - Version history

**Missing Features:**

- ❌ **Full Report List**: Currently only shows 5 recent reports
- ❌ **Report Filtering**: Filter by company, industry, framework, date range
- ❌ **Report Search**: Search reports by keywords
- ❌ **Report Status**: Visual status indicators (processing, completed, failed)
- ❌ **Enhanced Reports**: Actionable insights, risk scoring, scenario planning
- ❌ **Report Versions**: Version history and comparison view
- ❌ **Report Export**: Quick export buttons (PDF, JSON, Excel, Word)
- ❌ **Report Actions**: Delete, archive, duplicate reports

**Integration Priority**: 🔴 **HIGH** - Core functionality for report management

**Suggested UI Integration:**

- Replace the static “recent reports” list with `DataTable` + `TableFilters` for full filtering/search.
- Extend report rows into expandable panels hosting `ShareAnalytics`, comment counts, and quick actions (export, regenerate, compare versions).
- Reuse `TemplateCard` visuals to preview enhanced reports, linking to `ScenarioPlanner` and `VersionHistory` where relevant.

---

### 3. Templates & Custom Frameworks

**Available Endpoints:**

- `GET /templates` - List templates
- `GET /templates/{template_id}` - Get template details
- `POST /templates` - Create template
- `GET /custom-frameworks` - List custom frameworks
- `POST /custom-frameworks` - Create custom framework

**Missing Features:**

- ❌ **Template Gallery**: Browse available templates
- ❌ **Template Preview**: Preview template structure
- ❌ **Template Usage Stats**: How often each template is used
- ❌ **Custom Framework Builder**: UI for creating custom frameworks
- ❌ **Framework Library**: Browse all available frameworks (built-in + custom)
- ❌ **Template Recommendations**: Suggest templates based on industry/company

**Integration Priority**: 🟡 **MEDIUM** - Useful for power users

**Suggested UI Integration:**

- Add a “Templates” tab within the dashboard using `TemplateLibrary` and `TemplateFilters` components.
- Surface template usage stats alongside each card via `Badge` counters fed by analytics endpoints.

---

### 4. Sharing & Collaboration

**Available Endpoints:**

- `POST /shares` - Create share link
- `GET /shares/{share_id}` - Get share details
- `GET /shares/report/{report_id}` - List shares for report
- `DELETE /shares/{share_id}` - Revoke share

**Missing Features:**

- ❌ **Share Management**: List all active shares
- ❌ **Share Analytics**: View counts, access patterns
- ❌ **Quick Share**: One-click share button on reports
- ❌ **Share Permissions**: View/edit permission management
- ❌ **Share Expiration**: Set expiration dates
- ❌ **Share Notifications**: Notify when reports are accessed

**Integration Priority**: 🔵 **DEFERRED** - Moved to Future Work

**Suggested UI Integration:**

- Inline "Share" button on report rows invoking `ShareDialog` and `ShareSettings` modals.
- Notification hooks via `NotificationCenter` when shares are accessed or comments posted.

---

### 5. Comments & Community

**Available Endpoints:**

- `POST /comments` - Add comment
- `GET /comments/report/{report_id}` - Get comments for report
- `PUT /comments/{comment_id}` - Update comment
- `DELETE /comments/{comment_id}` - Delete comment
- `GET /community/trending` - Trending reports
- `GET /community/popular` - Popular frameworks

**Missing Features:**

- ❌ **Comment Threads**: View and reply to comments on reports
- ❌ **Comment Notifications**: Notify on new comments
- ❌ **Comment Count Badge**: Show comment count on reports
- ❌ **Community Feed**: Trending and popular content
- ❌ **Community Insights**: Most shared frameworks, popular companies

**Integration Priority**: 🔵 **DEFERRED** - Moved to Future Work

**Suggested UI Integration:**

- Attach `CommentThread` + `CommentNotifications` to report detail drawers.
- Add a right-rail "Community" card showing data from `/community/trending` using `Card` + `List` patterns.

---

### 6. Version Control

**Available Endpoints:**

- `POST /versions` - Create new version
- `GET /versions/report/{report_id}` - Get version history
- `GET /versions/{version_id}` - Get specific version
- `POST /versions/{version_id}/publish` - Publish version

**Missing Features:**

- ❌ **Version History Timeline**: Visual timeline of report versions
- ❌ **Version Comparison**: Side-by-side diff view
- ❌ **Version Labels**: Tag versions (draft, published, archived)
- ❌ **Version Rollback**: Restore previous version
- ❌ **Version Notes**: Changelog for each version

**Integration Priority**: 🟡 **MEDIUM** - Important for document management

**Suggested UI Integration:**

- Introduce a `VersionHistory` tab per report leveraging `VersionComparison` + `VersionRestore` components for diff + rollback flows.

---

### 7. Job Management

**Available Endpoints:**

- `GET /jobs` - List jobs (with status filtering)
- `GET /jobs/{job_id}` - Get job status
- `POST /jobs/{job_id}/cancel` - Cancel job

**Missing Features:**

- ❌ **Job Queue Dashboard**: Full job list with status
- ❌ **Job Progress**: Real-time progress indicators
- ❌ **Job History**: Completed and failed jobs
- ❌ **Job Details**: View job parameters, results, errors
- ❌ **Job Actions**: Cancel, retry failed jobs
- ❌ **Job Analytics**: Average processing time, success rate

**Integration Priority**: 🟡 **MEDIUM** - Currently only shows count

**Suggested UI Integration:**

- Embed `JobHistory`, `JobQueue`, and `JobStatusIndicator` components into the dashboard to replace the bare counter.
- Highlight job failures within the monitor cards and provide retry/cancel buttons using the existing job endpoints.

---

### 8. Notifications

**Available Endpoints:**

- `GET /notifications` - List notifications
- `POST /notifications/{notification_id}/read` - Mark as read
- `PUT /monitors/{monitor_id}/notification-preferences` - Update preferences

**Missing Features:**

- ❌ **Notification Center**: Dedicated notification panel
- ❌ **Notification Types**: Filter by type (alerts, comments, shares, jobs)
- ❌ **Notification Preferences**: Configure notification channels
- ❌ **Notification History**: View past notifications
- ❌ **Real-time Notifications**: WebSocket/polling for new notifications

**Integration Priority**: 🟡 **MEDIUM** - Improves user engagement

**Suggested UI Integration:**

- Mount `NotificationCenter` in the global navigation bar, hooking into WebSocket or polling for unread counts.
- Offer monitor-level notification toggles via `NotificationSettings` component tied to `/monitors/{id}/notification-preferences`.

---

### 9. Knowledge Base

**Available Endpoints:**

- `POST /knowledge/query` - Query knowledge base
- `POST /knowledge/documents` - Add document
- `GET /knowledge/documents` - List documents

**Missing Features:**

- ❌ **Knowledge Base Search**: Search across all stored knowledge
- ❌ **Document Management**: Upload, organize, tag documents
- ❌ **Knowledge Insights**: Related documents, topics
- ❌ **Knowledge Analytics**: Most accessed documents

**Integration Priority**: 🟢 **LOW** - Advanced feature

**Suggested UI Integration:**

- Provide a search drawer that queries `/knowledge/query` and renders results with `DataTable` or a simple list.
- Allow uploading/tagging through a modal built on `Modal` + `Input` primitives.

---

### 10. Saved Searches

**Available Endpoints:**

- `POST /saved-searches` - Create saved search
- `GET /saved-searches` - List saved searches
- `DELETE /saved-searches/{search_id}` - Delete saved search

**Missing Features:**

- ❌ **Saved Searches List**: View all saved searches
- ❌ **Quick Search**: Execute saved search with one click
- ❌ **Search History**: Recent searches
- ❌ **Search Suggestions**: Auto-complete suggestions

**Integration Priority**: 🟢 **LOW** - Nice-to-have feature

**Suggested UI Integration:**

- Add a “Saved Searches” dropdown above the primary tables, persisting selections via the saved-search APIs.

---

### 11. Advanced Analysis Features

**Available Endpoints:**

- `POST /integration/comprehensive` - Comprehensive analysis
- `POST /forecasting/generate` - Generate forecasts
- `POST /wargaming/simulate` - Run wargaming scenarios
- `POST /conversational/query` - Conversational AI queries
- `POST /social-media/insights` - Social media analysis

**Missing Features:**

- ❌ **Forecasting Dashboard**: View forecast results and scenarios
- ❌ **Wargaming Results**: Scenario simulation outcomes
- ❌ **Conversational AI Chat**: Chat interface for querying reports
- ❌ **Social Media Insights**: Sentiment analysis, trending topics
- ❌ **Dark Data Analysis**: Alternative data insights
- ❌ **Integration Status**: Status of comprehensive analyses

**Integration Priority**: 🟡 **MEDIUM** - Advanced analytics features

**Suggested UI Integration:**

- Incorporate tabs for Forecasting, Wargaming, and Conversational Chat adjacent to monitors, reusing `ForecastChart`, `ScenarioPlanner`, and `ChatDemo` components.
- Display “analysis readiness” badges per monitor to show whether required data inputs are configured.

---

### 12. Visualizations

**Available Endpoints:**

- `POST /visualizations/generate` - Generate visualization
- `GET /visualizations/{viz_id}` - Get visualization

**Missing Features:**

- ❌ **Visualization Gallery**: Browse generated visualizations
- ❌ **Chart Builder**: Interactive chart creation
- ❌ **Visualization Embedding**: Embed charts in reports
- ❌ **Chart Types**: Line, bar, pie, scatter, heatmap, etc.

**Integration Priority**: 🟡 **MEDIUM** - Enhances report presentation

**Suggested UI Integration:**

- Provide a Visualization Gallery grid populated via `TemplateCard` styling, each card opening a modal with the `PlotlyChart` component.
- Allow drag-to-embed interactions in report detail view so charts can be pinned to monitors.

---

### 13. Alert Feedback & Improvement

**Available Endpoints:**

- `POST /monitors/alerts/{alert_id}/feedback` - Submit alert feedback
- `GET /monitors/alerts/{alert_id}` - Get alert details

**Missing Features:**

- ❌ **Alert Feedback Form**: Rate alert quality, provide feedback
- ❌ **Alert Details View**: Full alert details with changes detected
- ❌ **Alert Actions**: Mark as false positive, take action
- ❌ **Alert History**: View past alerts and feedback
- ❌ **Alert Improvement**: System learns from feedback

**Integration Priority**: 🟡 **MEDIUM** - Improves alert quality

**Suggested UI Integration:**

- Add an expandable “Alert Details” panel in the Recent Alerts list, surfaced via `Modal` + `Alert` components.
- Include a short feedback form (radio buttons + textarea) posting to `/monitors/alerts/{alert_id}/feedback`; show aggregate feedback per monitor to close the loop.

---

### 14. Notification Preferences

**Available Endpoints:**

- `PUT /monitors/{monitor_id}/notification-preferences` - Update preferences
- `POST /notifications/test` - Test notification

**Missing Features:**

- ❌ **Notification Settings Panel**: Configure notification channels
- ❌ **Channel Configuration**: Email, Slack, webhook setup
- ❌ **Notification Rules**: When to send notifications
- ❌ **Test Notifications**: Test notification delivery

**Integration Priority**: 🟡 **MEDIUM** - Important for user control

**Suggested UI Integration:**

- Create a “Notification Settings” drawer accessible from the header avatar, using `NotificationSettings` + `Toggle` components to map channel + severity preferences.

---

### 15. User Profile & Settings

**Available Endpoints:**

- `GET /users/me` - Get user profile
- `PUT /users/me` - Update profile
- `GET /auth/api-keys` - List API keys
- `POST /auth/api-keys` - Create API key

**Missing Features:**

- ❌ **User Profile Page**: View and edit profile
- ❌ **API Key Management**: Create, revoke, view API keys
- ❌ **Usage Statistics**: Personal usage metrics
- ❌ **Account Settings**: Preferences, billing, security

**Integration Priority**: 🟡 **MEDIUM** - Essential for user management

**Suggested UI Integration:**

- Introduce a `/profile` dashboard section employing `ProfileSettings`, `ShareSettings`, and API key management UI to keep users inside the same experience.

---

## Disabled Features (Not Available)

These features exist in codebase but are disabled:

- ❌ **Teams** (`teams_router` - commented out)
- ❌ **History** (`history_router` - commented out)
- ❌ **Digest** (`digest_router` - commented out)
- ❌ **Feedback** (`feedback_router` - commented out)
- ❌ **Storytelling** (`storytelling_router` - not implemented)

**Note**: These would need to be enabled in `main.py` before integration.

---

## Recommended Integration Priority

### Phase 1: Core Functionality (High Priority)

1. **Full Report Management**

   - Complete report list with filtering
   - Report search
   - Report actions (delete, archive, export)
   - Report status indicators

2. **Analytics Dashboard**

   - Dashboard analytics endpoint integration
   - Productivity metrics
   - Business metrics
   - Report analytics

3. **Job Management**
   - Full job queue view
   - Job progress tracking
   - Job history

### Phase 2: Core Enhancements (Medium Priority)

4. **Version Control**

   - Version history timeline
   - Version comparison

5. **Notifications**
   - Notification center
   - Notification preferences

### Phase 3: Advanced Features (Lower Priority)

6. **Templates & Frameworks**

   - Template gallery
   - Custom framework builder

7. **Advanced Analytics**

   - Forecasting dashboard
   - Wargaming results
   - Conversational AI chat

8. **Visualizations**
   - Chart gallery
   - Chart builder

### Future Work (Deferred)

9. **Sharing & Collaboration**

   - Share management UI
   - Share analytics
   - Quick share functionality
   - Share permissions management

10. **Comments & Community**

- Comment threads
- Comment notifications
- Community feed
- Community insights

### Cross-Cutting Design Recommendations

- **Consolidate Data Fetching**: Ship a dedicated `/dashboard/overview` endpoint (monitors + stats + alerts + jobs) to reduce waterfall latency and simplify suspense/loading states.
- **Modular Layout**: Reuse the `Card` grid system from `InteractiveDashboard` so every section (monitors, analytics, jobs, comments) follows a consistent visual rhythm; add skeleton loaders for each card.
- **Detail Drawer Pattern**: Utilize the unused `selectedMonitor` state to open a right-hand drawer containing tabs (Overview, Jobs, Comments, Versions, Templates) for deep actions without navigation.
- **Global Notification Bar**: Mount `NotificationCenter` + job indicators in the header so collaboration feedback is omnipresent.
- **Theming & Density**: Apply Tailwind’s `bg-slate-900`/`bg-slate-50` combos with accent badges to clarify severity, and add micro-interactions (hover states, tooltips) for high-density tables.

---

## Implementation Notes

### API Integration Status

**Fully Available:**

- ✅ Analytics endpoints (productivity, business, dashboard)
- ✅ Report management endpoints
- ✅ Sharing endpoints
- ✅ Comments endpoints
- ✅ Versioning endpoints
- ✅ Jobs endpoints
- ✅ Templates endpoints
- ✅ Custom frameworks endpoints
- ✅ Saved searches endpoints
- ✅ Notifications endpoints
- ✅ Enhanced reports endpoints
- ✅ Visualization endpoints
- ✅ Knowledge base endpoints
- ✅ Advanced analysis endpoints (forecasting, wargaming, conversational)

**Partially Available:**

- ⚠️ Monitoring endpoints (enabled but not fully integrated in main router)
- ⚠️ Dashboard builder endpoints (exists but separate from main dashboard)

### Frontend Component Readiness

- ✅ UI primitives (cards, badges, tables, modals) live under `frontend/app/components/ui` and align with Tailwind theme tokens.
- ✅ Specialized widgets (InteractiveDashboard, ScenarioPlanner, JobHistory, NotificationCenter) are production-ready but require props/data wiring inside `/app/dashboard/page.tsx`.
- ⚠️ State management currently relies on local `useState` + imperative `fetch`; consider migrating critical dashboard data to React Query or SWR for caching, refetch controls, and optimistic updates.
- ⚠️ WebSocket hooks (`useWebSocket`) exist for live dashboards but are unused in the main monitors page—ideal for real-time alert + job updates.

**Disabled:**

- ❌ Teams endpoints
- ❌ History endpoints
- ❌ Digest endpoints
- ❌ Feedback endpoints
- ❌ Storytelling endpoints

### Frontend Components Available

Based on codebase analysis, these components exist and could be reused:

- `DataTable` - For lists
- `MetricCard` - For metrics
- `Badge` - For status indicators
- `Button` - For actions
- `Alert` - For notifications
- Various form components

### Suggested Dashboard Layout

**Main Dashboard Enhancement:**

```
┌─────────────────────────────────────────────────┐
│  Header: Intelligence Dashboard                 │
├─────────────────────────────────────────────────┤
│  Stats Row: 4-6 metric cards                    │
│  [Total Reports] [Active Jobs] [Alerts] [etc]   │
├─────────────────────────────────────────────────┤
│  Tabs: Reports | Monitors | Analytics | Jobs    │
├─────────────────────────────────────────────────┤
│  Content Area (tab-specific)                    │
│  - Reports: Full list with filters              │
│  - Monitors: Current monitor list                │
│  - Analytics: Charts and metrics                │
│  - Jobs: Job queue and history                   │
└─────────────────────────────────────────────────┘
```

**Sidebar (Optional):**

- Quick actions
- Recent activity
- Notifications
- Saved searches

---

## Next Steps

1. **Audit Current Implementation**: Review what's actually working vs. what's documented
2. **Prioritize Features**: Based on user feedback and usage patterns
3. **Design Mockups**: Create UI mockups for high-priority features
4. **Implement Incrementally**: Start with Phase 1 features
5. **Test & Iterate**: Gather user feedback and refine

---

**Last Updated**: 2025-11-10  
**Maintainer**: ConsultantOS Team
