# Advanced Strategic Intelligence Visualization Components

Production-ready React visualization components for ConsultantOS strategic intelligence platform.

## Overview

Four advanced visualization components built with React 18, TypeScript, D3.js, Recharts, and Framer Motion:

1. **CompetitivePositioningMap** - Interactive D3.js bubble chart with force-directed layout
2. **DisruptionRadar** - 5-dimensional disruption risk assessment with radar chart
3. **DecisionCard** - Strategic decision management with options comparison
4. **StrategicHealthDashboard** - Executive summary dashboard (30-second scan)

## Installation

Already installed in ConsultantOS frontend:

```bash
npm install d3 @types/d3 framer-motion recharts
```

## Components

### 1. CompetitivePositioningMap

Interactive bubble chart showing competitive landscape with D3.js force-directed layout.

**Features:**
- Force-directed bubble positioning based on market metrics
- Movement vectors showing 3-month trajectory
- Time scrubber for historical replay (12 months)
- Sentiment-based color gradients (red/yellow/green)
- Zoom/pan controls with D3 zoom behavior
- Interactive tooltips with detailed metrics
- White space opportunities and position threats

**Usage:**

```tsx
import { CompetitivePositioningMap } from '@/app/components';
import type { PositioningData } from '@/app/components';

const data: PositioningData = {
  company_position: {
    company: 'Your Company',
    x_coordinate: 15,      // Market share growth rate (%)
    y_coordinate: 25,      // Profit margin (%)
    bubble_size: 50000,    // Market cap ($M)
    sentiment_color: '#10b981',
    movement_vector: [3, 2],
    velocity: 3.6,
  },
  competitor_positions: [
    // ... competitor data
  ],
  white_space_opportunities: [
    'High-margin segment underserved',
  ],
  position_threats: [
    'Competitor moving into your segment',
  ],
  historical_snapshots: [
    // ... historical position data
  ],
};

<CompetitivePositioningMap
  data={data}
  width={800}
  height={600}
  onCompanyClick={(company) => console.log(company)}
/>
```

**Data Structure:**

```typescript
interface CompetitivePosition {
  company: string;
  x_coordinate: number;      // Growth rate %
  y_coordinate: number;      // Margin %
  bubble_size: number;       // Market cap scaled
  sentiment_color: string;   // Hex color or sentiment -1 to 1
  movement_vector: [number, number];
  velocity: number;
}

interface PositioningData {
  company_position: CompetitivePosition;
  competitor_positions: CompetitivePosition[];
  white_space_opportunities: string[];
  position_threats: string[];
  historical_snapshots?: {
    timestamp: string;
    positions: CompetitivePosition[];
  }[];
}
```

**Interactions:**
- Click bubble → Show company details
- Hover → Interactive tooltip
- Time scrubber → Animate historical movements
- Zoom/pan → Navigate large datasets

---

### 2. DisruptionRadar

5-dimensional disruption vulnerability analysis based on Christensen's disruption theory.

**Features:**
- Radar/spider chart with 5 disruption dimensions
- Risk zones color-coded (green/yellow/red)
- Threat detail cards with evidence
- Risk trend sparklines (30/60/90-day)
- Recommended action buttons
- Timeline urgency indicators

**Usage:**

```tsx
import { DisruptionRadar } from '@/app/components';
import type { DisruptionAssessment } from '@/app/components';

const data: DisruptionAssessment = {
  overall_risk: 62,          // 0-100
  risk_trend: 5.2,           // Delta from last assessment
  vulnerability_breakdown: {
    incumbent_overserving: 45,
    asymmetric_threat_velocity: 72,
    technology_shift_momentum: 68,
    customer_job_misalignment: 55,
    business_model_innovation: 50,
  },
  primary_threats: [
    {
      threat_type: 'AI-Powered Automation',
      severity: 78,
      description: 'New AI-native competitors automating workflows',
      evidence: ['Startup X raised $50M', 'Customer surveys...'],
      recommended_actions: ['Launch AI pilot', 'Acquire capability'],
      timeline: 'immediate',
    },
  ],
  risk_history: [
    // ... historical risk data
  ],
};

<DisruptionRadar
  data={data}
  onActionClick={(action, threat) => handleAction(action, threat)}
/>
```

**Disruption Dimensions:**

1. **Incumbent Overserving** - Sustaining vs disruptive innovation gap
2. **Asymmetric Threat Velocity** - Pace of disruption acceleration
3. **Technology Shift Momentum** - S-curve transition indicators
4. **Customer Job Misalignment** - Jobs-to-be-done gaps
5. **Business Model Innovation** - Value network threats

**Timeline Values:**
- `immediate` - Red (critical urgency)
- `3-months` - Orange (high urgency)
- `6-months` - Yellow (moderate urgency)
- `12-months` - Blue (low urgency)

---

### 3. DecisionCard

Strategic decision management with interactive options comparison.

**Features:**
- Urgency countdown timer
- Financial impact visualization
- Expandable options comparison table
- Pros/cons analysis with icons
- Evidence list (collapsible)
- Implementation roadmap timeline
- Action buttons: Accept, Defer, Customize

**Usage:**

```tsx
import { DecisionCard } from '@/app/components';
import type { StrategicDecision } from '@/app/components';

const decision: StrategicDecision = {
  decision_id: 'dec-001',
  title: 'Market Expansion Strategy',
  description: 'Geographic expansion approach',
  urgency_days: 14,
  financial_impact: 5000000,
  category: 'strategic',      // strategic | operational | tactical
  evidence: [
    'Market research shows $50M TAM',
    'Competitors establishing presence',
  ],
  options: [
    {
      option_id: 'opt-1',
      title: 'Organic Expansion',
      description: 'Build local teams from scratch',
      financial_impact: 2000000,
      implementation_time: '12-18 months',
      resource_requirements: ['5 local hires per market'],
      pros: ['Full control', 'Higher margins'],
      cons: ['Slower', 'Higher risk'],
      risk_level: 'medium',
      confidence: 0.75,
    },
  ],
  recommended_option: 'opt-1',
  recommendation_rationale: 'Optimal balance of speed, risk, ROI',
  implementation_roadmap: [
    {
      phase: 'Partner Selection',
      duration: '6-8 weeks',
      deliverables: ['Shortlist partners', 'Due diligence'],
    },
  ],
};

<DecisionCard
  decision={decision}
  onAccept={(decisionId, optionId) => handleAccept(decisionId, optionId)}
  onDefer={(decisionId, days) => handleDefer(decisionId, days)}
  onCustomize={(decisionId) => handleCustomize(decisionId)}
/>
```

**Urgency Levels:**
- ≤7 days: Critical (red)
- ≤30 days: High (orange)
- ≤90 days: Medium (yellow)
- >90 days: Low (blue)

**Animations:**
- Expand/collapse with Framer Motion
- Smooth transitions on option selection
- Entrance animation on mount

---

### 4. StrategicHealthDashboard

Executive summary dashboard for 30-second strategic awareness.

**Features:**
- Overall strategic health gauge (0-100)
- Top 3 threats (urgency × impact)
- Top 3 opportunities (ROI × feasibility)
- Category breakdown progress bars
- 30-day risk trend chart
- Competitive position mini-map
- Quick action buttons

**Usage:**

```tsx
import { StrategicHealthDashboard } from '@/app/components';
import type { StrategicHealthData } from '@/app/components';

const data: StrategicHealthData = {
  overall_health: 72,          // 0-100
  health_trend: 3.5,           // Delta
  last_updated: new Date().toISOString(),
  top_threats: [
    {
      threat_id: 'thr-1',
      title: 'AI-Native Competitor',
      urgency: 85,
      impact: 75,
      category: 'Competitive',
      description: 'New entrant with automation',
      mitigation_actions: ['Accelerate AI', 'Launch response'],
    },
  ],
  top_opportunities: [
    {
      opportunity_id: 'opp-1',
      title: 'Adjacent Market',
      roi_potential: 90,
      feasibility: 75,
      category: 'Growth',
      description: 'High-margin market',
      quick_wins: ['Leverage customer base'],
    },
  ],
  competitive_position: {
    x_coordinate: 15,
    y_coordinate: 25,
    market_share_percentile: 35,
    competitive_strength: 'challenger',
  },
  risk_trend_30d: [
    { date: '2025-10-10', risk_score: 35 },
    // ... more data points
  ],
  category_breakdown: {
    market_position: 68,
    innovation_capacity: 75,
    operational_efficiency: 72,
    financial_health: 73,
  },
};

<StrategicHealthDashboard
  data={data}
  onThreatAction={(threatId, action) => handleThreat(threatId, action)}
  onOpportunityAction={(oppId) => handleOpportunity(oppId)}
  onRefresh={() => refreshData()}
/>
```

**Health Levels:**
- 80-100: Excellent (green) - "Strong strategic position"
- 60-79: Good (blue) - "Stable with opportunities"
- 40-59: Fair (yellow) - "Attention required"
- 0-39: At Risk (red) - "Immediate action needed"

**Competitive Strength:**
- `leader` 👑 - Market leader position
- `challenger` ⚔️ - Strong challenger
- `follower` 🏃 - Following competition
- `at-risk` ⚠️ - Vulnerable position

---

## Demo Component

```tsx
import { VisualizationDemo } from '@/app/components';

// Includes sample data for all 4 components
<VisualizationDemo />
```

Access at: `/components/demo` or wherever you mount it.

---

## Integration with Backend

### Real-time Data Updates

**Option 1: Polling (Recommended for MVP)**

```tsx
import { useState, useEffect } from 'react';
import { StrategicHealthDashboard } from '@/app/components';

function DashboardPage() {
  const [data, setData] = useState<StrategicHealthData | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch('/api/strategic-health');
      const healthData = await res.json();
      setData(healthData);
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (!data) return <div>Loading...</div>;

  return <StrategicHealthDashboard data={data} />;
}
```

**Option 2: WebSocket (Production)**

```tsx
import { useState, useEffect } from 'react';

function useStrategicHealth() {
  const [data, setData] = useState<StrategicHealthData | null>(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080/ws/strategic-health');

    ws.onmessage = (event) => {
      const healthData = JSON.parse(event.data);
      setData(healthData);
    };

    return () => ws.close();
  }, []);

  return data;
}
```

### Backend Agent Integration

Connect to new backend agents:

```python
# Backend: consultantos/agents/visualization_agent.py

class VisualizationAgent(BaseAgent):
    async def get_competitive_positioning(self, company: str) -> PositioningData:
        """Generate competitive positioning data"""
        # Use market_agent, research_agent for data collection
        # Transform to PositioningData format
        pass

    async def get_disruption_assessment(self, company: str) -> DisruptionAssessment:
        """Calculate disruption risk across 5 dimensions"""
        # Use framework_agent for Christensen analysis
        pass

    async def get_strategic_decisions(self, company: str) -> List[StrategicDecision]:
        """Identify pending strategic decisions"""
        pass

    async def get_strategic_health(self, company: str) -> StrategicHealthData:
        """Calculate overall strategic health"""
        pass
```

---

## Performance Optimization

### Virtualization for Large Datasets

Use `react-window` or `react-virtualized` for large competitor lists:

```tsx
import { FixedSizeList } from 'react-window';

// For positioning map with 100+ competitors
const CompetitorList = ({ competitors }) => (
  <FixedSizeList
    height={600}
    itemCount={competitors.length}
    itemSize={80}
  >
    {({ index, style }) => (
      <div style={style}>
        {competitors[index].company}
      </div>
    )}
  </FixedSizeList>
);
```

### Memoization

```tsx
import { useMemo } from 'react';

const sortedThreats = useMemo(() => {
  return threats.sort((a, b) =>
    (b.urgency * b.impact) - (a.urgency * a.impact)
  );
}, [threats]);
```

### D3 Performance

For CompetitivePositioningMap with 50+ bubbles:

```tsx
// Limit simulation iterations for faster rendering
simulation.stop();
for (let i = 0; i < 100; i++) simulation.tick(); // Reduced from 300
```

---

## Accessibility (WCAG AA)

All components implement:

### Keyboard Navigation
- Tab through interactive elements
- Enter/Space to activate buttons
- Arrow keys for sliders/scrubbers
- Escape to close modals/tooltips

### Screen Reader Support
- Semantic HTML (`<button>`, `<nav>`, etc.)
- ARIA labels for charts and graphs
- Live regions for dynamic updates
- Descriptive alt text

### Color Contrast
- All text meets 4.5:1 contrast ratio
- Interactive elements distinguishable without color alone
- Focus indicators visible

### Testing

```tsx
import { render, screen } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

it('should have no accessibility violations', async () => {
  const { container } = render(<StrategicHealthDashboard data={mockData} />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

---

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile Safari 14+
- Chrome Android 90+

**Note:** IE11 not supported due to D3.js v7 and modern React features.

---

## Troubleshooting

### D3.js SVG Not Rendering

**Issue:** Blank SVG canvas

**Solution:**
```tsx
// Ensure ref is attached before D3 operations
useEffect(() => {
  if (!svgRef.current) return;

  const svg = d3.select(svgRef.current);
  // ... D3 operations
}, [data]); // Re-run when data changes
```

### Framer Motion Layout Shift

**Issue:** Content jumping during animations

**Solution:**
```tsx
// Use AnimatePresence with mode
<AnimatePresence mode="wait">
  {isExpanded && (
    <motion.div
      initial={{ height: 0 }}
      animate={{ height: 'auto' }}
      exit={{ height: 0 }}
    />
  )}
</AnimatePresence>
```

### Recharts Responsive Issues

**Issue:** Chart not resizing

**Solution:**
```tsx
// Ensure ResponsiveContainer has explicit dimensions
<ResponsiveContainer width="100%" height={300}>
  <RadarChart data={data}>
    {/* ... */}
  </RadarChart>
</ResponsiveContainer>
```

---

## Future Enhancements

### Phase 2 Features
- [ ] Export charts as PNG/SVG
- [ ] Share chart via URL
- [ ] Custom color themes
- [ ] Advanced filtering/search
- [ ] Comparative analysis mode

### Phase 3 Features
- [ ] Real-time collaboration
- [ ] Annotation system
- [ ] AI-powered insights overlay
- [ ] Predictive analytics
- [ ] Integration with external BI tools

---

## Contributing

When adding new visualization components:

1. **Follow existing patterns:**
   - TypeScript with strict types
   - Comprehensive JSDoc comments
   - Responsive design (desktop + tablet)
   - Accessibility compliance

2. **Include sample data:**
   - Add to `VisualizationDemo.tsx`
   - Document data structure in README

3. **Performance benchmarks:**
   - Test with 100+ data points
   - Ensure <100ms render time

4. **Browser testing:**
   - Chrome, Firefox, Safari
   - Desktop and mobile

---

## License

MIT License - Part of ConsultantOS Platform

---

## Support

For issues or questions:
- GitHub Issues: [Create an issue](https://github.com/rish2jain/consultantOS/issues)
- Documentation: See project README.md for setup and usage
- Email: contact@consultantos.com (or use GitHub Issues for support)
