"""
Data Flow Manager for ConsultantOS Integration.

Manages data flow between agents, ensuring outputs from one agent
can be properly used as inputs to another, with graceful degradation
when agents are unavailable.
"""
import logging
from typing import Dict, Any, Optional, List
from consultantos.agents import (
    is_agent_available,
    EnhancedForecastingAgent,
    WargamingAgent,
    AnalyticsBuilderAgent,
    StorytellingAgent
)
from consultantos.models.integration import (
    ForecastResult,
    WargameResult,
    Dashboard,
    Narrative,
    ComprehensiveAnalysisResult
)
from consultantos_core.models import FinancialSnapshot, MarketTrendResult

logger = logging.getLogger(__name__)


class DataFlowManager:
    """
    Manages data flow between agents in the integrated system.

    Provides methods to transform outputs from one agent into inputs
    for another, enabling seamless integration and data pipelines.
    """

    @staticmethod
    async def forecast_from_financial_data(
        financial_result: FinancialSnapshot,
        forecast_horizon_days: int = 90
    ) -> Optional[ForecastResult]:
        """
        Create forecast from financial agent output.

        Args:
            financial_result: Financial snapshot from FinancialAgent
            forecast_horizon_days: Number of days to forecast

        Returns:
            Forecast result or None if agent unavailable
        """
        if not is_agent_available("EnhancedForecastingAgent"):
            logger.warning("EnhancedForecastingAgent not available for forecasting")
            return None

        try:
            agent = EnhancedForecastingAgent()

            # Extract historical data from financial snapshot
            historical_data = {
                "current_price": financial_result.current_price,
                "market_cap": financial_result.market_cap,
                "revenue": getattr(financial_result, "revenue", None),
                "earnings": getattr(financial_result, "earnings", None)
            }

            # Execute forecast
            result = await agent.execute({
                "historical_data": historical_data,
                "metric_name": "Revenue",
                "forecast_horizon_days": forecast_horizon_days
            })

            return result

        except Exception as e:
            logger.error(f"Error creating forecast from financial data: {e}", exc_info=True)
            return None

    @staticmethod
    async def wargame_from_market_analysis(
        market_result: MarketTrendResult,
        company: str,
        industry: str
    ) -> Optional[WargameResult]:
        """
        Create wargaming scenarios from market analysis.

        Args:
            market_result: Market trends from MarketAgent
            company: Company name
            industry: Industry sector

        Returns:
            Wargaming result or None if agent unavailable
        """
        if not is_agent_available("WargamingAgent"):
            logger.warning("WargamingAgent not available for wargaming")
            return None

        try:
            agent = WargamingAgent()

            # Build scenario from market data
            scenario = {
                "scenario_name": f"{company} Competitive Scenario",
                "company": company,
                "industry": industry,
                "market_trends": market_result.trends if hasattr(market_result, "trends") else [],
                "emerging_topics": market_result.emerging_topics if hasattr(market_result, "emerging_topics") else [],
                "competitive_context": {
                    "industry": industry,
                    "market_dynamics": getattr(market_result, "market_dynamics", {})
                }
            }

            result = await agent.simulate_scenario(scenario)
            return result

        except Exception as e:
            logger.error(f"Error creating wargame from market analysis: {e}", exc_info=True)
            return None

    @staticmethod
    async def dashboard_from_all_results(
        results: ComprehensiveAnalysisResult,
        dashboard_type: str = "executive"
    ) -> Optional[Dashboard]:
        """
        Build dashboard from all analysis results.

        Args:
            results: Comprehensive analysis results
            dashboard_type: Type of dashboard (executive, technical, operational)

        Returns:
            Dashboard specification or None if agent unavailable
        """
        if not is_agent_available("AnalyticsBuilderAgent"):
            logger.warning("AnalyticsBuilderAgent not available for dashboard creation")
            return None

        try:
            agent = AnalyticsBuilderAgent()

            # Prepare data for dashboard
            dashboard_data = {
                "company": results.company,
                "industry": results.industry,
                "timestamp": results.timestamp.isoformat(),
                "phase1": results.phase1.dict() if results.phase1 else {},
                "phase2": results.phase2.dict() if results.phase2 else {},
                "confidence_score": results.confidence_score
            }

            # Create dashboard from template
            dashboard = await agent.create_from_template(
                template_name=dashboard_type,
                data=dashboard_data
            )

            return dashboard

        except Exception as e:
            logger.error(f"Error creating dashboard from results: {e}", exc_info=True)
            return None

    @staticmethod
    async def narratives_from_results(
        results: ComprehensiveAnalysisResult,
        personas: List[str] = None
    ) -> Dict[str, Narrative]:
        """
        Generate persona-specific narratives from analysis results.

        Args:
            results: Comprehensive analysis results
            personas: Target personas (default: ["executive", "technical"])

        Returns:
            Dictionary of narratives by persona
        """
        if not is_agent_available("StorytellingAgent"):
            logger.warning("StorytellingAgent not available for narrative generation")
            return {}

        if personas is None:
            personas = ["executive", "technical"]

        try:
            agent = StorytellingAgent()
            narratives = {}

            for persona in personas:
                try:
                    narrative = await agent.generate_narrative(
                        data=results.dict(),
                        persona=persona
                    )
                    narratives[persona] = narrative
                except Exception as e:
                    logger.error(f"Error generating narrative for {persona}: {e}")
                    continue

            return narratives

        except Exception as e:
            logger.error(f"Error generating narratives: {e}", exc_info=True)
            return {}

    @staticmethod
    def extract_key_metrics(results: ComprehensiveAnalysisResult) -> Dict[str, Any]:
        """
        Extract key metrics from comprehensive results for quick access.

        Args:
            results: Comprehensive analysis results

        Returns:
            Dictionary of key metrics
        """
        metrics = {
            "company": results.company,
            "industry": results.industry,
            "confidence_score": results.confidence_score,
            "partial_results": results.partial_results,
            "timestamp": results.timestamp.isoformat()
        }

        # Phase 1 metrics
        if results.phase1:
            if results.phase1.financial:
                metrics["market_cap"] = getattr(results.phase1.financial, "market_cap", None)
                metrics["current_price"] = getattr(results.phase1.financial, "current_price", None)

            if results.phase1.synthesis:
                metrics["overall_assessment"] = getattr(results.phase1.synthesis, "summary", None)

        # Phase 2 metrics
        if results.phase2:
            if results.phase2.forecast:
                metrics["forecast_available"] = True
                metrics["forecast_horizon"] = results.phase2.forecast.forecast_horizon_days

            if results.phase2.social_media:
                metrics["sentiment_score"] = results.phase2.social_media.sentiment_score
                metrics["overall_sentiment"] = results.phase2.social_media.overall_sentiment

        return metrics

    @staticmethod
    def build_data_pipeline(
        company: str,
        industry: str,
        enable_features: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Build execution pipeline for enabled features.

        Args:
            company: Company name
            industry: Industry sector
            enable_features: List of feature names to enable

        Returns:
            List of pipeline stages with dependencies
        """
        pipeline = []

        # Phase 1: Core research (always included)
        pipeline.append({
            "phase": 1,
            "stage": "core_research",
            "agents": ["ResearchAgent", "MarketAgent", "FinancialAgent"],
            "parallel": True,
            "dependencies": []
        })

        pipeline.append({
            "phase": 1,
            "stage": "framework_analysis",
            "agents": ["FrameworkAgent"],
            "parallel": False,
            "dependencies": ["core_research"]
        })

        pipeline.append({
            "phase": 1,
            "stage": "synthesis",
            "agents": ["SynthesisAgent"],
            "parallel": False,
            "dependencies": ["framework_analysis"]
        })

        # Phase 2: Advanced analytics (conditional)
        phase2_agents = []

        if "forecasting" in enable_features and is_agent_available("EnhancedForecastingAgent"):
            phase2_agents.append("EnhancedForecastingAgent")

        if "social_media" in enable_features and is_agent_available("SocialMediaAgent"):
            phase2_agents.append("SocialMediaAgent")

        if "dark_data" in enable_features and is_agent_available("DarkDataAgent"):
            phase2_agents.append("DarkDataAgent")

        if "wargaming" in enable_features and is_agent_available("WargamingAgent"):
            phase2_agents.append("WargamingAgent")

        if phase2_agents:
            pipeline.append({
                "phase": 2,
                "stage": "advanced_analytics",
                "agents": phase2_agents,
                "parallel": True,
                "dependencies": ["synthesis"]
            })

        # Phase 3: Output generation (conditional)
        phase3_agents = []

        if "dashboard" in enable_features and is_agent_available("AnalyticsBuilderAgent"):
            phase3_agents.append("AnalyticsBuilderAgent")

        if "narratives" in enable_features and is_agent_available("StorytellingAgent"):
            phase3_agents.append("StorytellingAgent")

        if phase3_agents:
            pipeline.append({
                "phase": 3,
                "stage": "output_generation",
                "agents": phase3_agents,
                "parallel": True,
                "dependencies": ["advanced_analytics"] if phase2_agents else ["synthesis"]
            })

        return pipeline

    @staticmethod
    def validate_data_flow(
        source_agent: str,
        target_agent: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Validate that data can flow from source to target agent.

        Args:
            source_agent: Source agent name
            target_agent: Target agent name
            data: Data to validate

        Returns:
            True if data flow is valid
        """
        # Define required fields for each agent
        agent_requirements = {
            "EnhancedForecastingAgent": ["historical_data", "metric_name"],
            "WargamingAgent": ["scenario_name", "competitive_context"],
            "AnalyticsBuilderAgent": ["company", "industry"],
            "StorytellingAgent": ["company", "industry"]
        }

        if target_agent not in agent_requirements:
            return True  # No specific requirements

        required_fields = agent_requirements[target_agent]
        return all(field in data for field in required_fields)
