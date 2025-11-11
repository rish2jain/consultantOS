# Phase 2 Critical Agents - Implementation Guide

This guide covers the two critical Phase 2 agents for ConsultantOS: **PositioningAgent** and **DisruptionAgent**.

## Table of Contents

- [Overview](#overview)
- [PositioningAgent](#positioningagent)
- [DisruptionAgent](#disruptionagent)
- [Integration Examples](#integration-examples)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Deployment](#deployment)

---

## Overview

### Purpose

These agents extend ConsultantOS with advanced competitive intelligence capabilities:

- **PositioningAgent**: Dynamic competitive positioning with movement vector analysis
- **DisruptionAgent**: Disruption vulnerability scoring using Christensen's frameworks

### Architecture Integration

Both agents integrate with existing Phase 1 agents:

```
┌─────────────────┐
│ ResearchAgent   │ → Sentiment, news signals
└─────────────────┘
         ↓
┌─────────────────┐
│  MarketAgent    │ → Search trends, keyword velocity
└─────────────────┘
         ↓
┌─────────────────┐
│ FinancialAgent  │ → Margins, market cap, revenue
└─────────────────┘
         ↓
┌─────────────────────────────────────┐
│  PositioningAgent | DisruptionAgent │
└─────────────────────────────────────┘
```

---

## PositioningAgent

### Capabilities

1. **Position Calculation**
   - X-axis: Market share growth rate (from Market Agent)
   - Y-axis: Profit margin (from Financial Agent)
   - Bubble size: Market capitalization
   - Color: News sentiment score

2. **Strategic Group Clustering**
   - K-means clustering on position vectors
   - Identifies companies competing on similar dimensions
   - Detects white space opportunities

3. **Trajectory Analysis**
   - 3-month movement vectors (where competitors are heading)
   - Collision detection (competitors moving toward your position)
   - Velocity calculation (speed of competitive movement)

4. **Alert Generation**
   - Warns when competitor threatens position (6-month window)
   - Identifies white space opportunities
   - Recommends strategic moves

### Models

#### DynamicPositioning (Main Output)

```python
from consultantos.models.positioning import DynamicPositioning

{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "current_position": {
        "axis_x": "Market Growth",
        "axis_y": "Profit Margin",
        "x_value": 65.0,
        "y_value": 25.0,
        "market_share": 18.0,
        "positioning_statement": "growing growth, 25.0% margin"
    },
    "movement_vector_x": 5.0,
    "movement_vector_y": 1.5,
    "velocity": 5.22,
    "predicted_x": 75.0,
    "predicted_y": 28.0,
    "strategic_groups": [
        {
            "group_id": 1,
            "companies": ["Tesla", "Rivian"],
            "centroid_x": 70.0,
            "centroid_y": 68.0,
            "characteristics": "Premium growth leaders",
            "white_space_distance": 14.14
        }
    ],
    "white_space_opportunities": [
        {
            "position_x": 75.0,
            "position_y": 75.0,
            "market_potential": 1000.0,
            "entry_barrier": 50.0,
            "required_capabilities": ["Premium innovation", "Market development"],
            "risk_score": 60.0
        }
    ],
    "position_threats": [
        {
            "threatening_company": "Competitor A",
            "threat_type": "collision",
            "severity": 75.0,
            "time_to_impact": 180,
            "recommended_response": "Differentiate on Profit Margin or accelerate Market Growth"
        }
    ],
    "recommendations": [
        "Strengthen premium positioning",
        "Monitor competitor movements",
        "Explore white space opportunities"
    ],
    "collision_risk": 45.0,
    "confidence_score": 85.0
}
```

### Usage Example

```python
from consultantos.agents.positioning_agent import PositioningAgent
from consultantos.agents import ResearchAgent, MarketAgent, FinancialAgent

# Initialize agents
research_agent = ResearchAgent()
market_agent = MarketAgent()
financial_agent = FinancialAgent()
positioning_agent = PositioningAgent()

# Gather data from Phase 1 agents
input_data = {"company": "Tesla", "industry": "Electric Vehicles"}

research_data = await research_agent.execute(input_data)
market_data = await market_agent.execute(input_data)
financial_data = await financial_agent.execute(input_data)

# Gather competitor data (same process for each competitor)
competitors = []
for comp_name in ["Rivian", "Lucid Motors", "Ford"]:
    comp_input = {"company": comp_name, "industry": "Electric Vehicles"}
    comp_data = {
        "name": comp_name,
        "market_data": await market_agent.execute(comp_input),
        "financial_data": await financial_agent.execute(comp_input),
        "research_data": await research_agent.execute(comp_input)
    }
    competitors.append(comp_data)

# Execute positioning analysis
positioning_input = {
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "market_data": market_data,
    "financial_data": financial_data,
    "research_data": research_data,
    "competitors": competitors
}

result = await positioning_agent.execute(positioning_input)

# Access results
print(f"Position: ({result.current_position.x_value}, {result.current_position.y_value})")
print(f"Velocity: {result.velocity:.2f}")
print(f"Collision Risk: {result.collision_risk:.1f}/100")
print(f"Strategic Groups: {len(result.strategic_groups)}")
print(f"White Spaces: {len(result.white_space_opportunities)}")

for threat in result.position_threats:
    print(f"⚠️  {threat.threatening_company}: {threat.severity:.0f}% severity")
```

---

## DisruptionAgent

### Capabilities

Calculates disruption risk (0-100) using Christensen's disruption theory framework:

1. **Incumbent Overserving (30%)**
   - Profit margin vs. industry average (high = vulnerable)
   - Sentiment analysis for "too expensive", "overkill" signals
   - Feature bloat indicators

2. **Asymmetric Threat Velocity (25%)**
   - Small competitors growing >3x industry average
   - Unusual geographic foothold markets
   - Different business model patterns

3. **Technology Shift Momentum (20%)**
   - Keyword velocity ("AI", "blockchain", emerging tech)
   - Competitor adoption rate of new technologies
   - Technology enabler identification

4. **Customer Job Misalignment (15%)**
   - Sentiment: customer pain point analysis
   - Search trends: "alternative to X" patterns
   - Jobs-to-be-Done inference from entity relationships

5. **Business Model Innovation (10%)**
   - Subscription vs. license model shifts
   - Platform vs. product trends
   - Value network analysis

### Models

#### DisruptionAssessment (Main Output)

```python
from consultantos.models.disruption import DisruptionAssessment

{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "overall_risk": 55.0,
    "risk_trend": 5.0,
    "risk_level": "high",
    "vulnerability_breakdown": {
        "incumbent_overserving": 65.0,
        "asymmetric_threat_velocity": 45.0,
        "technology_shift": 70.0,
        "customer_job_misalignment": 35.0,
        "business_model_innovation": 60.0
    },
    "primary_threats": [
        {
            "threat_name": "Competitor A",
            "disruption_score": 75.0,
            "growth_velocity": 3.0,
            "business_model": "Emerging platform",
            "customer_jobs": ["Simplified solution", "Lower cost alternative"],
            "timeline_to_impact": 122,
            "recommended_response": "Develop defensive innovation",
            "threat_indicators": ["Rapid growth", "Different business model"]
        }
    ],
    "technology_trends": [
        {
            "technology": "AI",
            "keyword_velocity": 45.0,
            "adoption_rate": 30.0,
            "enabler_score": 75.0,
            "maturity_stage": "growing"
        }
    ],
    "job_misalignments": [
        {
            "job_description": "Affordable, simple solution",
            "misalignment_score": 20.0,
            "alternative_searches": ["alternative to X", "cheaper EV", "simple electric car"],
            "pain_points": ["Price concerns", "Complexity"],
            "opportunity_size": 500.0
        }
    ],
    "model_shifts": [
        {
            "model_type": "Subscription",
            "shift_velocity": 15.0,
            "competitive_adoption": 40.0,
            "value_network_impact": "high",
            "disruption_potential": 90.0
        }
    ],
    "strategic_recommendations": [
        "Develop low-cost product line to compete with disruptors",
        "Invest in emerging technology adoption",
        "Simplify core offering to address customer jobs"
    ],
    "early_warning_signals": [
        "Monitor price sensitivity in customer feedback",
        "Track 'alternative to' search patterns",
        "Monitor emerging technology adoption rates"
    ],
    "confidence_score": 85.0,
    "generated_at": "2024-11-10T18:00:00Z"
}
```

### Usage Example

```python
from consultantos.agents.disruption_agent import DisruptionAgent
from consultantos.agents import ResearchAgent, MarketAgent, FinancialAgent

# Initialize agents
research_agent = ResearchAgent()
market_agent = MarketAgent()
financial_agent = FinancialAgent()
disruption_agent = DisruptionAgent()

# Gather data from Phase 1 agents
input_data = {"company": "Tesla", "industry": "Electric Vehicles"}

research_data = await research_agent.execute(input_data)
market_data = await market_agent.execute(input_data)
financial_data = await financial_agent.execute(input_data)

# Gather competitor data
competitors = []
for comp_name in ["Rivian", "BYD", "NIO"]:
    comp_input = {"company": comp_name, "industry": "Electric Vehicles"}
    comp_data = {
        "name": comp_name,
        "market_data": await market_agent.execute(comp_input),
        "financial_data": await financial_agent.execute(comp_input),
        "research_data": await research_agent.execute(comp_input)
    }
    competitors.append(comp_data)

# Execute disruption analysis
disruption_input = {
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "market_data": market_data,
    "financial_data": financial_data,
    "research_data": research_data,
    "competitors": competitors
}

result = await disruption_agent.execute(disruption_input)

# Access results
print(f"Overall Disruption Risk: {result.overall_risk:.1f}/100 ({result.risk_level})")
print(f"Risk Trend (30-day): {result.risk_trend:+.1f}")

print("\nVulnerability Breakdown:")
vb = result.vulnerability_breakdown
print(f"  Overserving: {vb.incumbent_overserving:.0f}/100")
print(f"  Threat Velocity: {vb.asymmetric_threat_velocity:.0f}/100")
print(f"  Tech Shift: {vb.technology_shift:.0f}/100")
print(f"  Job Misalignment: {vb.customer_job_misalignment:.0f}/100")
print(f"  Model Innovation: {vb.business_model_innovation:.0f}/100")

print(f"\nPrimary Threats: {len(result.primary_threats)}")
for threat in result.primary_threats:
    print(f"  {threat.threat_name}: {threat.disruption_score:.0f}% risk")
    print(f"    Timeline: {threat.timeline_to_impact} days")
    print(f"    Response: {threat.recommended_response}")

print(f"\nEarly Warning Signals:")
for signal in result.early_warning_signals:
    print(f"  📊 {signal}")
```

---

## Integration Examples

### Orchestrator Integration

Add agents to analysis orchestrator for comprehensive strategic reports:

```python
from consultantos.orchestrator import AnalysisOrchestrator
from consultantos.agents.positioning_agent import PositioningAgent
from consultantos.agents.disruption_agent import DisruptionAgent

# Extend orchestrator with Phase 2 agents
class EnhancedOrchestrator(AnalysisOrchestrator):
    async def run_phase2_analysis(self, input_data, phase1_results):
        """Run Phase 2 advanced intelligence analysis"""
        # Extract Phase 1 results
        research_data = phase1_results.get("research")
        market_data = phase1_results.get("market")
        financial_data = phase1_results.get("financial")

        # Gather competitor data
        competitors = await self._gather_competitor_data(input_data)

        # Run positioning analysis
        positioning_agent = PositioningAgent()
        positioning_input = {
            **input_data,
            "market_data": market_data,
            "financial_data": financial_data,
            "research_data": research_data,
            "competitors": competitors
        }
        positioning_result = await positioning_agent.execute(positioning_input)

        # Run disruption analysis
        disruption_agent = DisruptionAgent()
        disruption_input = {
            **input_data,
            "market_data": market_data,
            "financial_data": financial_data,
            "research_data": research_data,
            "competitors": competitors
        }
        disruption_result = await disruption_agent.execute(disruption_input)

        return {
            "positioning": positioning_result,
            "disruption": disruption_result
        }
```

### Dashboard Integration

Display real-time positioning and disruption metrics:

```python
# In dashboard API endpoint
from consultantos.agents.positioning_agent import PositioningAgent
from consultantos.agents.disruption_agent import DisruptionAgent

@app.get("/api/dashboard/competitive-intelligence/{company}")
async def get_competitive_intelligence(company: str, industry: str):
    """Get competitive positioning and disruption risk"""
    # Gather integrated data
    data = await gather_integrated_data(company, industry)

    # Run agents in parallel
    positioning_agent = PositioningAgent()
    disruption_agent = DisruptionAgent()

    positioning_task = asyncio.create_task(positioning_agent.execute(data))
    disruption_task = asyncio.create_task(disruption_agent.execute(data))

    positioning_result, disruption_result = await asyncio.gather(
        positioning_task,
        disruption_task
    )

    return {
        "company": company,
        "positioning": {
            "coordinates": {
                "x": positioning_result.current_position.x_value,
                "y": positioning_result.current_position.y_value
            },
            "velocity": positioning_result.velocity,
            "collision_risk": positioning_result.collision_risk,
            "threats": len(positioning_result.position_threats)
        },
        "disruption": {
            "overall_risk": disruption_result.overall_risk,
            "risk_level": disruption_result.risk_level,
            "risk_trend": disruption_result.risk_trend,
            "vulnerability": disruption_result.vulnerability_breakdown
        },
        "timestamp": datetime.utcnow().isoformat()
    }
```

---

## API Endpoints

### Create Positioning Analysis

**Endpoint**: `POST /api/positioning/analyze`

**Request**:
```json
{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "competitors": ["Rivian", "Lucid Motors", "Ford"]
}
```

**Response**:
```json
{
    "success": true,
    "positioning_analysis": { ... },
    "execution_time_ms": 2500
}
```

### Create Disruption Assessment

**Endpoint**: `POST /api/disruption/assess`

**Request**:
```json
{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "competitors": ["BYD", "NIO", "Rivian"]
}
```

**Response**:
```json
{
    "success": true,
    "disruption_assessment": { ... },
    "execution_time_ms": 3000
}
```

---

## Testing

Run comprehensive test suite:

```bash
# Run all Phase 2 agent tests
pytest tests/test_phase2_critical_agents.py -v

# Run specific test classes
pytest tests/test_phase2_critical_agents.py::TestPositioningAgent -v
pytest tests/test_phase2_critical_agents.py::TestDisruptionAgent -v

# Run with coverage
pytest tests/test_phase2_critical_agents.py --cov=consultantos.agents --cov-report=html
```

### Test Structure

- **Unit Tests**: Agent-specific logic (position calculation, scoring)
- **Integration Tests**: Agent interaction with Phase 1 data
- **Mock Tests**: External dependencies mocked (LLM calls, data sources)

---

## Deployment

### Environment Variables

No additional environment variables required beyond Phase 1:

- `GEMINI_API_KEY` - For LLM-based recommendations
- `TAVILY_API_KEY` - For web research (used by ResearchAgent)

### Production Considerations

1. **Timeout Configuration**
   - PositioningAgent: 90 seconds (default)
   - DisruptionAgent: 90 seconds (default)

2. **Competitor Data Volume**
   - Recommend max 5 competitors per analysis
   - Batch processing for large competitor sets

3. **Caching Strategy**
   - Cache competitor data for 1 hour
   - Cache positioning results for 30 minutes
   - Cache disruption assessments for 1 hour

4. **Error Handling**
   - Graceful degradation if Phase 1 data incomplete
   - Fallback recommendations if LLM fails
   - Partial results on timeout

### Performance Optimization

```python
# Parallel competitor data gathering
async def gather_competitor_data_parallel(competitors, agents):
    """Gather competitor data in parallel for efficiency"""
    tasks = []
    for comp in competitors:
        comp_input = {"company": comp, "industry": "..."}
        tasks.append(asyncio.gather(
            agents["research"].execute(comp_input),
            agents["market"].execute(comp_input),
            agents["financial"].execute(comp_input)
        ))

    results = await asyncio.gather(*tasks)

    return [
        {
            "name": comp,
            "research_data": res[0],
            "market_data": res[1],
            "financial_data": res[2]
        }
        for comp, res in zip(competitors, results)
    ]
```

---

## Key Takeaways

### PositioningAgent

✅ **Strengths**:
- Visual competitive landscape mapping
- Movement vector prediction
- Collision detection and threat warnings
- White space opportunity identification

⚠️ **Limitations**:
- Requires historical data for accurate trajectories
- Clustering quality depends on competitor data volume
- 6-month predictions are estimates

### DisruptionAgent

✅ **Strengths**:
- Christensen framework authenticity
- Multi-dimensional vulnerability scoring
- Early warning signal identification
- Technology trend detection

⚠️ **Limitations**:
- Scoring weights are configurable but defaults work well
- Requires rich market and sentiment data
- Job misalignment inference is heuristic-based

### Integration Best Practices

1. **Always run Phase 1 agents first** - Both agents depend on Phase 1 data
2. **Gather competitor data in parallel** - Reduces total execution time
3. **Cache intelligently** - Competitor data changes slowly
4. **Monitor LLM costs** - Recommendations use LLM, cache where possible
5. **Validate data quality** - Low confidence scores indicate data gaps

---

## Support & Contributions

For issues or feature requests, please file a GitHub issue with:
- Agent name (PositioningAgent or DisruptionAgent)
- Input data sample (redacted)
- Expected vs actual behavior
- Error logs if applicable

**Next Steps**: Integrate these agents into monitoring system for continuous competitive intelligence tracking.
