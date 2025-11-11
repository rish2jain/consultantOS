"""
Strategic Intelligence API Endpoints

Advanced strategic analysis endpoints providing:
- Competitive positioning and dynamics
- Disruption assessment and threats
- System dynamics and leverage points
- Flywheel momentum tracking
- Strategic decision intelligence
- Executive insights feed
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
import logging
from datetime import datetime

from consultantos.auth import get_current_user
from consultantos.models import (
    PositioningAnalysis,
    DynamicPositioning,
    DisruptionAssessment,
    SystemDynamicsAnalysis,
    MomentumAnalysis,
    DecisionBrief,
    StrategicDecision,
    SI_EnhancedReport,
    StrategicInsight,
    GeographicExpansionOpportunity
)

logger = logging.getLogger(__name__)
router = APIRouter()


# Response Models
class StrategicOverviewResponse(BaseModel):
    """30-second executive strategic overview"""
    company: str
    industry: str
    generated_at: str
    
    # Overall health
    strategic_health_score: float = Field(..., ge=0, le=100, description="Overall health (0-100)")
    health_level: str = Field(..., description="critical/concerning/stable/strong/excellent")
    health_trend: str = Field(..., description="improving/stable/declining")
    
    # Quick insights
    top_threats: List[str] = Field(default_factory=list, max_items=3)
    top_opportunities: List[str] = Field(default_factory=list, max_items=3)
    critical_decision: Optional[str] = None
    
    # Component scores
    competitive_position_score: float = Field(..., ge=0, le=100)
    disruption_risk_score: float = Field(..., ge=0, le=100)
    system_health_score: float = Field(..., ge=0, le=100)
    momentum_score: float = Field(..., ge=0, le=100)
    
    # Immediate actions
    immediate_actions: List[str] = Field(default_factory=list)
    

class IntelligenceFeedResponse(BaseModel):
    """Strategic intelligence feed"""
    insights: List[StrategicInsight]
    total_count: int
    has_more: bool
    

# Endpoints

@router.get("/overview/{monitor_id}", response_model=StrategicOverviewResponse, tags=["Strategic Intelligence"])
async def get_strategic_overview(
    monitor_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get 30-second executive strategic overview.

    Returns:
    - Strategic health score and trend
    - Top 3 threats and opportunities
    - Critical decision requiring attention
    - Component health scores
    - Immediate actions needed
    """
    try:
        from consultantos.database import get_db_service
        from consultantos.orchestrator.strategic_orchestrator import StrategicOrchestrator

        logger.info(f"Fetching strategic overview for monitor {monitor_id}, user {user_id}")

        # Get monitor configuration from database
        db_service = get_db_service()
        monitor_doc = await db_service.get_document("monitors", monitor_id)

        if not monitor_doc:
            raise HTTPException(status_code=404, detail=f"Monitor {monitor_id} not found")

        company = monitor_doc.get("company", "")
        industry = monitor_doc.get("industry", "")

        if not company or not industry:
            raise HTTPException(status_code=400, detail="Monitor missing company or industry data")

        # Generate strategic overview using orchestrator
        orchestrator = StrategicOrchestrator()
        overview = await orchestrator.generate_strategic_overview(
            company=company,
            industry=industry,
            monitor_id=monitor_id
        )

        logger.info(f"Successfully generated strategic overview for {company}")
        return overview

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching strategic overview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch strategic overview: {str(e)}")


@router.get("/positioning/{monitor_id}", response_model=DynamicPositioning, tags=["Strategic Intelligence"])
async def get_competitive_positioning(
    monitor_id: str,
    include_dynamics: bool = Query(False, description="Include dynamic positioning analysis")
):
    """
    Get competitive positioning analysis.

    Returns:
    - Current competitive position
    - Competitor positions
    - Strategic groups and clusters
    - White space opportunities
    - Position threats
    """
    try:
        from consultantos.database import get_db_service
        from consultantos.agents.positioning_agent import PositioningAgent
        from consultantos.orchestrator.orchestrator import AnalysisOrchestrator

        logger.info(f"Fetching competitive positioning for monitor {monitor_id}")

        # Get monitor configuration from database
        db_service = get_db_service()
        monitor_doc = await db_service.get_document("monitors", monitor_id)

        if not monitor_doc:
            raise HTTPException(status_code=404, detail=f"Monitor {monitor_id} not found")

        company = monitor_doc.get("company", "")
        industry = monitor_doc.get("industry", "")

        if not company or not industry:
            raise HTTPException(status_code=400, detail="Monitor missing company or industry data")

        # Run orchestrator to get integrated agent data
        orchestrator = AnalysisOrchestrator()
        analysis_result = await orchestrator.execute_phase_1(
            company=company,
            industry=industry,
            frameworks=["porter", "swot"],
            depth="quick"
        )

        # Initialize positioning agent
        positioning_agent = PositioningAgent()

        # Execute positioning analysis with integrated data
        positioning_result = await positioning_agent.execute({
            "company": company,
            "industry": industry,
            "market_data": analysis_result.get("market_analysis", {}),
            "financial_data": analysis_result.get("financial_analysis", {}),
            "research_data": analysis_result.get("research_summary", {}),
            "competitors": monitor_doc.get("competitors", [])
        })

        logger.info(f"Successfully generated positioning analysis for {company}")
        return positioning_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching competitive positioning: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch positioning: {str(e)}")


@router.get("/disruption/{monitor_id}", response_model=DisruptionAssessment, tags=["Strategic Intelligence"])
async def get_disruption_assessment(monitor_id: str):
    """
    Get disruption vulnerability assessment.

    Returns:
    - Overall disruption risk score
    - Active and emerging threats
    - Vulnerability breakdown
    - Technology trends
    - Customer job misalignments
    - Business model shifts
    - Strategic recommendations
    """
    try:
        from consultantos.database import get_db_service
        from consultantos.agents.disruption_agent import DisruptionAgent
        from consultantos.orchestrator.orchestrator import AnalysisOrchestrator

        logger.info(f"Fetching disruption assessment for monitor {monitor_id}")

        # Get monitor configuration from database
        db_service = get_db_service()
        monitor_doc = await db_service.get_document("monitors", monitor_id)

        if not monitor_doc:
            raise HTTPException(status_code=404, detail=f"Monitor {monitor_id} not found")

        company = monitor_doc.get("company", "")
        industry = monitor_doc.get("industry", "")

        if not company or not industry:
            raise HTTPException(status_code=400, detail="Monitor missing company or industry data")

        # Run orchestrator to get integrated agent data
        orchestrator = AnalysisOrchestrator()
        analysis_result = await orchestrator.execute_phase_1(
            company=company,
            industry=industry,
            frameworks=["porter"],
            depth="quick"
        )

        # Initialize disruption agent
        disruption_agent = DisruptionAgent()

        # Execute disruption analysis
        disruption_result = await disruption_agent.execute({
            "company": company,
            "industry": industry,
            "market_data": analysis_result.get("market_analysis", {}),
            "financial_data": analysis_result.get("financial_analysis", {}),
            "research_data": analysis_result.get("research_summary", {})
        })

        logger.info(f"Successfully generated disruption assessment for {company}")
        return disruption_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching disruption assessment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch disruption assessment: {str(e)}")


@router.get("/dynamics/{monitor_id}", response_model=SystemDynamicsAnalysis, tags=["Strategic Intelligence"])
async def get_system_dynamics(monitor_id: str):
    """
    Get system dynamics analysis (Meadows' framework).

    Returns:
    - Key system variables and causal links
    - Reinforcing and balancing feedback loops
    - Leverage points for intervention
    - System archetypes
    - Structural issues and fundamental solutions
    """
    try:
        from consultantos.database import get_db_service
        from consultantos.agents.systems_agent import SystemsAgent
        from consultantos.orchestrator.orchestrator import AnalysisOrchestrator

        logger.info(f"Fetching system dynamics for monitor {monitor_id}")

        # Get monitor configuration from database
        db_service = get_db_service()
        monitor_doc = await db_service.get_document("monitors", monitor_id)

        if not monitor_doc:
            raise HTTPException(status_code=404, detail=f"Monitor {monitor_id} not found")

        company = monitor_doc.get("company", "")
        industry = monitor_doc.get("industry", "")

        if not company or not industry:
            raise HTTPException(status_code=400, detail="Monitor missing company or industry data")

        # Run orchestrator to get integrated agent data
        orchestrator = AnalysisOrchestrator()
        analysis_result = await orchestrator.execute_phase_1(
            company=company,
            industry=industry,
            frameworks=["porter", "swot"],
            depth="standard"
        )

        # Initialize systems agent
        systems_agent = SystemsAgent()

        # Execute system dynamics analysis
        dynamics_result = await systems_agent.execute({
            "company": company,
            "industry": industry,
            "market_data": analysis_result.get("market_analysis", {}),
            "financial_data": analysis_result.get("financial_analysis", {}),
            "framework_analysis": analysis_result.get("framework_analysis", {})
        })

        logger.info(f"Successfully generated system dynamics analysis for {company}")
        return dynamics_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching system dynamics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch system dynamics: {str(e)}")


@router.get("/momentum/{monitor_id}", response_model=MomentumAnalysis, tags=["Strategic Intelligence"])
async def get_flywheel_momentum(monitor_id: str):
    """
    Get flywheel momentum analysis (Collins' framework).

    Returns:
    - Current momentum score and trend
    - Key contributing metrics
    - Strongest contributors and drag factors
    - Velocity history and patterns
    - Projected momentum (30d/90d)
    - Acceleration opportunities
    """
    try:
        from consultantos.database import get_db_service
        from consultantos.agents.momentum_agent import MomentumAgent
        from consultantos.orchestrator.orchestrator import AnalysisOrchestrator

        logger.info(f"Fetching flywheel momentum for monitor {monitor_id}")

        # Get monitor configuration from database
        db_service = get_db_service()
        monitor_doc = await db_service.get_document("monitors", monitor_id)

        if not monitor_doc:
            raise HTTPException(status_code=404, detail=f"Monitor {monitor_id} not found")

        company = monitor_doc.get("company", "")
        industry = monitor_doc.get("industry", "")

        if not company or not industry:
            raise HTTPException(status_code=400, detail="Monitor missing company or industry data")

        # Run orchestrator to get integrated agent data
        orchestrator = AnalysisOrchestrator()
        analysis_result = await orchestrator.execute_phase_1(
            company=company,
            industry=industry,
            frameworks=["swot"],
            depth="quick"
        )

        # Initialize momentum agent
        momentum_agent = MomentumAgent()

        # Execute momentum analysis
        momentum_result = await momentum_agent.execute({
            "company": company,
            "industry": industry,
            "market_data": analysis_result.get("market_analysis", {}),
            "financial_data": analysis_result.get("financial_analysis", {}),
            "research_data": analysis_result.get("research_summary", {})
        })

        logger.info(f"Successfully generated momentum analysis for {company}")
        return momentum_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching momentum analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch momentum: {str(e)}")


@router.get("/decisions/{monitor_id}", response_model=DecisionBrief, tags=["Strategic Intelligence"])
async def get_decision_briefs(monitor_id: str):
    """
    Get strategic decision briefs.
    
    Returns:
    - Critical and high-priority decisions
    - Decision options with analysis
    - Framework-based insights (Porter, Christensen, Taleb)
    - Strategic themes and resource conflicts
    """
    try:
        logger.info(f"Fetching decision briefs for monitor {monitor_id}")
        
        raise HTTPException(
            status_code=501,
            detail="Decision briefs endpoint not yet implemented. Requires decision intelligence agent."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching decision briefs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch decisions: {str(e)}")


@router.post("/decisions/{decision_id}/accept", tags=["Strategic Intelligence"])
async def accept_decision(
    decision_id: str,
    option_id: str = Query(..., description="Selected option ID"),
    user_id: str = Depends(get_current_user)
):
    """
    User accepts a recommended decision option.
    
    Tracks decision for feedback loop and learning.
    """
    try:
        logger.info(f"User {user_id} accepting decision {decision_id}, option {option_id}")
        
        # TODO: Implement decision tracking
        # - Store decision acceptance
        # - Track outcome over time
        # - Use for improving recommendations
        
        return {
            "status": "accepted",
            "decision_id": decision_id,
            "option_id": option_id,
            "accepted_at": datetime.utcnow().isoformat(),
            "message": "Decision tracking not yet implemented"
        }
        
    except Exception as e:
        logger.error(f"Error accepting decision: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to accept decision: {str(e)}")


@router.get("/feed", response_model=IntelligenceFeedResponse, tags=["Strategic Intelligence"])
async def get_intelligence_feed(
    user_id: str = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100, description="Number of insights to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    insight_type: Optional[str] = Query(None, description="Filter by type: threat/opportunity/decision/momentum/disruption")
):
    """
    Get live strategic intelligence feed.
    
    Returns:
    - Recent strategic insights across all monitors
    - Filtered by type if specified
    - Paginated results
    """
    try:
        logger.info(f"Fetching intelligence feed for user {user_id}, limit={limit}, type={insight_type}")
        
        raise HTTPException(
            status_code=501,
            detail="Intelligence feed endpoint not yet implemented. Requires feed aggregation logic."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching intelligence feed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch feed: {str(e)}")


@router.get("/opportunities/geographic/{monitor_id}", response_model=List[GeographicExpansionOpportunity], tags=["Strategic Intelligence"])
async def get_geographic_opportunities(monitor_id: str):
    """
    Get geographic expansion opportunities.
    
    Returns:
    - Region-specific market analysis
    - Entry barriers and competitive intensity
    - Recommended entry modes
    - Risk factors and time to profitability
    """
    try:
        logger.info(f"Fetching geographic opportunities for monitor {monitor_id}")
        
        raise HTTPException(
            status_code=501,
            detail="Geographic opportunities endpoint not yet implemented."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching geographic opportunities: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch opportunities: {str(e)}")


@router.get("/signals/triangulation/{monitor_id}", tags=["Strategic Intelligence"])
async def get_triangulation_signals(monitor_id: str):
    """
    Get cross-source validation signals.
    
    Returns signals that are validated across multiple data sources
    for higher confidence intelligence.
    """
    try:
        logger.info(f"Fetching triangulation signals for monitor {monitor_id}")
        
        raise HTTPException(
            status_code=501,
            detail="Triangulation signals endpoint not yet implemented."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching triangulation signals: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch signals: {str(e)}")


@router.get("/predictions/sentiment/{monitor_id}", tags=["Strategic Intelligence"])
async def get_sentiment_predictions(monitor_id: str):
    """
    Get sentiment-based performance predictions.
    
    Returns predictions based on sentiment analysis of market,
    customer, and analyst sentiment trends.
    """
    try:
        logger.info(f"Fetching sentiment predictions for monitor {monitor_id}")
        
        raise HTTPException(
            status_code=501,
            detail="Sentiment predictions endpoint not yet implemented."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sentiment predictions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch predictions: {str(e)}")


# Health check endpoint
@router.get("/health", tags=["Strategic Intelligence"])
async def strategic_intelligence_health():
    """Strategic intelligence module health check"""
    return {
        "status": "operational",
        "module": "strategic_intelligence",
        "endpoints_available": [
            "overview",
            "positioning",
            "disruption",
            "dynamics",
            "momentum",
            "decisions",
            "feed",
            "opportunities",
            "signals",
            "predictions"
        ],
        "implementation_status": "endpoints_defined_agents_pending",
        "message": "Strategic intelligence endpoints defined. Requires agent implementation and orchestrator integration."
    }
