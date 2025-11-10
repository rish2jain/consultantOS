# Analytics Builder - Complete Examples

## Example 1: Creating a Financial KPI Dashboard

### Step 1: Create Revenue Formula
```bash
curl -X POST http://localhost:8080/dashboards/formulas \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Revenue Forecast",
    "expression": "current_revenue * (1 + growth_rate)",
    "description": "Forecast revenue with growth rate",
    "category": "financial",
    "examples": {
      "optimistic": {
        "current_revenue": 1000000,
        "growth_rate": 0.25,
        "expected_result": 1250000
      }
    }
  }'
```

Response:
```json
{
  "formula_id": "f-abc123",
  "name": "Revenue Forecast",
  "expression": "current_revenue * (1 + growth_rate)",
  "variables": ["current_revenue", "growth_rate"],
  "created_at": "2025-11-09T14:00:00Z"
}
```

### Step 2: Create Gross Margin Formula
```bash
curl -X POST http://localhost:8080/dashboards/formulas \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gross Margin %",
    "expression": "(revenue - cogs) / revenue * 100",
    "description": "Gross profit margin percentage",
    "category": "financial"
  }'
```

### Step 3: Create KPI from Formulas
```bash
# Revenue KPI
curl -X POST "http://localhost:8080/dashboards/kpis?name=Projected+Revenue&formula_id=f-abc123&target_value=1500000&alert_threshold=1000000"

# Margin KPI  
curl -X POST "http://localhost:8080/dashboards/kpis?name=Gross+Margin&formula_id=f-xyz789&target_value=40&alert_threshold=30"
```

### Step 4: Evaluate KPIs
```bash
curl -X POST http://localhost:8080/dashboards/kpis/kpi-rev123/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "context": {
      "current_revenue": 1000000,
      "growth_rate": 0.20
    }
  }'
```

Response:
```json
{
  "kpi": {
    "kpi_id": "kpi-rev123",
    "name": "Projected Revenue",
    "current_value": 1200000,
    "target_value": 1500000,
    "trend": "up",
    "percentage_change": 5.5,
    "status": "normal"
  },
  "alerts": []
}
```

### Step 5: Create Dashboard
```bash
curl -X POST http://localhost:8080/dashboards \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Finance Dashboard Q4",
    "description": "Q4 2025 Financial Metrics",
    "layout": "grid",
    "refresh_interval": 300,
    "tags": ["finance", "q4", "executive"],
    "elements": [
      {
        "type": "kpi",
        "kpi_id": "kpi-rev123",
        "position": {"x": 0, "y": 0, "width": 6, "height": 2},
        "order": 1
      },
      {
        "type": "kpi",
        "kpi_id": "kpi-margin123",
        "position": {"x": 6, "y": 0, "width": 6, "height": 2},
        "order": 2
      }
    ]
  }'
```

---

## Example 2: Sales Pipeline Dashboard from Template

### Step 1: Create from Template
```bash
curl -X POST "http://localhost:8080/dashboards/templates/sales" \
  -H "Content-Type: application/json" \
  -d '{"name": "November Sales Pipeline"}'
```

Response:
```json
{
  "dashboard_id": "d-sales-nov",
  "name": "November Sales Pipeline",
  "layout": "grid",
  "created_at": "2025-11-09T14:05:00Z"
}
```

### Step 2: Create Sales Funnel Formula
```bash
curl -X POST http://localhost:8080/dashboards/formulas \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Conversion Rate",
    "expression": "(opportunities_closed / opportunities_created) * 100",
    "description": "Sales conversion rate",
    "category": "sales"
  }'
```

### Step 3: Create Sales Chart
```bash
curl -X POST http://localhost:8080/dashboards/charts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pipeline by Stage",
    "chart_type": "column",
    "data_source": {
      "type": "static",
      "data": [
        {"stage": "Leads", "value": 150},
        {"stage": "Qualified", "value": 75},
        {"stage": "Proposal", "value": 30},
        {"stage": "Closed", "value": 12}
      ]
    },
    "config": {
      "title": "Sales Pipeline by Stage",
      "x_axis_label": "Stage",
      "y_axis_label": "Opportunities"
    }
  }'
```

---

## Example 3: Marketing Campaign Analysis

### Step 1: Create Marketing Formulas
```bash
# CAC Formula
curl -X POST http://localhost:8080/dashboards/formulas \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Acquisition Cost",
    "expression": "marketing_spend / new_customers",
    "category": "marketing"
  }'

# ROI Formula
curl -X POST http://localhost:8080/dashboards/formulas \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Campaign ROI",
    "expression": "(revenue_generated - campaign_cost) / campaign_cost * 100",
    "category": "marketing"
  }'
```

### Step 2: Evaluate Campaign Performance
```bash
curl -X POST http://localhost:8080/dashboards/formulas/f-cac/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "context": {
      "marketing_spend": 50000,
      "new_customers": 1250
    }
  }'
```

Response:
```json
{
  "formula_id": "f-cac",
  "expression": "marketing_spend / new_customers",
  "result": 40,
  "context": {
    "marketing_spend": 50000,
    "new_customers": 1250
  }
}
```

---

## Example 4: Real-time KPI Monitoring

### Setup: Create Multiple KPIs
```bash
# Website Traffic KPI
curl -X POST "http://localhost:8080/dashboards/kpis?name=Daily+Users&formula_id=f-traffic&target_value=100000&alert_threshold=80000"

# Email Open Rate KPI
curl -X POST "http://localhost:8080/dashboards/kpis?name=Email+Opens&formula_id=f-opens&target_value=25&alert_threshold=15"
```

### Monitor KPI Alerts
```bash
# Get KPI alerts
curl -X GET "http://localhost:8080/dashboards/kpis/kpi-traffic/alerts"
```

Response when alert triggered:
```json
[
  {
    "alert_id": "alert-123",
    "kpi_id": "kpi-traffic",
    "severity": "warning",
    "message": "Daily Users below threshold: 75000 < 80000",
    "threshold_value": 80000,
    "actual_value": 75000,
    "triggered_at": "2025-11-09T14:30:00Z"
  }
]
```

### Get KPI History
```bash
curl -X GET "http://localhost:8080/dashboards/kpis/kpi-traffic/history?limit=30"
```

Response:
```json
[
  {
    "kpi_id": "kpi-traffic",
    "value": 95000,
    "timestamp": "2025-11-09T14:00:00Z"
  },
  {
    "kpi_id": "kpi-traffic",
    "value": 92000,
    "timestamp": "2025-11-09T13:00:00Z"
  }
]
```

---

## Example 5: Executive Dashboard with Advanced Analytics

### Create Executive Template
```bash
curl -X POST "http://localhost:8080/dashboards/templates/executive" \
  -H "Content-Type: application/json" \
  -d '{"name": "Executive Business Review"}'
```

### Add Complex Formula with Multiple Functions
```bash
curl -X POST http://localhost:8080/dashboards/formulas \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weighted Opportunity Score",
    "expression": "(AVG(deal_sizes) * COUNT(active_deals)) / (SUM(sales_costs) / SUM(revenue))",
    "description": "Opportunity score weighted by deal size and costs",
    "category": "financial"
  }'
```

### Evaluate with Advanced Analytics
```bash
curl -X POST http://localhost:8080/dashboards/kpis/kpi-opp/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "context": {
      "deal_sizes": [50000, 75000, 100000, 60000],
      "active_deals": 4,
      "sales_costs": 25000,
      "revenue": 285000
    }
  }'
```

---

## Example 6: Export Dashboard for Presentation

### Export to PDF
```bash
curl -X POST "http://localhost:8080/dashboards/d-finance/export" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "pdf",
    "include_data": true,
    "page_orientation": "landscape",
    "custom_title": "Q4 2025 Financial Report"
  }'
```

Response:
```json
{
  "dashboard_id": "d-finance",
  "format": "pdf",
  "status": "pending",
  "file_url": "/exports/d-finance.pdf"
}
```

### Export to Excel
```bash
curl -X POST "http://localhost:8080/dashboards/d-sales/export" \
  -H "Content-Type: application/json" \
  -d '{
    "format": "excel",
    "include_data": true
  }'
```

---

## Example 7: Get Analytics Summary

```bash
curl -X GET "http://localhost:8080/dashboards/summary"
```

Response:
```json
{
  "total_dashboards": 15,
  "total_charts": 42,
  "total_kpis": 28,
  "total_formulas": 35,
  "active_alerts": 3,
  "last_updated": "2025-11-09T14:45:00Z",
  "top_charts": [
    {
      "chart_id": "chart-revenue",
      "name": "Revenue Trend",
      "chart_type": "line"
    }
  ],
  "recent_alerts": [
    {
      "alert_id": "alert-123",
      "kpi_id": "kpi-traffic",
      "severity": "warning",
      "message": "Daily Users below threshold"
    }
  ]
}
```

---

## Business Use Cases

### 1. CFO Dashboard
Formulas: Revenue, Gross Margin, Operating Margin, Net Margin, Cash Flow
Charts: Trend lines for each metric, pie chart for revenue by segment
KPIs: Quarterly targets vs actuals

### 2. Sales Manager Dashboard
Formulas: Win Rate, Pipeline Value, Forecast Accuracy, CAC
Charts: Funnel chart, pipeline by stage, win rate trend
KPIs: Monthly quota progress, pipeline health

### 3. Marketing Director Dashboard
Formulas: CAC, LTV, ROI by channel, conversion rate
Charts: Channel performance, campaign performance, conversion funnel
KPIs: Lead generation, cost per lead, conversion rates

### 4. Operations Director Dashboard
Formulas: Process efficiency, cost per unit, quality metrics
Charts: Process efficiency trend, quality scorecard, cost breakdown
KPIs: On-time delivery, defect rate, cost per unit

### 5. CEO Dashboard
Formulas: Revenue growth, profitability, market share, employee satisfaction
Charts: Company trajectory, competitive positioning, key metrics
KPIs: Strategic objectives progress, market performance

---

## Formula Syntax Reference

### Arithmetic
```
revenue - cogs
cost * quantity
total / count
value ^ 2  (power)
amount % divisor  (modulo)
```

### Comparisons
```
value > threshold
amount < budget
score >= target
cost <= limit
value == target
amount != expected
```

### Functions
```
SUM(values)
AVG(values)
MIN(values)
MAX(values)
COUNT(values)
ABS(-100)
SQRT(16)
ROUND(3.14159, 2)
IF(condition, true_val, false_val)
AND(cond1, cond2)
OR(cond1, cond2)
NOT(condition)
```

### Complex Examples
```
(SUM(monthly_sales) - SUM(monthly_costs)) / SUM(monthly_sales) * 100
AVG(deal_sizes) * COUNT(closed_deals) - marketing_expense
IF(revenue > target, revenue - target, 0)
MAX(competitor_price) - our_price
```

