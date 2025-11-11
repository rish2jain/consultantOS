# ConsultantOS Frontend Architecture - Comprehensive Overview

## 1. PROJECT STRUCTURE & TECH STACK

### Technology Stack
- **Framework**: Next.js 16 (App Router - React 18)
- **Language**: TypeScript 5.9.2
- **Styling**: Tailwind CSS 4.0+ (⚠️ **Breaking Changes**: Tailwind CSS 4.0 introduced significant changes since January 2025. See migration notes below)
- **UI Components**: Custom component library (shadcn-inspired)
- **Visualization**: D3.js 7.9, Recharts 2.10, Plotly.js
- **Animation**: Framer Motion 12.23.24
- **Data Fetching**: Axios 1.6, TanStack React Query 5.90.7
- **Icons**: Lucide React 0.553.0
- **Testing**: Jest 30.0.0, Puppeteer 24.29.1 (E2E)
- **Date Handling**: date-fns 2.30
- **Build**: Next.js built-in (Turbopack)

**Tailwind CSS 4.0 Migration Notes**:
- Tailwind CSS 4.0 introduced breaking changes in January 2025, including:
  - New CSS-first configuration approach
  - Updated plugin system
  - Changes to custom property handling
  - Updated color system and opacity syntax
- Migration guidance: Review [Tailwind CSS 4.0 migration guide](https://tailwindcss.com/docs/upgrade-guide) before upgrading
- **Current project status**: Intentionally pinned to Tailwind CSS 3.3.0 in package.json for stability. The documented version (4.0+) reflects the latest available version, but the project uses 3.x until migration is completed.

### Project Version
- **Version**: 0.4.0
- **Node Port**: 3000
- **Backend Port**: 8080

---

## 2. PAGES & ROUTES (Next.js App Directory)

### Core Pages
```
/                           → Home/Dashboard Landing Page
├── page.tsx                 Hero section with quick actions
├── layout.tsx               Root layout with Navigation + Footer

/analysis                   → Analysis Request Page
├── page.tsx                 Two-tab interface (Quick/Async analysis forms)

/reports                    → Reports List/Manager
├── page.tsx                 Paginated, filterable report list with search
└── [id]/page.tsx            Single report detail view with tabs

/dashboard                  → Real-Time Monitoring Dashboard
├── page.tsx                 Overview of analytics, metrics, recent reports
├── [id]/page.tsx            Individual dashboard instance
└── strategic-intelligence/  → Strategic Intelligence Dashboard
    └── page.tsx             Advanced competitive intelligence views

/jobs                       → Job Queue & History
├── page.tsx                 Async job monitoring with queue visualization

/templates                  → Template Library & Creator
├── page.tsx                 Template browsing, filtering, creation

/analytics                  → Business Intelligence & Metrics
├── page.tsx                 Productivity, business, and usage analytics

/profile                    → User Profile & Settings
├── page.tsx                 Account settings, preferences, notifications

/mvp-demo                   → Hackathon MVP Demonstration
├── page.tsx                 Chat demo + forecasting visualization showcase

/login                      → User Authentication
├── page.tsx                 Login form with API key entry

/register                   → User Registration
├── page.tsx                 Registration form with email verification
```

### Key Page Components
- **Dynamic Routes**: `[id]` for parameterized routes (reports, dashboards)
- **Layout Structure**: Root layout with Navigation + children + Footer
- **Rendering**: Mix of static (SSG) and dynamic (force-dynamic for useSearchParams)
- **Suspense**: Lazy loading of heavy components

---

## 3. COMPONENT ARCHITECTURE

### Directory Structure
```
components/
├── index.ts                 Central exports (70+ components)
├── ui/                      Base UI components (6 files)
│   ├── button.tsx
│   ├── card.tsx
│   ├── badge.tsx
│   ├── label.tsx
│   ├── slider.tsx
│   └── switch.tsx
├── analytics/               KPI and formula builder
│   ├── KPIWidget.tsx
│   └── FormulaBuilder.tsx
├── storytelling/            Narrative and persona components
│   ├── NarrativeViewer.tsx
│   ├── PersonaSelector.tsx
│   └── index.ts
└── user-management/         User-related components (index only)
```

### Core UI Component Library (50+ Components)
✓ **Basic Components**: Button, Input, Card, Badge, Tooltip, Modal
✓ **Data Display**: DataTable, MetricCard, DataTableSkeleton
✓ **Forms**: AnalysisRequestForm, AsyncAnalysisForm, FrameworkSelector
✓ **Tables**: TablePagination, TableSort, TableFilters, TableActions
✓ **Feedback**: Alert (5 variants), Spinner (5 variants), LoadingStates
✓ **Navigation**: Navigation (top bar), Tabs, Dropdown
✓ **Job Management**: JobStatusIndicator, JobQueue, JobHistory

### Advanced Visualization Components (4 Main)
1. **CompetitivePositioningMap** - D3.js force-directed bubble chart
   - Market share vs profit margin visualization
   - Movement vectors showing trajectory
   - 12-month historical replay with time scrubber
   - Zoom/pan controls

2. **DisruptionRadar** - 5-dimensional risk assessment
   - Radar chart with Christensen disruption theory
   - 5 dimensions: incumbent overserving, asymmetric threat velocity, 
     technology shift, customer job misalignment, business model innovation
   - Threat detail cards with urgency indicators
   - Risk trend sparklines

3. **DecisionCard** - Strategic decision management
   - Urgency countdown timer (7/30/90/∞ days)
   - Financial impact visualization
   - Options comparison table with pros/cons
   - Implementation roadmap timeline
   - Accept/Defer/Customize actions

4. **StrategicHealthDashboard** - Executive summary (30-second scan)
   - Overall health gauge (0-100)
   - Top 3 threats (urgency × impact)
   - Top 3 opportunities (ROI × feasibility)
   - Category breakdown: market position, innovation, efficiency, financial
   - 30-day risk trend chart
   - Competitive position mini-map

### Collaboration & Sharing Components
- **CommentThread/CommentForm/CommentCard** - Nested comment threads
- **ShareDialog/ShareList/ShareSettings/ShareAnalytics** - Report sharing with analytics
- **VersionHistory/VersionComparison/VersionRestore** - Version control with diffs

### Template & Job Components
- **TemplateLibrary** - Template browsing and filtering
- **TemplateCard/TemplateDetail** - Template display and metadata
- **TemplateCreator** - Interactive template builder
- **JobStatusIndicator** - Real-time job status with progress
- **JobQueue/JobHistory** - Job management interface

### Form Components
- **AnalysisRequestForm** - Synchronous analysis (quick)
- **AsyncAnalysisForm** - Asynchronous analysis (for long-running)
- **FrameworkSelector** - Multi-select frameworks
- **IndustrySelector** - Industry dropdown with search
- **DepthSelector** - Quick/Standard/Deep analysis depth

### User Management Components
- **RegistrationForm** - User registration with validation
- **EmailVerification** - Email verification flow
- **PasswordResetForm/PasswordResetConfirm** - Password reset flow
- **ProfileSettings** - User account settings
- **NotificationSettings** - Notification preferences

---

## 4. DASHBOARD STRUCTURE & DISPLAY

### Home/Landing Dashboard (`/`)
**Hero Section**:
- Gradient header (blue to indigo)
- Call-to-action buttons: "Try MVP Demo", "Create Analysis", "View Reports"

**Dashboard Overview Metrics**:
- 4 metric cards (2x2 grid):
  1. Total Reports Created (with trend)
  2. Active Jobs (current count)
  3. Reports This Month (monthly breakdown)
  4. Avg Confidence Score (quality metric)
- Skeleton loaders during data fetch

**Recent Reports Section**:
- DataTable with pagination
- Columns: Company, Frameworks (badge list), Date, Status
- Click-through to detail view

**Quick Actions Grid** (4 cards):
1. Create Analysis → `/analysis`
2. Browse Templates → `/templates`
3. View Job Queue → `/jobs`
4. Manage Profile → `/profile`

**Getting Started Guide**:
- 3-step flow: Create Analysis → Review/Share Results → Collaborate

### Real-Time Monitoring Dashboard (`/dashboard`)
- **Metrics**: Total, Active, This Month, Confidence
- **Report Metrics**: DataTable with status, frameworks, dates
- **Graceful Degradation**: Fallback to sample data if API fails
- **Live Updates**: Polls `/api/analysis/list-reports` and `/api/jobs`
- **Error Handling**: Retry button + support contact link

### Strategic Intelligence Dashboard (`/dashboard/strategic-intelligence`)
**Layered Architecture**:
- **Executive Layer** (default): High-level threats/opportunities
- **Context Layer**: Positioning, disruption, dynamics, momentum, decisions
- **Evidence Layer**: Source citations and detailed data

**Components**:
- SystemDynamicsMap - Causal relationships visualization
- FlywheelDashboard - Momentum tracking
- IntelligenceFeed - Real-time intelligence updates
- DecisionCard - Strategic decisions with urgency

**Interaction Model**:
- Tab-based navigation (Executive/Context/Evidence)
- Expandable detail cards
- Refresh button for data sync
- Motion animations with Framer Motion

---

## 5. REPORT DISPLAY & INTERACTION

### Reports List Page (`/reports`)
**Features**:
- **Pagination**: 25 items per page (configurable)
- **Search**: Real-time text search with debounce
- **Sorting**: Sort by created_at, company, status, confidence
- **Filtering**: Filter by status (completed/processing/failed), frameworks
- **Bulk Actions**: 
  - Multi-select with checkboxes
  - Bulk delete with confirmation modal
  - Bulk export (CSV/JSON/Excel)
- **Row Actions**:
  - View (navigate to detail)
  - Share
  - Download PDF
  - Delete with confirmation

**Table Columns**:
| Column | Content | Interactive |
|--------|---------|-------------|
| Company | Name + Industry | Clickable row |
| Frameworks | Badge list | Color-coded by type |
| Created | Formatted date | Sortable |
| Status | Badge (success/warning/error) | Filterable |
| Confidence | Percentage | Sortable |
| Actions | View/Share/Download/Delete | Dropdowns |

**Status Colors**:
- ✅ completed = green
- ⚙️ processing = blue
- ⚠️ failed = red

### Report Detail Page (`/reports/[id]`)
**Header Section**:
- Back button
- Report title: Company + Industry
- Confidence score badge
- Status badge with timestamp
- Share button (dialog)

**Tab Interface** (4 tabs):
1. **Analysis** - Framework results
   - Sub-tabs per framework
   - PORTER: 5 Forces breakdown
   - SWOT: Strengths/Weaknesses/Opportunities/Threats
   - PESTEL: Political/Economic/Social/Technological/Environmental/Legal
   - Blue Ocean: Eliminate/Reduce/Raise/Create matrix
   - Market Insights: Trends + findings
   - Financial Insights: Metrics + findings

2. **Download** - Export options
   - PDF (primary)
   - Excel
   - Word
   - JSON

3. **Comments** - Collaboration
   - Comment thread with nesting
   - Reply functionality
   - Timestamps + user attribution
   - Edit/delete on own comments

4. **Versions** - Version control
   - Version history list
   - Diff comparison between versions
   - Restore to previous version
   - Change summaries

**Framework Display**:
- Filter by "All Frameworks" or individual
- Each framework renders specific structure
- Code blocks for deep dives
- Styled using Tailwind typography

---

## 6. VISUALIZATION COMPONENTS

### Chart Libraries
1. **Recharts** (default):
   - BarChart, LineChart, PieChart
   - ResponsiveContainer for auto-sizing
   - Custom tooltips and legends
   - Used in analytics, forecasting

2. **D3.js** (complex visualizations):
   - Force-directed layouts (CompetitivePositioningMap)
   - Zoom/pan behaviors
   - Simulation-based positioning
   - SVG-based rendering

3. **Plotly.js** (interactive charts):
   - 3D support
   - Advanced interactivity
   - Export to PNG/SVG

### Analytics Visualizations (`/analytics`)
**Productivity Metrics**:
- Reports per day (bar chart)
- Avg processing time (metric)
- Success rate (percentage)
- Template adoption rate

**Business Metrics**:
- Top industries (bar chart)
- Most used frameworks (pie chart)
- Peak usage times (line chart by hour)
- User adoption timeline

**Dashboard Analytics**:
- Report status pipeline (bar chart)
- Confidence distribution (histogram)
- Framework usage distribution

---

## 7. USER FLOW & INTERACTIONS

### Complete User Journey

```
1. LANDING
   ↓
   [Home Dashboard] (/) with hero + metrics + quick actions
   ↓
   ├→ [Create Analysis] → /analysis
   ├→ [View Reports] → /reports
   ├→ [Templates] → /templates
   ├→ [Jobs] → /jobs
   └→ [Profile] → /profile

2. CREATE ANALYSIS
   ↓
   [Analysis Page] (/analysis)
   │ - Two tabs: Quick (sync) vs Async
   │ - Form: Company, Industry, Frameworks, Depth
   ├→ [Quick Analysis] (sync, <5 min)
   │  └→ Direct to /reports/[id]
   └→ [Async Analysis] (enqueued job)
      └→ Redirects to /jobs with job_id

3. VIEW RESULTS
   ↓
   [Reports List] (/reports)
   │ - Paginated, searchable, filterable
   │ - Bulk export/delete
   ├→ [Report Detail] (/reports/[id])
   │  ├─ 4 tabs: Analysis/Download/Comments/Versions
   │  ├→ [Share Report] (dialog)
   │  ├→ [Download PDF/Excel]
   │  ├→ [Add Comments] (collaborate)
   │  └→ [View Versions] (version control)
   └→ [Back to List]

4. MONITOR JOBS
   ↓
   [Jobs Queue] (/jobs)
   │ - Real-time status updates
   │ - Job history with results
   └→ [Job Details Modal] (status breakdown)

5. USE TEMPLATES
   ↓
   [Templates] (/templates)
   │ - Browse library
   │ - Filter by industry/frameworks
   ├→ [Create New] (custom template)
   ├→ [Fork Template] (copy existing)
   └→ [Use Template] (run analysis)

6. ANALYTICS & INSIGHTS
   ↓
   [Analytics] (/analytics)
   │ - Productivity metrics
   │ - Business metrics
   │ - Dashboard metrics
   └→ [Strategic Intelligence] (/dashboard/strategic-intelligence)
      ├─ Executive brief
      ├─ System dynamics
      ├─ Disruption radar
      └─ Decision cards

7. SETTINGS & PROFILE
   ↓
   [Profile] (/profile)
   │ - Account info
   │ - Notification preferences
   └─ [Help & Support]
```

### Key Interaction Patterns

**Data Loading**:
- Skeleton loaders for initial content
- Progressive enhancement (load table, then rows)
- Error states with retry buttons
- Graceful fallback to sample data

**Search & Filter**:
- Debounced search input (300ms)
- Real-time filter updates
- Maintains sort order
- Preserves URL state (querystring)

**Modals & Dialogs**:
- Share dialog (report sharing UI)
- Delete confirmation (destructive actions)
- Job details modal (async operations)
- Theme: Centered, dark overlay, escape-to-close

**Tabs**:
- Keyboard navigation (arrow keys)
- Active indicator
- Content lazy-loaded or pre-rendered
- State preserved while navigating

---

## 8. DATA LAYER & API INTEGRATION

### API Client (`lib/api.ts`)
```typescript
// Centralized API with:
- Retry logic (2 attempts with exponential backoff)
- Timeout handling (10 seconds)
- API key authentication (X-API-Key header)
- Error mapping to APIError class
- JSON/text response handling
- Rate limit retry (429 status)
```

### API Endpoints Structure
```
/analyze                    → Sync analysis
/analyze/async              → Async analysis (job enqueue)
/analysis/list-reports      → Get report list
/analysis/[report_id]       → Get report detail
/reports/[id]/download      → Download report (PDF/Excel)
/jobs                       → Job management
/templates                  → Template CRUD
/monitoring                 → Monitor CRUD & alerts
/sharing                    → Report sharing
/comments                   → Comment threads
/analytics                  → Analytics data
/strategic-intelligence     → Strategic intelligence data
/auth/register              → User registration
/auth/login                 → Authentication
/auth/verify-email          → Email verification
/health                     → Backend health check
```

### Authentication
- **Method**: API Key (X-API-Key header)
- **Storage**: In-memory only (NOT localStorage for security)
- **Lifetime**: Session-based
- **Protected Endpoints**: User-specific features (history, sharing, templates)
- **Public Endpoints**: Work without authentication

### Data Synchronization
- **Polling**: 30-second intervals for dashboard updates
- **Real-time**: WebSocket hooks available (`useWebSocket` hook)
- **Caching**: React Query for deduplication
- **Fallback**: Sample data when API fails

---

## 9. HOOKS & UTILITIES

### Custom Hooks
- **useSort()** - Table sort state management
- **usePagination()** - Pagination state
- **useFilters()** - Table filtering logic
- **useModal()** - Modal open/close state
- **useDropdown()** - Dropdown menu state
- **useTabs()** - Tab navigation state
- **useAlert()** - Alert notification state
- **useWebSocket()** - WebSocket connection management
- **useKeyboardShortcuts()** - Global keyboard shortcuts

### Utility Functions (`app/utils/`)
- **dateFormat.ts** - Date formatting helpers
- **reportTransformers.ts** - API → Frontend data transformation
- **performance.ts** - Performance monitoring utilities

### Authentication (`lib/auth.ts`)
- getApiKey() - Retrieve stored API key
- setApiKey() - Store API key in memory
- clearApiKey() - Clear API key on logout

---

## 10. RESPONSIVE DESIGN & ACCESSIBILITY

### Breakpoints
- **Mobile**: < 640px (sm)
- **Tablet**: 640-1024px (md)
- **Desktop**: > 1024px (lg)
- **Grid**: Responsive cols (1 → 2 → 4)

### Accessibility Features
- Semantic HTML (button, nav, main, section)
- ARIA labels on icons
- Keyboard navigation (Tab, Enter, Escape, Arrow keys)
- Color contrast ≥ 4.5:1
- Focus indicators visible
- Screen reader support
- Live regions for dynamic updates

### Mobile Optimizations
- Hamburger menu for mobile nav
- Responsive grid layouts
- Touch-friendly button sizes (44x44px)
- Bottom sheet modals (when space-constrained)
- Hidden desktop elements (hidden sm:inline)

---

## 11. PERFORMANCE OPTIMIZATIONS

### Code Splitting
- Next.js automatic route-based splitting
- LazyComponents wrapper for heavy components
- Dynamic imports for visualization demos

### Rendering
- Strategic use of `'use client'` for interactivity
- Suspense boundaries for data fetching
- Memoization with useMemo/useCallback
- Image optimization with Next.js Image component

### Data Fetching
- React Query deduplication
- Pagination (not infinite scroll initially)
- Debounced search (300ms)
- Conditional API calls based on user action

### Bundle Size
- D3.js only loaded when needed (DisruptionRadar, etc.)
- Recharts for standard charts (smaller than Chart.js)
- Lucide icons (tree-shakeable)
- Tailwind CSS (production builds optimized)

---

## 12. STATE MANAGEMENT

### State Locations
1. **React State** (useState)
   - Form inputs
   - Modal/dropdown open state
   - Loading indicators
   - Error messages

2. **URL State** (Next.js params & searchParams)
   - Report ID: `/reports/[id]`
   - Page number: `/reports?page=2`
   - Search query: `/reports?q=tesla`
   - Sort: `/reports?sort=created_at&order=desc`

3. **LocalStorage**
   - User data (name, email)
   - Recent analyses (for quick re-runs)
   - User preferences

4. **Session/Memory**
   - API key (for security)
   - Current user context

---

## 13. CONFIGURATION & ENVIRONMENT

### Environment Variables
```bash
NEXT_PUBLIC_API_URL          # Backend URL (default: http://localhost:8080)
NEXT_PUBLIC_ENABLE_DEBUG     # Debug mode
```

### Build Configuration
- **next.config.js**: Webpack optimizations, image optimization
- **tailwind.config.js**: Custom theme, colors, spacing
- **tsconfig.json**: Strict type checking, path aliases (@/)
- **jest.config.js**: E2E test configuration
- **.eslintrc.json**: Code linting rules

---

## 14. CURRENT UI CAPABILITIES & FEATURES

### ✅ IMPLEMENTED
- Multi-page SPA with Next.js 14 App Router
- 70+ reusable components with TypeScript
- Advanced data tables (sort, filter, paginate, bulk actions)
- Report creation and detail views
- PDF/Excel export from reports
- Job queue monitoring
- Template library and management
- Real-time analytics dashboard
- Strategic intelligence visualizations (4 major components)
- Collaboration (comments, sharing, version control)
- User authentication & registration
- Responsive mobile-first design
- Accessibility (WCAG AA standards)
- Error handling with user-friendly messages
- Loading states and skeleton screens
- Notification system

### 🔄 IN PROGRESS / DEMO
- Conversational AI chat interface
- Forecasting visualizations
- System dynamics mapping
- Flywheel momentum tracking
- Real-time WebSocket updates

### 📋 POTENTIAL ENHANCEMENTS
- Dark mode theme
- Advanced charting with Plotly
- Export charts as PNG/SVG
- Collaborative real-time editing
- Custom dashboard builder
- AI-powered insights overlay
- Predictive analytics
- Integration with external BI tools

---

## 15. KEY FILES REFERENCE

### Pages (Main Routes)
- `/app/page.tsx` - Home dashboard
- `/app/analysis/page.tsx` - Analysis creation
- `/app/reports/page.tsx` - Report list
- `/app/reports/[id]/page.tsx` - Report detail
- `/app/dashboard/page.tsx` - Analytics dashboard
- `/app/dashboard/strategic-intelligence/page.tsx` - Strategic intelligence
- `/app/jobs/page.tsx` - Job queue
- `/app/templates/page.tsx` - Template library
- `/app/analytics/page.tsx` - Business analytics

### Components (Library)
- `/app/components/index.ts` - Central exports (70 components)
- `/app/components/AnalysisRequestForm.tsx` - Analysis form
- `/app/components/DataTable.tsx` - Data table with features
- `/app/components/CompetitivePositioningMap.tsx` - D3 visualization
- `/app/components/DisruptionRadar.tsx` - Radar chart
- `/app/components/DecisionCard.tsx` - Decision management
- `/app/components/StrategicHealthDashboard.tsx` - Executive dashboard

### Utilities & Libs
- `/lib/api.ts` - API client
- `/lib/auth.ts` - Authentication utilities
- `/lib/mvp-api.ts` - MVP-specific APIs
- `/app/utils/reportTransformers.ts` - Data transformation
- `/app/utils/dateFormat.ts` - Date utilities
- `/app/hooks/` - Custom hooks

### Styling & Config
- `/app/globals.css` - Global styles
- `/tailwind.config.js` - Tailwind configuration
- `/tsconfig.json` - TypeScript configuration

---

## SUMMARY

ConsultantOS frontend is a **modern, feature-rich React/Next.js application** built for business intelligence and competitive analysis. It features:

1. **Robust UI Component Library** - 70+ production-ready components
2. **Advanced Visualizations** - D3.js, Recharts, and interactive dashboards
3. **Data-Driven Tables** - Full-featured tables with sort, filter, pagination
4. **Collaboration Tools** - Comments, sharing, version control
5. **Responsive Design** - Mobile-first, WCAG AA compliant
6. **Performance Optimized** - Code splitting, lazy loading, query deduplication
7. **Graceful Error Handling** - Fallbacks, retries, user-friendly messages
8. **Real-Time Features** - Job monitoring, analytics, WebSocket support

The architecture separates **concerns effectively**: pages handle routing/layout, components provide UI, hooks manage state, and libs handle data/auth. The entire system is **type-safe with TypeScript** and **accessible** for diverse users.
