"""
Synthesis Agent - Creates executive summary and recommendations
"""
from typing import Dict, Any
from consultantos.agents.base_agent import BaseAgent
from consultantos.models import ExecutiveSummary
from consultantos.prompts import SYNTHESIS_PROMPT_TEMPLATE


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
        """Execute synthesis task"""
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
            result = self.structured_client.chat.completions.create(
                model=self.model,
                response_model=ExecutiveSummary,
                messages=[{"role": "user", "content": prompt}]
            )
            # Ensure company name and industry are set
            result.company_name = company
            result.industry = industry or "Unknown"
            return result
        except Exception as e:
            # Fallback
            return ExecutiveSummary(
                company_name=company,
                industry=industry or "Unknown",
                key_findings=["Analysis completed", "Review recommended"],
                strategic_recommendation="Further analysis recommended",
                confidence_score=0.5,
                supporting_evidence=[],
                next_steps=["Review detailed analysis", "Validate findings"]
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

