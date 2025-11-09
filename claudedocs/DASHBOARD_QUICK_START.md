# Live Dashboard Quick Start Guide

## 5-Minute Setup

### Prerequisites
- Backend running on `http://localhost:8080`
- Frontend running on `http://localhost:3000`
- API keys configured (GEMINI_API_KEY, TAVILY_API_KEY)

---

## Step 1: Start the Backend (Terminal 1)

```bash
cd /Users/rish2jain/Documents/Hackathons/ConsultantOS

# Start backend with auto-reload
python main.py

# Or with uvicorn directly
uvicorn consultantos.api.main:app --host 0.0.0.0 --port 8080 --reload
```

**Verify:** Visit `http://localhost:8080/docs` - should see Swagger UI with dashboard endpoints

---

## Step 2: Start the Frontend (Terminal 2)

```bash
cd frontend

# Install dependencies (if not already done)
npm install

# Start dev server
npm run dev
```

**Verify:** Visit `http://localhost:3000` - should see Next.js app

---

## Step 3: Create Your First Dashboard (Terminal 3)

```bash
# Create executive dashboard for Tesla
curl -X POST "http://localhost:8080/dashboards" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "template": "executive_summary",
    "frameworks": ["porter", "swot"],
    "depth": "standard"
  }'
```

**Response:**
```json
{
  "id": "dash_tesla_abc123",
  "company": "Tesla",
  "industry": "Electric Vehicles",
  "template": "executive_summary",
  ...
}
```

**Copy the `id` value** (e.g., `dash_tesla_abc123`)

---

## Step 4: View the Live Dashboard

Visit in browser:
```
http://localhost:3000/dashboard/dash_tesla_abc123
```

You should see:
- ✅ Real-time dashboard with WebSocket connection
- ✅ "Live" badge (green) indicating active connection
- ✅ Key metrics cards
- ✅ Critical alerts section
- ✅ Interactive charts
- ✅ Auto-refresh every 5 minutes

---

## Step 5: Test Real-Time Updates

**In Terminal 3, force a refresh:**
```bash
curl -X POST "http://localhost:8080/dashboards/dash_tesla_abc123/refresh"
```

**In Browser:**
- Watch the "Last updated" timestamp change
- Metrics should update (if new data available)
- All connected clients receive updates automatically

---

## Step 6: Run a Scenario Analysis

**Navigate to Scenario Planner tab in dashboard, or use API:**

```bash
curl -X POST "http://localhost:8080/dashboards/scenarios/run" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "assumptions": {
      "market_growth_rate": 10.0,
      "competitor_entry": false,
      "regulatory_change": false,
      "price_change": -10.0,
      "cost_change": 5.0,
      "market_share_target": 30.0
    },
    "forecast_period": 12
  }'
```

**Response:**
```json
{
  "scenario_id": "scenario_xyz789",
  "revenue_forecast": [25000000, 26000000, ...],
  "profit_forecast": [2500000, 2700000, ...],
  "market_share_forecast": [22.0, 23.5, ...],
  "risk_score": 0.35,
  "confidence": 0.78,
  "key_insights": [
    "Price reduction drives volume growth",
    "Market share gains offset margin pressure"
  ]
}
```

---

## Common Use Cases

### Use Case 1: Executive Dashboard
```bash
curl -X POST "http://localhost:8080/dashboards" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Apple",
    "industry": "Consumer Electronics",
    "template": "executive_summary",
    "frameworks": ["porter", "swot", "pestel"],
    "depth": "deep"
  }'
```

### Use Case 2: Competitive Intelligence
```bash
curl -X POST "http://localhost:8080/dashboards" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Netflix",
    "industry": "Streaming Services",
    "template": "competitive_intelligence",
    "frameworks": ["porter"],
    "depth": "standard"
  }'
```

### Use Case 3: Market Analysis
```bash
curl -X POST "http://localhost:8080/dashboards" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Beyond Meat",
    "industry": "Plant-Based Foods",
    "template": "market_analysis",
    "frameworks": ["swot"],
    "depth": "standard"
  }'
```

### Use Case 4: Financial Performance
```bash
curl -X POST "http://localhost:8080/dashboards" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Goldman Sachs",
    "industry": "Investment Banking",
    "template": "financial_performance",
    "frameworks": ["porter", "pestel"],
    "depth": "deep"
  }'
```

### Use Case 5: Risk Monitor
```bash
curl -X POST "http://localhost:8080/dashboards" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "BP",
    "industry": "Oil & Gas",
    "template": "risk_monitor",
    "frameworks": ["pestel"],
    "depth": "deep"
  }'
```

### Use Case 6: Innovation Tracker
```bash
curl -X POST "http://localhost:8080/dashboards" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Moderna",
    "industry": "Biotechnology",
    "template": "innovation_tracker",
    "frameworks": ["swot"],
    "depth": "standard"
  }'
```

---

## Testing WebSocket Connection

### JavaScript Console Test

Open browser console on dashboard page and run:

```javascript
// Get dashboard ID from URL
const dashboardId = window.location.pathname.split('/').pop();

// Create WebSocket connection
const ws = new WebSocket(`ws://localhost:8080/dashboards/${dashboardId}/ws`);

ws.onopen = () => {
  console.log('✅ WebSocket connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('📨 Message received:', data.type);
  console.log(data);
};

ws.onerror = (error) => {
  console.error('❌ WebSocket error:', error);
};

ws.onclose = () => {
  console.log('🔌 WebSocket disconnected');
};
```

**Expected Output:**
```
✅ WebSocket connected
📨 Message received: initial
{type: 'initial', data: {id: 'dash_tesla_abc123', ...}}
```

---

## Troubleshooting

### Issue: "Dashboard not found"
**Solution:**
```bash
# List all available templates
curl http://localhost:8080/dashboards/templates/all

# Verify dashboard ID is correct
# Check backend logs for errors
```

### Issue: "WebSocket connection failed"
**Solution:**
1. Verify backend is running on port 8080
2. Check browser console for CORS errors
3. Ensure WebSocket endpoint is accessible:
   ```bash
   curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     http://localhost:8080/dashboards/dash_test_123/ws
   ```

### Issue: "Dashboard shows old data"
**Solution:**
```bash
# Force manual refresh
curl -X POST "http://localhost:8080/dashboards/{dashboard_id}/refresh"

# Check auto-refresh is enabled
# Verify WebSocket connection status (should show "Live" badge)
```

### Issue: "Scenario analysis returns error"
**Solution:**
1. Verify assumptions are within valid ranges
2. Check API keys are configured
3. Review backend logs for agent errors
4. Try with default assumptions:
   ```bash
   curl -X POST "http://localhost:8080/dashboards/scenarios/run" \
     -H "Content-Type: application/json" \
     -d '{
       "company": "Test Company",
       "industry": "Technology",
       "assumptions": {
         "market_growth_rate": 5.0,
         "competitor_entry": false,
         "regulatory_change": false,
         "price_change": 0,
         "cost_change": 0
       },
       "forecast_period": 12
     }'
   ```

---

## API Reference Quick Links

### Dashboard Endpoints
- **Create:** `POST /dashboards`
- **Get:** `GET /dashboards/{id}`
- **Refresh:** `POST /dashboards/{id}/refresh`
- **WebSocket:** `WS /dashboards/{id}/ws`
- **Export PDF:** `POST /dashboards/{id}/export/pdf`
- **Export JSON:** `POST /dashboards/{id}/export/json`

### Template Endpoints
- **List All:** `GET /dashboards/templates/all`
- **Get Template:** `GET /dashboards/templates/{template_id}`
- **By Audience:** `GET /dashboards/templates/audience/{audience}`
- **By Use Case:** `GET /dashboards/templates/use-case/{use_case}`

### Scenario Endpoints
- **Run Scenario:** `POST /dashboards/scenarios/run`

### Documentation
- **Swagger UI:** `http://localhost:8080/docs`
- **ReDoc:** `http://localhost:8080/redoc`

---

## Component Usage Examples

### React: Using WebSocket Hook

```typescript
import { useWebSocket } from '@/app/hooks/useWebSocket';

function MyComponent({ dashboardId }) {
  const { lastMessage, isConnected, reconnect } = useWebSocket(
    `/dashboards/${dashboardId}/ws`,
    {
      onMessage: (data) => {
        console.log('Update:', data);
      },
      onError: (error) => {
        console.error('WebSocket error:', error);
      },
    }
  );

  return (
    <div>
      <p>Connected: {isConnected ? 'Yes' : 'No'}</p>
      {!isConnected && (
        <button onClick={reconnect}>Reconnect</button>
      )}
    </div>
  );
}
```

### React: Rendering Dashboard

```typescript
import { InteractiveDashboard } from '@/app/components/InteractiveDashboard';

export default function DashboardPage({ params }) {
  return (
    <div className="container mx-auto px-4 py-8">
      <InteractiveDashboard dashboardId={params.id} />
    </div>
  );
}
```

### React: Scenario Planning

```typescript
import { ScenarioPlanner } from '@/app/components/ScenarioPlanner';

export default function ScenarioPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <ScenarioPlanner
        company="Tesla"
        industry="Electric Vehicles"
      />
    </div>
  );
}
```

### React: Competitive Landscape

```typescript
import { CompetitiveLandscape } from '@/app/components/CompetitiveLandscape';

export default function CompetitivePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <CompetitiveLandscape company="Tesla" />
    </div>
  );
}
```

---

## Next Steps

1. ✅ **Create your first dashboard** using the examples above
2. ✅ **Test WebSocket updates** by refreshing dashboard
3. ✅ **Run scenario analysis** with different assumptions
4. ✅ **Explore templates** to find the right fit
5. ✅ **Customize components** for your specific needs

---

## Resources

- **Full Documentation:** [LIVE_DASHBOARDS_GUIDE.md](../LIVE_DASHBOARDS_GUIDE.md)
- **Implementation Details:** [LIVE_DASHBOARDS_IMPLEMENTATION.md](./LIVE_DASHBOARDS_IMPLEMENTATION.md)
- **API Documentation:** `http://localhost:8080/docs`
- **Component Library:** `frontend/app/components/`
- **Backend Service:** `consultantos/dashboards/service.py`

---

## Support

For issues or questions:
1. Check [LIVE_DASHBOARDS_GUIDE.md](../LIVE_DASHBOARDS_GUIDE.md) troubleshooting section
2. Review backend logs for errors
3. Check browser console for frontend errors
4. Verify WebSocket connection status
5. Test with simple examples first

**Happy Dashboarding! 📊✨**
