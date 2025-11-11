# Quick Start: Strategic Intelligence Implementation

## For Backend Developers

This guide shows you how to implement the strategic intelligence agents and integrate them into the existing orchestrator.

## Step 1: Implement PositioningAgent (30 minutes)

### Edit: `consultantos/agents/positioning_agent.py`

```python
"""
Competitive Positioning Agent - IMPLEMENTATION
"""
import logging
from typing import Optional
from consultantos.agents.base_agent import BaseAgent
from consultantos.models import (
    CompetitivePosition,
    PositioningAnalysis,
    StrategicGroup,
    WhiteSpaceOpportunity,
    PositionThreat
)

logger = logging.getLogger(__name__)


class PositioningAgent(BaseAgent):
    """Competitive positioning analysis using Porter's framework"""
    
    async def _execute_internal(
        self,
        company: str,
        industry: str,
        **kwargs
    ) -> PositioningAnalysis:
        """Execute competitive positioning analysis"""
        
        research = kwargs.get('research', {})
        market = kwargs.get('market', {})
        competitors = kwargs.get('competitors', [])
        
        # Build context for Gemini
        context = f"""
Company: {company}
Industry: {industry}

Research Summary:
{research.get('summary', 'No research available')}

Market Trends:
{market.get('trends', 'No market data available')}

Known Competitors: {', '.join(competitors) if competitors else 'Unknown'}
"""

        # Create positioning analysis prompt
        prompt = f"""
Analyze competitive positioning for {company} in the {industry} industry.

{context}

TASK: Create comprehensive competitive positioning analysis.

1. COMPETITIVE DIMENSIONS:
   - Identify the TWO most important competitive dimensions for this industry
   - Common dimensions: Price, Quality, Innovation, Scale, Customer Service, Technology
   - Choose dimensions that best differentiate competitors

2. CURRENT POSITION:
   - Position {company} on these dimensions (0-100 scale)
   - Estimate market share based on available data
   - Write clear positioning statement (1 sentence)

3. COMPETITOR POSITIONS:
   - Position each known competitor on same dimensions
   - Estimate their market shares
   - Write positioning statements for each

4. STRATEGIC GROUPS:
   - Cluster competitors into strategic groups (2-4 groups)
   - Identify shared characteristics of each group
   - Calculate distance to white space

5. WHITE SPACE OPPORTUNITIES:
   - Identify uncontested positioning spaces
   - Estimate market potential for each
   - Note entry barriers and required capabilities
   - Assess risk score

6. POSITION THREATS:
   - Identify competitors threatening {company}'s position
   - Classify threat type: collision (head-on), displacement (flanking), encirclement (multi-front)
   - Assess severity and time to impact
   - Recommend defensive responses

Provide detailed, data-driven analysis using structured format.
"""

        # Use Instructor for structured output
        response = await self.client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{"role": "user", "content": prompt}],
            response_model=PositioningAnalysis,
            temperature=0.3  # Lower temperature for factual analysis
        )
        
        logger.info(f"Positioning analysis completed for {company}")
        return response
```

## Step 2: Implement DisruptionAgent (30 minutes)

### Edit: `consultantos/agents/disruption_agent.py`

```python
"""
Disruption Assessment Agent - IMPLEMENTATION
"""
import logging
from consultantos.agents.base_agent import BaseAgent
from consultantos.models import DisruptionAssessment

logger = logging.getLogger(__name__)


class DisruptionAgent(BaseAgent):
    """Disruption vulnerability using Christensen's framework"""
    
    async def _execute_internal(
        self,
        company: str,
        industry: str,
        **kwargs
    ) -> DisruptionAssessment:
        """Execute disruption vulnerability assessment"""
        
        research = kwargs.get('research', {})
        market = kwargs.get('market', {})
        financial = kwargs.get('financial', {})
        
        context = f"""
Company: {company}
Industry: {industry}

Research: {research.get('summary', '')}
Market Trends: {market.get('trends', '')}
Financial Performance: {financial.get('revenue_growth', 'N/A')}
"""

        prompt = f"""
Assess disruption vulnerability for {company} using Christensen's disruption theory.

{context}

FRAMEWORK: Christensen's "Jobs To Be Done" and Disruption Theory

1. JOBS-TO-BE-DONE ANALYSIS:
   - What job are customers hiring {company} to do?
   - Are there unmet jobs or job misalignments?
   - What "jobs" are underserved or overserved?
   - Search for "alternative to {company}" patterns

2. OVERSERVING ASSESSMENT (0-100):
   - Is {company} providing performance customers don't value?
   - Are customers paying for features they don't use?
   - Evidence of feature bloat or complexity complaints?

3. ASYMMETRIC THREAT ANALYSIS:
   - Identify low-end disruptors (serving overshot customers with "good enough")
   - Identify new-market disruptors (creating new customer segments)
   - Identify business model innovators (different value network)
   - Calculate growth velocity vs industry average

4. TECHNOLOGY TRENDS:
   - Emerging technologies enabling disruption
   - Adoption rates among competitors
   - Technology maturity stage
   - Enabler score (0-100)

5. BUSINESS MODEL SHIFTS:
   - Subscription vs ownership trends
   - Platform vs linear models
   - Direct-to-consumer shifts
   - Competitor adoption rates

6. VULNERABILITY SCORING:
   - Overall disruption risk (0-100)
   - Component breakdown:
     * Overserving: 0-30 points
     * Threat velocity: 0-25 points
     * Tech momentum: 0-20 points
     * Job misalignment: 0-15 points
     * Model innovation: 0-10 points
   - Risk level: critical/high/medium/low

7. STRATEGIC RECOMMENDATIONS:
   - Immediate defensive actions
   - Long-term hedge strategies
   - Innovation opportunities to disrupt others
   - Early warning signals to monitor

Provide evidence-based assessment with specific examples.
"""

        response = await self.client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{"role": "user", "content": prompt}],
            response_model=DisruptionAssessment,
            temperature=0.3
        )
        
        logger.info(f"Disruption assessment completed for {company}")
        return response
```

## Step 3: Update Orchestrator (15 minutes)

### Edit: `consultantos/orchestrator/orchestrator.py`

Add at the end of the file:

```python
async def analyze_strategic(self, request: AnalysisRequest) -> dict:
    """
    Execute enhanced strategic intelligence analysis.
    
    Adds strategic intelligence on top of traditional analysis.
    """
    # Phase 1-3: Run traditional analysis
    traditional_result = await self.execute(request)
    
    # Import strategic agents
    from consultantos.agents.positioning_agent import PositioningAgent
    from consultantos.agents.disruption_agent import DisruptionAgent
    
    # Initialize agents
    positioning_agent = PositioningAgent()
    disruption_agent = DisruptionAgent()
    
    # Phase 4: Strategic Intelligence (parallel)
    logger.info(f"Phase 4: Strategic intelligence analysis for {request.company}")
    
    positioning_task = positioning_agent.execute(
        company=request.company,
        industry=request.industry,
        research=traditional_result.research,
        market=traditional_result.market
    )
    
    disruption_task = disruption_agent.execute(
        company=request.company,
        industry=request.industry,
        research=traditional_result.research,
        market=traditional_result.market,
        financial=traditional_result.financial
    )
    
    # Execute in parallel
    positioning, disruption = await asyncio.gather(
        positioning_task,
        disruption_task,
        return_exceptions=True
    )
    
    # Handle errors gracefully
    if isinstance(positioning, Exception):
        logger.error(f"Positioning analysis failed: {positioning}")
        positioning = None
    
    if isinstance(disruption, Exception):
        logger.error(f"Disruption analysis failed: {disruption}")
        disruption = None
    
    # Calculate strategic health
    health_score = 50.0  # Default
    if positioning and disruption:
        # Simple health calculation (can be made more sophisticated)
        position_score = positioning.current_position.y_value if positioning.current_position else 50.0
        resilience_score = 100 - disruption.overall_risk
        health_score = (position_score + resilience_score) / 2
    
    # Build enhanced result
    return {
        **traditional_result.dict(),
        "competitive_positioning": positioning.dict() if positioning else None,
        "disruption_assessment": disruption.dict() if disruption else None,
        "strategic_health_score": health_score,
        "top_threats": disruption.primary_threats[:3] if disruption and disruption.primary_threats else [],
        "top_opportunities": positioning.white_space_opportunities[:3] if positioning else []
    }
```

## Step 4: Update Endpoint (10 minutes)

### Edit: `consultantos/api/strategic_intelligence_endpoints.py`

Replace the overview endpoint:

```python
@router.get("/overview/{monitor_id}", response_model=StrategicOverviewResponse)
async def get_strategic_overview(
    monitor_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get 30-second executive strategic overview"""
    try:
        # Get latest analysis from database
        db = get_db_service()
        latest_analysis = await db.get_latest_analysis(monitor_id)
        
        if not latest_analysis:
            raise HTTPException(404, "No analysis found for this monitor")
        
        # Extract strategic metrics
        return StrategicOverviewResponse(
            company=latest_analysis.get('company'),
            industry=latest_analysis.get('industry'),
            generated_at=latest_analysis.get('generated_at'),
            strategic_health_score=latest_analysis.get('strategic_health_score', 0),
            health_level="strong" if latest_analysis.get('strategic_health_score', 0) > 70 else "stable",
            health_trend="improving",
            top_threats=latest_analysis.get('top_threats', []),
            top_opportunities=latest_analysis.get('top_opportunities', []),
            critical_decision=None,
            competitive_position_score=latest_analysis.get('competitive_positioning', {}).get('current_position', {}).get('y_value', 0) if latest_analysis.get('competitive_positioning') else 0,
            disruption_risk_score=latest_analysis.get('disruption_assessment', {}).get('overall_risk', 0) if latest_analysis.get('disruption_assessment') else 0,
            system_health_score=50.0,  # TODO: Calculate from systems analysis
            momentum_score=50.0,  # TODO: Calculate from momentum analysis
            immediate_actions=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching strategic overview: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to fetch overview: {str(e)}")
```

## Step 5: Test the Implementation (15 minutes)

### Create: `tests/test_strategic_intelligence.py`

```python
"""
Tests for strategic intelligence components
"""
import pytest
from consultantos.agents.positioning_agent import PositioningAgent
from consultantos.agents.disruption_agent import DisruptionAgent
from consultantos.models import AnalysisRequest


@pytest.mark.asyncio
async def test_positioning_agent():
    """Test positioning agent execution"""
    agent = PositioningAgent()
    
    result = await agent.execute(
        company="Tesla",
        industry="Electric Vehicles",
        research={"summary": "Leading EV manufacturer"},
        market={"trends": "Rapid EV adoption"},
        competitors=["Ford", "GM", "Toyota", "BYD"]
    )
    
    assert result.company == "Tesla"
    assert result.current_position is not None
    assert 0 <= result.current_position.x_value <= 100
    assert 0 <= result.current_position.y_value <= 100


@pytest.mark.asyncio
async def test_disruption_agent():
    """Test disruption agent execution"""
    agent = DisruptionAgent()
    
    result = await agent.execute(
        company="Tesla",
        industry="Electric Vehicles",
        research={"summary": "Premium EV maker"},
        market={"trends": "Mass market growth"},
        financial={"revenue_growth": 25.0}
    )
    
    assert result.company == "Tesla"
    assert 0 <= result.overall_risk <= 100
    assert result.risk_level in ["critical", "high", "medium", "low"]
    assert len(result.strategic_recommendations) > 0


@pytest.mark.asyncio
async def test_orchestrator_strategic_analysis():
    """Test orchestrator strategic analysis"""
    from consultantos.orchestrator import AnalysisOrchestrator
    
    orchestrator = AnalysisOrchestrator()
    
    result = await orchestrator.analyze_strategic(
        AnalysisRequest(
            company="Tesla",
            industry="Electric Vehicles",
            frameworks=["porter"]
        )
    )
    
    assert result['company'] == "Tesla"
    assert 'competitive_positioning' in result
    assert 'disruption_assessment' in result
    assert 'strategic_health_score' in result


# Run tests
# pytest tests/test_strategic_intelligence.py -v
```

## Step 6: Try It Out (5 minutes)

### Start the server:

```bash
python main.py
```

### Test the endpoint:

```bash
# Create a test analysis
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter"]
  }'

# Get strategic overview (once monitor is created)
curl http://localhost:8080/api/strategic-intelligence/overview/monitor_123 \
  -H "Authorization: Bearer your_token"
```

### Check Swagger UI:

```
http://localhost:8080/docs#/Strategic%20Intelligence
```

## Common Issues & Solutions

### Issue 1: Gemini API Key Not Set

```bash
# Set in .env
GEMINI_API_KEY=your_key_here
```

### Issue 2: Instructor Import Error

```bash
pip install instructor
```

### Issue 3: Model Validation Errors

Check that your Gemini response matches the Pydantic model structure. Use `temperature=0.3` for more consistent structured outputs.

### Issue 4: Agent Timeout

Increase timeout in BaseAgent or use async timeouts:

```python
response = await asyncio.wait_for(
    self.client.chat.completions.create(...),
    timeout=60.0  # 60 seconds
)
```

## Performance Tips

1. **Cache Agent Results**: Strategic intelligence is expensive. Cache for 1 hour minimum.

2. **Parallel Execution**: Always run positioning and disruption agents in parallel.

3. **Graceful Degradation**: Return partial results if one agent fails.

4. **Token Optimization**: Summarize research/market data before passing to agents.

5. **Rate Limiting**: Track Gemini API usage to avoid rate limits.

## Next Steps

After implementing the basic agents:

1. **Add SystemsAgent** - System dynamics analysis
2. **Add MomentumCalculation** - Flywheel momentum tracking  
3. **Add DecisionIntelligence** - Strategic decision synthesis
4. **Enhance Monitoring** - Alert generation from strategic insights
5. **Build Dashboard** - Frontend visualization components

## Support

- **Documentation**: `STRATEGIC_INTELLIGENCE_INTEGRATION.md`
- **API Reference**: `http://localhost:8080/docs`
- **Models Reference**: `consultantos/models/` directory
- **Examples**: `STRATEGIC_INTELLIGENCE_SUMMARY.md`

---

**Total Implementation Time**: ~90 minutes
**Difficulty**: Medium
**Value**: High - Transforms reporting into continuous intelligence
