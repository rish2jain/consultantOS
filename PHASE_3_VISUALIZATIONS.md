# Phase 3: Advanced Strategic Intelligence Visualizations

## Overview

This document describes the Phase 3 advanced visualization components for ConsultantOS, implementing a comprehensive strategic intelligence dashboard with real-time monitoring, system dynamics analysis, and flywheel momentum tracking.

## Architecture

### Component Structure

```
frontend/
├── types/
│   └── strategic-intelligence.ts       # Comprehensive TypeScript types
├── lib/
│   └── strategic-intelligence-api.ts   # API integration & WebSocket
├── app/
│   ├── components/
│   │   ├── SystemDynamicsMap.tsx      # D3.js force-directed graph
│   │   ├── FlywheelDashboard.tsx      # Momentum tracking with gauges
│   │   ├── IntelligenceFeed.tsx       # Real-time intelligence cards
│   │   ├── ErrorBoundary.tsx          # Error handling (existing)
│   │   └── LoadingStates.tsx          # Loading skeletons & spinners
│   └── dashboard/
│       └── strategic-intelligence/
│           └── page.tsx                # Main dashboard page
```

## Components

### 1. SystemDynamicsMap

**Purpose**: Visualize system dynamics with causal relationships, feedback loops, and leverage points.

**Features**:
- Force-directed graph using D3.js
- Node categories: Market, Financial, Strategic, Operational
- Edge types: Positive (+) and Negative (−) relationships
- Edge thickness represents time delay
- Feedback loop highlighting (Reinforcing = red, Balancing = blue)
- Interactive leverage point cards
- Node hover → highlight connected paths
- Drag-to-reposition simulation
- Zoom & pan controls

**Data Structure**:
```typescript
interface SystemDynamicsData {
  nodes: SystemNode[];              // Metrics with values & trends
  links: CausalLink[];              // Relationships with polarity
  feedback_loops: FeedbackLoop[];   // System loops
  leverage_points: LeveragePoint[]; // Intervention opportunities
}
```

**Usage**:
```tsx
import SystemDynamicsMap from '@/app/components/SystemDynamicsMap';

<SystemDynamicsMap
  data={dynamicsData}
  onNodeClick={(node) => console.log(node)}
  onLeveragePointClick={(point) => console.log(point)}
  height={600}
  width={800}
  simulationEnabled={true}
/>
```

**API Endpoint**: `/api/strategic-intelligence/dynamics/{company}`

---

### 2. FlywheelDashboard

**Purpose**: Track organizational momentum across 5 components with phase detection.

**Features**:
- Central circular gauge (0-100 velocity score)
- Color zones: Red (0-40), Yellow (41-70), Green (71-100)
- 5 component mini-gauges with 90-day sparklines
- Acceleration indicators (↑↑ strong, ↑ moderate, → stable, ↓ declining)
- Phase indicator: STALLED / BUILDING / ACCELERATING
- Historical pattern matching (e.g., "Similar to Salesforce 2008-2010")
- Inflection point timeline
- Component detail modal with full trend chart

**Data Structure**:
```typescript
interface FlywheelVelocity {
  overall_score: number;            // 0-100
  market_momentum: number;
  financial_momentum: number;
  strategic_momentum: number;
  execution_momentum: number;
  talent_momentum: number;
  phase: 'Stalled' | 'Building' | 'Accelerating';
  historical_matches: HistoricalMatch[];
  inflection_points: InflectionPoint[];
  components: MomentumComponent[];
}
```

**Usage**:
```tsx
import FlywheelDashboard from '@/app/components/FlywheelDashboard';

<FlywheelDashboard
  velocity={flywheelData}
  onComponentClick={(component) => console.log(component)}
  compact={false}
/>
```

**API Endpoint**: `/api/strategic-intelligence/flywheel/{company}`

---

### 3. IntelligenceFeed

**Purpose**: Real-time intelligence cards with urgency-based filtering and actions.

**Features**:
- Live-updating feed (WebSocket or SSE)
- Card types:
  - 🔴 Critical, 🟡 Important, 🔵 Info urgency levels
  - ⚡ Disruption Alert
  - ⚔️ Position Threat
  - 🔄 Loop Detection
  - 🎯 Flywheel Milestone
  - 📊 Pattern Match
  - ⏰ Decision Due
  - 💰 Opportunity
  - 📈 Metric Threshold
- Filters: By card type
- Unread indicator & mark all as read
- Quick actions from cards
- Card detail modal with full metadata

**Data Structure**:
```typescript
interface IntelligenceFeedData {
  cards: IntelligenceCard[];
  unread_count: number;
  last_updated: string;
}

interface IntelligenceCard {
  id: string;
  type: IntelligenceCardType;
  urgency: 'critical' | 'important' | 'info';
  title: string;
  description: string;
  timestamp: string;
  read: boolean;
  metadata: Record<string, any>;
  actions?: Array<{ label: string; action: string }>;
}
```

**Usage**:
```tsx
import IntelligenceFeed from '@/app/components/IntelligenceFeed';

<IntelligenceFeed
  initialData={feedData}
  enableRealtime={true}
  filters={['disruption_alert', 'decision_due']}
  onActionClick={(cardId, action) => handleAction(cardId, action)}
/>
```

**API Endpoint**: `/api/strategic-intelligence/feed?company={company}`

**WebSocket**: `ws://api/strategic-intelligence/live/{company}`

---

### 4. Strategic Intelligence Dashboard

**Purpose**: Three-layer progressive disclosure dashboard for strategic intelligence.

**Layers**:

#### Layer 1: Executive Brief (30-second view)
- Strategic Health Score with trend
- Top 3 Threats (with severity, timeline, mitigation status)
- Top 3 Opportunities (with value, ROI, timeframe)
- Decisions Required (with urgency, impact, recommendations)

#### Layer 2: Strategic Context (5-minute exploration)
Tabs:
- **Positioning**: Porter's 5 Forces, Blue Ocean Score, Differentiation Strength
- **Disruption**: Overall risk, disruptor analysis, market maturity
- **Dynamics**: System Dynamics Map (embedded)
- **Momentum**: Flywheel Dashboard (embedded)
- **Decisions**: Decision cards with options & pros/cons

#### Layer 3: Supporting Evidence (on-demand)
- Raw framework analyses
- Source data with validation
- Confidence intervals
- Historical comparisons
- Export options (PDF, Excel, API)

**Usage**:
```tsx
// Navigate to: /dashboard/strategic-intelligence
// Component auto-loads data via hooks
```

**API Endpoint**: `/api/strategic-intelligence/overview?company={company}`

---

## API Integration

### Hook: `useStrategicIntelligence`

Fetch complete strategic intelligence overview.

```typescript
import { useStrategicIntelligence } from '@/lib/strategic-intelligence-api';

const { data, loading, error, refresh } = useStrategicIntelligence(
  'Tesla',
  'Electric Vehicles'
);
```

### Hook: `useIntelligenceFeed`

Real-time intelligence feed with WebSocket.

```typescript
import { useIntelligenceFeed } from '@/lib/strategic-intelligence-api';

const { feedData, loading, error, connected, markAsRead } = useIntelligenceFeed(
  'Tesla',
  true, // enableRealtime
  ['disruption_alert', 'decision_due'] // filters
);
```

### Hook: `useExportData`

Export strategic intelligence data.

```typescript
import { useExportData } from '@/lib/strategic-intelligence-api';

const { exportData, exporting, error } = useExportData();

await exportData('Tesla', 'pdf'); // or 'excel', 'json'
```

### WebSocket Integration

```typescript
import { IntelligenceFeedWebSocket } from '@/lib/strategic-intelligence-api';

const ws = new IntelligenceFeedWebSocket(
  'Tesla',
  (update) => {
    // Handle update: new_card, update_card, delete_card, health_update
  },
  (error) => console.error(error),
  () => console.log('Connected'),
  () => console.log('Disconnected')
);

ws.connect();
// Later: ws.disconnect();
```

---

## Error Handling

All components wrapped with `ErrorBoundary`:

```tsx
import { ErrorBoundary } from '@/app/components/ErrorBoundary';

<ErrorBoundary errorContext="System Dynamics Map">
  <SystemDynamicsMap data={data} />
</ErrorBoundary>
```

Features:
- Catches runtime errors
- Displays user-friendly error UI
- Logs errors to backend (`/api/logs/client-error`)
- Retry & reload options
- Dev mode shows stack traces

---

## Loading States

Comprehensive loading skeletons for all components:

```tsx
import {
  SystemDynamicsMapLoading,
  FlywheelDashboardLoading,
  IntelligenceFeedLoading,
  ExecutiveBriefLoading,
  DashboardLoading,
  Spinner,
  EmptyState,
  ProgressBar,
} from '@/app/components/LoadingStates';

// Usage
{loading ? <SystemDynamicsMapLoading /> : <SystemDynamicsMap data={data} />}
```

---

## Accessibility

All components meet WCAG AA standards:

- **Keyboard Navigation**: Full keyboard support for all interactions
- **Screen Reader**: ARIA labels and semantic HTML
- **Color Contrast**: 4.5:1 minimum contrast ratios
- **Focus Management**: Visible focus indicators
- **Alternative Text**: All visual information has text equivalents

---

## Performance Optimizations

### 1. Virtualization
- Intelligence feed uses virtual scrolling for large datasets
- Renders only visible cards

### 2. Memoization
```tsx
// Components use React.memo() for expensive renders
const SystemDynamicsMap = React.memo(({ data }) => { /* ... */ });
```

### 3. Code Splitting
```tsx
// Lazy load heavy components
const SystemDynamicsMap = lazy(() => import('@/app/components/SystemDynamicsMap'));
```

### 4. WebSocket Reconnection
- Exponential backoff (1s, 2s, 4s, 8s, 16s)
- Max 5 reconnection attempts
- Graceful degradation to polling

### 5. D3 Simulation Control
- Pause simulation when not visible
- Throttle force updates to 60fps
- Cleanup on unmount

---

## Backend API Requirements

### Endpoints to Implement

1. **GET** `/api/strategic-intelligence/overview`
   - Query params: `company`, `industry` (optional)
   - Returns: `StrategicIntelligenceOverview`

2. **GET** `/api/strategic-intelligence/dynamics/{company}`
   - Returns: `SystemDynamicsData`

3. **GET** `/api/strategic-intelligence/flywheel/{company}`
   - Returns: `FlywheelVelocity`

4. **GET** `/api/strategic-intelligence/feed`
   - Query params: `company`, `filters` (comma-separated)
   - Returns: `IntelligenceFeedData`

5. **POST** `/api/strategic-intelligence/feed/{card_id}/read`
   - Marks card as read

6. **POST** `/api/strategic-intelligence/decisions/{decision_id}`
   - Body: `{ action: 'accept' | 'reject' | 'defer', option_id?: string }`

7. **POST** `/api/strategic-intelligence/refresh`
   - Body: `{ company: string }`
   - Triggers re-analysis

8. **GET** `/api/strategic-intelligence/export/{company}`
   - Query params: `format` (pdf | excel | json)
   - Returns: Blob

### WebSocket Endpoint

**WS** `ws://api/strategic-intelligence/live/{company}`

**Message Types**:
```typescript
interface LiveIntelligenceUpdate {
  type: 'new_card' | 'update_card' | 'delete_card' | 'health_update';
  data: IntelligenceCard | { strategic_health_score: number } | { card_id: string };
  timestamp: string;
}
```

---

## Demo Data

The dashboard includes demo data generator for testing:

```typescript
// Located in: frontend/app/dashboard/strategic-intelligence/page.tsx
function generateDemoData(): StrategicIntelligenceOverview {
  // Returns comprehensive demo data matching all type definitions
}
```

To use real data, implement backend endpoints and update API base URLs:
- `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- `NEXT_PUBLIC_WS_URL` for WebSocket

---

## Testing

### Component Tests
```bash
# Test individual components
npm run test SystemDynamicsMap.test.tsx
npm run test FlywheelDashboard.test.tsx
npm run test IntelligenceFeed.test.tsx
```

### Integration Tests
```bash
# Test full dashboard flow
npm run test:e2e strategic-intelligence
```

### Performance Tests
```bash
# Measure rendering performance
npm run test:perf
```

---

## Deployment

### Build
```bash
cd frontend
npm run build
```

### Environment Variables
```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=https://api.consultantos.com
NEXT_PUBLIC_WS_URL=wss://api.consultantos.com
```

### Production Checklist
- [ ] All API endpoints implemented
- [ ] WebSocket server configured
- [ ] Error logging service integrated
- [ ] Analytics tracking added
- [ ] Performance monitoring enabled
- [ ] Accessibility audit passed
- [ ] Cross-browser testing complete
- [ ] Mobile responsiveness verified

---

## Future Enhancements

1. **Simulation Mode**: Predict outcomes of leverage point interventions
2. **Collaborative Annotations**: Team notes on insights
3. **Custom Dashboards**: User-configurable layouts
4. **Mobile App**: Native iOS/Android apps
5. **AI Insights**: LLM-generated strategic recommendations
6. **Integration APIs**: Export to BI tools (Tableau, Power BI)
7. **Alerts**: Email/Slack notifications for critical intelligence
8. **Historical Playback**: Replay system evolution over time

---

## Support

For issues or questions:
- GitHub Issues: [consultantos/issues](https://github.com/consultantos/issues)
- Documentation: [docs.consultantos.com](https://docs.consultantos.com)
- Email: support@consultantos.com

---

## License

MIT License - See LICENSE file for details
