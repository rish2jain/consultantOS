# Live Dashboards Guide

## Overview

ConsultantOS Live Dashboards represent a **remarkable differentiation** from traditional static PDF reports. While competitors deliver frozen-in-time documents, ConsultantOS provides **real-time, interactive business intelligence** that updates automatically and enables what-if scenario planning.

### Key Differentiators

| Feature | Static PDFs | Live Dashboards |
|---------|------------|-----------------|
| **Updates** | Manual regeneration required | Real-time WebSocket updates |
| **Interactivity** | None | Interactive charts, filters, drill-down |
| **Scenario Planning** | Not available | Built-in what-if analysis |
| **Competitive Intelligence** | Static snapshots | Dynamic positioning maps |
| **Mobile Access** | Poor (PDF viewers) | Fully responsive web interface |
| **Collaboration** | Email attachments | Live sharing with updates |
| **Data Freshness** | Hours/days old | Minutes old |

---

## Architecture

### Backend Components

```
consultantos/dashboards/
├── __init__.py           # Package exports
├── models.py             # Pydantic models for dashboards
├── service.py            # DashboardService with WebSocket support
└── templates.py          # Pre-built dashboard templates
```

### Frontend Components

```
frontend/app/
├── dashboard/[id]/page.tsx          # Dashboard view page
├── components/
│   ├── InteractiveDashboard.tsx     # Main dashboard component
│   ├── ScenarioPlanner.tsx          # What-if analysis tool
│   ├── CompetitiveLandscape.tsx     # Competitive positioning map
│   └── ui/                          # Reusable UI components
└── hooks/
    └── useWebSocket.ts              # WebSocket connection hook
```

---

## Getting Started

### 1. Create a Dashboard

```bash
POST /dashboards
Content-Type: application/json

{
  "company": "Tesla",
  "industry": "Electric Vehicles",
  "template": "executive_summary",
  "frameworks": ["porter", "swot"],
  "depth": "standard"
}
```

**Response:**
```json
{
  "id": "dash_tesla_abc123",
  "company": "Tesla",
  "industry": "Electric Vehicles",
  "template": "executive_summary",
  "created_at": "2025-11-08T10:00:00Z",
  "last_updated": "2025-11-08T10:00:00Z",
  "sections": [...],
  "metrics": [...],
  "alerts": [],
  "refresh_enabled": true,
  "auto_refresh_interval": 300
}
```

### 2. View Dashboard

Navigate to: `/dashboard/{dashboard_id}`

The dashboard will:
- Load initial data via REST API
- Establish WebSocket connection for real-time updates
- Auto-refresh every 5 minutes (configurable)
- Display live connection status badge

### 3. Subscribe to Real-Time Updates (WebSocket)

```javascript
const ws = new WebSocket('ws://localhost:8080/dashboards/{dashboard_id}/ws');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);

  if (update.type === 'initial') {
    // Full dashboard data
    console.log('Initial data:', update.data);
  } else if (update.type === 'metric') {
    // Single metric update
    console.log('Metric updated:', update.data);
  } else if (update.type === 'alert') {
    // New alert
    console.log('New alert:', update.data);
  }
};
```

### 4. Force Refresh

```bash
POST /dashboards/{dashboard_id}/refresh
```

Triggers immediate data refresh and broadcasts update to all connected clients.

---

## Dashboard Templates

### Executive Summary
**Audience:** C-suite executives
**Use Cases:** Quarterly reviews, board meetings, investor updates

**Sections:**
- Key Performance Metrics (grid layout)
- Critical Alerts
- Revenue Trend Chart
- Top Strategic Insights

**Refresh Interval:** 5 minutes

---

### Competitive Intelligence
**Audience:** Strategy team
**Use Cases:** Competitive analysis, market monitoring

**Sections:**
- Competitive Positioning Map (interactive 2D)
- Competitor Comparison Table
- Competitor Moves Alerts
- Market Share Trends

**Refresh Interval:** 10 minutes

---

### Market Analysis
**Audience:** Market analysts
**Use Cases:** Market research, opportunity assessment

**Sections:**
- Market Size & Growth Chart
- Geographic Distribution Map
- Segment Analysis Table
- Emerging Trends Feed

**Refresh Interval:** 15 minutes

---

### Financial Performance
**Audience:** CFO, finance team
**Use Cases:** Financial review, investor relations

**Sections:**
- Key Financial Metrics (revenue, margin, ROCE, debt/equity)
- Revenue vs Profit Dual-Axis Chart
- Cash Flow Waterfall
- Financial Ratios Table
- Financial Alerts

**Refresh Interval:** 5 minutes

---

### Risk Monitor
**Audience:** Risk managers
**Use Cases:** Risk management, compliance, crisis monitoring

**Sections:**
- Active Risk Alerts (grouped by category)
- Risk Heat Map (likelihood vs impact)
- Risk Register Table
- Risk Indicators
- Risk Trends

**Refresh Interval:** 3 minutes

---

### Innovation Tracker
**Audience:** CTO, R&D team
**Use Cases:** Innovation management, technology scouting

**Sections:**
- Emerging Technologies Trends
- R&D Investment Chart
- Innovation Pipeline Table
- Technology Landscape Map
- Innovation Insights

**Refresh Interval:** 30 minutes

---

## Interactive Features

### Real-Time Metrics

Metrics update automatically and display:
- **Current Value** with units
- **Trend Direction** (↑ up, ↓ down, → stable)
- **Change %** since last period
- **Confidence Score** (0-100%)
- **Benchmark** comparison (if available)
- **Target** value (if set)

Example:
```
Revenue
$25.0M
↑ +12.5% | 92% confidence
Benchmark: $22.0M | Target: $30.0M
```

### Alerts System

Three severity levels:
- **Critical** (red) - Immediate action required
- **Warning** (yellow) - Monitor closely
- **Info** (blue) - FYI updates

Alerts include:
- Title and detailed message
- Timestamp
- Category (competitive, financial, market, regulatory)
- Source agent
- Action required flag
- Optional action URL

### Interactive Charts

All charts support:
- **Zoom** (click and drag)
- **Pan** (hold and drag)
- **Hover tooltips** with detailed data
- **Legend toggling** (click to show/hide series)
- **Export** (PNG, SVG)
- **Responsive scaling**

### Competitive Positioning Map

Interactive 2D bubble chart showing:
- **X-axis:** Price Index (0-100)
- **Y-axis:** Quality/Features Index (0-100)
- **Bubble Size:** Market Share
- **Color:** Your company (blue) vs competitors (gray)

**Quadrants:**
1. **Premium Value** (top-left): High quality, competitive price
2. **Premium Positioning** (top-right): High quality, premium price
3. **Budget Market** (bottom-left): Lower quality, competitive price
4. **Questionable Value** (bottom-right): Lower quality, high price

**Interactions:**
- Click bubble to see competitor details
- Hover for quick stats
- Compare your position to competitors
- Export chart for presentations

---

## Scenario Planning

### Running Scenarios

The scenario planner allows what-if analysis with adjustable assumptions:

**Market Assumptions:**
- Market Growth Rate: -20% to +50%
- Competitor Entry: Yes/No
- Regulatory Change: Yes/No

**Business Assumptions:**
- Price Change: -30% to +30%
- Cost Change: -20% to +40%
- Market Share Target: 5% to 50%

### Example Scenario

**Assumptions:**
```json
{
  "market_growth_rate": 10.0,
  "competitor_entry": false,
  "regulatory_change": false,
  "price_change": -10.0,
  "cost_change": 5.0,
  "market_share_target": 30.0
}
```

**Results:**
- 12-month revenue forecast
- 12-month profit forecast
- Market share trajectory
- Risk score (0-100%)
- Confidence level (0-100%)
- Key insights and recommendations

**Visualization:**
- Revenue trend chart
- Profit trend chart
- Market share growth chart
- Risk assessment summary

### Scenario API

```bash
POST /dashboards/scenarios/run
Content-Type: application/json

{
  "company": "Tesla",
  "industry": "Electric Vehicles",
  "assumptions": {
    "market_growth_rate": 10.0,
    "price_change": -10.0,
    "cost_change": 5.0
  },
  "forecast_period": 12
}
```

---

## Mobile Responsiveness

### Responsive Grid

Dashboard sections automatically adapt:
- **Desktop (>1024px):** 2-column grid
- **Tablet (768-1023px):** 2-column grid with smaller cards
- **Mobile (<768px):** Single column stack

### Touch Optimizations

- **Swipeable cards** for metric browsing
- **Collapsible sections** to save screen space
- **Touch-friendly controls** (larger tap targets)
- **Simplified charts** for small screens
- **Bottom navigation** for easy access

### Mobile-Specific Features

- **Pull to refresh** gesture
- **Offline caching** of last view
- **Push notifications** for critical alerts
- **Share sheet integration**

---

## WebSocket Protocol

### Connection

```
ws://[host]/dashboards/{dashboard_id}/ws
```

### Message Types

#### Initial State
```json
{
  "type": "initial",
  "data": {
    "id": "dash_tesla_001",
    "company": "Tesla",
    "sections": [...],
    "metrics": [...],
    "alerts": [...]
  }
}
```

#### Metric Update
```json
{
  "type": "metric",
  "data": {
    "id": "metric_revenue",
    "name": "Revenue",
    "value": 26000000,
    "change": 4.0,
    "trend": "up",
    "confidence": 0.89
  }
}
```

#### Alert
```json
{
  "type": "alert",
  "data": {
    "id": "alert_123",
    "title": "Competitor Price Drop",
    "message": "Tesla reduced Model 3 price by 15%",
    "severity": "critical",
    "category": "competitive",
    "timestamp": "2025-11-08T10:35:00Z"
  }
}
```

#### Full Update
```json
{
  "type": "update",
  "data": {
    // Complete dashboard object
  }
}
```

### Connection Management

- **Auto-reconnect:** Up to 5 attempts with exponential backoff
- **Heartbeat:** Every 30 seconds
- **Timeout:** 60 seconds idle before reconnection
- **Connection status:** Displayed as badge in UI

---

## PDF Export (Secondary Feature)

PDF export is available but positioned as a **snapshot**, not the primary output.

### Export Endpoint

```bash
POST /dashboards/{dashboard_id}/export/pdf
```

### PDF Characteristics

**Watermark:**
```
Snapshot taken at 2025-11-08 10:45:00 UTC
For latest data, view live dashboard at:
https://consultantos.com/dashboard/{id}
```

**Contents:**
- Current state of all sections
- Timestamp on every page
- "Data as of [time]" disclaimers
- Link to live dashboard (QR code)
- Export settings and filters applied

### When to Use PDF Export

1. **Compliance:** Regulatory filings requiring static documents
2. **Offline Distribution:** Email to stakeholders without web access
3. **Archival:** Record-keeping and audit trails
4. **Print Needs:** Physical presentations or handouts
5. **Third-Party Sharing:** External stakeholders requiring documents

### PDF Export Best Practices

❌ **Don't:**
- Use PDF as primary delivery method
- Email PDFs for routine updates
- Print dashboards regularly

✅ **Do:**
- Direct stakeholders to live dashboard
- Use sharing links with live updates
- Export only when static snapshot needed
- Include live dashboard URL in PDF

---

## Performance Optimization

### Caching Strategy

- **Dashboard metadata:** 5-minute cache
- **Metric values:** 1-minute cache
- **Chart data:** 5-minute cache
- **Static template data:** 1-hour cache

### WebSocket Optimization

- **Selective updates:** Only changed data transmitted
- **Compression:** gzip for message payload
- **Batching:** Multiple updates combined when possible
- **Throttling:** Max 1 update per second per client

### Frontend Optimization

- **Lazy loading:** Charts load on scroll into view
- **Virtual scrolling:** For large data tables
- **Debouncing:** Filter inputs debounced 300ms
- **Memoization:** React components memoized
- **Code splitting:** Dashboard components lazy-loaded

---

## Integration Examples

### React Hook Usage

```typescript
import { useWebSocket } from '@/app/hooks/useWebSocket';

function MyDashboard({ dashboardId }) {
  const { lastMessage, isConnected } = useWebSocket(
    `/dashboards/${dashboardId}/ws`,
    {
      onMessage: (data) => {
        console.log('Update received:', data);
      },
      reconnectAttempts: 5,
      reconnectInterval: 3000,
    }
  );

  return (
    <div>
      <Badge variant={isConnected ? 'default' : 'destructive'}>
        {isConnected ? 'Live' : 'Disconnected'}
      </Badge>
    </div>
  );
}
```

### Dashboard Creation Flow

```typescript
async function createAndViewDashboard(company: string, industry: string) {
  // 1. Create dashboard
  const response = await fetch('/dashboards', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      company,
      industry,
      template: 'executive_summary',
      frameworks: ['porter', 'swot'],
      depth: 'standard',
    }),
  });

  const dashboard = await response.json();

  // 2. Navigate to dashboard view
  window.location.href = `/dashboard/${dashboard.id}`;
}
```

### Scenario Analysis Flow

```typescript
async function analyzeScenario() {
  const assumptions = {
    market_growth_rate: 10.0,
    competitor_entry: false,
    regulatory_change: false,
    price_change: -10.0,
    cost_change: 5.0,
    market_share_target: 30.0,
  };

  const response = await fetch('/dashboards/scenarios/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      company: 'Tesla',
      industry: 'Electric Vehicles',
      assumptions,
      forecast_period: 12,
    }),
  });

  const forecast = await response.json();
  console.log('Forecast:', forecast);
  // Display forecast charts and insights
}
```

---

## Best Practices

### For Executives

1. **Start with Executive Summary template**
2. **Set critical alert thresholds** for important metrics
3. **Review dashboard daily** (auto-updates mean no effort)
4. **Share live links** instead of PDF exports
5. **Use mobile app** for on-the-go monitoring

### For Analysts

1. **Use Market Analysis or Competitive Intelligence templates**
2. **Run scenario analyses** before making recommendations
3. **Export scenarios as PDFs** for documentation
4. **Bookmark dashboards** for quick access
5. **Set up alert notifications** for key events

### For Strategy Teams

1. **Use Competitive Intelligence template**
2. **Monitor positioning map weekly**
3. **Run multiple scenarios** to stress-test strategies
4. **Compare scenarios side-by-side**
5. **Share insights via live dashboard links**

### For Risk Managers

1. **Use Risk Monitor template**
2. **Set aggressive alert thresholds**
3. **Review risk heat map daily**
4. **Document scenarios in PDF** for compliance
5. **Share dashboard with audit team**

---

## Troubleshooting

### WebSocket Connection Issues

**Symptom:** "Disconnected" badge showing

**Solutions:**
1. Check network connectivity
2. Verify WebSocket port (8080) is open
3. Check browser console for errors
4. Try manual reconnect button
5. Refresh page to reset connection

### Dashboard Not Updating

**Symptom:** Old data showing despite auto-refresh

**Solutions:**
1. Check "Last Updated" timestamp
2. Force manual refresh
3. Verify WebSocket connection status
4. Check backend service health
5. Review agent execution logs

### Scenario Analysis Errors

**Symptom:** Scenario fails to run

**Solutions:**
1. Verify assumptions are within valid ranges
2. Check API key permissions
3. Review error message details
4. Try with default assumptions
5. Contact support if persists

### Performance Issues

**Symptom:** Slow dashboard loading or updates

**Solutions:**
1. Clear browser cache
2. Check network latency
3. Reduce number of sections
4. Increase refresh interval
5. Use simpler chart types
6. Check backend resource utilization

---

## Future Enhancements

### Planned Features

- **Collaboration:** Real-time multi-user editing and annotations
- **Custom Dashboards:** Drag-and-drop dashboard builder
- **Advanced Analytics:** ML-powered insights and predictions
- **Export to Excel:** Interactive Excel with live data connections
- **Mobile Apps:** Native iOS and Android apps
- **Notifications:** Email/SMS alerts for critical events
- **API Webhooks:** Push updates to external systems
- **Embedded Dashboards:** iframe embedding for portals
- **White-Labeling:** Customize branding and styling
- **Multi-Language:** Support for non-English users

### Roadmap

**Q1 2026:**
- Custom dashboard builder
- Advanced filtering and drill-down
- Collaboration features

**Q2 2026:**
- Native mobile apps
- Push notifications
- API webhooks

**Q3 2026:**
- ML-powered insights
- Predictive analytics
- Anomaly detection

**Q4 2026:**
- White-labeling
- Multi-language support
- Enterprise SSO

---

## Support

### Documentation
- API Reference: `/docs`
- Component Storybook: `/storybook`
- Video Tutorials: `/help/videos`

### Community
- Discord: `discord.gg/consultantos`
- Forum: `forum.consultantos.com`
- GitHub: `github.com/consultantos/dashboards`

### Enterprise Support
- Email: `support@consultantos.com`
- Slack Channel: Available for Enterprise plans
- Dedicated Success Manager: Enterprise tier

---

## Conclusion

Live Dashboards transform ConsultantOS from a **report generation tool** into a **real-time business intelligence platform**. By providing interactive, auto-updating dashboards with scenario planning capabilities, ConsultantOS offers **remarkable value** that static PDFs simply cannot match.

**Key Takeaway:** While competitors send outdated PDFs, ConsultantOS delivers **living, breathing business intelligence** that evolves with your business.
