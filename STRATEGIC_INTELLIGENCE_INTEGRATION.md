# Strategic Intelligence Integration Guide

## Overview

This document describes the integration of advanced strategic intelligence capabilities into ConsultantOS, transforming it from a one-time report generator to a comprehensive continuous competitive intelligence platform.

## Architecture

### Multi-Phase Analysis Pipeline

```
Phase 1: Data Collection (Parallel)
├─ ResearchAgent
├─ MarketAgent
└─ FinancialAgent

Phase 2: Context Enrichment (NEW - Parallel)
├─ get_competitive_context(industry)
└─ calculate_temporal_metrics(historical_snapshots)

Phase 3: Framework Analysis (Sequential)
└─ FrameworkAgent (Porter, SWOT, PESTEL, Blue Ocean)

Phase 4: Strategic Intelligence (NEW - Parallel)
├─ PositioningAgent (competitive positioning & dynamics)
├─ DisruptionAgent (disruption vulnerability assessment)
├─ SystemsAgent (system dynamics & leverage points)
└─ calculate_momentum(flywheel analysis)

Phase 5: Decision Synthesis (NEW)
└─ DecisionIntelligence.generate_brief()

Phase 6: Executive Summary
└─ SynthesisAgent
```

## Models Created

### 1. Positioning Models (`consultantos/models/positioning.py`)

- **CompetitivePosition**: Individual position marker with axes, values, market share
- **PositionTrajectory**: Historical movement and velocity
- **StrategicGroup**: Competitor clustering
- **WhiteSpaceOpportunity**: Uncontested market spaces
- **PositionThreat**: Competitive threats (collision/displacement/encirclement)
- **DynamicPositioning**: Advanced dynamic analysis with vectors
- **PositioningAnalysis**: Complete positioning intelligence

### 2. Disruption Models (`consultantos/models/disruption.py`)

- **DisruptionThreat**: Individual threat with Christensen framework
- **VulnerabilityBreakdown**: Component risk scores
- **TechnologyTrend**: Emerging tech analysis
- **CustomerJobMisalignment**: Jobs-to-be-done gaps
- **BusinessModelShift**: Business model innovation tracking
- **DisruptionAssessment**: Complete vulnerability assessment
- **DisruptionScoreComponents**: Transparent scoring breakdown

### 3. Decision Models (`consultantos/models/decisions.py`)

- **DecisionUrgency**: critical/high/medium/low
- **DecisionCategory**: market_entry, product_launch, pricing, etc.
- **DecisionOption**: Individual option with impact, probability, risks
- **StrategicDecision**: Complete decision analysis with framework insights
- **DecisionBrief**: Executive decision brief with themes

### 4. Systems Models (`consultantos/models/systems.py`)

- **LoopType**: reinforcing/balancing
- **CausalLink**: Causal relationships with polarity and strength
- **FeedbackLoop**: System feedback loop with dynamics
- **LeveragePoint**: Meadows' 12 leverage levels
- **SystemDynamicsAnalysis**: Complete systems analysis

### 5. Momentum Models (`consultantos/models/momentum.py`)

- **MomentumMetric**: Individual metric measurement
- **FlywheelVelocity**: Velocity over time
- **MomentumAnalysis**: Complete flywheel momentum analysis

### 6. Strategic Intelligence Models (`consultantos/models/strategic_intelligence.py`)

- **StrategicHealthScore**: Overall health with component scores
- **EnhancedStrategicReport**: Complete enhanced report
- **StrategicInsight**: Individual insight for feed
- **GeographicExpansionOpportunity**: Geographic expansion analysis

## API Endpoints Created

### Strategic Intelligence Router (`consultantos/api/strategic_intelligence_endpoints.py`)

#### Executive Dashboard
- `GET /api/strategic-intelligence/overview/{monitor_id}` - 30-second executive view
  - Strategic health score and trend
  - Top 3 threats and opportunities
  - Critical decision
  - Component scores

#### Analysis Endpoints
- `GET /api/strategic-intelligence/positioning/{monitor_id}` - Competitive positioning
- `GET /api/strategic-intelligence/disruption/{monitor_id}` - Disruption assessment
- `GET /api/strategic-intelligence/dynamics/{monitor_id}` - System dynamics
- `GET /api/strategic-intelligence/momentum/{monitor_id}` - Flywheel momentum
- `GET /api/strategic-intelligence/decisions/{monitor_id}` - Decision briefs

#### Decision Management
- `POST /api/strategic-intelligence/decisions/{decision_id}/accept` - Accept decision option
  - Tracks for feedback loop

#### Intelligence Feed
- `GET /api/strategic-intelligence/feed` - Live strategic insights feed
  - Filterable by type (threat/opportunity/decision/momentum/disruption)
  - Paginated results

#### Opportunities & Signals
- `GET /api/strategic-intelligence/opportunities/geographic/{monitor_id}` - Geographic expansion
- `GET /api/strategic-intelligence/signals/triangulation/{monitor_id}` - Cross-source validation
- `GET /api/strategic-intelligence/predictions/sentiment/{monitor_id}` - Sentiment predictions

#### Health Check
- `GET /api/strategic-intelligence/health` - Module health status

## Agents Created (Placeholders)

### 1. PositioningAgent (`consultantos/agents/positioning_agent.py`)

**Purpose**: Competitive positioning analysis

**Analyzes**:
- Current competitive position on defined axes
- Competitor positions and strategic groups
- Movement vectors and velocity
- White space opportunities
- Position threats and collision risks

**Framework**: Porter's positioning framework

**Status**: Placeholder - requires Gemini implementation

### 2. DisruptionAgent (`consultantos/agents/disruption_agent.py`)

**Purpose**: Disruption vulnerability assessment

**Analyzes**:
- Jobs-to-be-done analysis
- Overserving assessment
- Asymmetric motivation detection
- Low-end and new-market disruption threats
- Technology shifts and business model innovation

**Framework**: Christensen's disruption theory

**Status**: Placeholder - requires Gemini implementation

### 3. SystemsAgent (`consultantos/agents/systems_agent.py`)

**Purpose**: System dynamics analysis

**Analyzes**:
- System structure (variables, causal links)
- Feedback loops (reinforcing and balancing)
- Leverage points (Meadows' 12 levels)
- System archetypes
- Unintended consequences

**Framework**: Meadows' systems thinking

**Status**: Placeholder - requires Gemini implementation

## Next Steps for Full Implementation

### 1. Implement Strategic Intelligence Agents

Each agent needs to be implemented with Gemini + Instructor for structured outputs:

```python
# Example pattern for PositioningAgent
async def _execute_internal(self, company, industry, **kwargs):
    prompt = f"""
    Analyze competitive positioning for {company} in {industry}.
    
    Context:
    {kwargs.get('research', '')}
    {kwargs.get('market', '')}
    
    Instructions:
    1. Identify the two most important competitive dimensions
    2. Position {company} and competitors on these axes
    3. Calculate market share estimates
    4. Identify white space opportunities
    5. Detect position threats
    """
    
    response = await self.client.chat.completions.create(
        model="gemini-1.5-flash",
        messages=[{"role": "user", "content": prompt}],
        response_model=PositioningAnalysis
    )
    
    return response
```

### 2. Update Analysis Orchestrator

Modify `consultantos/orchestrator/orchestrator.py`:

```python
async def analyze_strategic(self, request):
    """Execute enhanced strategic intelligence analysis"""
    
    # Phase 1-3: Existing analysis
    traditional_result = await self.execute(request)
    
    # Phase 4: Strategic Intelligence (parallel)
    positioning, disruption, systems = await asyncio.gather(
        self.positioning_agent.execute(
            company=request.company,
            industry=request.industry,
            research=traditional_result.research,
            market=traditional_result.market
        ),
        self.disruption_agent.execute(
            company=request.company,
            industry=request.industry,
            research=traditional_result.research,
            market=traditional_result.market,
            financial=traditional_result.financial
        ),
        self.systems_agent.execute(
            company=request.company,
            industry=request.industry,
            frameworks=traditional_result.frameworks
        )
    )
    
    # Phase 5: Calculate momentum
    momentum = calculate_momentum_from_history(request.company)
    
    # Phase 6: Generate decision brief
    decision_brief = await generate_decision_brief(
        positioning, disruption, systems, momentum,
        traditional_result.frameworks
    )
    
    # Phase 7: Calculate strategic health
    health = calculate_strategic_health(
        positioning, disruption, systems, momentum
    )
    
    return EnhancedStrategicReport(
        report_id=str(uuid.uuid4()),
        company=request.company,
        industry=request.industry,
        # Traditional outputs
        research=traditional_result.research,
        market=traditional_result.market,
        financial=traditional_result.financial,
        frameworks=traditional_result.frameworks,
        executive_summary=traditional_result.executive_summary,
        # Enhanced intelligence
        competitive_positioning=positioning,
        disruption_assessment=disruption,
        system_dynamics=systems,
        flywheel_momentum=momentum,
        decision_brief=decision_brief,
        overall_strategic_health=health,
        # Quick view
        top_threats=extract_top_threats(disruption, positioning),
        top_opportunities=extract_top_opportunities(positioning),
        critical_decision=decision_brief.top_decision
    )
```

### 3. Integrate with Monitoring Worker

Modify `consultantos/jobs/monitoring_worker.py`:

```python
async def process_monitor_check(monitor: Monitor):
    """Enhanced monitoring with strategic intelligence"""
    
    # Run analysis
    if monitor.config.enable_strategic_intelligence:
        result = await orchestrator.analyze_strategic(
            AnalysisRequest(
                company=monitor.company,
                industry=monitor.industry,
                frameworks=monitor.config.frameworks
            )
        )
    else:
        result = await orchestrator.execute(...)
    
    # Generate alerts from strategic intelligence
    alerts = []
    
    if result.disruption_assessment:
        if result.disruption_assessment.overall_risk > 70:
            alerts.append(Alert(
                alert_type="HIGH_DISRUPTION_RISK",
                severity=result.disruption_assessment.overall_risk,
                title="High disruption risk detected",
                description=...,
                recommended_actions=result.disruption_assessment.immediate_actions
            ))
    
    if result.competitive_positioning:
        for threat in result.competitive_positioning.position_threats:
            if threat.severity > 75:
                alerts.append(Alert(
                    alert_type="POSITION_THREAT",
                    severity=threat.severity,
                    title=f"Position threat: {threat.threat_type}",
                    description=threat.recommended_response
                ))
    
    if result.decision_brief and result.decision_brief.critical_decisions:
        alerts.append(Alert(
            alert_type="DECISION_REQUIRED",
            severity=100,
            title=f"{len(result.decision_brief.critical_decisions)} critical decisions",
            description="Strategic decisions require immediate attention"
        ))
    
    # Store alerts
    for alert in alerts:
        await db.store_alert(monitor.monitor_id, alert)
```

### 4. Implement Endpoint Logic

Connect endpoints to orchestrator and database:

```python
@router.get("/overview/{monitor_id}")
async def get_strategic_overview(monitor_id, user_id):
    # Get latest analysis for monitor
    analysis = await db.get_latest_analysis(monitor_id)
    
    # Extract strategic overview
    return StrategicOverviewResponse(
        company=analysis.company,
        industry=analysis.industry,
        generated_at=analysis.generated_at,
        strategic_health_score=analysis.overall_strategic_health.overall_health,
        health_level=analysis.overall_strategic_health.health_level,
        health_trend=analysis.overall_strategic_health.trend,
        top_threats=analysis.top_threats,
        top_opportunities=analysis.top_opportunities,
        critical_decision=analysis.critical_decision.decision_question if analysis.critical_decision else None,
        competitive_position_score=analysis.overall_strategic_health.competitive_position_score,
        disruption_risk_score=analysis.disruption_assessment.overall_risk,
        system_health_score=analysis.overall_strategic_health.system_health_score,
        momentum_score=analysis.flywheel_momentum.current_momentum,
        immediate_actions=analysis.overall_strategic_health.immediate_actions
    )
```

### 5. Update Monitor Configuration

Add strategic intelligence toggle to monitor configuration:

```python
class MonitorConfig(BaseModel):
    frequency: str  # hourly, daily, weekly, monthly
    frameworks: List[str]
    alert_threshold: float
    enable_strategic_intelligence: bool = False  # NEW
    strategic_depth: str = "standard"  # quick/standard/deep/comprehensive
```

### 6. Frontend Dashboard Integration

Create dashboard components:
- Strategic health score widget
- Competitive positioning map (interactive)
- Disruption risk gauge
- Decision cards (actionable)
- Momentum trend chart
- Intelligence feed (real-time)

## Configuration Flags

### Monitor-Level Configuration

```python
{
    "enable_strategic_intelligence": true,
    "strategic_depth": "comprehensive",  # quick/standard/deep/comprehensive
    "analysis_components": {
        "positioning": true,
        "disruption": true,
        "systems": true,
        "momentum": true,
        "decisions": true
    },
    "alert_thresholds": {
        "disruption_risk": 70,
        "position_threat_severity": 75,
        "decision_urgency": "high"
    }
}
```

## Testing Strategy

### Unit Tests
- Model validation (Pydantic)
- Agent prompt engineering
- Scoring calculations

### Integration Tests
- Orchestrator phase execution
- Alert generation logic
- Endpoint response formats

### End-to-End Tests
- Monitor creation → analysis → alerts → dashboard
- Decision acceptance flow
- Feed aggregation

## Performance Considerations

### Token Usage
- Strategic intelligence adds ~15-25K tokens per analysis
- Use caching aggressively for repeated analyses
- Consider parallel execution for independent agents

### Rate Limiting
- Strategic intelligence counts as "deep" analysis
- May need separate rate limits for enhanced features
- Consider tiered access (Free: basic, Pro: strategic intelligence)

### Database
- Store strategic intelligence results separately
- Enable partial result storage
- Index on monitor_id, generated_at, health_score

## Deployment Checklist

- [ ] All models defined and tested
- [ ] Agents implemented with Gemini
- [ ] Orchestrator updated with new phases
- [ ] Endpoints connected to database
- [ ] Monitoring worker integrated
- [ ] Frontend dashboard components
- [ ] Documentation updated
- [ ] Tests passing
- [ ] Performance benchmarked
- [ ] Rate limits configured
- [ ] Feature flags enabled

## Current Status

✅ **Completed**:
- All strategic intelligence models defined
- API endpoints created with full documentation
- Models package updated with imports
- Main API router integrated
- Agent placeholders created

⏳ **Pending**:
- Agent implementation with Gemini + Instructor
- Orchestrator enhancement with new phases
- Endpoint logic implementation (database integration)
- Monitoring worker integration
- Frontend dashboard components
- Comprehensive testing

## Support & Resources

- **Models**: `consultantos/models/positioning.py`, `disruption.py`, `decisions.py`, `systems.py`, `momentum.py`, `strategic_intelligence.py`
- **Endpoints**: `consultantos/api/strategic_intelligence_endpoints.py`
- **Agents**: `consultantos/agents/positioning_agent.py`, `disruption_agent.py`, `systems_agent.py`
- **Documentation**: This file + API docs at `/docs`

## Business Frameworks Used

1. **Porter's Five Forces** - Competitive positioning (existing)
2. **Porter's Positioning Framework** - Strategic positioning (new)
3. **Christensen's Disruption Theory** - Disruption assessment (new)
4. **Meadows' Systems Thinking** - System dynamics (new)
5. **Collins' Flywheel** - Momentum analysis (new)
6. **SWOT Analysis** - Strategic context (existing)
7. **Blue Ocean Strategy** - White space opportunities (existing + new)
8. **Taleb's Antifragility** - Decision resilience (new)

---

**Note**: This is a comprehensive integration requiring significant implementation work. The structure is in place, but each agent needs full Gemini-powered implementation with carefully crafted prompts and structured outputs.
