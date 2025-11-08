"""
Framework Agent - Applies business frameworks (Porter, SWOT, PESTEL, Blue Ocean)
"""
from typing import Dict, Any, List
from consultantos.agents.base_agent import BaseAgent
from consultantos.models import FrameworkAnalysis, PortersFiveForces, SWOTAnalysis, PESTELAnalysis, BlueOceanStrategy
from consultantos.prompts import (
    PORTER_PROMPT_TEMPLATE,
    SWOT_PROMPT_TEMPLATE,
    PESTEL_PROMPT_TEMPLATE,
    BLUE_OCEAN_PROMPT_TEMPLATE
)


class FrameworkAgent(BaseAgent):
    """Framework analyst agent for applying strategic frameworks"""
    
    def __init__(self):
        super().__init__(
            name="framework_analyst",
            model="gemini-2.0-flash-exp"
        )
        self.instruction = """
        You are a strategic framework expert trained in McKinsey/BCG methodologies.

        Apply rigorous business frameworks:
        - Porter's Five Forces (competitive dynamics)
        - SWOT Analysis (internal/external factors)
        - PESTEL Analysis (macro environment)
        - Blue Ocean Strategy (value innovation)

        Requirements:
        - Evidence-Based: Every claim must cite specific data
        - Quantitative: Use scores, percentages, specific numbers
        - Structured: Follow framework methodology precisely
        - Actionable: Link analysis to strategic implications
        """
    
    async def _execute_internal(self, input_data: Dict[str, Any]) -> FrameworkAnalysis:
        """Execute framework analysis"""
        company = input_data.get("company", "")
        industry = input_data.get("industry", "")
        frameworks = input_data.get("frameworks", ["porter", "swot", "pestel", "blue_ocean"])
        
        # Get context from previous agents
        research = input_data.get("research", {})
        market = input_data.get("market", {})
        financial = input_data.get("financial", {})
        
        # Format context summaries
        research_summary = self._format_research(research)
        market_summary = self._format_market(market)
        financial_summary = self._format_financial(financial)
        
        framework_results = FrameworkAnalysis()
        
        # Apply requested frameworks
        if "porter" in frameworks:
            framework_results.porter_five_forces = await self._analyze_porter(
                company, industry, research_summary, market_summary, financial_summary
            )
        
        if "swot" in frameworks:
            framework_results.swot_analysis = await self._analyze_swot(
                company, research_summary, market_summary, financial_summary
            )
        
        if "pestel" in frameworks:
            framework_results.pestel_analysis = await self._analyze_pestel(
                company, research_summary, market_summary, financial_summary
            )
        
        if "blue_ocean" in frameworks:
            competitors = research.get("key_competitors", []) if isinstance(research, dict) else []
            framework_results.blue_ocean_strategy = await self._analyze_blue_ocean(
                company, industry, competitors, research_summary, market_summary, financial_summary
            )
        
        return framework_results
    
    async def _analyze_porter(self, company: str, industry: str, research: str, market: str, financial: str) -> PortersFiveForces:
        """Analyze using Porter's 5 Forces"""
        prompt = PORTER_PROMPT_TEMPLATE.format(
            company_name=company,
            industry=industry or "Unknown",
            research_summary=research,
            market_summary=market,
            financial_summary=financial
        )
        
        try:
            result = self.structured_client.chat.completions.create(
                model=self.model,
                response_model=PortersFiveForces,
                messages=[{"role": "user", "content": prompt}]
            )
            return result
        except Exception as e:
            # Fallback with default scores
            return PortersFiveForces(
                supplier_power=3.0,
                buyer_power=3.0,
                competitive_rivalry=3.0,
                threat_of_substitutes=3.0,
                threat_of_new_entrants=3.0,
                overall_intensity="Moderate",
                detailed_analysis={}
            )
    
    async def _analyze_swot(self, company: str, research: str, market: str, financial: str) -> SWOTAnalysis:
        """Analyze using SWOT"""
        prompt = SWOT_PROMPT_TEMPLATE.format(
            company_name=company,
            research_summary=research,
            market_summary=market,
            financial_summary=financial
        )
        
        try:
            result = self.structured_client.chat.completions.create(
                model=self.model,
                response_model=SWOTAnalysis,
                messages=[{"role": "user", "content": prompt}]
            )
            return result
        except Exception as e:
            return SWOTAnalysis(
                strengths=["Analysis pending"],
                weaknesses=["Analysis pending"],
                opportunities=["Analysis pending"],
                threats=["Analysis pending"]
            )
    
    async def _analyze_pestel(self, company: str, research: str, market: str, financial: str) -> PESTELAnalysis:
        """Analyze using PESTEL"""
        prompt = PESTEL_PROMPT_TEMPLATE.format(company_name=company)
        
        try:
            result = self.structured_client.chat.completions.create(
                model=self.model,
                response_model=PESTELAnalysis,
                messages=[{"role": "user", "content": prompt}]
            )
            return result
        except Exception as e:
            return PESTELAnalysis(
                political=[],
                economic=[],
                social=[],
                technological=[],
                environmental=[],
                legal=[]
            )
    
    async def _analyze_blue_ocean(self, company: str, industry: str, competitors: List[str], 
                                  research: str, market: str, financial: str) -> BlueOceanStrategy:
        """Analyze using Blue Ocean Strategy"""
        prompt = BLUE_OCEAN_PROMPT_TEMPLATE.format(
            company_name=company,
            industry=industry or "Unknown",
            competitors=", ".join(competitors) if competitors else "Unknown"
        )
        
        try:
            result = self.structured_client.chat.completions.create(
                model=self.model,
                response_model=BlueOceanStrategy,
                messages=[{"role": "user", "content": prompt}]
            )
            return result
        except Exception as e:
            return BlueOceanStrategy(
                eliminate=[],
                reduce=[],
                raise_factors=[],
                create=[]
            )
    
    def _format_research(self, research: Any) -> str:
        """Format research data"""
        if isinstance(research, dict):
            return f"Company: {research.get('company_name', 'Unknown')}\nDescription: {research.get('description', 'N/A')}"
        return str(research)
    
    def _format_market(self, market: Any) -> str:
        """Format market data"""
        if isinstance(market, dict):
            return f"Trend: {market.get('search_interest_trend', 'Unknown')}"
        return str(market)
    
    def _format_financial(self, financial: Any) -> str:
        """Format financial data"""
        if isinstance(financial, dict):
            return f"Revenue: {financial.get('revenue', 'N/A')}\nMarket Cap: {financial.get('market_cap', 'N/A')}"
        return str(financial)

