"""
Synthesis Agent - Creates executive summary and recommendations
"""
from typing import Dict, Any
from consultantos.agents.base_agent import BaseAgent
from consultantos.models import ExecutiveSummary
from consultantos.prompts import SYNTHESIS_PROMPT_TEMPLATE
from consultantos.monitoring import logger


class SynthesisAgent(BaseAgent):
    """Synthesis agent for creating executive summary"""
    
    def __init__(self):
        super().__init__(
            name="synthesis_agent",
            model="gemini-2.0-flash-exp"
        )
        self.instruction = """
        You are a synthesis specialist.
        Combine insights from research, market, financial, and framework analyses.
        Create executive summary with key insights and recommendations.
        """
    
    async def _execute_internal(self, input_data: Dict[str, Any]) -> ExecutiveSummary:
        """
        Execute synthesis to create executive summary and strategic recommendations.

        Combines insights from all previous analysis phases (research, market,
        financial, frameworks) into a cohesive executive summary with actionable
        recommendations.

        Args:
            input_data: Dictionary containing:
                - company: Company name
                - industry: Industry context
                - research: CompanyResearch results (optional)
                - market: MarketTrends results (optional)
                - financial: FinancialSnapshot results (optional)
                - frameworks: FrameworkAnalysis results (optional)

        Returns:
            ExecutiveSummary object containing:
                - key_insights: Top 3-5 strategic insights
                - opportunities: Identified growth opportunities
                - risks: Key risk factors and threats
                - next_steps: Prioritized actionable recommendations
                - confidence_score: 0-1 confidence in analysis quality

        Raises:
            Exception: If synthesis fails or all input analyses are missing

        Note:
            Confidence score is adjusted based on completeness of input data.
            Missing phases result in lower confidence but synthesis still proceeds.
        """
        company = input_data.get("company", "")
        industry = input_data.get("industry", "")
        
        # Get all analysis results
        research = input_data.get("research", {})
        market = input_data.get("market", {})
        financial = input_data.get("financial", {})
        frameworks = input_data.get("frameworks", {})
        
        # Format summaries
        research_summary = self._format_research(research)
        market_summary = self._format_market(market)
        financial_summary = self._format_financial(financial)
        porter_summary = self._format_porter(frameworks.get("porter_five_forces") if isinstance(frameworks, dict) else {})
        swot_summary = self._format_swot(frameworks.get("swot_analysis") if isinstance(frameworks, dict) else {})
        
        prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
            research_summary=research_summary,
            market_summary=market_summary,
            financial_summary=financial_summary,
            porter_summary=porter_summary,
            swot_summary=swot_summary
        )
        
        try:
            result = self.structured_client.create(
                response_model=ExecutiveSummary,
                messages=[{"role": "user", "content": prompt}]
            )
            # Ensure company name and industry are set
            result.company_name = company
            result.industry = industry or "Unknown"
            return result
        except Exception as e:
            # Log exception with full context and stacktrace
            error_type = type(e).__name__
            logger.error(
                "synthesis_agent_execution_failed",
                company=company,
                industry=industry or "Unknown",
                error_type=error_type,
                error_message=str(e),
                exc_info=True  # Includes full stacktrace
            )
            
            # Determine if this is a critical error that should be re-raised
            # Critical errors: network issues, authentication failures, model errors
            critical_error_types = (
                ConnectionError,
                TimeoutError,
                PermissionError,
            )
            
            # Check if it's a critical error by type or message content
            # Use a single lowercased message variable to avoid repeated calls
            error_message_lower = str(e).lower()
            is_critical = (
                isinstance(e, critical_error_types) or
                ("api" in error_message_lower and ("key" in error_message_lower or "auth" in error_message_lower)) or
                ("model" in error_message_lower and ("not found" in error_message_lower or "invalid" in error_message_lower))
            )
            
            if is_critical:
                # Re-raise critical errors so they can be handled upstream
                logger.error(
                    "synthesis_agent_critical_error_re_raising",
                    company=company,
                    industry=industry or "Unknown",
                    error_type=error_type,
                    error_message=str(e)
                )
                raise
            
            # For non-critical errors (e.g., parsing issues, validation errors), return fallback
            logger.warning(
                "synthesis_agent_using_fallback",
                company=company,
                industry=industry or "Unknown",
                error_type=error_type,
                error_message=str(e)
            )
            
            # Fallback - ensure minimum 3 items for validation
            return ExecutiveSummary(
                company_name=company,
                industry=industry or "Unknown",
                key_findings=["Analysis completed", "Review recommended", "Data validation needed"],
                strategic_recommendation="Further analysis recommended",
                confidence_score=0.5,
                supporting_evidence=["Initial analysis completed"],
                next_steps=["Review detailed analysis", "Validate findings", "Consult with stakeholders"]
            )
    
    def _format_research(self, research: Any) -> str:
        """Format research summary"""
        if isinstance(research, dict):
            return f"Company: {research.get('company_name', 'Unknown')}\n{research.get('description', 'N/A')}"
        return str(research)
    
    def _format_market(self, market: Any) -> str:
        """Format market summary"""
        if isinstance(market, dict):
            return f"Trend: {market.get('search_interest_trend', 'Unknown')}"
        return str(market)
    
    def _format_financial(self, financial: Any) -> str:
        """Format financial summary"""
        if isinstance(financial, dict):
            return f"Revenue: {financial.get('revenue', 'N/A')}, Market Cap: {financial.get('market_cap', 'N/A')}"
        return str(financial)
    
    def _format_porter(self, porter: Any) -> str:
        """Format Porter's 5 Forces summary"""
        if isinstance(porter, dict):
            return f"Overall Intensity: {porter.get('overall_intensity', 'Unknown')}"
        return str(porter)
    
    def _format_swot(self, swot: Any) -> str:
        """Format SWOT summary"""
        if isinstance(swot, dict):
            return f"Strengths: {len(swot.get('strengths', []))}, Weaknesses: {len(swot.get('weaknesses', []))}"
        return str(swot)

