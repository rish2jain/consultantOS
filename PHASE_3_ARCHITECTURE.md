# Phase 3 Architecture Diagram

## Component Hierarchy

```
Strategic Intelligence Dashboard
├── Header
│   ├── Company Info
│   ├── Layer Navigation (3 tabs)
│   └── Refresh Button
│
├── Layer 1: Executive Brief
│   ├── Strategic Health Score Card
│   ├── Top Threats Grid (3 cards)
│   ├── Top Opportunities Grid (3 cards)
│   └── Decisions Required (expandable cards)
│
├── Layer 2: Strategic Context
│   ├── Tab Navigation (5 tabs)
│   ├── Positioning Tab
│   │   ├── Porter's 5 Forces (bar charts)
│   │   └── Strategic Metrics (gauges)
│   ├── Disruption Tab
│   │   ├── Overall Risk Gauge
│   │   └── Disruptor Cards
│   ├── Dynamics Tab
│   │   └── SystemDynamicsMap
│   │       ├── D3 Force Graph
│   │       ├── Legend Panel
│   │       ├── Feedback Loops Panel
│   │       └── Leverage Points Panel
│   ├── Momentum Tab
│   │   └── FlywheelDashboard
│   │       ├── Central Velocity Gauge
│   │       ├── Component Breakdown (5 cards)
│   │       ├── Historical Matches Grid
│   │       └── Inflection Points Timeline
│   └── Decisions Tab
│       └── Decision Cards with Options
│
└── Layer 3: Supporting Evidence
    ├── Raw Data Display
    ├── Source Attribution
    ├── Confidence Intervals
    └── Export Controls (PDF, Excel, API)
```

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend Layer                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │   Strategic Intelligence Dashboard Page          │  │
│  │   /dashboard/strategic-intelligence/page.tsx     │  │
│  └────────────┬─────────────────────────────────────┘  │
│               │                                          │
│               ├──► SystemDynamicsMap Component           │
│               │    - D3.js Force Simulation             │
│               │    - SVG Rendering                      │
│               │                                          │
│               ├──► FlywheelDashboard Component           │
│               │    - Recharts Integration               │
│               │    - Animated Gauges                    │
│               │                                          │
│               ├──► IntelligenceFeed Component            │
│               │    - Real-time Updates                  │
│               │    - Filter Logic                       │
│               │                                          │
│               └──► LoadingStates & ErrorBoundary         │
│                    - Skeleton Screens                   │
│                    - Error Recovery                     │
└──────────────┬──────────────────────────────────────────┘
               │
               │ HTTP / WebSocket
               ▼
┌─────────────────────────────────────────────────────────┐
│                    API Integration Layer                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │   strategic-intelligence-api.ts                   │  │
│  │                                                    │  │
│  │   StrategicIntelligenceAPI (static class)        │  │
│  │   ├─ fetchOverview()                             │  │
│  │   ├─ fetchSystemDynamics()                       │  │
│  │   ├─ fetchFlywheelVelocity()                     │  │
│  │   ├─ fetchIntelligenceFeed()                     │  │
│  │   ├─ markCardAsRead()                            │  │
│  │   ├─ handleDecision()                            │  │
│  │   ├─ refreshAnalysis()                           │  │
│  │   └─ exportData()                                │  │
│  │                                                    │  │
│  │   IntelligenceFeedWebSocket (class)              │  │
│  │   ├─ connect()                                    │  │
│  │   ├─ disconnect()                                 │  │
│  │   └─ auto-reconnect with backoff                 │  │
│  │                                                    │  │
│  │   React Hooks:                                    │  │
│  │   ├─ useStrategicIntelligence()                  │  │
│  │   ├─ useIntelligenceFeed()                       │  │
│  │   └─ useExportData()                             │  │
│  └──────────────────────────────────────────────────┘  │
└──────────────┬──────────────────────────────────────────┘
               │
               │ HTTP / WebSocket
               ▼
┌─────────────────────────────────────────────────────────┐
│                     Backend API Layer                    │
│                    (TO BE IMPLEMENTED)                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET  /api/strategic-intelligence/overview              │
│  GET  /api/strategic-intelligence/dynamics/{company}    │
│  GET  /api/strategic-intelligence/flywheel/{company}    │
│  GET  /api/strategic-intelligence/feed                  │
│  POST /api/strategic-intelligence/feed/{id}/read        │
│  POST /api/strategic-intelligence/decisions/{id}        │
│  POST /api/strategic-intelligence/refresh               │
│  GET  /api/strategic-intelligence/export/{company}      │
│                                                          │
│  WS   ws://api/strategic-intelligence/live/{company}    │
│                                                          │
└──────────────┬──────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│                   Business Logic Layer                   │
│                    (TO BE IMPLEMENTED)                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  - System Dynamics Analysis Engine                      │
│  - Flywheel Momentum Calculator                         │
│  - Intelligence Card Generator                          │
│  - Pattern Matching Algorithm                           │
│  - Leverage Point Identifier                            │
│  - Real-time Event Processor                            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## State Management Flow

```
┌─────────────────────────────────────────────────────────┐
│                      Component State                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Dashboard Page                                          │
│  ├─ activeLayer: 'executive' | 'context' | 'evidence'   │
│  ├─ activeTab: 'positioning' | 'disruption' | ...       │
│  ├─ data: StrategicIntelligenceOverview | null          │
│  ├─ loading: boolean                                     │
│  └─ error: string | null                                 │
│                                                          │
│  IntelligenceFeed                                        │
│  ├─ feedData: IntelligenceFeedData                      │
│  ├─ selectedFilters: Set<IntelligenceCardType>          │
│  ├─ showOnlyUnread: boolean                             │
│  └─ selectedCard: IntelligenceCard | null               │
│                                                          │
│  SystemDynamicsMap                                       │
│  ├─ selectedNode: SystemNode | null                     │
│  ├─ selectedLoop: FeedbackLoop | null                   │
│  ├─ highlightedPaths: Set<string>                       │
│  ├─ showLeveragePoints: boolean                         │
│  └─ activeLoops: Set<string>                            │
│                                                          │
│  FlywheelDashboard                                       │
│  ├─ selectedComponent: MomentumComponent | null         │
│  └─ showHistoricalMatches: boolean                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Real-time Update Flow

```
WebSocket Server                Frontend
      │                            │
      │   New Intelligence Card    │
      ├───────────────────────────►│
      │   { type: 'new_card' }     │
      │                            │
      │                            ├──► Update feedData state
      │                            ├──► Increment unread_count
      │                            └──► Animate new card in
      │                            │
      │   Health Score Update      │
      ├───────────────────────────►│
      │   { type: 'health_update'} │
      │                            │
      │                            ├──► Update health score
      │                            └──► Trigger gauge animation
      │                            │
      │   Card Read Confirmation   │
      │◄───────────────────────────┤
      │   { card_id: '...' }       │
      │                            │
      ├──► Process read event      │
      └──► Broadcast to other      │
           connected clients       │
```

## Error Handling Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Error Boundary Tree                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Root ErrorBoundary                                      │
│  └─► Strategic Intelligence Dashboard                    │
│      ├─► ErrorBoundary (Executive Brief)                │
│      │   ├─ Threats Cards                               │
│      │   └─ Opportunities Cards                         │
│      │                                                    │
│      ├─► ErrorBoundary (Strategic Context)               │
│      │   ├─ ErrorBoundary (SystemDynamicsMap)           │
│      │   │   └─ D3 Simulation                           │
│      │   │                                                │
│      │   ├─ ErrorBoundary (FlywheelDashboard)           │
│      │   │   └─ Recharts Components                     │
│      │   │                                                │
│      │   └─ ErrorBoundary (Other Tabs)                  │
│      │                                                    │
│      └─► ErrorBoundary (Intelligence Feed)               │
│          └─ Card List                                    │
│                                                          │
│  Each ErrorBoundary:                                     │
│  - Catches errors in subtree                            │
│  - Logs to backend /api/logs/client-error              │
│  - Shows fallback UI                                    │
│  - Allows retry without full page reload               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Loading State Progression

```
┌─────────────────────────────────────────────────────────┐
│                   Loading Sequence                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Initial Load                                            │
│  ├─ 1. Show DashboardLoading skeleton                   │
│  │                                                        │
│  ├─ 2. Fetch /api/strategic-intelligence/overview       │
│  │     (Parallel requests for all data)                 │
│  │                                                        │
│  ├─ 3. Progressive hydration:                           │
│  │     ├─ Executive Brief appears first                 │
│  │     ├─ Charts render as data arrives                 │
│  │     └─ Real-time feed connects last                  │
│  │                                                        │
│  └─ 4. Loading complete → full interactivity            │
│                                                          │
│  Refresh                                                 │
│  ├─ 1. Show spinner in header                           │
│  ├─ 2. Keep existing content visible                    │
│  ├─ 3. Update data in background                        │
│  └─ 4. Smooth transition to new data                    │
│                                                          │
│  Component-level Loading                                 │
│  ├─ SystemDynamicsMap → spinning graph icon             │
│  ├─ FlywheelDashboard → rotating gauge skeleton         │
│  ├─ IntelligenceFeed → animated card skeletons          │
│  └─ Charts → shimmer effect on axes/bars                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Type System Architecture

```
┌─────────────────────────────────────────────────────────┐
│              TypeScript Type Hierarchy                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  StrategicIntelligenceOverview (Root)                   │
│  ├─ executive_brief: ExecutiveBrief                     │
│  │   ├─ top_threats: StrategicThreat[]                  │
│  │   ├─ top_opportunities: StrategicOpportunity[]       │
│  │   └─ decisions_required: DecisionCard[]              │
│  │                                                        │
│  ├─ strategic_context: StrategicContext                 │
│  │   ├─ positioning: PositioningAnalysis                │
│  │   ├─ disruption: DisruptionAnalysis                  │
│  │   ├─ dynamics: SystemDynamicsData                    │
│  │   │   ├─ nodes: SystemNode[]                         │
│  │   │   ├─ links: CausalLink[]                         │
│  │   │   ├─ feedback_loops: FeedbackLoop[]              │
│  │   │   └─ leverage_points: LeveragePoint[]            │
│  │   ├─ momentum: FlywheelVelocity                      │
│  │   │   ├─ components: MomentumComponent[]             │
│  │   │   ├─ historical_matches: HistoricalMatch[]       │
│  │   │   └─ inflection_points: InflectionPoint[]        │
│  │   └─ decisions: DecisionCard[]                       │
│  │                                                        │
│  └─ intelligence_feed: IntelligenceFeedData             │
│      └─ cards: IntelligenceCard[]                       │
│                                                          │
│  All types are:                                          │
│  - Fully documented with JSDoc                          │
│  - Exported for reuse                                   │
│  - Strict (no any types)                                │
│  - Compatible with API responses                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Performance Optimization Strategy

```
┌─────────────────────────────────────────────────────────┐
│              Performance Optimizations                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Code Splitting                                       │
│     ├─ Lazy load heavy components (D3, Recharts)        │
│     └─ Route-based splitting (Next.js automatic)        │
│                                                          │
│  2. Memoization                                          │
│     ├─ React.memo() on expensive components             │
│     ├─ useMemo() for derived calculations               │
│     └─ useCallback() for event handlers                 │
│                                                          │
│  3. Virtualization                                       │
│     ├─ Intelligence feed (only render visible)          │
│     └─ Long lists of cards/nodes                        │
│                                                          │
│  4. D3 Optimization                                      │
│     ├─ Throttle force updates to 60fps                  │
│     ├─ Pause simulation when not visible                │
│     └─ Cleanup listeners on unmount                     │
│                                                          │
│  5. WebSocket Efficiency                                 │
│     ├─ Reconnect with exponential backoff               │
│     ├─ Batch multiple updates                           │
│     └─ Debounce rapid changes                           │
│                                                          │
│  6. Image/Asset Optimization                             │
│     ├─ Next.js Image component                          │
│     ├─ SVG sprites for icons                            │
│     └─ CSS animations > JS animations                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Responsive Design Breakpoints

```
┌─────────────────────────────────────────────────────────┐
│                  Responsive Strategy                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Desktop (>1024px)                                       │
│  ├─ 3-column layout for Executive Brief                 │
│  ├─ Full D3 graph (800x600)                             │
│  ├─ Side-by-side gauge + components                     │
│  └─ All features enabled                                 │
│                                                          │
│  Tablet (768px - 1024px)                                 │
│  ├─ 2-column layout                                      │
│  ├─ Reduced D3 graph (600x500)                          │
│  ├─ Stacked gauge + components                          │
│  └─ Compact mode for some components                    │
│                                                          │
│  Mobile (<768px)                                         │
│  ├─ Single column layout                                │
│  ├─ Simplified D3 graph (touch-optimized)               │
│  ├─ Compact FlywheelDashboard                           │
│  └─ Progressive disclosure emphasized                   │
│                                                          │
│  Tailwind Classes Used:                                  │
│  - sm: (640px)  → Mobile adjustments                    │
│  - md: (768px)  → Tablet layouts                        │
│  - lg: (1024px) → Desktop grids                         │
│  - xl: (1280px) → Wide desktop features                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

**Visual Component Tree**: See `PHASE_3_VISUALIZATIONS.md` for detailed component specifications.

**API Contracts**: See `types/strategic-intelligence.ts` for complete type definitions.

**Integration Guide**: See `lib/strategic-intelligence-api.ts` for API usage patterns.
