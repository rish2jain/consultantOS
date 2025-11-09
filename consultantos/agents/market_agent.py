"""
Market Agent - Analyzes market trends using Google Trends
"""
from typing import Dict, Any
from consultantos.agents.base_agent import BaseAgent
from consultantos.models import MarketTrends
from consultantos.tools import google_trends_tool


class MarketAgent(BaseAgent):
    """Market analyst agent for trend analysis"""
    
    def __init__(self):
        super().__init__(
            name="market_analyst",
            model="gemini-2.0-flash-exp"
        )
        self.instruction = """
        You are a market trend analyst.
        Analyze market interest trends using Google Trends data.
        Identify: growth trends, seasonal patterns, regional interest, competitive dynamics.
        """
    
    async def _execute_internal(self, input_data: Dict[str, Any]) -> MarketTrends:
        """
        Execute market trend analysis using Google Trends data.

        Analyzes search interest trends, regional patterns, and competitive dynamics
        using pytrends library to gather Google Trends data.

        Args:
            input_data: Dictionary containing:
                - company: Company name to analyze (required, non-empty)
                - industry: Industry for comparative analysis (optional)

        Returns:
            MarketTrends object containing:
                - growth_trajectory: Trend direction (growing, stable, declining)
                - interest_over_time: Time series data of search interest
                - regional_interest: Geographic distribution of interest
                - competitive_landscape: Comparison with competitors
                - insights: Key market insights and patterns

        Raises:
            ValueError: If company name is empty
            Exception: If trends data fetch or LLM analysis fails
        """
        company = input_data.get("company", "").strip()
        
        # Validate company is not empty
        if not company:
            raise ValueError("Company name is required and cannot be empty")
        
        industry = input_data.get("industry", "").strip()
        
        # Build keywords for trends analysis (only non-empty values)
        keywords = [company]
        if industry:
            keywords.append(industry)
        
        # Get trends data with error handling
        try:
            trends_data = google_trends_tool(keywords, timeframe='today 12-m')
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to fetch trends data: {e}")
            raise ValueError(f"Failed to fetch market trends data: {e}")
        
        # Check for errors in response
        if trends_data.get("error"):
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Trends data contains error: {trends_data.get('error')}")
            raise ValueError(f"Market trends data unavailable: {trends_data.get('error')}")
        
        # Use structured output to format market trends
        prompt = f"""
        {self.instruction}
        
        Analyze market trends for: {company}
        Industry: {industry}
        
        Trends Data:
        {self._format_trends_data(trends_data)}
        
        Extract and structure:
        1. Search interest trend (Growing/Stable/Declining)
        2. Interest data (time series)
        3. Geographic distribution
        4. Related searches
        5. Competitive comparison
        """
        
        try:
            result = await self.generate_structured(
                prompt=prompt,
                response_model=MarketTrends
            )
            return result
        except Exception as e:
            # Fallback
            return MarketTrends(
                search_interest_trend=trends_data.get("search_interest_trend", "Unknown"),
                interest_data=trends_data.get("interest_data", {}),
                geographic_distribution=trends_data.get("geographic_distribution", {}),
                related_searches=[],
                competitive_comparison={}
            )
    
    def _format_trends_data(self, trends_data: Dict[str, Any]) -> str:
        """Format trends data for LLM"""
        return f"""
        Trend Direction: {trends_data.get('search_interest_trend', 'Unknown')}
        Keywords Analyzed: {', '.join(trends_data.get('keywords_analyzed', []))}
        Related Queries: {trends_data.get('related_queries', {})}
        """

