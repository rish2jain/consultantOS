"""
Research Agent - Gathers company intelligence using Tavily
"""
from typing import Dict, Any
from consultantos.agents.base_agent import BaseAgent
from consultantos.models import CompanyResearch
from consultantos.tools import tavily_search_tool


class ResearchAgent(BaseAgent):
    """Research agent for gathering company information"""
    
    def __init__(self, timeout: int = 60):
        super().__init__(
            name="research_agent",
            model="gemini-2.0-flash-exp",
            timeout=timeout
        )
        self.instruction = """
        You are a business research specialist with expertise in:
        - Company intelligence gathering
        - Competitive landscape analysis
        - News monitoring and trend identification

        Gather comprehensive information about companies using web search.
        Focus on: company overview, recent news, market position, products/services.
        Cite all sources with URLs.
        """
    
    async def _execute_internal(self, input_data: Dict[str, Any]) -> CompanyResearch:
        """Execute research task"""
        company = input_data.get("company", "")
        
        # Search for company information
        search_query = f"{company} company overview business model products services competitors"
        search_results = tavily_search_tool(search_query, max_results=10)
        
        # Check for errors in search results
        if search_results.get("error"):
            # Return partial result with error note
            return CompanyResearch(
                company_name=company,
                description=f"Research partially available for {company}. Some data sources unavailable.",
                products_services=[],
                target_market="Unknown",
                key_competitors=[],
                recent_news=[],
                sources=[r.get("url", "") for r in search_results.get("results", [])]
            )
        
        # Format research data for LLM
        research_context = self._format_search_results(search_results)
        
        # Use structured output to extract company research
        prompt = f"""
        {self.instruction}
        
        Research the following company: {company}
        
        Search Results:
        {research_context}
        
        Extract and structure the following information:
        1. Company name
        2. Description (2-3 sentences)
        3. Products/services (list)
        4. Target market
        5. Key competitors (list)
        6. Recent news (3-5 items)
        7. Sources (URLs from search results)
        """
        
        try:
            result = self.structured_client.chat.completions.create(
                model=self.model,
                response_model=CompanyResearch,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return result
        except Exception as e:
            # Fallback to basic structure if structured output fails
            return CompanyResearch(
                company_name=company,
                description=f"Research gathered for {company}",
                products_services=[],
                target_market="Unknown",
                key_competitors=[],
                recent_news=[],
                sources=[r.get("url", "") for r in search_results.get("results", [])]
            )
    
    def _format_search_results(self, search_results: Dict[str, Any]) -> str:
        """Format search results for LLM consumption"""
        formatted = []
        for result in search_results.get("results", []):
            formatted.append(f"Title: {result.get('title', '')}\nURL: {result.get('url', '')}\nContent: {result.get('content', '')[:500]}\n")
        return "\n".join(formatted)

