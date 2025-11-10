"""
Agent router - routes queries to specialized agents based on intent
"""
import logging
from typing import Dict, Any, Optional
from consultantos.routing.query_classifier import QueryClassifier, AgentIntent

logger = logging.getLogger(__name__)


class AgentRouter:
    """Route queries to appropriate specialized agents"""

    def __init__(self):
        """Initialize agent router"""
        self.classifier = QueryClassifier()

    async def classify_query(self, query: str) -> Optional[AgentIntent]:
        """
        Classify query and determine if routing is needed

        Args:
            query: User query text

        Returns:
            AgentIntent if routing needed, None for general RAG response
        """
        intent = self.classifier.classify(query)

        # Return None for GENERAL intent (no routing, use RAG)
        if intent == AgentIntent.GENERAL:
            return None

        return intent

    async def execute_route(
        self,
        intent: AgentIntent,
        query: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute routing to specialized agent

        Args:
            intent: Target agent intent
            query: User query
            input_data: Additional input data for agent

        Returns:
            Agent execution result
        """
        logger.info(f"Routing query to {intent.value} agent")

        # Prepare input data
        if input_data is None:
            input_data = {}
        input_data["query"] = query

        try:
            # Route to appropriate agent
            if intent == AgentIntent.RESEARCH:
                return await self._route_to_research(input_data)

            elif intent == AgentIntent.MARKET:
                return await self._route_to_market(input_data)

            elif intent == AgentIntent.FINANCIAL:
                return await self._route_to_financial(input_data)

            elif intent == AgentIntent.FORECASTING:
                return await self._route_to_forecasting(input_data)

            elif intent == AgentIntent.SOCIAL_MEDIA:
                return await self._route_to_social_media(input_data)

            elif intent == AgentIntent.DARK_DATA:
                return await self._route_to_dark_data(input_data)

            elif intent == AgentIntent.FRAMEWORK:
                return await self._route_to_framework(input_data)

            elif intent == AgentIntent.SYNTHESIS:
                return await self._route_to_synthesis(input_data)

            else:
                logger.warning(f"Unknown intent: {intent}")
                return {
                    "success": False,
                    "error": f"Unknown routing intent: {intent}",
                    "data": None
                }

        except Exception as e:
            logger.error(f"Agent routing failed for {intent.value}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Routing to {intent.value} agent failed: {str(e)}",
                "data": None
            }

    async def _route_to_research(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route to ResearchAgent"""
        from consultantos.agents.research_agent import ResearchAgent
        agent = ResearchAgent()
        return await agent.execute(input_data)

    async def _route_to_market(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route to MarketAgent"""
        from consultantos.agents.market_agent import MarketAgent
        agent = MarketAgent()
        return await agent.execute(input_data)

    async def _route_to_financial(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route to FinancialAgent"""
        from consultantos.agents.financial_agent import FinancialAgent
        agent = FinancialAgent()
        return await agent.execute(input_data)

    async def _route_to_forecasting(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route to ForecastingAgent (MVP)"""
        try:
            from consultantos.agents.forecasting_agent_mvp import ForecastingAgentMVP
            agent = ForecastingAgentMVP()
            return await agent.execute(input_data)
        except ImportError:
            logger.warning("ForecastingAgent not yet implemented")
            return {
                "success": False,
                "error": "Forecasting agent not yet available",
                "data": None
            }

    async def _route_to_social_media(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route to SocialMediaAgent (future)"""
        logger.warning("SocialMediaAgent not yet implemented")
        return {
            "success": False,
            "error": "Social media analysis agent coming soon",
            "data": None
        }

    async def _route_to_dark_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route to DarkDataAgent (future)"""
        logger.warning("DarkDataAgent not yet implemented")
        return {
            "success": False,
            "error": "Dark data analysis agent coming soon",
            "data": None
        }

    async def _route_to_framework(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route to FrameworkAgent"""
        from consultantos.agents.framework_agent import FrameworkAgent
        agent = FrameworkAgent()
        return await agent.execute(input_data)

    async def _route_to_synthesis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route to SynthesisAgent"""
        from consultantos.agents.synthesis_agent import SynthesisAgent
        agent = SynthesisAgent()
        return await agent.execute(input_data)

    def get_routing_info(self, query: str) -> Dict[str, Any]:
        """
        Get routing information without executing

        Args:
            query: User query

        Returns:
            Routing metadata
        """
        return self.classifier.get_routing_metadata(query)
