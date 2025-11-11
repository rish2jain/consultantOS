"""
Integration endpoints for comprehensive analysis.

Provides end-to-end workflow endpoints that tie together all agents
from Phase 1 (core research), Phase 2 (advanced analytics), and
Phase 3 (output generation).
"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from consultantos.orchestrator.orchestrator import AnalysisOrchestrator
from consultantos.models.integration import (
    ComprehensiveAnalysisRequest,
    ComprehensiveAnalysisResult,
    ConversationalQueryRequest,
    ConversationalQueryResponse,
    IntegrationHealthCheck
)
from consultantos.agents import get_available_agents, is_agent_available
from consultantos.database import get_db_service
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/integration", tags=["integration"])


@router.post("/comprehensive-analysis", response_model=ComprehensiveAnalysisResult)
async def comprehensive_analysis(
    request: ComprehensiveAnalysisRequest
) -> ComprehensiveAnalysisResult:
    """
    Execute comprehensive analysis using all enabled agents.

    This is the main integration endpoint that orchestrates:
    - Phase 1: Core research (Research, Market, Financial, Framework, Synthesis)
    - Phase 2: Advanced analytics (Forecasting, Social Media, Dark Data, Wargaming)
    - Phase 3: Output generation (Dashboard, Narratives)

    Features are enabled/disabled based on request flags and agent availability.
    Returns gracefully degraded results if some agents fail.

    Args:
        request: Comprehensive analysis request with feature flags

    Returns:
        Complete analysis result with all phases

    Raises:
        HTTPException: If core analysis fails completely
    """
    try:
        orchestrator = AnalysisOrchestrator()

        logger.info(
            f"Starting comprehensive analysis for {request.company} "
            f"with features: forecasting={request.enable_forecasting}, "
            f"social_media={request.enable_social_media}, "
            f"dark_data={request.enable_dark_data}, "
            f"wargaming={request.enable_wargaming}"
        )

        result = await orchestrator.execute_comprehensive_analysis(
            company=request.company,
            industry=request.industry,
            enable_forecasting=request.enable_forecasting,
            enable_social_media=request.enable_social_media,
            enable_dark_data=request.enable_dark_data,
            enable_wargaming=request.enable_wargaming,
            enable_dashboard=request.generate_dashboard,
            enable_narratives=request.generate_narratives,
            narrative_personas=request.narrative_personas,
            forecast_horizon_days=request.forecast_horizon_days,
            frameworks=request.frameworks,
            depth=request.depth
        )

        # Store in Firestore if available
        try:
            await store_comprehensive_analysis(result)
        except Exception as e:
            logger.warning(f"Failed to store analysis in Firestore: {e}")

        logger.info(
            f"Comprehensive analysis completed for {request.company}. "
            f"ID: {result.analysis_id}, Confidence: {result.confidence_score:.2f}"
        )

        return result

    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Comprehensive analysis failed: {str(e)}"
        )


@router.get("/analysis/{analysis_id}", response_model=ComprehensiveAnalysisResult)
async def get_analysis(analysis_id: str):
    """
    Retrieve a comprehensive analysis by ID.

    Args:
        analysis_id: Unique analysis identifier

    Returns:
        Comprehensive analysis result

    Raises:
        HTTPException: If analysis not found
    """
    try:
        result = await retrieve_comprehensive_analysis(analysis_id)

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis {analysis_id} not found"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve analysis {analysis_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve analysis: {str(e)}"
        )


@router.post("/chat-with-analysis/{analysis_id}", response_model=ConversationalQueryResponse)
async def chat_with_analysis(
    analysis_id: str,
    request: ConversationalQueryRequest
):
    """
    Chat about a specific analysis using conversational agent with RAG.

    The analysis is indexed for retrieval-augmented generation, allowing
    natural language queries about the results.

    Args:
        analysis_id: Analysis to query
        request: Conversational query request

    Returns:
        Conversational response with sources

    Raises:
        HTTPException: If analysis not found or conversational agent unavailable
    """
    if not is_agent_available("ConversationalAgent"):
        raise HTTPException(
            status_code=503,
            detail="Conversational agent not available. Install required dependencies."
        )

    try:
        # Retrieve analysis
        analysis = await retrieve_comprehensive_analysis(analysis_id)

        if not analysis:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis {analysis_id} not found"
            )

        # Index for RAG if not already done
        if not analysis.indexed_for_rag:
            await index_analysis_for_rag(analysis)

        # Use conversational agent
        from consultantos.agents import ConversationalAgent
        conv_agent = ConversationalAgent()

        response = await conv_agent.execute({
            "query": request.query,
            "conversation_id": request.conversation_id,
            "use_rag": request.use_rag,
            "analysis_context": analysis.dict()
        })

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversational query failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Conversational query failed: {str(e)}"
        )


@router.get("/health", response_model=IntegrationHealthCheck)
async def integration_health_check():
    """
    Check health and availability of integrated system.

    Returns status of all agents and system capabilities.

    Returns:
        Health check result with agent availability
    """
    try:
        available_agents_info = get_available_agents()

        available = available_agents_info["core"] + available_agents_info["advanced"]
        unavailable = []

        # Check which advanced agents are unavailable
        all_advanced_agents = [
            "ConversationalAgent",
            "EnhancedForecastingAgent",
            "DarkDataAgent",
            "SocialMediaAgent",
            "WargamingAgent",
            "AnalyticsBuilderAgent",
            "StorytellingAgent"
        ]

        for agent_name in all_advanced_agents:
            if not is_agent_available(agent_name):
                unavailable.append(agent_name)

        # Determine overall status
        if len(available_agents_info["core"]) == 6:  # All core agents available
            if len(unavailable) == 0:
                status = "healthy"
            else:
                status = "degraded"
        else:
            status = "unavailable"

        # System capabilities
        capabilities = {
            "core_research": len(available_agents_info["core"]) == 6,
            "forecasting": is_agent_available("EnhancedForecastingAgent"),
            "social_media": is_agent_available("SocialMediaAgent"),
            "dark_data": is_agent_available("DarkDataAgent"),
            "wargaming": is_agent_available("WargamingAgent"),
            "dashboard": is_agent_available("AnalyticsBuilderAgent"),
            "narratives": is_agent_available("StorytellingAgent"),
            "conversational": is_agent_available("ConversationalAgent")
        }

        # Agent details
        agent_details = {}
        for agent in available:
            agent_details[agent] = {
                "status": "available",
                "type": "core" if agent in available_agents_info["core"] else "advanced"
            }

        for agent in unavailable:
            agent_details[agent] = {
                "status": "unavailable",
                "type": "advanced",
                "reason": "missing_dependencies"
            }

        return IntegrationHealthCheck(
            status=status,
            available_agents=available,
            unavailable_agents=unavailable,
            agent_details=agent_details,
            system_capabilities=capabilities,
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


async def store_comprehensive_analysis(result: ComprehensiveAnalysisResult):
    """
    Store comprehensive analysis in Firestore.

    Args:
        result: Comprehensive analysis result to store
    """
    try:
        db = get_db_service()
        if not db:
            logger.warning("Firestore not available, skipping storage")
            return

        # Store in comprehensive_analyses collection
        doc_ref = db.collection("comprehensive_analyses").document(result.analysis_id)

        await doc_ref.set(result.dict())

        logger.info(f"Stored comprehensive analysis {result.analysis_id}")

    except Exception as e:
        logger.error(f"Failed to store comprehensive analysis: {e}", exc_info=True)
        raise


async def retrieve_comprehensive_analysis(analysis_id: str) -> Optional[ComprehensiveAnalysisResult]:
    """
    Retrieve comprehensive analysis from Firestore.

    Args:
        analysis_id: Analysis ID to retrieve

    Returns:
        Comprehensive analysis result or None if not found
    """
    try:
        db = get_db_service()
        if not db:
            logger.warning("Firestore not available")
            return None

        doc_ref = db.collection("comprehensive_analyses").document(analysis_id)
        doc = await doc_ref.get()

        if not doc.exists:
            return None

        return ComprehensiveAnalysisResult(**doc.to_dict())

    except Exception as e:
        logger.error(f"Failed to retrieve comprehensive analysis: {e}", exc_info=True)
        return None


async def index_analysis_for_rag(analysis: ComprehensiveAnalysisResult):
    """
    Index analysis for RAG-based conversational queries.

    Args:
        analysis: Comprehensive analysis to index
    """
    if not is_agent_available("ConversationalAgent"):
        logger.warning("ConversationalAgent not available for indexing")
        return

    try:
        from consultantos.agents import ConversationalAgent
        agent = ConversationalAgent()

        # Index analysis content
        await agent.index_content({
            "analysis_id": analysis.analysis_id,
            "company": analysis.company,
            "industry": analysis.industry,
            "content": analysis.dict()
        })

        # Update indexed flag in Firestore
        analysis.indexed_for_rag = True
        analysis.rag_index_id = analysis.analysis_id

        await store_comprehensive_analysis(analysis)

        logger.info(f"Indexed analysis {analysis.analysis_id} for RAG")

    except Exception as e:
        logger.error(f"Failed to index analysis for RAG: {e}", exc_info=True)
